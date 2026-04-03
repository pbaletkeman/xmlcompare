"""Schema analyzer for xmlcompare.

Parses XSD files and returns metadata that the comparison engine can use
for smarter, type-aware element matching.

Requires ``lxml`` for full XSD introspection; falls back gracefully when
``lxml`` is not available (schema hints simply won't be applied).
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


# XSD namespace
_XSD_NS = 'http://www.w3.org/2001/XMLSchema'
_XSD = f'{{{_XSD_NS}}}'


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ElementInfo:
    """Metadata about a single XSD element declaration."""
    name: str
    min_occurs: int = 1
    max_occurs: Optional[int] = 1          # None means unbounded
    xs_type: Optional[str] = None          # e.g. 'xs:date', 'xs:integer'
    is_required: bool = True
    is_ordered: bool = True                # False if schema allows any order


@dataclass
class SchemaMetadata:
    """Aggregated XSD metadata returned by :func:`analyze_schema`."""
    # element name → ElementInfo for top-level / globally-named elements
    elements: dict = field(default_factory=dict)
    # path (parent/child) → ElementInfo for locally-scoped elements
    path_elements: dict = field(default_factory=dict)

    def get_element_info(self, name: str, path: str = '') -> Optional[ElementInfo]:
        """Look up element metadata by path first, then by bare name."""
        if path and path in self.path_elements:
            return self.path_elements[path]
        return self.elements.get(name)

    def is_unordered_children(self, parent_path: str) -> bool:
        """Return True if the parent element uses xs:all (unordered children)."""
        key = f'_all:{parent_path}'
        return self.path_elements.get(key, False)

    def get_xs_type(self, name: str, path: str = '') -> Optional[str]:
        """Return the XSD simple type name for the element, or None."""
        info = self.get_element_info(name, path)
        return info.xs_type if info else None


# ---------------------------------------------------------------------------
# Broad XSD type categories
# ---------------------------------------------------------------------------

_DATE_TYPES = {
    'date', 'dateTime', 'time', 'gYear', 'gYearMonth', 'gMonth',
    'gMonthDay', 'gDay', 'duration',
}
_NUMERIC_TYPES = {
    'integer', 'int', 'long', 'short', 'byte',
    'unsignedInt', 'unsignedLong', 'unsignedShort', 'unsignedByte',
    'positiveInteger', 'nonNegativeInteger', 'negativeInteger', 'nonPositiveInteger',
    'decimal', 'float', 'double',
}
_BOOLEAN_TYPES = {'boolean'}


def xs_type_category(xs_type: Optional[str]) -> Optional[str]:
    """Return ``'date'``, ``'numeric'``, ``'boolean'``, or ``None``."""
    if xs_type is None:
        return None
    local = xs_type.split(':')[-1]
    if local in _DATE_TYPES:
        return 'date'
    if local in _NUMERIC_TYPES:
        return 'numeric'
    if local in _BOOLEAN_TYPES:
        return 'boolean'
    return None


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _max_occurs(value: Optional[str]) -> Optional[int]:
    """Parse maxOccurs attribute value.  Returns ``None`` for *unbounded*."""
    if value is None:
        return 1
    if value == 'unbounded':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return 1


def _min_occurs(value: Optional[str]) -> int:
    if value is None:
        return 1
    try:
        return int(value)
    except (ValueError, TypeError):
        return 1


def _local_type(type_attr: Optional[str]) -> Optional[str]:
    """Normalise a type attribute (strips prefix if already xs:)."""
    if not type_attr:
        return None
    return type_attr  # Keep as-is (e.g. 'xs:date', 'xs:integer')


def _strip_xsd_prefix(tag: str) -> str:
    return tag.replace(_XSD, 'xs:').replace('{' + _XSD_NS + '}', 'xs:')


# ---------------------------------------------------------------------------
# Main analyzer
# ---------------------------------------------------------------------------

def analyze_schema(xsd_path: str) -> SchemaMetadata:
    """Parse an XSD file and return a :class:`SchemaMetadata` object.

    Works with Python's standard ``xml.etree.ElementTree``; no external
    dependencies required.

    Parameters
    ----------
    xsd_path:
        Path to the XSD file.

    Returns
    -------
    SchemaMetadata
        Metadata about elements declared in the schema.
    """
    meta = SchemaMetadata()
    try:
        tree = ET.parse(xsd_path)
    except (ET.ParseError, OSError):
        return meta

    root = tree.getroot()
    _parse_complex_type_or_sequence(root, meta, parent_path='', parent_tag='')
    return meta


def _parse_element(elem_node, meta: SchemaMetadata, parent_path: str) -> None:
    """Recursively process a single xs:element node."""
    name = elem_node.get('name')
    if not name:
        return  # ref= elements without a local name – skip

    path = f"{parent_path}/{name}" if parent_path else name
    min_occ = _min_occurs(elem_node.get('minOccurs'))
    max_occ = _max_occurs(elem_node.get('maxOccurs'))
    xs_type = _local_type(elem_node.get('type'))

    # Resolve simple type if inlined
    simple_type = elem_node.find(f'{_XSD}simpleType')
    if simple_type is not None:
        restriction = simple_type.find(f'{_XSD}restriction')
        if restriction is not None:
            base = restriction.get('base')
            if base:
                xs_type = base

    info = ElementInfo(
        name=name,
        min_occurs=min_occ,
        max_occurs=max_occ,
        xs_type=xs_type,
        is_required=(min_occ > 0),
    )

    # Store in both registries
    meta.elements[name] = info
    meta.path_elements[path] = info

    # Recurse into complexType / sequence / all / choice
    complex_type = elem_node.find(f'{_XSD}complexType')
    if complex_type is not None:
        _parse_complex_type_or_sequence(complex_type, meta, parent_path=path, parent_tag=name)


def _parse_complex_type_or_sequence(node, meta: SchemaMetadata,
                                    parent_path: str, parent_tag: str) -> None:
    """Walk xs:sequence, xs:all, xs:choice, xs:complexType nodes."""
    tag = node.tag
    if tag == f'{_XSD}all':
        _parse_all_group(node, meta, parent_path, parent_tag)
    elif tag in (f'{_XSD}sequence', f'{_XSD}choice'):
        _parse_sequence_or_choice(node, meta, parent_path, parent_tag)
    elif tag == f'{_XSD}complexType':
        _parse_complex_type_children(node, meta, parent_path, parent_tag)
    elif tag in (f'{_XSD}complexContent', f'{_XSD}simpleContent'):
        _parse_content_children(node, meta, parent_path, parent_tag)
    elif tag in (f'{_XSD}extension', f'{_XSD}restriction'):
        _parse_extension_or_restriction(node, meta, parent_path, parent_tag)
    elif tag == f'{_XSD}schema':
        _parse_schema_root(node, meta)


def _parse_all_group(node, meta: SchemaMetadata, parent_path: str, parent_tag: str) -> None:
    """Handle xs:all — children may appear in any order."""
    if parent_path:
        meta.path_elements[f'_all:{parent_path}'] = True
    for child in node:
        if child.tag == f'{_XSD}element':
            _parse_element(child, meta, parent_path)


def _parse_sequence_or_choice(node, meta: SchemaMetadata, parent_path: str, parent_tag: str) -> None:
    """Handle xs:sequence or xs:choice children."""
    for child in node:
        if child.tag == f'{_XSD}element':
            _parse_element(child, meta, parent_path)
        elif child.tag in (f'{_XSD}sequence', f'{_XSD}all', f'{_XSD}choice'):
            _parse_complex_type_or_sequence(child, meta, parent_path, parent_tag)


def _parse_complex_type_children(node, meta: SchemaMetadata, parent_path: str, parent_tag: str) -> None:
    """Handle children of xs:complexType."""
    _COMPLEX_CHILDREN = (
        f'{_XSD}sequence', f'{_XSD}all', f'{_XSD}choice',
        f'{_XSD}complexContent', f'{_XSD}simpleContent',
    )
    for child in node:
        if child.tag in _COMPLEX_CHILDREN:
            _parse_complex_type_or_sequence(child, meta, parent_path, parent_tag)


def _parse_content_children(node, meta: SchemaMetadata, parent_path: str, parent_tag: str) -> None:
    """Handle children of xs:complexContent or xs:simpleContent."""
    for child in node:
        if child.tag in (f'{_XSD}extension', f'{_XSD}restriction'):
            _parse_complex_type_or_sequence(child, meta, parent_path, parent_tag)


def _parse_extension_or_restriction(node, meta: SchemaMetadata, parent_path: str, parent_tag: str) -> None:
    """Handle children of xs:extension or xs:restriction."""
    for child in node:
        if child.tag in (f'{_XSD}sequence', f'{_XSD}all', f'{_XSD}choice'):
            _parse_complex_type_or_sequence(child, meta, parent_path, parent_tag)


def _parse_schema_root(node, meta: SchemaMetadata) -> None:
    """Handle top-level xs:schema children."""
    for child in node:
        if child.tag == f'{_XSD}element':
            _parse_element(child, meta, parent_path='')


# ---------------------------------------------------------------------------
# Type-aware value comparison helpers
# ---------------------------------------------------------------------------

def _parse_date(text: str):
    """Try to parse *text* as an ISO date/datetime. Returns normalized string or None."""
    import datetime
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ'):
        try:
            return datetime.datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    return None


def type_aware_equal(a: str, b: str, xs_type: Optional[str]) -> Optional[bool]:
    """Compare two string values using schema type awareness.

    Returns
    -------
    bool
        ``True`` if equal, ``False`` if different.
    ``None``
        If the type is not recognised or not applicable – caller should fall
        back to default comparison.
    """
    cat = xs_type_category(xs_type)
    if cat is None:
        return None

    na = a.strip() if a else ''
    nb = b.strip() if b else ''

    if cat == 'boolean':
        return (na.lower() in ('true', '1')) == (nb.lower() in ('true', '1'))

    if cat == 'numeric':
        try:
            return float(na) == float(nb)
        except (ValueError, TypeError):
            return None

    if cat == 'date':
        da = _parse_date(na)
        db = _parse_date(nb)
        if da is not None and db is not None:
            return da == db
        return None

    return None
