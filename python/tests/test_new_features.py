"""Tests for new features: structure_only and max_depth."""

import sys
import pytest
from pathlib import Path

# Ensure the package root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))
import xmlcompare as xc


def _opts(**kwargs):
    opts = xc.CompareOptions()
    for k, v in kwargs.items():
        setattr(opts, k, v)
    return opts


def write(path, content):
    Path(path).write_text(content)
    return str(path)


# ---------------------------------------------------------------------------
# Structure-only comparison
# ---------------------------------------------------------------------------

class TestStructureOnly:
    """Test structure_only option - comparing only XML structure, not values."""

    def test_structure_only_ignores_text_differences(self, tmp_path):
        """Same structure but different text values should be equal in structure_only mode."""
        f1 = write(tmp_path / 'a.xml', '<r><a>hello</a><b>world</b></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a>foo</a><b>bar</b></r>')
        assert xc.compare_xml_files(f1, f2, _opts(structure_only=True)) == []

    def test_structure_only_ignores_attribute_differences(self, tmp_path):
        """Same structure but different attribute values should be equal in structure_only mode."""
        f1 = write(tmp_path / 'a.xml', '<r><a id="1">text</a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a id="2">text</a></r>')
        assert xc.compare_xml_files(f1, f2, _opts(structure_only=True)) == []

    def test_structure_only_detects_missing_element(self, tmp_path):
        """Missing elements should still be detected in structure_only mode."""
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(structure_only=True))
        assert len(diffs) > 0
        assert any(d.kind == 'extra' for d in diffs)

    def test_structure_only_detects_extra_element(self, tmp_path):
        """Extra elements should still be detected in structure_only mode."""
        f1 = write(tmp_path / 'a.xml', '<r><a/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/><b/></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(structure_only=True))
        assert len(diffs) > 0
        assert any(d.kind == 'missing' for d in diffs)

    def test_structure_only_detects_tag_mismatch(self, tmp_path):
        """Different tag names should still be detected in structure_only mode."""
        f1 = write(tmp_path / 'a.xml', '<r><a/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><b/></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(structure_only=True))
        assert len(diffs) > 0
        assert any(d.kind == 'tag' for d in diffs)

    def test_structure_only_with_unordered(self, tmp_path):
        """structure_only should work with unordered option."""
        f1 = write(tmp_path / 'a.xml', '<r><a>x</a><b>y</b></r>')
        f2 = write(tmp_path / 'b.xml', '<r><b>z</b><a>w</a></r>')
        assert xc.compare_xml_files(f1, f2, _opts(structure_only=True, unordered=True)) == []

    def test_structure_only_nested_elements(self, tmp_path):
        """structure_only should ignore text values in nested structures."""
        f1 = write(tmp_path / 'a.xml', '<r><a><b>hello</b></a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a><b>world</b></a></r>')
        assert xc.compare_xml_files(f1, f2, _opts(structure_only=True)) == []

    def test_structure_only_with_multiple_attributes_ignored(self, tmp_path):
        """Multiple attributes should all be ignored in structure_only mode."""
        f1 = write(tmp_path / 'a.xml', '<r><a id="1" class="x" data="foo">val</a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a id="2" class="y" data="bar">different</a></r>')
        assert xc.compare_xml_files(f1, f2, _opts(structure_only=True)) == []


# ---------------------------------------------------------------------------
# Max-depth comparison
# ---------------------------------------------------------------------------

class TestMaxDepth:
    """Test max_depth option - limiting comparison to specified depth."""

    def test_max_depth_zero_root_only(self, tmp_path):
        """max_depth=0 should only compare root element."""
        f1 = write(tmp_path / 'a.xml', '<r><child>val1</child></r>')
        f2 = write(tmp_path / 'b.xml', '<r><child>val2</child></r>')
        assert xc.compare_xml_files(f1, f2, _opts(max_depth=0)) == []

    def test_max_depth_one_ignores_grandchildren(self, tmp_path):
        """max_depth=1 should compare root and direct children but not grandchildren."""
        f1 = write(tmp_path / 'a.xml', '<r><a><b>x</b></a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a><b>y</b></a></r>')
        # max_depth=1: root (depth 0) and direct children (depth 1) are compared
        # depth 2 (<b>) is not compared
        assert xc.compare_xml_files(f1, f2, _opts(max_depth=1)) == []

    def test_max_depth_detects_missing_at_max_level(self, tmp_path):
        """max_depth should still detect missing/extra elements at the limit level."""
        f1 = write(tmp_path / 'a.xml', '<r><a/><b/></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a/></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(max_depth=1))
        assert len(diffs) > 0

    def test_max_depth_respects_values_at_max_level(self, tmp_path):
        """max_depth should still compare values at the limit level."""
        f1 = write(tmp_path / 'a.xml', '<r><a>x</a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a>y</a></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(max_depth=1))
        assert len(diffs) > 0
        assert any(d.kind == 'text' for d in diffs)

    def test_max_depth_three_levels(self, tmp_path):
        """max_depth=2 should compare up to depth 2."""
        f1 = write(tmp_path / 'a.xml', '<r><a><b><c>x</c></b></a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a><b><c>y</c></b></a></r>')
        # depth 0: r, depth 1: a, depth 2: b, depth 3: c
        # max_depth=2 should not compare c's content
        assert xc.compare_xml_files(f1, f2, _opts(max_depth=2)) == []

    def test_max_depth_with_unordered(self, tmp_path):
        """max_depth should work with unordered option."""
        f1 = write(tmp_path / 'a.xml', '<r><a><x>1</x></a><b><y>2</y></b></r>')
        f2 = write(tmp_path / 'b.xml', '<r><b><y>z</y></b><a><x>w</x></a></r>')
        # With unordered and max_depth=1, children order doesn't matter,
        # and grandchildren values are not compared
        assert xc.compare_xml_files(f1, f2, _opts(max_depth=1, unordered=True)) == []

    def test_max_depth_with_multiple_children(self, tmp_path):
        """max_depth should apply to all children uniformly."""
        f1 = write(tmp_path / 'a.xml', '<r><a><x>A</x></a><b><y>B</y></b><c><z>C</z></c></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a><x>1</x></a><b><y>2</y></b><c><z>3</z></c></r>')
        # max_depth=1: compare children a, b, c but not their children
        assert xc.compare_xml_files(f1, f2, _opts(max_depth=1)) == []

    def test_max_depth_none_means_unlimited(self, tmp_path):
        """max_depth=None should compare all depths (default behavior)."""
        f1 = write(tmp_path / 'a.xml', '<r><a><b><c>x</c></b></a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a><b><c>y</c></b></a></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(max_depth=None))
        assert len(diffs) > 0  # Should detect the difference


# ---------------------------------------------------------------------------
# Combining structure_only with max_depth
# ---------------------------------------------------------------------------

class TestStructureOnlyWithMaxDepth:
    """Test combining structure_only and max_depth options."""

    def test_structure_only_and_max_depth_together(self, tmp_path):
        """structure_only and max_depth should work together."""
        f1 = write(tmp_path / 'a.xml', '<r><a id="1"><b id="2">x</b></a></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a id="9"><b id="8">y</b></a></r>')
        # max_depth=1: only root and direct children
        # structure_only: ignore text/attribute values
        assert xc.compare_xml_files(f1, f2, _opts(max_depth=1, structure_only=True)) == []

    def test_structure_only_max_depth_detects_missing_element(self, tmp_path):
        """Should still detect missing elements when combining options."""
        f1 = write(tmp_path / 'a.xml', '<r><a>x</a><b>y</b></r>')
        f2 = write(tmp_path / 'b.xml', '<r><a>a</a></r>')
        diffs = xc.compare_xml_files(f1, f2, _opts(max_depth=1, structure_only=True))
        assert len(diffs) > 0


# ---------------------------------------------------------------------------
# Unordered with many different elements
# ---------------------------------------------------------------------------

class TestUnorderedWithManyElements:
    """Test unordered comparison with various element types and quantities."""

    def test_unordered_many_different_elements(self, tmp_path):
        """unordered should handle many different element types."""
        xml1 = '''<root>
            <user id="1"><name>Alice</name></user>
            <item priority="high"><title>Task 1</title></item>
            <event type="start"><timestamp>2024-01-01</timestamp></event>
            <config key="debug"><value>true</value></config>
            <log level="info"><message>Started</message></log>
        </root>'''
        xml2 = '''<root>
            <log level="debug"><message>Process running</message></log>
            <config key="timeout"><value>5000</value></config>
            <event type="end"><timestamp>2024-12-31</timestamp></event>
            <item priority="low"><title>Task 2</title></item>
            <user id="2"><name>Bob</name></user>
        </root>'''
        f1 = write(tmp_path / 'a.xml', xml1)
        f2 = write(tmp_path / 'b.xml', xml2)
        diffs = xc.compare_xml_files(f1, f2, _opts(unordered=True))
        assert len(diffs) > 0  # Different values, but same structure

    def test_unordered_many_same_elements(self, tmp_path):
        """unordered should handle many instances of the same element type."""
        xml1 = '''<items>
            <item>1</item>
            <item>2</item>
            <item>3</item>
            <item>4</item>
            <item>5</item>
        </items>'''
        xml2 = '''<items>
            <item>5</item>
            <item>3</item>
            <item>1</item>
            <item>2</item>
            <item>4</item>
        </items>'''
        f1 = write(tmp_path / 'a.xml', xml1)
        f2 = write(tmp_path / 'b.xml', xml2)
        diffs = xc.compare_xml_files(f1, f2, _opts(unordered=True))
        # Values differ, so should find differences
        assert len(diffs) > 0

    def test_unordered_same_elements_different_order(self, tmp_path):
        """unordered should handle elements with different tag names in different order."""
        xml1 = '''<items>
            <alpha>a</alpha>
            <beta>b</beta>
            <gamma>c</gamma>
        </items>'''
        xml2 = '''<items>
            <gamma>c</gamma>
            <alpha>a</alpha>
            <beta>b</beta>
        </items>'''
        f1 = write(tmp_path / 'a.xml', xml1)
        f2 = write(tmp_path / 'b.xml', xml2)
        # Different tag names in different order should be equal with unordered
        assert xc.compare_xml_files(f1, f2, _opts(unordered=True)) == []

    def test_unordered_mixed_counts(self, tmp_path):
        """unordered should detect when counts of element types differ."""
        xml1 = '<root><a>1</a><a>2</a><b>x</b></root>'
        xml2 = '<root><a>1</a><b>x</b><b>y</b></root>'
        f1 = write(tmp_path / 'a.xml', xml1)
        f2 = write(tmp_path / 'b.xml', xml2)
        diffs = xc.compare_xml_files(f1, f2, _opts(unordered=True))
        assert len(diffs) > 0  # Different element counts

    def test_unordered_nested_with_many_types(self, tmp_path):
        """unordered should work with nested elements of many types."""
        xml1 = '''<root>
            <group>
                <user>Alice</user>
                <role>admin</role>
                <perm>read</perm>
            </group>
        </root>'''
        xml2 = '''<root>
            <group>
                <perm>write</perm>
                <user>Bob</user>
                <role>user</role>
            </group>
        </root>'''
        f1 = write(tmp_path / 'a.xml', xml1)
        f2 = write(tmp_path / 'b.xml', xml2)
        diffs = xc.compare_xml_files(f1, f2, _opts(unordered=True))
        assert len(diffs) > 0  # Different values
