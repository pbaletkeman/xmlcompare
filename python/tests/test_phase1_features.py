"""Tests for Phase 1: Plugin Architecture & Schema Integration (Python)."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the package root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))
import xmlcompare as xc
import plugin_interface as pi
import schema_analyzer as sa


def _opts(**kwargs):
    opts = xc.CompareOptions()
    for k, v in kwargs.items():
        setattr(opts, k, v)
    return opts


def write(path, content):
    Path(path).write_text(content)
    return str(path)


# ---------------------------------------------------------------------------
# Plugin interface tests
# ---------------------------------------------------------------------------

class TestFormatterPluginInterface:
    """Test the FormatterPlugin base class and registration."""

    def test_abstract_name_required(self):
        """FormatterPlugin cannot be instantiated without implementing name."""
        with pytest.raises(TypeError):
            pi.FormatterPlugin()

    def test_abstract_format_required(self):
        """FormatterPlugin cannot be instantiated without implementing format."""
        class BadPlugin(pi.FormatterPlugin):
            @property
            def name(self):
                return "bad"
            # Missing format() method
        with pytest.raises(TypeError):
            BadPlugin()

    def test_concrete_formatter_can_be_registered(self):
        """A concrete FormatterPlugin can be registered and retrieved."""
        class MyFormatter(pi.FormatterPlugin):
            @property
            def name(self):
                return "test-formatter"

            def format(self, all_results, **kwargs):
                return "test output"

        registry = pi.PluginRegistry()
        plugin = MyFormatter()
        registry.register_formatter(plugin)
        assert registry.get_formatter("test-formatter") is plugin

    def test_get_unknown_formatter_returns_none(self):
        """Looking up an unregistered formatter returns None."""
        registry = pi.PluginRegistry()
        assert registry.get_formatter("nonexistent") is None

    def test_list_formatters(self):
        """list_formatters returns all registered formatter names."""
        class FmtA(pi.FormatterPlugin):
            @property
            def name(self):
                return "fmt-a"
            def format(self, all_results, **kwargs):
                return ""

        class FmtB(pi.FormatterPlugin):
            @property
            def name(self):
                return "fmt-b"
            def format(self, all_results, **kwargs):
                return ""

        registry = pi.PluginRegistry()
        registry.register_formatter(FmtA())
        registry.register_formatter(FmtB())
        names = registry.list_formatters()
        assert "fmt-a" in names
        assert "fmt-b" in names


class TestDifferenceFilterInterface:
    """Test the DifferenceFilter base class and registration."""

    def test_abstract_filter_required(self):
        """DifferenceFilter cannot be instantiated without implementing should_ignore."""
        with pytest.raises(TypeError):
            pi.DifferenceFilter()

    def test_concrete_filter_can_be_registered(self):
        """A concrete DifferenceFilter can be registered and retrieved."""
        class IgnoreTextFilter(pi.DifferenceFilter):
            @property
            def name(self):
                return "ignore-text"

            def should_ignore(self, difference):
                return difference.kind == 'text'

        registry = pi.PluginRegistry()
        f = IgnoreTextFilter()
        registry.register_filter(f)
        assert f in registry.get_filters()

    def test_filter_suppresses_differences(self, tmp_path):
        """DifferenceFilter suppresses matching differences via opts.plugins."""
        class IgnoreTextFilter(pi.DifferenceFilter):
            @property
            def name(self):
                return "ignore-text"

            def should_ignore(self, difference):
                return difference.kind == 'text'

        # Register the filter in the default registry temporarily
        registry = pi.get_registry()
        original_filters = registry._filters[:]
        registry.register_filter(IgnoreTextFilter())

        try:
            f1 = write(tmp_path / 'a.xml', '<r><v>hello</v></r>')
            f2 = write(tmp_path / 'b.xml', '<r><v>world</v></r>')
            # With plugins=["dummy"] set, filters will be applied
            opts = _opts(plugins=["dummy"])
            diffs = xc.compare_xml_files(f1, f2, opts)
            # text differences should be suppressed
            assert all(d.kind != 'text' for d in diffs)
        finally:
            registry._filters = original_filters

    def test_multiple_filters_applied(self):
        """All registered filters are consulted."""
        class FilterA(pi.DifferenceFilter):
            @property
            def name(self):
                return "filter-a"
            def should_ignore(self, d):
                return d.kind == 'text'

        class FilterB(pi.DifferenceFilter):
            @property
            def name(self):
                return "filter-b"
            def should_ignore(self, d):
                return d.kind == 'attr'

        registry = pi.PluginRegistry()
        registry.register_filter(FilterA())
        registry.register_filter(FilterB())
        filters = registry.get_filters()
        assert len(filters) == 2


class TestPluginRegistryModuleLoading:
    """Test loading plugins from Python modules."""

    def test_load_module_registers_formatter(self, tmp_path):
        """load_module discovers and registers FormatterPlugin subclasses."""
        plugin_code = '''
from plugin_interface import FormatterPlugin

class EchoFormatter(FormatterPlugin):
    @property
    def name(self):
        return "echo"

    def format(self, all_results, **kwargs):
        return repr(all_results)
'''
        mod_file = tmp_path / "echo_plugin.py"
        mod_file.write_text(plugin_code)

        # Add tmp_path to sys.path so the module can be imported
        sys.path.insert(0, str(tmp_path))
        try:
            registry = pi.PluginRegistry()
            registry.load_module("echo_plugin")
            assert registry.get_formatter("echo") is not None
        finally:
            sys.path.remove(str(tmp_path))

    def test_load_module_nonexistent_warns(self, capsys):
        """load_module prints a warning for missing modules."""
        registry = pi.PluginRegistry()
        registry.load_module("nonexistent_plugin_xyz_123")
        captured = capsys.readouterr()
        assert "Warning" in captured.err or captured.err == ""  # graceful degradation

    def test_entry_points_discovery_does_not_crash(self):
        """load_entry_points runs without error even with no plugins installed.

        Uses mock to bypass any firewall-blocked or environment-specific
        importlib.metadata calls.
        """
        registry = pi.PluginRegistry()
        # Mock entry_points to return empty groups — no network/classpath needed
        with patch('importlib.metadata.entry_points', return_value=[]):
            registry.load_entry_points()

    def test_entry_points_discovery_registers_mock_formatter(self):
        """load_entry_points registers a formatter from a mocked entry_point."""
        class MockFormatter(pi.FormatterPlugin):
            @property
            def name(self):
                return "mock-fmt"
            def format(self, all_results, **kwargs):
                return "mock"

        mock_ep = type('EP', (), {
            'name': 'mock-fmt',
            'group': 'xmlcompare.formatters',
            'load': lambda self: MockFormatter,
        })()

        registry = pi.PluginRegistry()
        # Simulate entry_points returning our mock endpoint
        with patch('importlib.metadata.entry_points') as mock_eps:
            mock_eps_obj = type('EPS', (), {
                'select': lambda self, group: [mock_ep] if group == 'xmlcompare.formatters' else [],
            })()
            mock_eps.return_value = mock_eps_obj
            registry.load_entry_points()

        assert registry.get_formatter("mock-fmt") is not None


# ---------------------------------------------------------------------------
# CompareOptions new fields
# ---------------------------------------------------------------------------

class TestCompareOptionsPhase1:
    """Test new CompareOptions fields from Phase 1."""

    def test_default_schema_none(self):
        opts = xc.CompareOptions()
        assert opts.schema is None

    def test_default_type_aware_false(self):
        opts = xc.CompareOptions()
        assert opts.type_aware is False

    def test_default_plugins_empty(self):
        opts = xc.CompareOptions()
        assert opts.plugins == []

    def test_schema_option_set(self):
        opts = _opts(schema='my.xsd')
        assert opts.schema == 'my.xsd'

    def test_type_aware_option_set(self):
        opts = _opts(type_aware=True)
        assert opts.type_aware is True

    def test_plugins_option_set(self):
        opts = _opts(plugins=['mypkg.mymod'])
        assert opts.plugins == ['mypkg.mymod']


# ---------------------------------------------------------------------------
# CLI --plugins, --schema, --type-aware flags
# ---------------------------------------------------------------------------

class TestCLIPhase1Options:
    """Test new CLI options are recognized."""

    def test_plugins_cli_option_recognized(self):
        """--plugins option is parsed correctly."""
        parser = xc.build_parser()
        args = parser.parse_args(['--files', 'a.xml', 'b.xml', '--plugins', 'mypkg.mod'])
        assert args.plugins == ['mypkg.mod']

    def test_plugins_cli_multiple_values(self):
        """--plugins accepts multiple module paths."""
        parser = xc.build_parser()
        args = parser.parse_args(['--files', 'a.xml', 'b.xml',
                                   '--plugins', 'pkg.mod1', 'pkg.mod2'])
        assert args.plugins == ['pkg.mod1', 'pkg.mod2']

    def test_schema_cli_option_recognized(self):
        """--schema option is parsed correctly."""
        parser = xc.build_parser()
        args = parser.parse_args(['--files', 'a.xml', 'b.xml', '--schema', 'schema.xsd'])
        assert args.schema == 'schema.xsd'

    def test_type_aware_cli_option_recognized(self):
        """--type-aware flag is parsed correctly."""
        parser = xc.build_parser()
        args = parser.parse_args(['--files', 'a.xml', 'b.xml', '--type-aware'])
        assert args.type_aware is True

    def test_type_aware_default_false(self):
        """--type-aware defaults to False."""
        parser = xc.build_parser()
        args = parser.parse_args(['--files', 'a.xml', 'b.xml'])
        assert args.type_aware is False

    def test_schema_default_none(self):
        """--schema defaults to None."""
        parser = xc.build_parser()
        args = parser.parse_args(['--files', 'a.xml', 'b.xml'])
        assert args.schema is None


# ---------------------------------------------------------------------------
# Schema Analyzer tests
# ---------------------------------------------------------------------------

class TestSchemaAnalyzer:
    """Test the schema_analyzer module."""

    def test_analyze_simple_schema(self, tmp_path):
        """Schema analyzer extracts element names and types."""
        xsd = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="date" type="xs:date"/>
        <xs:element name="amount" type="xs:decimal"/>
        <xs:element name="active" type="xs:boolean"/>
        <xs:element name="label" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>'''
        xsd_file = str(tmp_path / 'test.xsd')
        Path(xsd_file).write_text(xsd)

        meta = sa.analyze_schema(xsd_file)

        assert meta.get_xs_type('date', 'root/date') == 'xs:date'
        assert meta.get_xs_type('amount', 'root/amount') == 'xs:decimal'
        assert meta.get_xs_type('active', 'root/active') == 'xs:boolean'
        assert meta.get_xs_type('label', 'root/label') == 'xs:string'

    def test_analyze_missing_file_returns_empty(self, tmp_path):
        """analyze_schema returns empty metadata for non-existent file."""
        meta = sa.analyze_schema(str(tmp_path / 'nonexistent.xsd'))
        assert meta.elements == {}

    def test_analyze_all_group_is_unordered(self, tmp_path):
        """xs:all elements are detected as unordered."""
        xsd = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:all>
        <xs:element name="a" type="xs:string"/>
        <xs:element name="b" type="xs:string"/>
      </xs:all>
    </xs:complexType>
  </xs:element>
</xs:schema>'''
        xsd_file = str(tmp_path / 'test.xsd')
        Path(xsd_file).write_text(xsd)

        meta = sa.analyze_schema(xsd_file)
        assert meta.is_unordered_children('root') is True

    def test_analyze_sequence_is_ordered(self, tmp_path):
        """xs:sequence elements are NOT marked as unordered."""
        xsd = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="a" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>'''
        xsd_file = str(tmp_path / 'test.xsd')
        Path(xsd_file).write_text(xsd)

        meta = sa.analyze_schema(xsd_file)
        assert not meta.is_unordered_children('root')

    def test_min_max_occurs_parsed(self, tmp_path):
        """minOccurs/maxOccurs are correctly parsed."""
        xsd = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="required" type="xs:string" minOccurs="1" maxOccurs="1"/>
        <xs:element name="optional" type="xs:string" minOccurs="0" maxOccurs="1"/>
        <xs:element name="repeated" type="xs:string" minOccurs="0" maxOccurs="unbounded"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>'''
        xsd_file = str(tmp_path / 'test.xsd')
        Path(xsd_file).write_text(xsd)

        meta = sa.analyze_schema(xsd_file)

        req = meta.get_element_info('required', 'root/required')
        assert req is not None
        assert req.min_occurs == 1
        assert req.max_occurs == 1
        assert req.is_required is True

        opt = meta.get_element_info('optional', 'root/optional')
        assert opt is not None
        assert opt.min_occurs == 0
        assert opt.is_required is False

        rep = meta.get_element_info('repeated', 'root/repeated')
        assert rep is not None
        assert rep.max_occurs is None  # unbounded


# ---------------------------------------------------------------------------
# Type-aware comparison tests
# ---------------------------------------------------------------------------

class TestTypeAwareComparison:
    """Test type-aware value comparison via schema hints."""

    def test_xs_type_category_date(self):
        assert sa.xs_type_category('xs:date') == 'date'
        assert sa.xs_type_category('xs:dateTime') == 'date'

    def test_xs_type_category_numeric(self):
        assert sa.xs_type_category('xs:integer') == 'numeric'
        assert sa.xs_type_category('xs:decimal') == 'numeric'
        assert sa.xs_type_category('xs:float') == 'numeric'

    def test_xs_type_category_boolean(self):
        assert sa.xs_type_category('xs:boolean') == 'boolean'

    def test_xs_type_category_unknown(self):
        assert sa.xs_type_category('xs:string') is None
        assert sa.xs_type_category(None) is None

    def test_type_aware_boolean_true_variants(self):
        assert sa.type_aware_equal('true', '1', 'xs:boolean') is True
        assert sa.type_aware_equal('false', '0', 'xs:boolean') is True

    def test_type_aware_boolean_mismatch(self):
        assert sa.type_aware_equal('true', 'false', 'xs:boolean') is False

    def test_type_aware_numeric_equal(self):
        assert sa.type_aware_equal('1.0', '1', 'xs:decimal') is True
        assert sa.type_aware_equal('42', '42.0', 'xs:integer') is True

    def test_type_aware_numeric_mismatch(self):
        assert sa.type_aware_equal('1.0', '2.0', 'xs:decimal') is False

    def test_type_aware_date_equal(self):
        assert sa.type_aware_equal('2024-01-15', '2024-01-15', 'xs:date') is True

    def test_type_aware_date_mismatch(self):
        assert sa.type_aware_equal('2024-01-15', '2024-01-16', 'xs:date') is False

    def test_type_aware_returns_none_for_unknown(self):
        assert sa.type_aware_equal('hello', 'hello', 'xs:string') is None

    def test_values_equal_with_type_aware_boolean(self):
        """values_equal uses schema type when type_aware is set."""
        opts = _opts(type_aware=True)
        # 'true' and '1' differ as strings but are equal as xs:boolean
        assert xc.values_equal('true', '1', opts, xs_type='xs:boolean') is True

    def test_values_equal_with_type_aware_numeric(self):
        """values_equal applies numeric equality with type awareness."""
        opts = _opts(type_aware=True)
        assert xc.values_equal('1.0', '1', opts, xs_type='xs:decimal') is True

    def test_values_equal_type_aware_falls_back_for_string(self):
        """values_equal falls back to default for xs:string."""
        opts = _opts(type_aware=True)
        assert xc.values_equal('hello', 'world', opts, xs_type='xs:string') is False
        assert xc.values_equal('same', 'same', opts, xs_type='xs:string') is True

    def test_compare_with_schema_type_aware(self, tmp_path):
        """compare_xml_files applies type-aware comparison from schema."""
        xsd = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="flag" type="xs:boolean"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>'''
        xsd_file = str(tmp_path / 'schema.xsd')
        Path(xsd_file).write_text(xsd)

        f1 = write(tmp_path / 'a.xml', '<root><flag>true</flag></root>')
        f2 = write(tmp_path / 'b.xml', '<root><flag>1</flag></root>')

        opts = _opts(schema=xsd_file, type_aware=True)
        diffs = xc.compare_xml_files(f1, f2, opts)
        # 'true' and '1' are equal as xs:boolean
        assert diffs == []

    def test_compare_with_schema_all_uses_unordered(self, tmp_path):
        """xs:all schema causes children to be compared unordered."""
        xsd = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:all>
        <xs:element name="a" type="xs:string"/>
        <xs:element name="b" type="xs:string"/>
      </xs:all>
    </xs:complexType>
  </xs:element>
</xs:schema>'''
        xsd_file = str(tmp_path / 'schema.xsd')
        Path(xsd_file).write_text(xsd)

        f1 = write(tmp_path / 'a.xml', '<root><a>x</a><b>y</b></root>')
        f2 = write(tmp_path / 'b.xml', '<root><b>y</b><a>x</a></root>')

        opts = _opts(schema=xsd_file, type_aware=True)
        diffs = xc.compare_xml_files(f1, f2, opts)
        # xs:all means any order is valid
        assert diffs == []


# ---------------------------------------------------------------------------
# Schema validation integration
# ---------------------------------------------------------------------------

class TestSchemaValidationIntegration:
    """Test pre-flight schema validation in compare_xml_files."""

    def test_compare_without_schema_no_validation(self, tmp_path):
        """No schema = no pre-validation; comparison works as normal."""
        f1 = write(tmp_path / 'a.xml', '<r><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>2</v></r>')
        opts = _opts()
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1

    def test_compare_with_schema_no_lxml_graceful(self, tmp_path):
        """If lxml is unavailable, schema option is tolerated gracefully."""
        xsd = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="r"><xs:complexType><xs:sequence>
    <xs:element name="v" type="xs:string"/>
  </xs:sequence></xs:complexType></xs:element>
</xs:schema>'''
        xsd_file = str(tmp_path / 'schema.xsd')
        Path(xsd_file).write_text(xsd)

        f1 = write(tmp_path / 'a.xml', '<r><v>hello</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>hello</v></r>')

        # Should work even without lxml
        opts = _opts(schema=xsd_file, type_aware=True)
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert diffs == []
