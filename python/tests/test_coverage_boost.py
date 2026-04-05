"""
Comprehensive tests targeting previously uncovered modules to reach >90% coverage.

Covers: format_unified_diff, format_html_sidebyside, validate_xsd, api_server,
        parse_streaming, parallel, cache, plugin_interface, xmlcompare edge cases.
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree as ET

import pytest

# Ensure the python/ directory is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(path, content):
    Path(path).write_text(content, encoding='utf-8')
    return path


def _xml(content):
    """Write XML to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix='.xml')
    os.close(fd)
    _write(path, content)
    return path


def _make_diff(path='root/a', kind='text', msg='differs', expected='X', actual='Y'):
    from xmlcompare import Difference
    return Difference(path, kind, msg, expected, actual)


# ===========================================================================
# format_unified_diff.py
# ===========================================================================

class TestUnifiedDiffFormatter:
    def setup_method(self):
        from format_unified_diff import UnifiedDiffFormatter
        self.fmt = UnifiedDiffFormatter()

    def test_name(self):
        assert self.fmt.name == 'unified-diff'

    def test_equal_files(self):
        result = self.fmt.format({'k': []}, label1='a.xml', label2='b.xml')
        assert '--- a.xml' in result
        assert '+++ b.xml' in result
        assert '(no differences)' in result

    def test_text_diff(self):
        d = _make_diff(kind='text', expected='old', actual='new')
        result = self.fmt.format({'k': [d]})
        assert '- old' in result
        assert '+ new' in result
        assert '@@ root/a @@' in result

    def test_attr_diff(self):
        d = _make_diff(kind='attr', expected='v1', actual='v2')
        result = self.fmt.format({'k': [d]})
        assert '- v1' in result
        assert '+ v2' in result

    def test_tag_diff(self):
        d = _make_diff(kind='tag', msg='tag mismatch', expected=None, actual=None)
        result = self.fmt.format({'k': [d]})
        assert '! tag mismatch' in result

    def test_missing_diff(self):
        d = _make_diff(kind='missing', msg='element gone', expected=None, actual=None)
        result = self.fmt.format({'k': [d]})
        assert '- element gone' in result

    def test_extra_diff(self):
        d = _make_diff(kind='extra', msg='element added', expected=None, actual=None)
        result = self.fmt.format({'k': [d]})
        assert '+ element added' in result

    def test_other_kind(self):
        d = _make_diff(kind='structure', msg='structure issue', expected=None, actual=None)
        result = self.fmt.format({'k': [d]})
        assert 'structure issue' in result

    def test_error_case(self):
        result = self.fmt.format({'k': 'some error'})
        assert 'Error: some error' in result

    def test_no_trailing_newline(self):
        result = self.fmt.format({'k': []})
        assert not result.endswith('\n')

    def test_diff_without_expected_or_actual(self):
        d = _make_diff(kind='text', expected=None, actual=None)
        result = self.fmt.format({'k': [d]})
        assert '@@ root/a @@' in result

    def test_multiple_keys(self):
        d = _make_diff()
        result = self.fmt.format({'k1': [d], 'k2': []})
        assert '(no differences)' in result
        assert '- X' in result


# ===========================================================================
# format_html_sidebyside.py
# ===========================================================================

class TestHtmlSideBySideFormatter:
    def setup_method(self):
        from format_html_sidebyside import HtmlSideBySideFormatter
        self.fmt = HtmlSideBySideFormatter()

    def test_name(self):
        assert self.fmt.name == 'html-diff'

    def test_equal_produces_html(self):
        result = self.fmt.format({'k': []})
        assert '<!DOCTYPE html>' in result
        assert 'No differences' in result

    def test_with_text_diff(self):
        d = _make_diff(kind='text', expected='old', actual='new')
        result = self.fmt.format({'k': [d]}, label1='Expected', label2='Actual')
        assert '<table' in result
        assert 'old' in result
        assert 'new' in result

    def test_with_missing_diff(self):
        d = _make_diff(kind='missing', expected='X', actual=None)
        result = self.fmt.format({'k': [d]})
        assert 'removed' in result

    def test_with_extra_diff(self):
        d = _make_diff(kind='extra', expected=None, actual='Y')
        result = self.fmt.format({'k': [d]})
        assert 'added' in result

    def test_with_tag_diff(self):
        d = _make_diff(kind='tag', expected='a', actual='b')
        result = self.fmt.format({'k': [d]})
        assert 'TAG' in result

    def test_with_attr_diff(self):
        d = _make_diff(kind='attr', expected='v1', actual='v2')
        result = self.fmt.format({'k': [d]})
        assert 'ATTR' in result

    def test_error_case(self):
        result = self.fmt.format({'k': 'some <error>'})
        assert 'Error' in result
        assert '&lt;error&gt;' in result

    def test_html_escape(self):
        from format_html_sidebyside import HtmlSideBySideFormatter
        assert HtmlSideBySideFormatter._html_escape('<b>&amp;"') == '&lt;b&gt;&amp;amp;&quot;'
        assert HtmlSideBySideFormatter._html_escape(None) == ''

    def test_no_trailing_newline(self):
        result = self.fmt.format({'k': []})
        assert not result.endswith('\n')

    def test_summary_total_count(self):
        d1 = _make_diff()
        d2 = _make_diff()
        result = self.fmt.format({'k': [d1, d2]})
        assert 'Total differences: <strong>2</strong>' in result

    def test_context_diff_kind(self):
        d = _make_diff(kind='context', expected='a', actual='b')
        result = self.fmt.format({'k': [d]})
        assert 'CONTEXT' in result

    def test_labels_in_output(self):
        result = self.fmt.format({'k': []}, label1='File1', label2='File2')
        assert 'File1' in result
        assert 'File2' in result


# ===========================================================================
# validate_xsd.py
# ===========================================================================

class TestValidateXsd:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path):
        self.xsd = str(tmp_path / 'schema.xsd')
        self.valid_xml = str(tmp_path / 'valid.xml')
        self.invalid_xml = str(tmp_path / 'invalid.xml')
        _write(self.xsd, '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="value" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>''')
        _write(self.valid_xml, '<root><value>hello</value></root>')
        _write(self.invalid_xml, '<root><wrong>hello</wrong></root>')

    def test_validate_xml_with_xsd_valid(self, capsys):
        from validate_xsd import validate_xml_with_xsd
        result = validate_xml_with_xsd(self.valid_xml, self.xsd)
        assert result is True

    def test_validate_xml_with_xsd_invalid(self, capsys):
        from validate_xsd import validate_xml_with_xsd
        result = validate_xml_with_xsd(self.invalid_xml, self.xsd)
        assert result is False

    def test_get_validation_errors_valid(self):
        from validate_xsd import get_validation_errors
        errors = get_validation_errors(self.valid_xml, self.xsd)
        assert errors == []

    def test_get_validation_errors_invalid(self):
        from validate_xsd import get_validation_errors
        errors = get_validation_errors(self.invalid_xml, self.xsd)
        assert len(errors) > 0

    def test_get_validation_errors_bad_xsd(self, tmp_path):
        from validate_xsd import get_validation_errors
        bad_xsd = str(tmp_path / 'bad.xsd')
        _write(bad_xsd, 'NOT XML')
        errors = get_validation_errors(self.valid_xml, bad_xsd)
        assert errors is not None

    def test_get_validation_errors_bad_xml(self, tmp_path):
        from validate_xsd import get_validation_errors
        bad_xml = str(tmp_path / 'bad.xml')
        _write(bad_xml, '<not-closed')
        errors = get_validation_errors(bad_xml, self.xsd)
        assert errors is not None


# ===========================================================================
# api_server.py – Flask test client
# ===========================================================================

class TestApiServer:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path):
        from api_server import app
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.tmp = tmp_path
        _write(str(tmp_path / 'a.xml'), '<root><v>1</v></root>')
        _write(str(tmp_path / 'b.xml'), '<root><v>2</v></root>')
        _write(str(tmp_path / 'eq.xml'), '<root><v>1</v></root>')

    def test_health(self):
        resp = self.client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'

    def test_compare_files_equal(self):
        resp = self.client.post('/compare/files', json={
            'file1': str(self.tmp / 'a.xml'),
            'file2': str(self.tmp / 'eq.xml'),
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['equal'] is True

    def test_compare_files_different(self):
        resp = self.client.post('/compare/files', json={
            'file1': str(self.tmp / 'a.xml'),
            'file2': str(self.tmp / 'b.xml'),
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['equal'] is False
        assert len(data['differences']) > 0

    def test_compare_files_missing_params(self):
        resp = self.client.post('/compare/files', json={})
        assert resp.status_code == 400

    def test_compare_files_file_not_found(self):
        resp = self.client.post('/compare/files', json={
            'file1': '/nonexistent/a.xml',
            'file2': '/nonexistent/b.xml',
        })
        assert resp.status_code == 400

    def test_compare_files_with_options(self):
        resp = self.client.post('/compare/files', json={
            'file1': str(self.tmp / 'a.xml'),
            'file2': str(self.tmp / 'b.xml'),
            'options': {'ignore_case': True},
        })
        assert resp.status_code == 200

    def test_compare_content_equal(self):
        resp = self.client.post('/compare/content', json={
            'xml1': '<root><v>42</v></root>',
            'xml2': '<root><v>42</v></root>',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['equal'] is True

    def test_compare_content_different(self):
        resp = self.client.post('/compare/content', json={
            'xml1': '<root><v>1</v></root>',
            'xml2': '<root><v>2</v></root>',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['equal'] is False

    def test_compare_content_missing_params(self):
        resp = self.client.post('/compare/content', json={})
        assert resp.status_code == 400

    def test_compare_content_with_options(self):
        resp = self.client.post('/compare/content', json={
            'xml1': '<root><V>HELLO</V></root>',
            'xml2': '<root><V>hello</V></root>',
            'options': {'ignore_case': True},
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['equal'] is True

    def test_compare_files_both_missing(self):
        resp = self.client.post('/compare/files', json={
            'file1': '/no/such/file.xml',
            'file2': str(self.tmp / 'a.xml'),
        })
        assert resp.status_code == 400


# ===========================================================================
# parse_streaming.py
# ===========================================================================

class TestParseStreaming:
    def test_equal_files(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a>1</a><b>2</b></root>')
        _write(f2, '<root><a>1</a><b>2</b></root>')
        diffs = compare_xml_files_streaming(f1, f2)
        assert diffs == []

    def test_text_diff(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v>1</v></root>')
        _write(f2, '<root><v>2</v></root>')
        diffs = compare_xml_files_streaming(f1, f2)
        assert any(d.kind == 'text' for d in diffs)

    def test_tag_mismatch(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a>1</a></root>')
        _write(f2, '<root><b>1</b></root>')
        diffs = compare_xml_files_streaming(f1, f2)
        assert any(d.kind == 'tag' for d in diffs)

    def test_attribute_diff(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v id="1">text</v></root>')
        _write(f2, '<root><v id="2">text</v></root>')
        diffs = compare_xml_files_streaming(f1, f2)
        assert any(d.kind == 'attr' for d in diffs)

    def test_attribute_missing_in_first(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v>text</v></root>')
        _write(f2, '<root><v id="2">text</v></root>')
        diffs = compare_xml_files_streaming(f1, f2)
        assert any(d.kind == 'attr' for d in diffs)

    def test_attribute_missing_in_second(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v id="1">text</v></root>')
        _write(f2, '<root><v>text</v></root>')
        diffs = compare_xml_files_streaming(f1, f2)
        assert any(d.kind == 'attr' for d in diffs)

    def test_fallback_unordered(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        from xmlcompare import CompareOptions
        opts = CompareOptions()
        opts.unordered = True
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a>1</a><b>2</b></root>')
        _write(f2, '<root><b>2</b><a>1</a></root>')
        diffs = compare_xml_files_streaming(f1, f2, opts)
        assert diffs == []

    def test_structure_only(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        from xmlcompare import CompareOptions
        opts = CompareOptions()
        opts.structure_only = True
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v>1</v></root>')
        _write(f2, '<root><v>999</v></root>')
        diffs = compare_xml_files_streaming(f1, f2, opts)
        assert diffs == []

    def test_fail_fast(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        from xmlcompare import CompareOptions
        opts = CompareOptions()
        opts.fail_fast = True
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a>1</a><b>2</b></root>')
        _write(f2, '<root><a>X</a><b>Y</b></root>')
        diffs = compare_xml_files_streaming(f1, f2, opts)
        assert len(diffs) == 1

    def test_different_element_counts(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a>1</a><b>2</b></root>')
        _write(f2, '<root><a>1</a></root>')
        diffs = compare_xml_files_streaming(f1, f2)
        assert len(diffs) > 0

    def test_get_stream_stats(self, tmp_path):
        from parse_streaming import get_stream_stats
        f = str(tmp_path / 'a.xml')
        _write(f, '<root><a>1</a></root>')
        stats = get_stream_stats(f)
        assert stats.element_count >= 2
        assert stats.file_size_mb >= 0.0
        assert 'MB' in str(stats)
        assert repr(stats) == str(stats)

    def test_get_stream_stats_not_found(self, tmp_path):
        from parse_streaming import get_stream_stats
        with pytest.raises(FileNotFoundError):
            get_stream_stats(str(tmp_path / 'missing.xml'))

    def test_get_memory_usage(self):
        from parse_streaming import get_memory_usage
        mem = get_memory_usage()
        assert mem >= 0.0

    def test_count_elements(self, tmp_path):
        from parse_streaming import count_elements_iterparse
        f = str(tmp_path / 'a.xml')
        _write(f, '<root><a>1</a><b>2</b></root>')
        assert count_elements_iterparse(f) == 3

    def test_ignore_namespaces_streaming(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        from xmlcompare import CompareOptions
        opts = CompareOptions()
        opts.ignore_namespaces = True
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<ns:root xmlns:ns="http://x"><ns:v>1</ns:v></ns:root>')
        _write(f2, '<root><v>1</v></root>')
        diffs = compare_xml_files_streaming(f1, f2, opts)
        assert diffs == []

    def test_default_options(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        diffs = compare_xml_files_streaming(f1, f2, options=None)
        assert diffs == []

    def test_malformed_xml_handled(self, tmp_path):
        from parse_streaming import compare_xml_files_streaming
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><unclosed>')
        _write(f2, '<root/>')
        # Parser is lenient — returns whatever diffs it finds rather than raising
        result = compare_xml_files_streaming(f1, f2)
        assert isinstance(result, list)


# ===========================================================================
# parallel.py
# ===========================================================================

class TestParallel:
    def test_options_roundtrip(self):
        from parallel import _options_to_dict, _dict_to_options
        from xmlcompare import CompareOptions
        opts = CompareOptions()
        opts.tolerance = 0.05
        opts.ignore_case = True
        opts.match_attr = 'id'
        d = _options_to_dict(opts)
        restored = _dict_to_options(d)
        assert restored.tolerance == 0.05
        assert restored.ignore_case is True
        assert restored.match_attr == 'id'

    def test_compare_xml_files_parallel_equal(self, tmp_path):
        from parallel import compare_xml_files_parallel
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<r><a>1</a><b>2</b></r>')
        _write(f2, '<r><a>1</a><b>2</b></r>')
        diffs = compare_xml_files_parallel(f1, f2, num_processes=2)
        assert diffs == []

    def test_compare_xml_files_parallel_different(self, tmp_path):
        from parallel import compare_xml_files_parallel
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<r><a>1</a><b>2</b></r>')
        _write(f2, '<r><a>1</a><b>99</b></r>')
        diffs = compare_xml_files_parallel(f1, f2, num_processes=2)
        assert len(diffs) > 0

    def test_compare_xml_files_parallel_serial_fallback(self, tmp_path):
        from parallel import compare_xml_files_parallel
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<r><a>1</a></r>')   # < 2 children → serial
        _write(f2, '<r><a>1</a></r>')
        diffs = compare_xml_files_parallel(f1, f2, num_processes=1)
        assert diffs == []

    def test_compare_xml_files_parallel_auto_processes(self, tmp_path):
        from parallel import compare_xml_files_parallel
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<r><a>1</a><b>2</b></r>')
        _write(f2, '<r><a>1</a><b>2</b></r>')
        diffs = compare_xml_files_parallel(f1, f2, num_processes=0)
        assert diffs == []

    def test_compare_xml_files_parallel_missing_element_in_second(self, tmp_path):
        from parallel import compare_xml_files_parallel
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<r><a>1</a><b>2</b><c>3</c></r>')
        _write(f2, '<r><a>1</a><b>2</b></r>')
        diffs = compare_xml_files_parallel(f1, f2, num_processes=2)
        assert any(d.kind in ('missing', 'extra') for d in diffs)

    def test_compare_xml_files_parallel_missing_element_in_first(self, tmp_path):
        from parallel import compare_xml_files_parallel
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<r><a>1</a></r>')
        _write(f2, '<r><a>1</a><b>2</b><c>3</c></r>')
        diffs = compare_xml_files_parallel(f1, f2, num_processes=2)
        assert len(diffs) > 0

    def test_compare_xml_files_parallel_invalid_xml(self, tmp_path):
        from parallel import compare_xml_files_parallel
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<unclosed>')
        _write(f2, '<root/>')
        with pytest.raises(ValueError):
            compare_xml_files_parallel(f1, f2)

    def test_compare_xml_files_parallel_not_found(self, tmp_path):
        from parallel import compare_xml_files_parallel
        with pytest.raises(FileNotFoundError):
            compare_xml_files_parallel(str(tmp_path / 'no.xml'), str(tmp_path / 'no2.xml'))

    def test_compare_dirs_parallel_equal(self, tmp_path):
        from parallel import compare_dirs_parallel
        d1 = tmp_path / 'd1'; d1.mkdir()
        d2 = tmp_path / 'd2'; d2.mkdir()
        _write(str(d1 / 'a.xml'), '<root><v>1</v></root>')
        _write(str(d2 / 'a.xml'), '<root><v>1</v></root>')
        results = compare_dirs_parallel(str(d1), str(d2))
        assert results['a.xml'] == []

    def test_compare_dirs_parallel_different(self, tmp_path):
        from parallel import compare_dirs_parallel
        d1 = tmp_path / 'd1'; d1.mkdir()
        d2 = tmp_path / 'd2'; d2.mkdir()
        _write(str(d1 / 'a.xml'), '<root><v>1</v></root>')
        _write(str(d2 / 'a.xml'), '<root><v>2</v></root>')
        results = compare_dirs_parallel(str(d1), str(d2))
        assert len(results['a.xml']) > 0

    def test_compare_dirs_parallel_missing_file(self, tmp_path):
        from parallel import compare_dirs_parallel
        d1 = tmp_path / 'd1'; d1.mkdir()
        d2 = tmp_path / 'd2'; d2.mkdir()
        _write(str(d1 / 'only_in_d1.xml'), '<root/>')
        results = compare_dirs_parallel(str(d1), str(d2))
        assert 'only_in_d1.xml' in results

    def test_compare_dirs_parallel_recursive(self, tmp_path):
        from parallel import compare_dirs_parallel
        d1 = tmp_path / 'd1'; (d1 / 'sub').mkdir(parents=True)
        d2 = tmp_path / 'd2'; (d2 / 'sub').mkdir(parents=True)
        _write(str(d1 / 'sub' / 'a.xml'), '<root><v>1</v></root>')
        _write(str(d2 / 'sub' / 'a.xml'), '<root><v>1</v></root>')
        results = compare_dirs_parallel(str(d1), str(d2), recursive=True)
        assert len(results) >= 1

    def test_get_recommended_process_count(self):
        from parallel import get_recommended_process_count
        count = get_recommended_process_count()
        assert count >= 1

    def test_get_parallel_stats(self):
        from parallel import get_parallel_stats
        stats = get_parallel_stats()
        assert stats.available_cores >= 1
        assert stats.recommended_processes >= 1
        assert stats.expected_speedup >= 1.0
        assert 'Cores:' in str(stats)
        assert repr(stats) == str(stats)

    def test_compare_subtree_worker_error(self):
        from parallel import _compare_subtree_worker
        result = _compare_subtree_worker(('BAD XML', '<root/>', {}, '/test'))
        assert result == []

    def test_compare_file_pair_worker(self, tmp_path):
        from parallel import _compare_file_pair_worker
        from xmlcompare import CompareOptions
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v>1</v></root>')
        _write(f2, '<root><v>1</v></root>')
        opts = {'tolerance': 0.0, 'ignore_case': False, 'unordered': False,
                'ignore_namespaces': False, 'ignore_attributes': False,
                'skip_keys': [], 'skip_pattern': None, 'filter_xpath': None,
                'output_format': 'text', 'structure_only': False,
                'fail_fast': False, 'max_depth': None, 'verbose': False,
                'quiet': True, 'summary': False, 'schema': None,
                'type_aware': False, 'match_attr': None, 'plugins': []}
        label, result = _compare_file_pair_worker((f1, f2, opts))
        assert result == []

    def test_compare_file_pair_worker_error(self, tmp_path):
        from parallel import _compare_file_pair_worker
        opts = {'tolerance': 0.0, 'ignore_case': False, 'unordered': False,
                'ignore_namespaces': False, 'ignore_attributes': False,
                'skip_keys': [], 'skip_pattern': None, 'filter_xpath': None,
                'output_format': 'text', 'structure_only': False,
                'fail_fast': False, 'max_depth': None, 'verbose': False,
                'quiet': True, 'summary': False, 'schema': None,
                'type_aware': False, 'match_attr': None, 'plugins': []}
        label, result = _compare_file_pair_worker(('/no/such.xml', '/no/other.xml', opts))
        assert isinstance(result, str)


# ===========================================================================
# cache.py
# ===========================================================================

class TestCacheModule:
    def test_load_cache_not_found(self, tmp_path):
        import cache
        result = cache.load_cache(str(tmp_path / 'missing.json'))
        assert result == {}

    def test_load_cache_corrupt_json(self, tmp_path):
        import cache
        path = str(tmp_path / 'bad.json')
        _write(path, 'NOT JSON {{{{')
        result = cache.load_cache(path)
        assert result == {}

    def test_save_and_reload(self, tmp_path):
        import cache
        path = str(tmp_path / 'c.json')
        cache.save_cache(path, {'key': True})
        loaded = cache.load_cache(path)
        assert loaded == {'key': True}

    def test_is_cached_equal_true(self, tmp_path):
        import cache
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        c = {}
        cache.update_cache_entry(f1, f2, c, [])
        assert cache.is_cached_equal(f1, f2, c) is True

    def test_is_cached_equal_false_no_entry(self, tmp_path):
        import cache
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        assert cache.is_cached_equal(f1, f2, {}) is False

    def test_is_cached_equal_false_has_diffs(self, tmp_path):
        import cache
        from xmlcompare import Difference
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        c = {}
        cache.update_cache_entry(f1, f2, c, [Difference('p', 'text', 'x')])
        assert cache.is_cached_equal(f1, f2, c) is False

    def test_is_cached_equal_false_file_changed(self, tmp_path):
        import cache
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        c = {}
        cache.update_cache_entry(f1, f2, c, [])
        _write(f1, '<root><changed/></root>')
        assert cache.is_cached_equal(f1, f2, c) is False


# ===========================================================================
# plugin_interface.py – edge cases
# ===========================================================================

class TestPluginInterface:
    def test_register_and_get_filter(self):
        from plugin_interface import PluginRegistry, DifferenceFilter
        registry = PluginRegistry()

        class AlwaysIgnore(DifferenceFilter):
            @property
            def name(self): return 'always-ignore'
            def should_ignore(self, diff):
                return True

        registry.register_filter(AlwaysIgnore())
        filters = registry.get_filters()
        assert len(filters) == 1
        from xmlcompare import Difference
        assert filters[0].should_ignore(Difference('p', 'text', 'msg'))

    def test_load_entry_points_no_crash(self):
        from plugin_interface import PluginRegistry
        registry = PluginRegistry()
        registry.load_entry_points()  # should not raise

    def test_load_module_not_found(self):
        from plugin_interface import PluginRegistry
        registry = PluginRegistry()
        registry.load_module('nonexistent.module.that.does.not.exist')

    def test_load_module_with_formatter(self, tmp_path):
        import importlib
        from plugin_interface import PluginRegistry, FormatterPlugin
        mod_path = tmp_path / 'myplugin.py'
        mod_path.write_text(
            'from plugin_interface import FormatterPlugin\n'
            'class MyFmt(FormatterPlugin):\n'
            '    @property\n'
            '    def name(self): return "my-fmt"\n'
            '    def format(self, r, **kw): return ""\n'
        )
        sys.path.insert(0, str(tmp_path))
        try:
            registry = PluginRegistry()
            registry.load_module('myplugin')
            assert 'my-fmt' in registry.list_formatters()
        finally:
            sys.path.remove(str(tmp_path))

    def test_formatter_plugin_abstract_methods(self):
        from plugin_interface import FormatterPlugin, DifferenceFilter
        class MinFmt(FormatterPlugin):
            @property
            def name(self): return 'x'
            def format(self, r, **kw): return ''
        f = MinFmt()
        assert f.name == 'x'
        assert f.format({}) == ''

        class MinFilter(DifferenceFilter):
            @property
            def name(self): return 'min-filter'
            def should_ignore(self, d): return False
        fil = MinFilter()
        assert fil.should_ignore(None) is False


# ===========================================================================
# xmlcompare.py – specific missing line coverage
# ===========================================================================

class TestXmlcompareCoverage:
    def test_use_color_no_color_env(self, monkeypatch):
        import xmlcompare
        monkeypatch.setenv('NO_COLOR', '1')
        monkeypatch.setattr(xmlcompare, '_COLOR_OVERRIDE', None)
        assert xmlcompare._use_color() is False

    def test_use_color_force_color_env(self, monkeypatch):
        import xmlcompare
        monkeypatch.delenv('NO_COLOR', raising=False)
        monkeypatch.setenv('FORCE_COLOR', '1')
        monkeypatch.setattr(xmlcompare, '_COLOR_OVERRIDE', None)
        assert xmlcompare._use_color() is True

    def test_use_color_override_true(self, monkeypatch):
        import xmlcompare
        monkeypatch.setattr(xmlcompare, '_COLOR_OVERRIDE', True)
        assert xmlcompare._use_color() is True

    def test_use_color_override_false(self, monkeypatch):
        import xmlcompare
        monkeypatch.setattr(xmlcompare, '_COLOR_OVERRIDE', False)
        assert xmlcompare._use_color() is False

    def test_colorize_when_color_disabled(self, monkeypatch):
        import xmlcompare
        monkeypatch.setattr(xmlcompare, '_COLOR_OVERRIDE', False)
        result = xmlcompare._colorize('hello', xmlcompare.RED)
        assert result == 'hello'

    def test_colorize_when_color_enabled(self, monkeypatch):
        import xmlcompare
        monkeypatch.setattr(xmlcompare, '_COLOR_OVERRIDE', True)
        result = xmlcompare._colorize('hello', xmlcompare.RED)
        assert xmlcompare.RED in result
        assert 'hello' in result

    def test_verbose_compare(self, tmp_path, capsys):
        from xmlcompare import compare_xml_files, CompareOptions
        opts = CompareOptions()
        opts.verbose = True
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a>1</a></root>')
        _write(f2, '<root><a>1</a></root>')
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []

    def test_max_depth_limits_comparison(self, tmp_path):
        from xmlcompare import compare_xml_files, CompareOptions
        opts = CompareOptions()
        opts.max_depth = 0
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a><b>different</b></a></root>')
        _write(f2, '<root><a><b>value</b></a></root>')
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []

    def test_swap_option(self, tmp_path):
        from xmlcompare import compare_xml_files, CompareOptions
        opts = CompareOptions()
        opts.swap = True
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v>1</v></root>')
        _write(f2, '<root><v>2</v></root>')
        diffs_swapped = compare_xml_files(f1, f2, opts)
        opts2 = CompareOptions()
        diffs_normal = compare_xml_files(f2, f1, opts2)
        assert len(diffs_swapped) == len(diffs_normal)

    def test_no_color_in_main(self, tmp_path):
        from xmlcompare import main
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        with pytest.raises(SystemExit) as exc_info:
            main(['--files', f1, f2, '--no-color'])
        assert exc_info.value.code == 0

    def test_xmlignore_in_main(self, tmp_path):
        from xmlcompare import main
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><ts>2024</ts><v>1</v></root>')
        _write(f2, '<root><ts>2025</ts><v>1</v></root>')
        ignore = str(tmp_path / '.xmlignore')
        _write(ignore, '# comment\n//ts\n')
        old_cwd = os.getcwd()
        try:
            os.chdir(str(tmp_path))
            with pytest.raises(SystemExit) as exc_info:
                main(['--files', f1, f2])
            assert exc_info.value.code == 0
        finally:
            os.chdir(old_cwd)

    def test_load_xmlignore_not_found(self, tmp_path):
        from xmlcompare import _load_xmlignore
        old_cwd = os.getcwd()
        try:
            os.chdir(str(tmp_path))
            result = _load_xmlignore()
            assert result == []
        finally:
            os.chdir(old_cwd)

    def test_load_xmlignore_with_comments(self, tmp_path):
        from xmlcompare import _load_xmlignore
        _write(str(tmp_path / '.xmlignore'), '# skip timestamps\n//ts\n\n//id\n')
        old_cwd = os.getcwd()
        try:
            os.chdir(str(tmp_path))
            result = _load_xmlignore()
            assert '//ts' in result
            assert '//id' in result
        finally:
            os.chdir(old_cwd)

    def test_diff_only_format_skips_equal(self, tmp_path):
        from xmlcompare import main
        d1 = tmp_path / 'd1'; d1.mkdir()
        d2 = tmp_path / 'd2'; d2.mkdir()
        _write(str(d1 / 'a.xml'), '<root><v>1</v></root>')
        _write(str(d2 / 'a.xml'), '<root><v>1</v></root>')
        _write(str(d1 / 'b.xml'), '<root><v>1</v></root>')
        _write(str(d2 / 'b.xml'), '<root><v>9</v></root>')
        with pytest.raises(SystemExit):
            main(['--dirs', str(d1), str(d2), '--diff-only'])

    def test_output_to_file(self, tmp_path):
        from xmlcompare import main
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        out = str(tmp_path / 'out.txt')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        with pytest.raises(SystemExit) as exc_info:
            main(['--files', f1, f2, '--output-file', out])
        assert exc_info.value.code == 0
        assert Path(out).exists()

    def test_stream_mode_in_main(self, tmp_path):
        from xmlcompare import main
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><v>1</v></root>')
        _write(f2, '<root><v>1</v></root>')
        with pytest.raises(SystemExit) as exc_info:
            main(['--files', f1, f2, '--stream'])
        assert exc_info.value.code == 0

    def test_parallel_mode_in_main(self, tmp_path):
        from xmlcompare import main
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><a>1</a><b>2</b></root>')
        _write(f2, '<root><a>1</a><b>2</b></root>')
        with pytest.raises(SystemExit) as exc_info:
            main(['--files', f1, f2, '--parallel'])
        assert exc_info.value.code == 0

    def test_invalid_dir_in_main(self, tmp_path):
        from xmlcompare import main
        with pytest.raises(SystemExit) as exc_info:
            main(['--dirs', str(tmp_path / 'no_such'), str(tmp_path / 'no_other')])
        assert exc_info.value.code == 2

    def test_schema_validation_in_compare(self, tmp_path):
        from xmlcompare import compare_xml_files, CompareOptions
        xsd = str(tmp_path / 'schema.xsd')
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(xsd, '''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root" type="xs:string"/>
</xs:schema>''')
        _write(f1, '<root>hello</root>')
        _write(f2, '<root>hello</root>')
        opts = CompareOptions()
        opts.schema = xsd
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []

    def test_has_yaml_import_coverage(self):
        import xmlcompare
        assert hasattr(xmlcompare, 'HAS_YAML')

    def test_build_output_with_errors(self, tmp_path):
        from xmlcompare import _build_output, CompareOptions
        opts = CompareOptions()
        results = {'file.xml': 'parse error message'}
        output = _build_output(results, opts, None)
        assert 'ERROR' in output

    def test_summary_output(self, tmp_path):
        from xmlcompare import _build_output, CompareOptions
        from xmlcompare import Difference
        opts = CompareOptions()
        opts.summary = True
        results = {
            'eq.xml': [],
            'diff.xml': [Difference('p', 'text', 'x')],
        }
        output = _build_output(results, opts, None)
        assert 'Total:' in output
        assert 'Equal: 1' in output

    def test_format_text_report_with_diff_only_colors(self, tmp_path, monkeypatch):
        import xmlcompare
        monkeypatch.setattr(xmlcompare, '_COLOR_OVERRIDE', True)
        from xmlcompare import _format_output, CompareOptions, Difference
        opts = CompareOptions()
        opts.diff_only = True
        opts.output_format = 'text'
        results = {
            'equal.xml': [],
            'diff.xml': [Difference('p', 'text', 'differs')],
        }
        output = _format_output(results, opts, None)
        assert 'differs' in output

    def test_json_output_format(self, tmp_path):
        from xmlcompare import main
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        with pytest.raises(SystemExit) as exc_info:
            main(['--files', f1, f2, '--output-format', 'json'])
        assert exc_info.value.code == 0

    def test_html_output_format(self, tmp_path):
        from xmlcompare import main
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root/>')
        _write(f2, '<root/>')
        with pytest.raises(SystemExit) as exc_info:
            main(['--files', f1, f2, '--output-format', 'html'])
        assert exc_info.value.code == 0

    def test_xslt_preprocessing(self, tmp_path):
        pytest.importorskip('lxml')
        from xmlcompare import compare_xml_files, CompareOptions
        xslt = str(tmp_path / 'strip.xsl')
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(xslt, '''<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml"/>
  <xsl:template match="@*|node()">
    <xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>
  </xsl:template>
</xsl:stylesheet>''')
        _write(f1, '<root><v>1</v></root>')
        _write(f2, '<root><v>1</v></root>')
        opts = CompareOptions()
        opts.xslt = xslt
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []

    def test_canonicalize_removes_comments(self, tmp_path):
        from xmlcompare import compare_xml_files, CompareOptions
        f1 = str(tmp_path / 'a.xml')
        f2 = str(tmp_path / 'b.xml')
        _write(f1, '<root><!-- a comment --><v>1</v></root>')
        _write(f2, '<root><v>1</v></root>')
        opts = CompareOptions()
        opts.canonicalize = True
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []

    def test_dirs_parallel_mode(self, tmp_path):
        from xmlcompare import main
        d1 = tmp_path / 'd1'; d1.mkdir()
        d2 = tmp_path / 'd2'; d2.mkdir()
        _write(str(d1 / 'a.xml'), '<root><a>1</a><b>2</b></root>')
        _write(str(d2 / 'a.xml'), '<root><a>1</a><b>2</b></root>')
        with pytest.raises(SystemExit) as exc_info:
            main(['--dirs', str(d1), str(d2), '--parallel'])
        assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# Benchmark module coverage tests
# ---------------------------------------------------------------------------

class TestBenchmarkCoverage:
    def test_generate_large_xml_named(self, tmp_path):
        from benchmark import generate_large_xml
        fpath = generate_large_xml(0.001, str(tmp_path / 'test.xml'))
        assert fpath.exists()
        assert fpath.stat().st_size > 0

    def test_generate_large_xml_default_filename(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from benchmark import generate_large_xml
        fpath = generate_large_xml(0.001)
        assert fpath.exists()

    def test_benchmark_result_ok_str(self):
        from benchmark import BenchmarkResult
        r = BenchmarkResult('my-label', 1.0, 1.0, 2.0, 5, 'OK')
        s = str(r)
        assert '2.00s' in s
        assert '5 diffs' in s

    def test_benchmark_result_error_str(self):
        from benchmark import BenchmarkResult
        r = BenchmarkResult('my-label', 0, 0, 0, 0, 'ERROR: not found')
        s = str(r)
        assert 'ERROR: not found' in s

    def test_benchmark_result_zero_elapsed(self):
        from benchmark import BenchmarkResult
        r = BenchmarkResult('zero', 1.0, 1.0, 0.0, 0, 'OK')
        s = str(r)
        assert 'zero' in s

    def test_benchmark_comparison_ok(self, tmp_path):
        from benchmark import benchmark_comparison
        f1 = tmp_path / 'a.xml'
        f2 = tmp_path / 'b.xml'
        f1.write_text('<root><item>1</item></root>')
        f2.write_text('<root><item>2</item></root>')
        r = benchmark_comparison(f1, f2, 'dom-test')
        assert r.label == 'dom-test'
        assert r.status == 'OK'
        assert r.diff_count > 0

    def test_benchmark_comparison_equal_files(self, tmp_path):
        from benchmark import benchmark_comparison
        f1 = tmp_path / 'c.xml'
        f2 = tmp_path / 'd.xml'
        f1.write_text('<root/>')
        f2.write_text('<root/>')
        r = benchmark_comparison(f1, f2, 'equal')
        assert r.status == 'OK'
        assert r.diff_count == 0

    def test_benchmark_comparison_error(self, tmp_path):
        from benchmark import benchmark_comparison
        r = benchmark_comparison(
            tmp_path / 'missing1.xml',
            tmp_path / 'missing2.xml',
            'err',
        )
        assert 'ERROR' in r.status

    def test_benchmark_streaming_ok(self, tmp_path):
        from benchmark import benchmark_streaming
        f1 = tmp_path / 'a.xml'
        f2 = tmp_path / 'b.xml'
        f1.write_text('<root><item>hello</item></root>')
        f2.write_text('<root><item>hello</item></root>')
        r = benchmark_streaming(f1, f2, 'stream-ok')
        assert r.label == 'stream-ok'

    def test_benchmark_streaming_error(self, tmp_path):
        from benchmark import benchmark_streaming
        r = benchmark_streaming(
            tmp_path / 'missing.xml',
            tmp_path / 'missing2.xml',
            'stream-err',
        )
        assert 'ERROR' in r.status

    def test_benchmark_parallel_ok(self, tmp_path):
        from benchmark import benchmark_parallel
        f1 = tmp_path / 'a.xml'
        f2 = tmp_path / 'b.xml'
        f1.write_text('<root/>')
        f2.write_text('<root/>')
        r = benchmark_parallel(f1, f2, 'par-ok', threads=1)
        assert r.label == 'par-ok'

    def test_benchmark_parallel_error(self, tmp_path):
        from benchmark import benchmark_parallel
        r = benchmark_parallel(
            tmp_path / 'missing.xml',
            tmp_path / 'missing2.xml',
            'par-err',
        )
        assert 'ERROR' in r.status

    def test_run_benchmark_suite_mocked(self, tmp_path, monkeypatch, capsys):
        from benchmark import BenchmarkResult
        tiny = tmp_path / 'small.xml'
        tiny.write_text('<root/>')

        mock_result = BenchmarkResult('lbl', 0.001, 0.001, 0.001, 0, 'OK')

        monkeypatch.setattr('benchmark.generate_large_xml', lambda *a, **k: tiny)
        monkeypatch.setattr('benchmark.benchmark_comparison', lambda *a, **k: mock_result)
        monkeypatch.setattr('benchmark.benchmark_streaming', lambda *a, **k: mock_result)
        monkeypatch.setattr('benchmark.benchmark_parallel', lambda *a, **k: mock_result)

        import benchmark as bm
        bm.run_benchmark_suite()

        out = capsys.readouterr().out
        assert 'Benchmark' in out


# ---------------------------------------------------------------------------
# validate_xsd ImportError and __main__ coverage tests
# ---------------------------------------------------------------------------

class TestValidateXsdImportCoverage:
    def test_validate_xml_with_xsd_no_lxml(self, tmp_path, monkeypatch):
        import builtins
        import sys
        import validate_xsd

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'lxml' or name == 'lxml.etree':
                raise ImportError('mocked lxml missing')
            return real_import(name, *args, **kwargs)

        for key in list(sys.modules.keys()):
            if 'lxml' in key:
                monkeypatch.delitem(sys.modules, key)

        monkeypatch.setattr(builtins, '__import__', mock_import)

        with pytest.raises(SystemExit):
            validate_xsd.validate_xml_with_xsd(
                str(tmp_path / 'a.xml'), str(tmp_path / 'b.xsd')
            )

    def test_get_validation_errors_no_lxml(self, tmp_path, monkeypatch):
        import builtins
        import sys
        import validate_xsd

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'lxml' or name == 'lxml.etree':
                raise ImportError('mocked lxml missing')
            return real_import(name, *args, **kwargs)

        for key in list(sys.modules.keys()):
            if 'lxml' in key:
                monkeypatch.delitem(sys.modules, key)

        monkeypatch.setattr(builtins, '__import__', mock_import)

        result = validate_xsd.get_validation_errors(
            str(tmp_path / 'a.xml'), str(tmp_path / 'b.xsd')
        )
        assert result is None

    def test_validate_xsd_main_wrong_args(self, monkeypatch):
        import sys
        import runpy
        from pathlib import Path

        monkeypatch.setattr(sys, 'argv', ['validate_xsd'])
        vxsd_path = str(Path(__file__).parent.parent / 'validate_xsd.py')

        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(vxsd_path, run_name='__main__')
        assert exc_info.value.code == 1

    def test_validate_xsd_main_with_valid_xml(self, tmp_path, monkeypatch):
        pytest.importorskip('lxml')
        import sys
        import runpy
        from pathlib import Path

        xsd_content = (
            '<?xml version="1.0"?>'
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:element name="root"/>'
            '</xs:schema>'
        )
        xml_file = str(tmp_path / 'test.xml')
        xsd_file = str(tmp_path / 'test.xsd')
        Path(xml_file).write_text('<root/>')
        Path(xsd_file).write_text(xsd_content)

        monkeypatch.setattr(sys, 'argv', ['validate_xsd', xml_file, xsd_file])
        vxsd_path = str(Path(__file__).parent.parent / 'validate_xsd.py')

        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(vxsd_path, run_name='__main__')
        assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# api_server error paths and main() coverage tests
# ---------------------------------------------------------------------------

class TestApiServerCoverage:
    @pytest.fixture
    def client(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from api_server import app
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c

    def test_compare_files_file2_not_found(self, client, tmp_path):
        f1 = tmp_path / 'a.xml'
        f1.write_text('<root/>')
        resp = client.post('/compare/files', json={
            'file1': str(f1),
            'file2': str(tmp_path / 'nonexistent_xyz.xml'),
        })
        assert resp.status_code == 400
        assert 'file2 not found' in resp.get_json()['error']

    def test_compare_files_comparison_exception(self, client, tmp_path, monkeypatch):
        f1 = tmp_path / 'a.xml'
        f2 = tmp_path / 'b.xml'
        f1.write_text('<root/>')
        f2.write_text('<root/>')

        monkeypatch.setattr('api_server.compare_xml_files',
                            lambda *a, **k: (_ for _ in ()).throw(ValueError('boom')))

        resp = client.post('/compare/files', json={
            'file1': str(f1), 'file2': str(f2),
        })
        assert resp.status_code == 500
        assert 'boom' in resp.get_json()['error']

    def test_compare_content_comparison_exception(self, client, monkeypatch):
        monkeypatch.setattr('api_server.compare_xml_files',
                            lambda *a, **k: (_ for _ in ()).throw(ValueError('content boom')))

        resp = client.post('/compare/content', json={
            'xml1': '<r/>', 'xml2': '<r/>',
        })
        assert resp.status_code == 500
        assert 'content boom' in resp.get_json()['error']

    def test_api_server_main_function(self, monkeypatch):
        import sys
        from api_server import main, app

        monkeypatch.setattr(sys, 'argv', [
            'api_server', '--host', '127.0.0.1', '--port', '5001',
        ])
        run_calls = []

        def mock_run(*args, **kwargs):
            run_calls.append(kwargs)

        monkeypatch.setattr(app, 'run', mock_run)
        main()
        assert len(run_calls) == 1
        assert run_calls[0]['host'] == '127.0.0.1'
        assert run_calls[0]['port'] == 5001

    def test_api_server_main_debug_flag(self, monkeypatch):
        import sys
        from api_server import main, app

        monkeypatch.setattr(sys, 'argv', ['api_server', '--debug'])
        run_calls = []

        def mock_run(*args, **kwargs):
            run_calls.append(kwargs)

        monkeypatch.setattr(app, 'run', mock_run)
        main()
        assert run_calls[0].get('debug') is True


# ---------------------------------------------------------------------------
# plugin_interface deeper coverage tests
# ---------------------------------------------------------------------------

class TestPluginInterfaceCoverage:
    def test_load_entry_points_with_failing_filter_eps(self, monkeypatch):
        from unittest.mock import MagicMock
        from plugin_interface import PluginRegistry

        bad_fmt_ep = MagicMock()
        bad_fmt_ep.load.side_effect = RuntimeError('bad formatter ep')
        bad_fmt_ep.name = 'bad_fmt'

        bad_flt_ep = MagicMock()
        bad_flt_ep.load.side_effect = RuntimeError('bad filter ep')
        bad_flt_ep.name = 'bad_flt'

        monkeypatch.setattr(
            'plugin_interface.importlib.metadata.entry_points',
            lambda: {
                'xmlcompare.formatters': [bad_fmt_ep],
                'xmlcompare.filters': [bad_flt_ep],
            },
        )

        registry = PluginRegistry()
        registry.load_entry_points()  # must not raise

    def test_load_module_skips_difference_filter_base(self, monkeypatch):
        import importlib
        import types
        from plugin_interface import PluginRegistry, DifferenceFilter

        class ConcreteFilter(DifferenceFilter):
            @property
            def name(self):
                return 'concrete'

            def should_ignore(self, diff):
                return True

        fake_mod = types.ModuleType('fake_mod_178_test')
        fake_mod.DifferenceFilter = DifferenceFilter
        fake_mod.ConcreteFilter = ConcreteFilter

        real_import_module = importlib.import_module

        def mock_import_module(name):
            if name == 'fake_mod_178_test':
                return fake_mod
            return real_import_module(name)

        monkeypatch.setattr('plugin_interface.importlib.import_module', mock_import_module)

        registry = PluginRegistry()
        registry.load_module('fake_mod_178_test')
        assert len(registry.get_filters()) >= 1

    def test_load_module_formatter_instantiation_fails(self, monkeypatch):
        import importlib
        import types
        from plugin_interface import PluginRegistry, FormatterPlugin

        class BrokenFormatter(FormatterPlugin):
            @property
            def name(self):
                return 'broken-fmt'

            def format(self, diffs, label1='', label2=''):
                return ''

            def __init__(self):
                raise RuntimeError('cannot instantiate formatter')

        fake_mod = types.ModuleType('fake_mod_182_test')
        fake_mod.BrokenFormatter = BrokenFormatter

        real_import_module = importlib.import_module

        def mock_import_module(name):
            if name == 'fake_mod_182_test':
                return fake_mod
            return real_import_module(name)

        monkeypatch.setattr('plugin_interface.importlib.import_module', mock_import_module)

        registry = PluginRegistry()
        registry.load_module('fake_mod_182_test')  # must not raise

    def test_load_module_filter_instantiation_fails(self, monkeypatch):
        import importlib
        import types
        from plugin_interface import PluginRegistry, DifferenceFilter

        class BrokenFilter(DifferenceFilter):
            @property
            def name(self):
                return 'broken-flt'

            def should_ignore(self, diff):
                return True

            def __init__(self):
                raise RuntimeError('cannot instantiate filter')

        fake_mod = types.ModuleType('fake_mod_186_test')
        fake_mod.BrokenFilter = BrokenFilter

        real_import_module = importlib.import_module

        def mock_import_module(name):
            if name == 'fake_mod_186_test':
                return fake_mod
            return real_import_module(name)

        monkeypatch.setattr('plugin_interface.importlib.import_module', mock_import_module)

        registry = PluginRegistry()
        registry.load_module('fake_mod_186_test')  # must not raise

    def test_register_builtin_formatters_import_errors(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name in ('format_unified_diff', 'format_html_sidebyside'):
                raise ImportError('mocked missing formatter')
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, '__import__', mock_import)

        from plugin_interface import _register_builtin_formatters
        _register_builtin_formatters()  # must not raise
