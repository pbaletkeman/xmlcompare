#!/usr/bin/env python3
"""xmlcompare - XML file comparison tool."""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def _use_color():
    return sys.stdout.isatty()


def _colorize(text, color):
    if _use_color():
        return color + text + RESET
    return text


class CompareOptions:
    """Holds all comparison configuration."""

    def __init__(self):
        self.tolerance = 0.0
        self.ignore_case = False
        self.unordered = False
        self.ignore_namespaces = False
        self.ignore_attributes = False
        self.skip_keys = []
        self.skip_pattern = None
        self.filter_xpath = None
        self.output_format = 'text'
        self.output_file = None
        self.summary = False
        self.verbose = False
        self.quiet = False
        self.fail_fast = False
        self.structure_only = False
        self.max_depth = None
        # Phase 1 additions
        self.schema = None          # Path to XSD schema file
        self.type_aware = False     # Enable type-aware comparison from schema
        self.plugins = []           # List of plugin module paths to load


class Difference:
    """Represents a single detected difference between two XML documents."""

    def __init__(self, path, kind, msg, expected=None, actual=None):
        self.path = path
        self.kind = kind
        self.msg = msg
        self.expected = expected
        self.actual = actual

    def to_dict(self):
        d = {'path': self.path, 'kind': self.kind, 'message': self.msg}
        if self.expected is not None:
            d['expected'] = self.expected
        if self.actual is not None:
            d['actual'] = self.actual
        return d

    def __repr__(self):
        return f"Difference(path={self.path!r}, kind={self.kind!r}, msg={self.msg!r})"


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def strip_namespace(tag):
    """Remove XML namespace from a tag string, e.g. {http://...}name -> name."""
    if tag and tag.startswith('{'):
        return tag.split('}', 1)[1]
    return tag


def get_tag(elem, opts):
    tag = elem.tag
    if opts.ignore_namespaces:
        tag = strip_namespace(tag)
    return tag


def normalize_text(text):
    """Collapse whitespace in a text value."""
    if text is None:
        return ''
    return ' '.join(text.split())


def _to_numeric(text):
    """Try to convert text to float. Returns None on failure."""
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def values_equal(a, b, opts, xs_type=None):
    """Return True if two text values are considered equal under opts.

    When *xs_type* is provided and ``opts.type_aware`` is True, attempts
    type-aware comparison (date, numeric, boolean) before falling back to
    the standard comparison logic.
    """
    # Type-aware comparison using schema hints
    if xs_type and getattr(opts, 'type_aware', False):
        try:
            from schema_analyzer import type_aware_equal
            result = type_aware_equal(a or '', b or '', xs_type)
            if result is not None:
                return result
        except ImportError:
            pass

    na = normalize_text(a)
    nb = normalize_text(b)
    # Numeric comparison
    fa = _to_numeric(na)
    fb = _to_numeric(nb)
    if fa is not None and fb is not None:
        return abs(fa - fb) <= opts.tolerance
    # Text comparison
    if opts.ignore_case:
        return na.lower() == nb.lower()
    return na == nb


def build_path(parent, tag):
    return f"{parent}/{tag}" if parent else tag


def should_skip(path, tag, opts):
    """Return True if the element at *path* with bare *tag* should be skipped."""
    for skip_key in opts.skip_keys:
        if skip_key.startswith('//'):
            sk_tag = skip_key[2:]
            if tag == sk_tag:
                return True
        else:
            if path == skip_key:
                return True
    if opts.skip_pattern and re.search(opts.skip_pattern, tag):
        return True
    return False


def _compare_text(elem1, elem2, opts, current_path, diffs, xs_type):
    """Compare text content of two elements; append to diffs. Returns True if fail_fast triggers."""
    text1 = normalize_text(elem1.text)
    text2 = normalize_text(elem2.text)
    if not values_equal(text1, text2, opts, xs_type=xs_type):
        diffs.append(Difference(
            current_path, 'text',
            f"Text mismatch at {current_path!r}: {text1!r} != {text2!r}",
            text1, text2,
        ))
        if opts.fail_fast:
            return True
    return False


def _compare_attributes(elem1, elem2, opts, current_path, diffs):
    """Compare attributes of two elements; append to diffs. Returns True if fail_fast triggers."""
    attrs1 = dict(elem1.attrib)
    attrs2 = dict(elem2.attrib)
    if opts.ignore_namespaces:
        attrs1 = {strip_namespace(k): v for k, v in attrs1.items()}
        attrs2 = {strip_namespace(k): v for k, v in attrs2.items()}
    all_keys = sorted(set(attrs1) | set(attrs2))
    for key in all_keys:
        if key not in attrs1:
            diffs.append(Difference(
                current_path, 'attr',
                f"Attribute {key!r} missing in first element at {current_path!r}",
                None, attrs2[key],
            ))
        elif key not in attrs2:
            diffs.append(Difference(
                current_path, 'attr',
                f"Attribute {key!r} missing in second element at {current_path!r}",
                attrs1[key], None,
            ))
        elif not values_equal(attrs1[key], attrs2[key], opts):
            diffs.append(Difference(
                current_path, 'attr',
                f"Attribute {key!r} mismatch at {current_path!r}: {attrs1[key]!r} != {attrs2[key]!r}",
                attrs1[key], attrs2[key],
            ))
        if opts.fail_fast and diffs:
            return True
    return False


# ---------------------------------------------------------------------------
# Core comparison
# ---------------------------------------------------------------------------

def _get_xs_type(tag, path, opts, schema_meta):
    """Return the XSD type for an element from schema metadata, or None."""
    if schema_meta is not None and getattr(opts, 'type_aware', False):
        return schema_meta.get_xs_type(tag, path)
    return None


def compare_elements(elem1, elem2, opts, path='', diffs=None, depth=0,
                     schema_meta=None):
    """Recursively compare two XML elements, appending Difference objects to *diffs*.

    Parameters
    ----------
    schema_meta:
        Optional :class:`~schema_analyzer.SchemaMetadata` instance.  When
        provided (and ``opts.type_aware`` is True), used to apply
        type-aware comparison and schema-driven ordering hints.
    """
    if diffs is None:
        diffs = []

    tag1 = get_tag(elem1, opts)
    tag2 = get_tag(elem2, opts)
    current_path = path or tag1

    if opts.verbose:
        print(f"  Comparing: {current_path} (depth={depth})", file=sys.stderr)

    if opts.max_depth is not None and depth > opts.max_depth:
        return diffs

    if tag1 != tag2:
        diffs.append(Difference(current_path, 'tag',
                                f"Tag mismatch: {tag1!r} != {tag2!r}", tag1, tag2))
        return diffs

    xs_type = _get_xs_type(tag1, current_path, opts, schema_meta)

    if not opts.structure_only and _compare_text(elem1, elem2, opts, current_path, diffs, xs_type):
        return diffs

    if not opts.ignore_attributes and not opts.structure_only:
        if _compare_attributes(elem1, elem2, opts, current_path, diffs):
            return diffs

    if opts.fail_fast and diffs:
        return diffs

    if opts.max_depth is None or depth < opts.max_depth:
        _compare_children(elem1, elem2, opts, current_path, diffs, depth, schema_meta)

    return diffs


def _compare_children(elem1, elem2, opts, current_path, diffs, depth, schema_meta):
    """Filter and compare child elements."""
    def _keep(child, parent_path):
        ctag = get_tag(child, opts)
        cpath = build_path(parent_path, ctag)
        return not should_skip(cpath, ctag, opts)

    children1 = [c for c in list(elem1) if _keep(c, current_path)]
    children2 = [c for c in list(elem2) if _keep(c, current_path)]

    schema_unordered = (
        schema_meta is not None
        and getattr(opts, 'type_aware', False)
        and schema_meta.is_unordered_children(current_path)
    )
    if opts.unordered or schema_unordered:
        _compare_unordered(children1, children2, opts, current_path, diffs,
                           depth, schema_meta=schema_meta)
    else:
        _compare_ordered(children1, children2, opts, current_path, diffs,
                         depth, schema_meta=schema_meta)


def _compare_ordered(children1, children2, opts, path, diffs, depth=0,
                     schema_meta=None):
    max_len = max(len(children1), len(children2))
    for i in range(max_len):
        if i >= len(children1):
            tag = get_tag(children2[i], opts)
            diffs.append(Difference(
                build_path(path, tag), 'missing',
                f"Element {tag!r} missing in first document at position {i}",
            ))
            if opts.fail_fast:
                return
        elif i >= len(children2):
            tag = get_tag(children1[i], opts)
            diffs.append(Difference(
                build_path(path, tag), 'extra',
                f"Element {tag!r} missing in second document at position {i}",
            ))
            if opts.fail_fast:
                return
        else:
            child_path = build_path(path, get_tag(children1[i], opts))
            compare_elements(children1[i], children2[i], opts, child_path, diffs,
                             depth + 1, schema_meta=schema_meta)
            if opts.fail_fast and diffs:
                return


def _compare_unordered(children1, children2, opts, path, diffs, depth=0,
                       schema_meta=None):
    groups1 = defaultdict(list)
    groups2 = defaultdict(list)
    for c in children1:
        groups1[get_tag(c, opts)].append(c)
    for c in children2:
        groups2[get_tag(c, opts)].append(c)

    all_tags = sorted(set(groups1) | set(groups2))
    for tag in all_tags:
        elems1 = groups1.get(tag, [])
        elems2 = groups2.get(tag, [])
        child_path = build_path(path, tag)
        max_len = max(len(elems1), len(elems2))
        for i in range(max_len):
            if i >= len(elems1):
                diffs.append(Difference(
                    child_path, 'missing',
                    f"Element {tag!r} occurrence {i + 1} missing in first document",
                ))
                if opts.fail_fast:
                    return
            elif i >= len(elems2):
                diffs.append(Difference(
                    child_path, 'extra',
                    f"Element {tag!r} occurrence {i + 1} missing in second document",
                ))
                if opts.fail_fast:
                    return
            else:
                compare_elements(elems1[i], elems2[i], opts, child_path, diffs,
                                 depth + 1, schema_meta=schema_meta)
                if opts.fail_fast and diffs:
                    return


def _load_schema_meta(opts):
    """Load SchemaMetadata from opts.schema if set. Returns None if unavailable."""
    if not getattr(opts, 'schema', None):
        return None
    try:
        from schema_analyzer import analyze_schema
        return analyze_schema(opts.schema)
    except ImportError:
        return None


def _validate_against_schema(file1, file2, opts):
    """Run pre-flight schema validation for both files. Raises ValueError on failure."""
    try:
        from validate_xsd import get_validation_errors
    except ImportError:
        return
    for xml_path in (file1, file2):
        errors = get_validation_errors(xml_path, opts.schema)
        if errors is None:
            return  # lxml unavailable – skip silently
        if errors:
            raise ValueError(
                f"Schema validation failed for {xml_path}: "
                + "; ".join(errors[:3])
            )


def _parse_xml(path):
    """Parse an XML file and return its root element."""
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"Failed to parse {path}: {exc}") from exc
    except OSError as exc:
        raise FileNotFoundError(f"File not found: {path}") from exc


def compare_xml_files(file1, file2, opts):
    """Parse and compare two XML files. Returns a list of Difference objects.

    When ``opts.schema`` is set, performs pre-flight schema validation (if lxml
    is available) and loads schema metadata for smarter comparison.
    Loaded plugins' difference filters are applied to the final result.
    """
    schema_meta = _load_schema_meta(opts)
    if getattr(opts, 'schema', None):
        _validate_against_schema(file1, file2, opts)

    root1 = _parse_xml(file1)
    root2 = _parse_xml(file2)

    if opts.filter_xpath:
        try:
            elems1 = root1.findall(opts.filter_xpath)
            elems2 = root2.findall(opts.filter_xpath)
        except ET.ParseError as exc:
            raise ValueError(f"Invalid filter XPath {opts.filter_xpath!r}: {exc}") from exc
        diffs = []
        _compare_ordered(elems1, elems2, opts, '', diffs, schema_meta=schema_meta)
        return _apply_filters(diffs, opts)

    diffs = compare_elements(root1, root2, opts, schema_meta=schema_meta)
    return _apply_filters(diffs, opts)


def _apply_filters(diffs, opts):
    """Apply registered DifferenceFilter plugins to the list of differences."""
    plugin_paths = getattr(opts, 'plugins', [])
    if not plugin_paths:
        return diffs
    try:
        from plugin_interface import get_registry
        registry = get_registry()
        filters = registry.get_filters()
        if not filters:
            return diffs
        return [d for d in diffs if not any(f.should_ignore(d) for f in filters)]
    except ImportError:
        return diffs


def compare_dirs(dir1, dir2, opts, recursive=False):
    """Compare two directories of XML files. Returns dict[filename -> diffs or error str]."""
    results = {}
    dir1_path = Path(dir1)
    dir2_path = Path(dir2)

    if recursive:
        files1 = {str(p.relative_to(dir1_path)) for p in dir1_path.rglob('*.xml')}
        files2 = {str(p.relative_to(dir2_path)) for p in dir2_path.rglob('*.xml')}
    else:
        files1 = {p.name for p in dir1_path.glob('*.xml')}
        files2 = {p.name for p in dir2_path.glob('*.xml')}

    for fname in sorted(files1 | files2):
        if fname not in files1:
            results[fname] = [Difference(fname, 'missing', f"File {fname!r} missing in {dir1}")]
        elif fname not in files2:
            results[fname] = [Difference(fname, 'missing', f"File {fname!r} missing in {dir2}")]
        else:
            try:
                results[fname] = compare_xml_files(
                    str(dir1_path / fname), str(dir2_path / fname), opts
                )
            except (ValueError, FileNotFoundError) as exc:
                results[fname] = str(exc)

        if opts.fail_fast and results.get(fname):
            break

    return results


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_text_report(diffs, label1=None, label2=None):
    lines = []
    if label1 and label2:
        lines.append(f"Comparing: {label1} vs {label2}")
        lines.append('-' * 60)
    if not diffs:
        msg = "Files are equal"
        lines.append(_colorize(msg, GREEN) if _use_color() else msg)
    else:
        for diff in diffs:
            msg = f"  [{diff.kind.upper()}] {diff.msg}"
            lines.append(_colorize(msg, RED) if _use_color() else msg)
            if diff.expected is not None:
                lines.append(f"    Expected : {diff.expected!r}")
            if diff.actual is not None:
                lines.append(f"    Actual   : {diff.actual!r}")
    return '\n'.join(lines)


def format_json_report(all_results):
    output = {}
    for key, val in all_results.items():
        if isinstance(val, str):
            output[key] = {'error': val}
        else:
            output[key] = {
                'equal': len(val) == 0,
                'differences': [d.to_dict() for d in val],
            }
    return json.dumps(output, indent=2)


def format_html_report(all_results):
    lines = [
        '<html><head><title>XML Compare Report</title>',
        '<style>',
        'body { font-family: monospace; }',
        '.equal { color: green; }',
        '.diff  { color: red;   }',
        '.error { color: orange; }',
        '</style></head><body>',
        '<h1>XML Compare Report</h1>',
    ]
    for key, val in all_results.items():
        if isinstance(val, str):
            lines.append(f'<h2 class="error">{key}: ERROR</h2>')
            lines.append(f'<p class="error">{val}</p>')
        elif not val:
            lines.append(f'<h2 class="equal">{key}: EQUAL</h2>')
        else:
            lines.append(f'<h2 class="diff">{key}: {len(val)} difference(s)</h2><ul>')
            for d in val:
                detail = ''
                if d.expected is not None or d.actual is not None:
                    detail = f' &mdash; expected: {d.expected!r}, actual: {d.actual!r}'
                lines.append(f'<li class="diff">[{d.kind.upper()}] {d.msg}{detail}</li>')
            lines.append('</ul>')
    lines.append('</body></html>')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_file):
    with open(config_file) as fh:
        if config_file.endswith(('.yaml', '.yml')):
            if not HAS_YAML:
                raise ImportError("pyyaml is required for YAML config support")
            return yaml.safe_load(fh)
        return json.load(fh)


def _opts_from_dict(config):
    opts = CompareOptions()
    opts.tolerance = float(config.get('tolerance', 0.0))
    opts.ignore_case = bool(config.get('ignore_case', False))
    opts.unordered = bool(config.get('unordered', False))
    opts.ignore_namespaces = bool(config.get('ignore_namespaces', False))
    opts.ignore_attributes = bool(config.get('ignore_attributes', False))
    opts.skip_keys = list(config.get('skip_keys', []))
    opts.skip_pattern = config.get('skip_pattern') or None
    opts.filter_xpath = config.get('filter') or None
    opts.output_format = config.get('output_format', 'text')
    opts.output_file = config.get('output_file') or None
    opts.summary = bool(config.get('summary', False))
    opts.verbose = bool(config.get('verbose', False))
    opts.quiet = bool(config.get('quiet', False))
    opts.fail_fast = bool(config.get('fail_fast', False))
    opts.structure_only = bool(config.get('structure_only', False))
    opts.max_depth = config.get('max_depth')
    if opts.max_depth is not None:
        opts.max_depth = int(opts.max_depth)
    # Phase 1 additions
    opts.schema = config.get('schema') or None
    opts.type_aware = bool(config.get('type_aware', False))
    opts.plugins = list(config.get('plugins', []))
    return opts


def _opts_from_args(args):
    opts = CompareOptions()
    opts.tolerance = args.tolerance
    opts.ignore_case = args.ignore_case
    opts.unordered = args.unordered
    opts.ignore_namespaces = args.ignore_namespaces
    opts.ignore_attributes = args.ignore_attributes
    opts.skip_keys = args.skip_keys or []
    opts.skip_pattern = args.skip_pattern
    opts.filter_xpath = args.filter
    opts.output_format = args.output_format
    opts.output_file = args.output_file
    opts.summary = args.summary
    opts.verbose = args.verbose
    opts.quiet = args.quiet
    opts.fail_fast = args.fail_fast
    opts.structure_only = args.structure_only
    opts.max_depth = args.max_depth
    # Phase 1 additions
    opts.schema = args.schema
    opts.type_aware = args.type_aware
    opts.plugins = args.plugins or []
    return opts


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog='xmlcompare',
        description='Compare XML files and report differences.',
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('--files', nargs=2, metavar=('FILE1', 'FILE2'),
                     help='Compare two XML files')
    grp.add_argument('--dirs', nargs=2, metavar=('DIR1', 'DIR2'),
                     help='Compare two directories of XML files')
    parser.add_argument('--recursive', action='store_true',
                        help='Recurse into subdirectories')
    parser.add_argument('--config', metavar='FILE',
                        help='Load options from YAML/JSON config file')
    parser.add_argument('--tolerance', type=float, default=0.0,
                        metavar='FLOAT', help='Numeric tolerance threshold')
    parser.add_argument('--ignore-case', action='store_true',
                        help='Case-insensitive text comparison')
    parser.add_argument('--unordered', action='store_true',
                        help='Set-based child element comparison')
    parser.add_argument('--ignore-namespaces', action='store_true',
                        help='Strip namespaces before comparing')
    parser.add_argument('--ignore-attributes', action='store_true',
                        help='Skip attribute comparison')
    parser.add_argument('--structure-only', action='store_true',
                        help='Compare only XML structure, ignore text and attribute values')
    parser.add_argument('--max-depth', type=int, metavar='INT',
                        help='Maximum depth for comparison (compare elements up to specified depth only)')
    parser.add_argument('--skip-keys', nargs='+', metavar='PATH',
                        help='XPath-style element paths to skip')
    parser.add_argument('--skip-pattern', metavar='REGEX',
                        help='Skip elements whose tag matches regex')
    parser.add_argument('--filter', metavar='XPATH',
                        help='Compare only elements matching XPath')
    parser.add_argument('--output-format', metavar='FORMAT',
                        default='text',
                        help='Output format: text, json, html, unified-diff, html-diff (default: text)')
    parser.add_argument('--output-file', metavar='FILE',
                        help='Write report to file instead of stdout')
    parser.add_argument('--summary', action='store_true',
                        help='Print only pass/fail count')
    parser.add_argument('--verbose', action='store_true',
                        help='Detailed element-by-element trace')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress all output')
    parser.add_argument('--fail-fast', action='store_true',
                        help='Stop on first detected difference')
    # Phase 1: plugin and schema options
    parser.add_argument('--plugins', nargs='+', metavar='MODULE',
                        help='Python module paths for plugins to load (e.g. mypkg.mymodule)')
    parser.add_argument('--schema', metavar='XSD',
                        help='Path to XSD schema for pre-validation and type hints')
    parser.add_argument('--type-aware', action='store_true',
                        help='Use schema type hints for smarter comparison (requires --schema)')
    # Phase 3: Performance and Phase 4: Interactive
    parser.add_argument('--stream', action='store_true',
                        help='Use streaming parser for large files (memory-efficient, slower)')
    parser.add_argument('--interactive', action='store_true',
                        help='Interactive mode: menu-based file selection and filtering')
    return parser


def _load_plugins(opts):
    """Load plugins from opts.plugins module paths into the default registry."""
    if not opts.plugins:
        return
    try:
        from plugin_interface import get_registry
        registry = get_registry()
        registry.load_entry_points()
        for module_path in opts.plugins:
            registry.load_module(module_path)
    except ImportError:
        pass


def _resolve_config(args):
    """Return (opts, files, dirs, recursive) from args, merging config file if present."""
    if args.config:
        try:
            config = load_config(args.config)
        except OSError:
            print(f"Error: config file not found: {args.config}", file=sys.stderr)
            sys.exit(2)
        except Exception as exc:  # noqa: BLE001
            print(f"Error loading config: {exc}", file=sys.stderr)
            sys.exit(2)
        opts = _opts_from_dict(config)
        return (opts,
                args.files or config.get('files'),
                args.dirs or config.get('dirs'),
                args.recursive or bool(config.get('recursive', False)))
    opts = _opts_from_args(args)
    return opts, args.files, args.dirs, args.recursive


def _run_comparison(files, dirs, opts, recursive):
    """Execute file or directory comparison. Returns all_results dict."""
    all_results = {}
    try:
        if files:
            file1, file2 = files
            diffs = compare_xml_files(file1, file2, opts)
            all_results[f"{file1} vs {file2}"] = diffs
        else:
            dir1, dir2 = dirs
            if not os.path.isdir(dir1):
                print(f"Error: not a directory: {dir1}", file=sys.stderr)
                sys.exit(2)
            if not os.path.isdir(dir2):
                print(f"Error: not a directory: {dir2}", file=sys.stderr)
                sys.exit(2)
            all_results = compare_dirs(dir1, dir2, opts, recursive=recursive)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
    return all_results


def _build_output(all_results, opts, files):
    """Build the output string from comparison results."""
    errors = sum(1 for v in all_results.values() if isinstance(v, str))
    different = sum(1 for v in all_results.values() if isinstance(v, list) and v)
    equal = sum(1 for v in all_results.values() if isinstance(v, list) and not v)
    if opts.summary:
        total = len(all_results)
        return (f"Total: {total} | Equal: {equal} | "
                f"Different: {different} | Errors: {errors}")
    return _format_output(all_results, opts, files)


def _format_output(all_results, opts, files):
    """Select and apply the appropriate formatter."""
    try:
        from plugin_interface import get_registry
        formatter = get_registry().get_formatter(opts.output_format)
        if formatter is not None:
            return formatter.format(
                all_results,
                label1=files[0] if files else None,
                label2=files[1] if files else None,
            )
    except (ImportError, AttributeError):
        pass

    # Fallback to built-in formatters
    if opts.output_format == 'json':
        return format_json_report(all_results)
    if opts.output_format == 'html':
        return format_html_report(all_results)
    parts = []
    for key, val in all_results.items():
        if isinstance(val, str):
            msg = f"ERROR: {key}: {val}"
            parts.append(_colorize(msg, YELLOW) if _use_color() else msg)
        elif files:
            parts.append(format_text_report(val, files[0], files[1]))
        else:
            parts.append(format_text_report(val, key, ''))
    return '\n'.join(parts)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # Handle interactive mode
    if args.interactive:
        from interactive_cli import run_interactive
        run_interactive()
        return

    opts, files, dirs, recursive = _resolve_config(args)

    if not files and not dirs:
        parser.error("One of --files or --dirs is required.")

    _load_plugins(opts)

    all_results = _run_comparison(files, dirs, opts, recursive)

    errors = sum(1 for v in all_results.values() if isinstance(v, str))
    different = sum(1 for v in all_results.values() if isinstance(v, list) and v)
    has_differences = different > 0 or errors > 0

    if not opts.quiet:
        output_str = _build_output(all_results, opts, files)
        if opts.output_file:
            try:
                with open(opts.output_file, 'w') as fh:
                    fh.write(output_str + '\n')
            except OSError as exc:
                print(f"Error writing output file: {exc}", file=sys.stderr)
                sys.exit(2)
        else:
            print(output_str)

    sys.exit(1 if has_differences else 0)


if __name__ == '__main__':
    main()
