"""Tests for xmlcompare."""

import json
import sys
import os
from pathlib import Path

import pytest

# Ensure the package root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))
import xmlcompare as xc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _opts(**kwargs):
    opts = xc.CompareOptions()
    for k, v in kwargs.items():
        setattr(opts, k, v)
    return opts


def write(path, content):
    Path(path).write_text(content)
    return str(path)


# ---------------------------------------------------------------------------
# Numeric normalisation
# ---------------------------------------------------------------------------

class TestNumericNormalisation:
    def test_trailing_zero(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>10.10</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>10.1</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts()) == []

    def test_integer_vs_float(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>10.0</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>10</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts()) == []

    def test_tolerance_within(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>1.001</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>1.002</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts(tolerance=0.01)) == []

    def test_tolerance_exceeded(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>1.0</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>2.0</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(tolerance=0.001))
        assert len(diffs) == 1
        assert diffs[0].kind == 'text'

    def test_different_text_values(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>hello</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>world</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts())
        assert len(diffs) == 1


# ---------------------------------------------------------------------------
# Whitespace normalisation
# ---------------------------------------------------------------------------

class TestWhitespaceNormalisation:
    def test_expanded_vs_inline(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>true</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>\n    true\n</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts()) == []

    def test_multiple_spaces_vs_single(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>hello   world</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>hello world</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts()) == []


# ---------------------------------------------------------------------------
# Ignore case
# ---------------------------------------------------------------------------

class TestIgnoreCase:
    def test_case_equal(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>Hello</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>hello</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts(ignore_case=True)) == []

    def test_case_sensitive_default(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>Hello</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>hello</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts())
        assert len(diffs) == 1


# ---------------------------------------------------------------------------
# Attribute comparison
# ---------------------------------------------------------------------------

class TestAttributes:
    def test_attrs_equal(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v id="1">x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v id="1">x</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts()) == []

    def test_attrs_differ(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v id="1">x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v id="2">x</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts())
        assert any(d.kind == 'attr' for d in diffs)

    def test_ignore_attributes(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v id="1">x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v id="2">x</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts(ignore_attributes=True)) == []

    def test_missing_attribute(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v id="1">x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>x</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts())
        assert any(d.kind == 'attr' for d in diffs)


# ---------------------------------------------------------------------------
# Namespace handling
# ---------------------------------------------------------------------------

class TestNamespaces:
    NS = 'http://example.com/ns'

    def test_namespace_aware_equal(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', f'<r xmlns="{self.NS}"><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', f'<r xmlns="{self.NS}"><v>x</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts()) == []

    def test_namespace_mismatch(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', f'<r xmlns="http://a.com"><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', f'<r xmlns="http://b.com"><v>x</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts())
        assert len(diffs) > 0

    def test_ignore_namespaces(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', f'<r xmlns="http://a.com"><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', f'<r xmlns="http://b.com"><v>x</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts(ignore_namespaces=True)) == []


# ---------------------------------------------------------------------------
# Ordered vs unordered
# ---------------------------------------------------------------------------

class TestOrdering:
    def test_ordered_equal(self, tmp_path):
        xml = '<r><a/><b/></r>'
        f1 = write(tmp_path / 'a.xml', xml)
        f2 = write(tmp_path / 'b.xml', xml)
        assert xc.compare_xml_files(f1, f2, _opts()) == []

    def test_ordered_different_order(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><b/><a/></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts())
        assert len(diffs) > 0

    def test_unordered_equal_regardless_of_order(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><b/><a/></r>')
        assert xc.compare_xml_files(f1, f2, _opts(unordered=True)) == []

    def test_unordered_detects_missing(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(unordered=True))
        assert len(diffs) > 0


# ---------------------------------------------------------------------------
# Skip keys and skip pattern
# ---------------------------------------------------------------------------

class TestSkipping:
    def test_skip_key_double_slash(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><ts>2024-01-01</ts><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><ts>2024-12-31</ts><v>1</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts(skip_keys=['//ts'])) == []

    def test_skip_key_exact_path(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><ts>2024-01-01</ts><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><ts>2024-12-31</ts><v>1</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts(skip_keys=['r/ts'])) == []

    def test_skip_key_not_matched(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><ts>2024-01-01</ts><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><ts>2024-12-31</ts><v>1</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(skip_keys=['//other']))
        assert len(diffs) > 0

    def test_skip_pattern(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><timestamp>2024-01-01</timestamp><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><timestamp>2024-12-31</timestamp><v>1</v></r>')
        assert xc.compare_xml_files(f1, f2, _opts(skip_pattern=r'time')) == []

    def test_skip_pattern_no_match(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><timestamp>A</timestamp></r>')
        f2 = write(tmp_path / 'b.xml', '<r><timestamp>B</timestamp></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(skip_pattern=r'xyz'))
        assert len(diffs) > 0


# ---------------------------------------------------------------------------
# Filter XPath
# ---------------------------------------------------------------------------

class TestFilter:
    def test_filter_matches(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><keep>same</keep><ignore>X</ignore></r>')
        f2 = write(tmp_path / 'b.xml', '<r><keep>same</keep><ignore>Y</ignore></r>')
        assert xc.compare_xml_files(f1, f2, _opts(filter_xpath='keep')) == []

    def test_filter_finds_difference(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><keep>A</keep><ignore>same</ignore></r>')
        f2 = write(tmp_path / 'b.xml', '<r><keep>B</keep><ignore>same</ignore></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(filter_xpath='keep'))
        assert len(diffs) > 0


# ---------------------------------------------------------------------------
# Fail fast
# ---------------------------------------------------------------------------

class TestFailFast:
    def test_stops_early(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><a>1</a><b>2</b><c>3</c></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a>X</a><b>Y</b><c>Z</c></r>')
        diffs_ff = xc.compare_xml_files(f1, f2, _opts(fail_fast=True))
        diffs_all = xc.compare_xml_files(f1, f2, _opts())
        assert len(diffs_ff) < len(diffs_all)
        assert len(diffs_ff) >= 1


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_file_not_found(self, tmp_path):
        f2 = write(tmp_path / 'b.xml', '<r/>')
        with pytest.raises(FileNotFoundError):
            xc.compare_xml_files(str(tmp_path / 'nope.xml'), f2, _opts())

    def test_invalid_xml(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><unclosed></r>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        with pytest.raises(ValueError, match='Failed to parse'):
            xc.compare_xml_files(f1, f2, _opts())


# ---------------------------------------------------------------------------
# Directory comparison
# ---------------------------------------------------------------------------

class TestDirComparison:
    def _make_dirs(self, tmp_path):
        d1 = tmp_path / 'd1'
        d2 = tmp_path / 'd2'
        d1.mkdir()
        d2.mkdir()
        return d1, d2

    def test_matching_files_equal(self, tmp_path):
        d1, d2 = self._make_dirs(tmp_path)
        write(d1 / 'file.xml', '<r><v>1</v></r>')
        write(d2 / 'file.xml', '<r><v>1</v></r>')
        results = xc.compare_dirs(str(d1), str(d2), _opts())
        assert results['file.xml'] == []

    def test_matching_files_differ(self, tmp_path):
        d1, d2 = self._make_dirs(tmp_path)
        write(d1 / 'file.xml', '<r><v>1</v></r>')
        write(d2 / 'file.xml', '<r><v>2</v></r>')
        results = xc.compare_dirs(str(d1), str(d2), _opts())
        assert len(results['file.xml']) > 0

    def test_missing_in_second(self, tmp_path):
        d1, d2 = self._make_dirs(tmp_path)
        write(d1 / 'only_in_d1.xml', '<r/>')
        results = xc.compare_dirs(str(d1), str(d2), _opts())
        assert any(d.kind == 'missing' for d in results['only_in_d1.xml'])

    def test_missing_in_first(self, tmp_path):
        d1, d2 = self._make_dirs(tmp_path)
        write(d2 / 'only_in_d2.xml', '<r/>')
        results = xc.compare_dirs(str(d1), str(d2), _opts())
        assert any(d.kind == 'missing' for d in results['only_in_d2.xml'])

    def test_recursive(self, tmp_path):
        d1, d2 = self._make_dirs(tmp_path)
        (d1 / 'sub').mkdir()
        (d2 / 'sub').mkdir()
        write(d1 / 'sub' / 'deep.xml', '<r><v>1</v></r>')
        write(d2 / 'sub' / 'deep.xml', '<r><v>2</v></r>')
        results = xc.compare_dirs(str(d1), str(d2), _opts(), recursive=True)
        key = os.path.join('sub', 'deep.xml')
        assert key in results
        assert len(results[key]) > 0

    def test_non_recursive_ignores_subdirs(self, tmp_path):
        d1, d2 = self._make_dirs(tmp_path)
        (d1 / 'sub').mkdir()
        (d2 / 'sub').mkdir()
        write(d1 / 'sub' / 'deep.xml', '<r><v>1</v></r>')
        write(d2 / 'sub' / 'deep.xml', '<r><v>2</v></r>')
        results = xc.compare_dirs(str(d1), str(d2), _opts(), recursive=False)
        key = os.path.join('sub', 'deep.xml')
        assert key not in results


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

class TestOutputFormatting:
    def _diffs(self):
        return [xc.Difference('root/a', 'text', 'Text mismatch', 'foo', 'bar')]

    def test_text_equal(self):
        result = xc.format_text_report([])
        assert 'equal' in result.lower()

    def test_text_diff(self):
        result = xc.format_text_report(self._diffs())
        assert 'TEXT' in result
        assert 'mismatch' in result.lower()

    def test_json_equal(self):
        data = {'file.xml': []}
        result = xc.format_json_report(data)
        obj = json.loads(result)
        assert obj['file.xml']['equal'] is True
        assert obj['file.xml']['differences'] == []

    def test_json_diff(self):
        data = {'file.xml': self._diffs()}
        result = xc.format_json_report(data)
        obj = json.loads(result)
        assert obj['file.xml']['equal'] is False
        assert len(obj['file.xml']['differences']) == 1

    def test_json_error(self):
        data = {'file.xml': 'parse error'}
        result = xc.format_json_report(data)
        obj = json.loads(result)
        assert 'error' in obj['file.xml']

    def test_html_equal(self):
        result = xc.format_html_report({'f.xml': []})
        assert 'EQUAL' in result
        assert '<html>' in result

    def test_html_diff(self):
        result = xc.format_html_report({'f.xml': self._diffs()})
        assert 'difference' in result.lower()


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

class TestConfigLoading:
    def test_json_config(self, tmp_path):
        cfg = tmp_path / 'cfg.json'
        cfg.write_text(json.dumps({'tolerance': 0.5, 'ignore_case': True}))
        opts = xc._opts_from_dict(xc.load_config(str(cfg)))
        assert opts.tolerance == 0.5
        assert opts.ignore_case is True

    def test_yaml_config(self, tmp_path):
        cfg = tmp_path / 'cfg.yaml'
        cfg.write_text('tolerance: 0.1\nunordered: true\n')
        opts = xc._opts_from_dict(xc.load_config(str(cfg)))
        assert opts.tolerance == 0.1
        assert opts.unordered is True


# ---------------------------------------------------------------------------
# CLI (exit codes and argument handling)
# ---------------------------------------------------------------------------

class TestCLI:
    def _run(self, args, expected_exit):
        with pytest.raises(SystemExit) as exc_info:
            xc.main(args)
        assert exc_info.value.code == expected_exit

    def test_exit_0_equal(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>1</v></r>')
        self._run(['--files', f1, f2, '--quiet'], 0)

    def test_exit_1_different(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>2</v></r>')
        self._run(['--files', f1, f2, '--quiet'], 1)

    def test_exit_2_file_not_found(self, tmp_path):
        f2 = write(tmp_path / 'b.xml', '<r/>')
        self._run(['--files', str(tmp_path / 'missing.xml'), f2, '--quiet'], 2)

    def test_exit_2_invalid_xml(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<bad><unclosed></bad>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        self._run(['--files', f1, f2, '--quiet'], 2)

    def test_exit_2_no_input(self):
        self._run(['--quiet'], 2)

    def test_summary_output(self, tmp_path, capsys):
        f1 = write(tmp_path / 'a.xml', '<r><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>1</v></r>')
        with pytest.raises(SystemExit):
            xc.main(['--files', f1, f2, '--summary'])
        captured = capsys.readouterr()
        assert 'Total' in captured.out
        assert 'Equal' in captured.out

    def test_json_output(self, tmp_path, capsys):
        f1 = write(tmp_path / 'a.xml', '<r/>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        with pytest.raises(SystemExit):
            xc.main(['--files', f1, f2, '--output-format', 'json'])
        captured = capsys.readouterr()
        obj = json.loads(captured.out)
        assert isinstance(obj, dict)

    def test_output_file(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r/>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        out_file = str(tmp_path / 'report.txt')
        with pytest.raises(SystemExit):
            xc.main(['--files', f1, f2, '--output-file', out_file])
        assert os.path.exists(out_file)

    def test_dirs_cli(self, tmp_path):
        d1 = tmp_path / 'd1'
        d2 = tmp_path / 'd2'
        d1.mkdir()
        d2.mkdir()
        write(d1 / 'f.xml', '<r/>')
        write(d2 / 'f.xml', '<r/>')
        self._run(['--dirs', str(d1), str(d2), '--quiet'], 0)

    def test_config_cli(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>Hello</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>hello</v></r>')
        cfg = tmp_path / 'cfg.json'
        cfg.write_text(json.dumps({'ignore_case': True}))
        self._run(['--files', f1, f2, '--config', str(cfg), '--quiet'], 0)

    def test_tolerance_cli(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><v>1.001</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>1.002</v></r>')
        self._run(['--files', f1, f2, '--tolerance', '0.01', '--quiet'], 0)

    def test_ignore_namespaces_cli(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r xmlns="http://a.com"><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r xmlns="http://b.com"><v>x</v></r>')
        self._run(['--files', f1, f2, '--ignore-namespaces', '--quiet'], 0)

    def test_html_output_format(self, tmp_path, capsys):
        f1 = write(tmp_path / 'a.xml', '<r/>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        with pytest.raises(SystemExit):
            xc.main(['--files', f1, f2, '--output-format', 'html'])
        captured = capsys.readouterr()
        assert '<html>' in captured.out
