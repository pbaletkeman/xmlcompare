"""Tests for xmlcompare."""

import json
import os
import sys
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
        f1 = write(tmp_path / 'a.xml', '<r xmlns="http://a.com"><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r xmlns="http://b.com"><v>x</v></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts())
        assert len(diffs) > 0

    def test_ignore_namespaces(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r xmlns="http://a.com"><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r xmlns="http://b.com"><v>x</v></r>')
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

    def test_verbose_cli(self, tmp_path, capsys):
        f1 = write(tmp_path / 'a.xml', '<r><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>1</v></r>')
        with pytest.raises(SystemExit) as exc_info:
            xc.main(['--files', f1, f2, '--verbose', '--quiet'])
        # Files are equal → exit 0; --quiet suppresses output even with --verbose
        assert exc_info.value.code == 0

    def test_unordered_cli(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><b/><a/></r>')
        self._run(['--files', f1, f2, '--unordered', '--quiet'], 0)

    def test_skip_keys_cli(self, tmp_path):
        f1 = write(tmp_path / 'a.xml', '<r><ts>2024-01-01</ts><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><ts>2024-12-31</ts><v>1</v></r>')
        self._run(['--files', f1, f2, '--skip-keys', '//ts', '--quiet'], 0)

    def test_dirs_text_output(self, tmp_path, capsys):
        """Exercises the dirs branch of text-format output (format_text_report with key)."""
        d1 = tmp_path / 'd1'
        d2 = tmp_path / 'd2'
        d1.mkdir()
        d2.mkdir()
        write(d1 / 'f.xml', '<r><v>1</v></r>')
        write(d2 / 'f.xml', '<r><v>2</v></r>')
        with pytest.raises(SystemExit):
            xc.main(['--dirs', str(d1), str(d2)])

    def test_dirs_error_string_text_output(self, tmp_path, capsys):
        """Exercises error-string branch in text output when a file is invalid XML."""
        d1 = tmp_path / 'd1'
        d2 = tmp_path / 'd2'
        d1.mkdir()
        d2.mkdir()
        write(d1 / 'bad.xml', '<unclosed>')
        write(d2 / 'bad.xml', '<r/>')
        with pytest.raises(SystemExit):
            xc.main(['--dirs', str(d1), str(d2)])
        captured = capsys.readouterr()
        assert 'ERROR' in captured.out

    def test_dir1_not_a_directory(self, tmp_path):
        """main() exits 2 when dir1 is not a real directory."""
        f = write(tmp_path / 'a.xml', '<r/>')
        d2 = tmp_path / 'd2'
        d2.mkdir()
        with pytest.raises(SystemExit) as exc_info:
            xc.main(['--dirs', f, str(d2), '--quiet'])
        assert exc_info.value.code == 2

    def test_dir2_not_a_directory(self, tmp_path):
        """main() exits 2 when dir2 is not a real directory."""
        d1 = tmp_path / 'd1'
        d1.mkdir()
        f = write(tmp_path / 'b.xml', '<r/>')
        with pytest.raises(SystemExit) as exc_info:
            xc.main(['--dirs', str(d1), f, '--quiet'])
        assert exc_info.value.code == 2

    def test_config_file_not_found(self, tmp_path):
        """main() exits 2 when the --config file does not exist."""
        f1 = write(tmp_path / 'a.xml', '<r/>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        with pytest.raises(SystemExit) as exc_info:
            xc.main(['--files', f1, f2, '--config', str(tmp_path / 'missing.json')])
        assert exc_info.value.code == 2

    def test_config_invalid_content(self, tmp_path):
        """main() exits 2 when the --config file contains invalid JSON."""
        cfg = tmp_path / 'bad.json'
        cfg.write_text('not valid json {{{')
        f1 = write(tmp_path / 'a.xml', '<r/>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        with pytest.raises(SystemExit) as exc_info:
            xc.main(['--files', f1, f2, '--config', str(cfg)])
        assert exc_info.value.code == 2

    def test_output_file_write_error(self, tmp_path):
        """main() exits 2 when the output file cannot be written."""
        f1 = write(tmp_path / 'a.xml', '<r/>')
        f2 = write(tmp_path / 'b.xml', '<r/>')
        bad_dir = tmp_path / 'nonexistent_dir' / 'report.txt'
        with pytest.raises(SystemExit) as exc_info:
            xc.main(['--files', f1, f2, '--output-file', str(bad_dir)])
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# Additional coverage for low-coverage paths
# ---------------------------------------------------------------------------

class TestCoverageGaps:
    """Tests targeting specific uncovered branches to push coverage >90%."""

    def test_difference_repr(self):
        d = xc.Difference('root/a', 'text', 'Text mismatch', 'foo', 'bar')
        r = repr(d)
        assert 'root/a' in r
        assert 'text' in r
        assert 'Text mismatch' in r

    def test_strip_namespace_no_ns(self):
        """strip_namespace should return the tag unchanged when there is no namespace."""
        assert xc.strip_namespace('myTag') == 'myTag'
        assert xc.strip_namespace('') == ''

    def test_ignore_namespaces_plain_tags(self, tmp_path):
        """ignore_namespaces=True on plain (non-namespaced) XML should still work."""
        f1 = write(tmp_path / 'a.xml', '<r><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>x</v></r>')
        opts = xc.CompareOptions()
        opts.ignore_namespaces = True
        assert xc.compare_xml_files(f1, f2, opts) == []

    def test_verbose_mode(self, tmp_path, capsys):
        """verbose=True should print element paths to stderr."""
        f1 = write(tmp_path / 'a.xml', '<r><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>1</v></r>')
        opts = xc.CompareOptions()
        opts.verbose = True
        xc.compare_xml_files(f1, f2, opts)
        captured = capsys.readouterr()
        assert 'Comparing' in captured.err

    def test_attr_missing_in_first(self, tmp_path):
        """Attribute present in second but absent in first should be detected."""
        f1 = write(tmp_path / 'a.xml', '<r><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v id="1">x</v></r>')
        diffs = xc.compare_xml_files(f1, f2, xc.CompareOptions())
        assert any(d.kind == 'attr' for d in diffs)

    def test_attr_missing_in_first_fail_fast(self, tmp_path):
        """fail_fast should stop after an attr-missing-in-first difference."""
        f1 = write(tmp_path / 'a.xml', '<r><v>x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v id="1" class="c">x</v></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1

    def test_attr_missing_in_second_fail_fast(self, tmp_path):
        """fail_fast should stop after an attr-missing-in-second difference."""
        f1 = write(tmp_path / 'a.xml', '<r><v id="1" class="c">x</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>x</v></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1

    def test_attr_value_mismatch_fail_fast(self, tmp_path):
        """fail_fast should stop after an attribute-value mismatch."""
        f1 = write(tmp_path / 'a.xml', '<r><v id="1" x="a">t</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v id="2" x="b">t</v></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1

    def test_fail_fast_after_text_before_children(self, tmp_path):
        """fail_fast should stop after a text difference without descending into children."""
        f1 = write(tmp_path / 'a.xml', '<r>X<a>1</a></r>')
        f2 = write(tmp_path / 'b.xml', '<r>Y<a>2</a></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1

    def test_ordered_missing_in_first_fail_fast(self, tmp_path):
        """_compare_ordered: element present in second but not first, with fail_fast."""
        f1 = write(tmp_path / 'a.xml', '<r><a/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/><b/><c/></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1
        assert diffs[0].kind == 'missing'

    def test_ordered_extra_in_first_fail_fast(self, tmp_path):
        """_compare_ordered: element present in first but not second, with fail_fast."""
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/><c/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1
        assert diffs[0].kind == 'extra'

    def test_unordered_missing_in_first(self, tmp_path):
        """_compare_unordered: tag present in second but missing in first."""
        f1 = write(tmp_path / 'a.xml', '<r><a/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/><b/></r>')
        opts = xc.CompareOptions()
        opts.unordered = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert any(d.kind == 'missing' for d in diffs)

    def test_unordered_missing_in_first_fail_fast(self, tmp_path):
        """_compare_unordered: fail_fast stops after first missing element."""
        f1 = write(tmp_path / 'a.xml', '<r></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/><b/></r>')
        opts = xc.CompareOptions()
        opts.unordered = True
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1

    def test_unordered_extra_fail_fast(self, tmp_path):
        """_compare_unordered: fail_fast stops when tag present in first but not second."""
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/></r>')
        f2 = write(tmp_path / 'b.xml', '<r></r>')
        opts = xc.CompareOptions()
        opts.unordered = True
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1
        assert diffs[0].kind == 'extra'

    def test_unordered_child_diff_fail_fast(self, tmp_path):
        """_compare_unordered: fail_fast stops after first differing child element."""
        f1 = write(tmp_path / 'a.xml', '<r><a>1</a><b>1</b></r>')
        f2 = write(tmp_path / 'b.xml', '<r><b>2</b><a>2</a></r>')
        opts = xc.CompareOptions()
        opts.unordered = True
        opts.fail_fast = True
        diffs = xc.compare_xml_files(f1, f2, opts)
        assert len(diffs) == 1

    def test_invalid_second_file(self, tmp_path):
        """compare_xml_files raises ValueError when the second file is invalid XML."""
        f1 = write(tmp_path / 'a.xml', '<r/>')
        f2 = write(tmp_path / 'b.xml', '<bad><unclosed></bad>')
        with pytest.raises(ValueError, match='Failed to parse'):
            xc.compare_xml_files(f1, f2, xc.CompareOptions())

    def test_second_file_not_found(self, tmp_path):
        """compare_xml_files raises FileNotFoundError when the second file is missing."""
        f1 = write(tmp_path / 'a.xml', '<r/>')
        with pytest.raises(FileNotFoundError):
            xc.compare_xml_files(f1, str(tmp_path / 'nope.xml'), xc.CompareOptions())

    def test_invalid_filter_xpath(self, tmp_path):
        """compare_xml_files raises ValueError for an invalid filter XPath."""
        f1 = write(tmp_path / 'a.xml', '<r><v>1</v></r>')
        f2 = write(tmp_path / 'b.xml', '<r><v>1</v></r>')
        opts = xc.CompareOptions()
        opts.filter_xpath = '[-invalid-'
        with pytest.raises((ValueError, SyntaxError, Exception)):
            xc.compare_xml_files(f1, f2, opts)

    def test_compare_dirs_invalid_xml_file(self, tmp_path):
        """compare_dirs stores error string when a file in the directory is invalid XML."""
        d1 = tmp_path / 'd1'
        d2 = tmp_path / 'd2'
        d1.mkdir()
        d2.mkdir()
        write(d1 / 'bad.xml', '<unclosed>')
        write(d2 / 'bad.xml', '<r/>')
        results = xc.compare_dirs(str(d1), str(d2), xc.CompareOptions())
        assert isinstance(results['bad.xml'], str)

    def test_compare_dirs_fail_fast(self, tmp_path):
        """compare_dirs stops after the first file with differences when fail_fast=True."""
        d1 = tmp_path / 'd1'
        d2 = tmp_path / 'd2'
        d1.mkdir()
        d2.mkdir()
        write(d1 / 'a.xml', '<r><v>1</v></r>')
        write(d2 / 'a.xml', '<r><v>2</v></r>')
        write(d1 / 'b.xml', '<r><v>3</v></r>')
        write(d2 / 'b.xml', '<r><v>4</v></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        results = xc.compare_dirs(str(d1), str(d2), opts)
        assert len(results) == 1

    def test_format_html_report_error(self):
        """format_html_report should render error entries with the error CSS class."""
        result = xc.format_html_report({'file.xml': 'some parse error'})
        assert 'ERROR' in result
        assert 'error' in result
        assert '<html>' in result

    def test_colorize_with_color(self, monkeypatch):
        """_colorize should wrap text in ANSI codes when _use_color() returns True."""
        monkeypatch.setattr(xc, '_use_color', lambda: True)
        colored = xc._colorize('hello', xc.RED)
        assert xc.RED in colored
        assert 'hello' in colored
        assert xc.RESET in colored

    def test_no_yaml_raises_import_error(self, monkeypatch, tmp_path):
        """load_config raises ImportError when pyyaml is unavailable."""
        monkeypatch.setattr(xc, 'HAS_YAML', False)
        cfg = tmp_path / 'cfg.yaml'
        cfg.write_text('tolerance: 0.1\n')
        with pytest.raises(ImportError, match='pyyaml'):
            xc.load_config(str(cfg))

    def test_format_text_report_labels(self):
        """format_text_report should include labels when provided."""
        result = xc.format_text_report([], label1='file1.xml', label2='file2.xml')
        assert 'file1.xml' in result
        assert 'file2.xml' in result

    def test_colorize_no_color(self):
        """_colorize returns plain text when _use_color() is False (no tty in tests)."""
        # In a test environment sys.stdout is not a tty, so _use_color() returns False.
        result = xc._colorize('hello', xc.RED)
        assert result == 'hello'

    def test_fail_fast_before_children_with_preexisting_diffs(self):
        """Line 217: fail_fast returns early when diffs are already present from caller."""
        import xml.etree.ElementTree as ET
        elem1 = ET.fromstring('<r><a>x</a></r>')
        elem2 = ET.fromstring('<r><a>x</a></r>')
        opts = xc.CompareOptions()
        opts.fail_fast = True
        opts.ignore_attributes = True
        pre_existing = [xc.Difference('other', 'text', 'earlier diff')]
        result = xc.compare_elements(elem1, elem2, opts, path='r', diffs=pre_existing)
        # Should have returned early due to fail_fast + pre-existing diffs
        assert result is pre_existing
        assert len(result) == 1
