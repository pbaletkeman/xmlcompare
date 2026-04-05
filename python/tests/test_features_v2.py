"""Tests for Phase-4 features: match_attr, diff_only, canonicalize, xslt, cache,
streaming/parallel benchmarks, and the REST API."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from xmlcompare import CompareOptions, compare_xml_files, _format_output

try:
    import lxml  # noqa: F401
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

try:
    import flask  # noqa: F401
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(content: str, suffix: str = ".xml") -> str:
    """Write content to a temp file and return the path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


def _opts(**kwargs) -> CompareOptions:
    opts = CompareOptions()
    for k, v in kwargs.items():
        setattr(opts, k, v)
    return opts


# ---------------------------------------------------------------------------
# --match-attr
# ---------------------------------------------------------------------------

class TestMatchAttr:
    def test_equal_with_match_attr(self):
        """Items in different order are equal when matched by 'id' attribute."""
        f1 = _write("<root><item id='1'>A</item><item id='2'>B</item></root>")
        f2 = _write("<root><item id='2'>B</item><item id='1'>A</item></root>")
        opts = _opts(unordered=True, match_attr="id")
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == [], f"Expected no diffs, got {diffs}"
        os.unlink(f1); os.unlink(f2)

    def test_diff_with_match_attr_value_mismatch(self):
        """Matched items with same id but different text produce a diff."""
        f1 = _write("<root><item id='1'>A</item></root>")
        f2 = _write("<root><item id='1'>CHANGED</item></root>")
        opts = _opts(unordered=True, match_attr="id")
        diffs = compare_xml_files(f1, f2, opts)
        assert len(diffs) >= 1

    def test_missing_id_in_second(self):
        """An item with a unique id in the first document is reported as extra."""
        f1 = _write("<root><item id='1'>A</item><item id='2'>B</item></root>")
        f2 = _write("<root><item id='1'>A</item></root>")
        opts = _opts(unordered=True, match_attr="id")
        diffs = compare_xml_files(f1, f2, opts)
        assert len(diffs) >= 1

    def test_match_attr_without_unordered(self):
        """match_attr without unordered falls back to normal ordered comparison."""
        f1 = _write("<root><item id='1'>A</item></root>")
        f2 = _write("<root><item id='1'>A</item></root>")
        opts = _opts(match_attr="id")
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []


# ---------------------------------------------------------------------------
# --canonicalize
# ---------------------------------------------------------------------------

class TestCanonicalize:
    def test_comments_ignored_when_canonicalize(self):
        """Files differing only in XML comments are equal after canonicalization."""
        f1 = _write("<root><!-- a comment --><val>42</val></root>")
        f2 = _write("<root><val>42</val></root>")
        opts = _opts(canonicalize=True)
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []
        os.unlink(f1); os.unlink(f2)

    def test_comments_matter_without_canonicalize(self):
        """Without canonicalize, identical element trees give no diff regardless."""
        f1 = _write("<root><!-- ignored --><val>42</val></root>")
        f2 = _write("<root><val>42</val></root>")
        opts = _opts(canonicalize=False)
        # ElementTree strips comments during parse, so these are still equal
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []

    def test_pi_stripped_when_canonicalize(self):
        """Processing instructions are stripped when canonicalize is True."""
        f1 = _write("<?xml version='1.0'?><?pi target?><root><v>1</v></root>")
        f2 = _write("<root><v>1</v></root>")
        opts = _opts(canonicalize=True)
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []
        os.unlink(f1); os.unlink(f2)


# ---------------------------------------------------------------------------
# --diff-only
# ---------------------------------------------------------------------------

class TestDiffOnly:
    def test_equal_files_produce_empty_output(self):
        """When diff_only=True, equal files yield an empty output string."""
        f1 = _write("<root><a>1</a></root>")
        f2 = _write("<root><a>1</a></root>")
        opts = _opts(diff_only=True)
        diffs = compare_xml_files(f1, f2, opts)
        all_results = {"files": diffs}
        # Simulate _format_output with files
        output = _format_output(all_results, opts, files=[f1, f2])
        assert output == ""
        os.unlink(f1); os.unlink(f2)

    def test_diff_files_still_output_when_diff_only(self):
        """Files with differences produce output even when diff_only=True."""
        f1 = _write("<root><a>1</a></root>")
        f2 = _write("<root><a>2</a></root>")
        opts = _opts(diff_only=True)
        diffs = compare_xml_files(f1, f2, opts)
        all_results = {"files": diffs}
        output = _format_output(all_results, opts, files=[f1, f2])
        assert output != ""
        os.unlink(f1); os.unlink(f2)


# ---------------------------------------------------------------------------
# --xslt (requires lxml)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_LXML, reason="lxml not installed")
class TestXslt:

    def test_xslt_identity_transform(self):
        """An identity XSLT leaves files unchanged; equal files stay equal."""
        identity_xslt = """\
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>"""
        xslt_file = _write(identity_xslt, suffix=".xslt")
        f1 = _write("<root><val>1</val></root>")
        f2 = _write("<root><val>1</val></root>")
        opts = _opts(xslt=xslt_file)
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []
        os.unlink(xslt_file); os.unlink(f1); os.unlink(f2)

    def test_xslt_transform_normalizes_files(self):
        """An XSLT that normalises element names makes previously-unequal files equal."""
        rename_xslt = """\
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="old"><new><xsl:apply-templates/></new></xsl:template>
  <xsl:template match="@*|node()">
    <xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>
  </xsl:template>
</xsl:stylesheet>"""
        xslt_file = _write(rename_xslt, suffix=".xslt")
        f1 = _write("<root><old>42</old></root>")
        f2 = _write("<root><new>42</new></root>")
        opts = _opts(xslt=xslt_file)
        diffs = compare_xml_files(f1, f2, opts)
        assert diffs == []
        os.unlink(xslt_file); os.unlink(f1); os.unlink(f2)


# ---------------------------------------------------------------------------
# --cache
# ---------------------------------------------------------------------------

class TestCache:
    def test_cache_skips_unchanged_equal_pair(self, tmp_path):
        """A file pair that was equal is skipped (returns []) on the second run."""
        import cache as cache_mod

        f1 = str(tmp_path / "a.xml")
        f2 = str(tmp_path / "b.xml")
        Path(f1).write_text("<root><v>1</v></root>", encoding="utf-8")
        Path(f2).write_text("<root><v>1</v></root>", encoding="utf-8")

        cache_data = {}
        assert not cache_mod.is_cached_equal(f1, f2, cache_data)

        # Record equal result
        cache_mod.update_cache_entry(f1, f2, cache_data, [])
        assert cache_mod.is_cached_equal(f1, f2, cache_data)

    def test_cache_not_hit_after_file_change(self, tmp_path):
        """Changing a file invalidates the cache entry."""
        import cache as cache_mod

        f1 = str(tmp_path / "a.xml")
        f2 = str(tmp_path / "b.xml")
        Path(f1).write_text("<root><v>1</v></root>", encoding="utf-8")
        Path(f2).write_text("<root><v>1</v></root>", encoding="utf-8")

        cache_data = {}
        cache_mod.update_cache_entry(f1, f2, cache_data, [])
        assert cache_mod.is_cached_equal(f1, f2, cache_data)

        # Modify f1
        Path(f1).write_text("<root><v>99</v></root>", encoding="utf-8")
        assert not cache_mod.is_cached_equal(f1, f2, cache_data)

    def test_cache_not_hit_for_differ_pair(self, tmp_path):
        """A pair recorded as differing is not reported as cached-equal."""
        import cache as cache_mod
        from xmlcompare import Difference

        f1 = str(tmp_path / "a.xml")
        f2 = str(tmp_path / "b.xml")
        Path(f1).write_text("<root><v>1</v></root>", encoding="utf-8")
        Path(f2).write_text("<root><v>2</v></root>", encoding="utf-8")

        cache_data = {}
        fake_diffs = [Difference("/root/v", "text", "1 != 2")]
        cache_mod.update_cache_entry(f1, f2, cache_data, fake_diffs)
        assert not cache_mod.is_cached_equal(f1, f2, cache_data)

    def test_cache_save_and_load(self, tmp_path):
        """Cache round-trips through save/load."""
        import cache as cache_mod

        f1 = str(tmp_path / "a.xml")
        f2 = str(tmp_path / "b.xml")
        Path(f1).write_text("<root/>", encoding="utf-8")
        Path(f2).write_text("<root/>", encoding="utf-8")

        cache_file = str(tmp_path / "cache.json")
        cache_data = {}
        cache_mod.update_cache_entry(f1, f2, cache_data, [])
        cache_mod.save_cache(cache_file, cache_data)

        loaded = cache_mod.load_cache(cache_file)
        assert cache_mod.is_cached_equal(f1, f2, loaded)


# ---------------------------------------------------------------------------
# benchmark_streaming / benchmark_parallel smoke tests
# ---------------------------------------------------------------------------

class TestBenchmarkExtensions:
    def test_benchmark_streaming_returns_result(self, tmp_path):
        """benchmark_streaming returns a BenchmarkResult without error."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from benchmark import benchmark_streaming

        f = tmp_path / "test.xml"
        f.write_text("<root><val>1</val></root>", encoding="utf-8")
        result = benchmark_streaming(f, f, label="smoke")
        assert result.label == "smoke"
        assert result.status == "OK"
        assert result.diff_count == 0

    def test_benchmark_parallel_returns_result(self, tmp_path):
        """benchmark_parallel returns a BenchmarkResult without error."""
        from benchmark import benchmark_parallel

        f = tmp_path / "test.xml"
        f.write_text("<root><val>1</val></root>", encoding="utf-8")
        result = benchmark_parallel(f, f, label="psmoke")
        assert result.label == "psmoke"
        assert result.status == "OK"
        assert result.diff_count == 0


# ---------------------------------------------------------------------------
# REST API (requires Flask)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_FLASK, reason="flask not installed")
class TestApiServer:

    @pytest.fixture()
    def client(self):
        """Create a Flask test client from api_server.py."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import api_server
        api_server.app.config["TESTING"] = True
        with api_server.app.test_client() as c:
            yield c

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "xmlcompare-api"

    def test_compare_content_equal(self, client):
        resp = client.post("/compare/content", json={
            "xml1": "<root><a>1</a></root>",
            "xml2": "<root><a>1</a></root>",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["equal"] is True
        assert data["differences"] == []

    def test_compare_content_different(self, client):
        resp = client.post("/compare/content", json={
            "xml1": "<root><a>1</a></root>",
            "xml2": "<root><a>2</a></root>",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["equal"] is False
        assert len(data["differences"]) >= 1

    def test_compare_content_missing_field(self, client):
        resp = client.post("/compare/content", json={"xml1": "<root/>"})
        assert resp.status_code == 400

    def test_compare_content_with_options(self, client):
        resp = client.post("/compare/content", json={
            "xml1": "<root><a>HELLO</a></root>",
            "xml2": "<root><a>hello</a></root>",
            "options": {"ignore_case": True},
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["equal"] is True
