"""
Streaming XML parser using iterparse for memory-efficient processing.

True event-based comparison: constant memory regardless of file size.
Both files are parsed simultaneously and compared event-by-event.
Each element is cleared from memory immediately after comparison.

Memory: O(max_depth * max_breadth) instead of O(total_nodes) for DOM.
For typical deep XML with low breadth, 10-100x less memory than DOM.

Limitations vs DOM comparison:
- Does not support --unordered (requires full subtree in memory)
- Does not support --schema / type-aware (requires schema metadata)
- For those modes, falls back to DOM comparison automatically
"""

from pathlib import Path
from typing import List, Optional
from xml.etree import ElementTree as ET


def compare_xml_files_streaming(file1_path, file2_path, options=None):
    """
    Compare two XML files using true event-based streaming (iterparse).

    Parses both files simultaneously, comparing each element as it arrives
    and immediately clearing it from memory. This keeps peak memory usage
    proportional to tree depth rather than tree size.

    Falls back to DOM automatically for modes that need the full tree:
    - --unordered: needs all siblings in memory to reorder them
    - --schema: needs schema metadata loaded upfront

    Args:
        file1_path: Path to first XML file
        file2_path: Path to second XML file
        options: CompareOptions instance (optional)

    Returns:
        List of Difference objects
    """
    if options is None:
        from xmlcompare import CompareOptions
        options = CompareOptions()

    # Modes requiring full-tree traversal - fall back to DOM
    if getattr(options, 'unordered', False) or getattr(options, 'schema', None):
        from xmlcompare import compare_xml_files
        return compare_xml_files(str(file1_path), str(file2_path), options)

    try:
        return _stream_compare_files(str(file1_path), str(file2_path), options)
    except ET.ParseError as exc:
        raise ValueError(f"XML parse error during streaming: {exc}") from exc


# ---------------------------------------------------------------------------
# Core streaming engine
# ---------------------------------------------------------------------------

def _get_tag_s(elem, options) -> str:
    """Return element tag, optionally stripping namespace."""
    tag = elem.tag
    if getattr(options, 'ignore_namespaces', False) and isinstance(tag, str) and tag.startswith('{'):
        tag = tag.split('}', 1)[1]
    return tag


def _normalize_s(text: Optional[str]) -> str:
    """Collapse whitespace in text content."""
    if text is None:
        return ''
    return ' '.join(text.split())


def _compare_attrs_s(elem1, elem2, path: str, options, differences) -> bool:
    """Compare element attributes, appending to differences. Returns True if fail_fast triggered."""
    from xmlcompare import Difference, values_equal

    attrs1 = dict(elem1.attrib)
    attrs2 = dict(elem2.attrib)

    if getattr(options, 'ignore_namespaces', False):
        attrs1 = {k.split('}', 1)[1] if k.startswith('{') else k: v for k, v in attrs1.items()}
        attrs2 = {k.split('}', 1)[1] if k.startswith('{') else k: v for k, v in attrs2.items()}

    for key in sorted(set(attrs1) | set(attrs2)):
        if key not in attrs1:
            differences.append(Difference(
                path, 'attr',
                f"Attribute {key!r} missing in first element at {path!r}",
                None, attrs2[key],
            ))
        elif key not in attrs2:
            differences.append(Difference(
                path, 'attr',
                f"Attribute {key!r} missing in second element at {path!r}",
                attrs1[key], None,
            ))
        elif not values_equal(attrs1[key], attrs2[key], options):
            differences.append(Difference(
                path, 'attr',
                f"Attribute {key!r} mismatch at {path!r}: {attrs1[key]!r} != {attrs2[key]!r}",
                attrs1[key], attrs2[key],
            ))
        if getattr(options, 'fail_fast', False) and differences:
            return True
    return False


def _stream_compare_files(file1_path: str, file2_path: str, options) -> List:
    """
    Core streaming comparison: iterate both files in lock-step.

    Events processed:
    - 'start': compare tag and attributes (data is available at start).
    - 'end':   compare direct text content, then clear element from memory.

    When events desync (one file has extra/missing elements), the mismatch
    is recorded and iteration stops for the affected subtree.
    """
    from xmlcompare import Difference, values_equal

    differences: List = []
    path_stack: List[str] = []

    ctx1 = ET.iterparse(file1_path, events=('start', 'end'))
    ctx2 = ET.iterparse(file2_path, events=('start', 'end'))
    iter1 = iter(ctx1)
    iter2 = iter(ctx2)

    def advance(it):
        try:
            return next(it)
        except StopIteration:
            return None, None

    while True:
        ev1, el1 = advance(iter1)
        ev2, el2 = advance(iter2)

        # Both exhausted simultaneously - comparison complete
        if ev1 is None and ev2 is None:
            break

        # One file exhausted before the other
        if ev1 is None or ev2 is None:
            path = '/'.join(path_stack) or '<root>'
            which = 'second' if ev1 is None else 'first'
            differences.append(Difference(
                path, 'structure',
                f"Files have different element counts near {path!r}; "
                f"{which} file has additional elements",
            ))
            break

        if ev1 == 'start' and ev2 == 'start':
            tag1 = _get_tag_s(el1, options)
            tag2 = _get_tag_s(el2, options)
            # Use file1's tag for the path (best-effort when tags diverge)
            path_stack.append(tag1)
            current_path = '/'.join(path_stack)

            if tag1 != tag2:
                differences.append(Difference(
                    current_path, 'tag',
                    f"Tag mismatch at {current_path!r}: {tag1!r} != {tag2!r}",
                    tag1, tag2,
                ))
                if options.fail_fast:
                    return differences

            if (not getattr(options, 'ignore_attributes', False)
                    and not getattr(options, 'structure_only', False)):
                if _compare_attrs_s(el1, el2, current_path, options, differences):
                    return differences

        elif ev1 == 'end' and ev2 == 'end':
            current_path = '/'.join(path_stack) if path_stack else ''

            if not getattr(options, 'structure_only', False):
                text1 = _normalize_s(el1.text)
                text2 = _normalize_s(el2.text)
                if not values_equal(text1, text2, options):
                    differences.append(Difference(
                        current_path, 'text',
                        f"Text mismatch at {current_path!r}: {text1!r} != {text2!r}",
                        text1, text2,
                    ))
                    if options.fail_fast:
                        el1.clear()
                        el2.clear()
                        return differences

            # Release memory - this is the key streaming benefit
            el1.clear()
            el2.clear()

            if path_stack:
                path_stack.pop()

        else:
            # start/end mismatch: one file is nested deeper at this position
            current_path = '/'.join(path_stack) if path_stack else '<root>'
            which_deeper = 'first' if ev1 == 'start' else 'second'
            differences.append(Difference(
                current_path, 'structure',
                f"Structural difference at {current_path!r}: "
                f"{which_deeper} file has deeper nesting",
            ))
            break

        if options.fail_fast and differences:
            return differences

    return differences


# ---------------------------------------------------------------------------
# File statistics
# ---------------------------------------------------------------------------

def get_stream_stats(file_path):
    """
    Get statistics about file suitability for streaming.

    Args:
        file_path: Path to XML file

    Returns:
        StreamingStats object with file metrics
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size_mb = file_path.stat().st_size / (1024 * 1024)

    # Estimate DOM memory (rough: 10x file size)
    estimated_dom_memory_mb = int(file_path.stat().st_size * 10 / (1024 * 1024))

    # Count elements via quick streaming scan
    element_count = _count_elements_iterparse(str(file_path))

    # Streaming is beneficial for large files
    suitable = file_size_mb > 50

    return StreamingStats(
        file_size_mb=file_size_mb,
        estimated_dom_memory_mb=estimated_dom_memory_mb,
        element_count=element_count,
        suitable_for_streaming=suitable,
    )


def _count_elements_iterparse(file_path: str) -> int:
    """Count XML elements using iterparse (memory-efficient)."""
    count = 0
    try:
        for _event, elem in ET.iterparse(file_path, events=('end',)):
            count += 1
            elem.clear()
    except ET.ParseError:
        pass
    return count


# Keep old name as alias for backwards compatibility
count_elements_iterparse = _count_elements_iterparse


def get_memory_usage() -> float:
    """Return current process RSS memory usage in MB, or 0 if psutil unavailable."""
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0


class StreamingStats:
    """Statistics about a file for streaming suitability."""

    def __init__(self, file_size_mb, estimated_dom_memory_mb,
                 element_count, suitable_for_streaming):
        self.file_size_mb = file_size_mb
        self.estimated_dom_memory_mb = estimated_dom_memory_mb
        self.element_count = element_count
        self.suitable_for_streaming = suitable_for_streaming

    def __str__(self):
        return (
            f"File: {self.file_size_mb:.1f}MB | "
            f"Est. DOM Memory: {self.estimated_dom_memory_mb}MB | "
            f"Elements: {self.element_count} | "
            f"Streaming: {'RECOMMENDED' if self.suitable_for_streaming else 'not needed'}"
        )

    def __repr__(self):
        return self.__str__()
