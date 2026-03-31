package com.xmlcompare;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class XmlCompareTest {

    private static final String SIMPLE_XML_1 = "<root><child>hello</child></root>";
    private static final String SIMPLE_XML_2 = "<root><child>hello</child></root>";
    private static final String SIMPLE_XML_DIFF = "<root><child>world</child></root>";

    private List<Difference> compareStrings(String xml1, String xml2, CompareOptions opts) throws Exception {
        var doc1 = XmlCompare.parseXmlString(xml1);
        var doc2 = XmlCompare.parseXmlString(xml2);
        return XmlCompare.compareElements(doc1.getDocumentElement(), doc2.getDocumentElement(), opts, "", null);
    }

    // --- normalizeText ---

    @Test
    void testNormalizeTextNull() {
        assertEquals("", XmlCompare.normalizeText(null));
    }

    @Test
    void testNormalizeTextWhitespace() {
        assertEquals("hello world", XmlCompare.normalizeText("  hello   world  "));
    }

    @Test
    void testNormalizeTextEmpty() {
        assertEquals("", XmlCompare.normalizeText(""));
    }

    // --- toNumeric ---

    @Test
    void testToNumericInteger() {
        assertTrue(XmlCompare.toNumeric("42").isPresent());
        assertEquals(42.0, XmlCompare.toNumeric("42").get());
    }

    @Test
    void testToNumericFloat() {
        assertTrue(XmlCompare.toNumeric("3.14").isPresent());
        assertEquals(3.14, XmlCompare.toNumeric("3.14").get(), 0.001);
    }

    @Test
    void testToNumericNonNumeric() {
        assertFalse(XmlCompare.toNumeric("hello").isPresent());
    }

    @Test
    void testToNumericEmpty() {
        assertFalse(XmlCompare.toNumeric("").isPresent());
    }

    // --- valuesEqual ---

    @Test
    void testValuesEqualNumericTolerance() {
        CompareOptions opts = new CompareOptions();
        opts.tolerance = 0.01;
        assertTrue(XmlCompare.valuesEqual("1.0", "1.005", opts));
        assertFalse(XmlCompare.valuesEqual("1.0", "1.02", opts));
    }

    @Test
    void testValuesEqualIntegerVsFloat() {
        CompareOptions opts = new CompareOptions();
        assertTrue(XmlCompare.valuesEqual("1", "1.0", opts));
        assertTrue(XmlCompare.valuesEqual("42", "42.00", opts));
    }

    @Test
    void testValuesEqualIgnoreCase() {
        CompareOptions opts = new CompareOptions();
        opts.ignoreCase = true;
        assertTrue(XmlCompare.valuesEqual("Hello", "hello", opts));
        assertTrue(XmlCompare.valuesEqual("WORLD", "world", opts));
    }

    @Test
    void testValuesEqualCaseSensitive() {
        CompareOptions opts = new CompareOptions();
        assertFalse(XmlCompare.valuesEqual("Hello", "hello", opts));
    }

    // --- stripNamespace ---

    @Test
    void testStripNamespace() {
        assertEquals("tag", XmlCompare.stripNamespace("{http://example.com}tag"));
    }

    @Test
    void testStripNamespaceNoNamespace() {
        assertEquals("tag", XmlCompare.stripNamespace("tag"));
    }

    // --- buildPath ---

    @Test
    void testBuildPath() {
        assertEquals("root/child", XmlCompare.buildPath("root", "child"));
    }

    @Test
    void testBuildPathEmptyParent() {
        assertEquals("child", XmlCompare.buildPath("", "child"));
    }

    // --- shouldSkip ---

    @Test
    void testShouldSkipDoubleSlash() {
        CompareOptions opts = new CompareOptions();
        opts.skipKeys.add("//secret");
        assertTrue(XmlCompare.shouldSkip("root/secret", "secret", opts));
        assertFalse(XmlCompare.shouldSkip("root/other", "other", opts));
    }

    @Test
    void testShouldSkipExactPath() {
        CompareOptions opts = new CompareOptions();
        opts.skipKeys.add("root/password");
        assertTrue(XmlCompare.shouldSkip("root/password", "password", opts));
        assertFalse(XmlCompare.shouldSkip("root/other", "other", opts));
    }

    @Test
    void testShouldSkipPattern() {
        CompareOptions opts = new CompareOptions();
        opts.skipPattern = "temp.*";
        assertTrue(XmlCompare.shouldSkip("root/tempField", "tempField", opts));
        assertFalse(XmlCompare.shouldSkip("root/field", "field", opts));
    }

    // --- compareElements ---

    @Test
    void testEqualXml() throws Exception {
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = compareStrings(SIMPLE_XML_1, SIMPLE_XML_2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testTextDifference() throws Exception {
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = compareStrings(SIMPLE_XML_1, SIMPLE_XML_DIFF, opts);
        assertFalse(diffs.isEmpty());
        assertEquals("text", diffs.get(0).kind);
    }

    @Test
    void testTagMismatch() throws Exception {
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = compareStrings("<root><a/></root>", "<root><b/></root>", opts);
        boolean hasMismatch = diffs.stream().anyMatch(d -> d.kind.equals("tag") || d.kind.equals("extra") || d.kind.equals("missing"));
        assertTrue(hasMismatch);
    }

    @Test
    void testAttributeEqual() throws Exception {
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = compareStrings(
            "<root id=\"1\"/>",
            "<root id=\"1\"/>",
            opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testAttributeDiffer() throws Exception {
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = compareStrings(
            "<root id=\"1\"/>",
            "<root id=\"2\"/>",
            opts);
        assertFalse(diffs.isEmpty());
        assertEquals("attr", diffs.get(0).kind);
    }

    @Test
    void testAttributeMissingInFirst() throws Exception {
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = compareStrings(
            "<root/>",
            "<root id=\"1\"/>",
            opts);
        assertFalse(diffs.isEmpty());
        assertEquals("attr", diffs.get(0).kind);
        assertNull(diffs.get(0).expected);
        assertEquals("1", diffs.get(0).actual);
    }

    @Test
    void testAttributeMissingInSecond() throws Exception {
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = compareStrings(
            "<root id=\"1\"/>",
            "<root/>",
            opts);
        assertFalse(diffs.isEmpty());
        assertEquals("attr", diffs.get(0).kind);
        assertEquals("1", diffs.get(0).expected);
        assertNull(diffs.get(0).actual);
    }

    @Test
    void testIgnoreAttributes() throws Exception {
        CompareOptions opts = new CompareOptions();
        opts.ignoreAttributes = true;
        List<Difference> diffs = compareStrings(
            "<root id=\"1\"/>",
            "<root id=\"2\"/>",
            opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testNamespaceAware() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root xmlns=\"http://example.com\"><child>text</child></root>";
        String xml2 = "<root xmlns=\"http://example.com\"><child>text</child></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testNamespaceMismatch() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<ns1:root xmlns:ns1=\"http://example.com/a\"><ns1:child>text</ns1:child></ns1:root>";
        String xml2 = "<ns2:root xmlns:ns2=\"http://example.com/b\"><ns2:child>text</ns2:child></ns2:root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertFalse(diffs.isEmpty());
    }

    @Test
    void testIgnoreNamespaces() throws Exception {
        CompareOptions opts = new CompareOptions();
        opts.ignoreNamespaces = true;
        String xml1 = "<ns1:root xmlns:ns1=\"http://example.com/a\"><ns1:child>text</ns1:child></ns1:root>";
        String xml2 = "<ns2:root xmlns:ns2=\"http://example.com/b\"><ns2:child>text</ns2:child></ns2:root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testOrderedChildren() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root><a/><b/></root>";
        String xml2 = "<root><b/><a/></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertFalse(diffs.isEmpty());
    }

    @Test
    void testUnorderedChildren() throws Exception {
        CompareOptions opts = new CompareOptions();
        opts.unordered = true;
        String xml1 = "<root><a>1</a><b>2</b></root>";
        String xml2 = "<root><b>2</b><a>1</a></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testSkipKeyDoubleSlash() throws Exception {
        CompareOptions opts = new CompareOptions();
        opts.skipKeys.add("//secret");
        String xml1 = "<root><secret>abc</secret><value>1</value></root>";
        String xml2 = "<root><secret>xyz</secret><value>1</value></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testSkipKeyExactPath() throws Exception {
        CompareOptions opts = new CompareOptions();
        opts.skipKeys.add("root/secret");
        String xml1 = "<root><secret>abc</secret><value>1</value></root>";
        String xml2 = "<root><secret>xyz</secret><value>1</value></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testSkipPattern() throws Exception {
        CompareOptions opts = new CompareOptions();
        opts.skipPattern = "temp.*";
        String xml1 = "<root><tempField>abc</tempField><value>1</value></root>";
        String xml2 = "<root><tempField>xyz</tempField><value>1</value></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testFailFast() throws Exception {
        CompareOptions opts = new CompareOptions();
        opts.failFast = true;
        String xml1 = "<root><a>1</a><b>2</b><c>3</c></root>";
        String xml2 = "<root><a>X</a><b>Y</b><c>Z</c></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertEquals(1, diffs.size());
    }

    @Test
    void testMissingElementInFirst() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root><a/></root>";
        String xml2 = "<root><a/><b/></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertFalse(diffs.isEmpty());
        assertTrue(diffs.stream().anyMatch(d -> d.kind.equals("missing")));
    }

    @Test
    void testExtraElementInFirst() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root><a/><b/></root>";
        String xml2 = "<root><a/></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertFalse(diffs.isEmpty());
        assertTrue(diffs.stream().anyMatch(d -> d.kind.equals("extra")));
    }

    // --- compareXmlFiles ---

    @Test
    void testCompareXmlFilesEqual(@TempDir Path tempDir) throws Exception {
        Path f1 = tempDir.resolve("a.xml");
        Path f2 = tempDir.resolve("b.xml");
        Files.writeString(f1, "<root><child>hello</child></root>");
        Files.writeString(f2, "<root><child>hello</child></root>");
        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = XmlCompare.compareXmlFiles(f1.toString(), f2.toString(), opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testCompareXmlFilesFileNotFound() {
        CompareOptions opts = new CompareOptions();
        assertThrows(IOException.class, () ->
            XmlCompare.compareXmlFiles("/nonexistent/a.xml", "/nonexistent/b.xml", opts));
    }

    @Test
    void testCompareXmlFilesInvalidXml(@TempDir Path tempDir) throws Exception {
        Path f1 = tempDir.resolve("bad.xml");
        Path f2 = tempDir.resolve("good.xml");
        Files.writeString(f1, "<root><unclosed>");
        Files.writeString(f2, "<root/>");
        CompareOptions opts = new CompareOptions();
        assertThrows(IOException.class, () ->
            XmlCompare.compareXmlFiles(f1.toString(), f2.toString(), opts));
    }

    // --- compareDirs ---

    @Test
    void testCompareDirsEqual(@TempDir Path tempDir) throws Exception {
        Path d1 = tempDir.resolve("d1");
        Path d2 = tempDir.resolve("d2");
        Files.createDirectories(d1);
        Files.createDirectories(d2);
        Files.writeString(d1.resolve("test.xml"), "<root><child>hello</child></root>");
        Files.writeString(d2.resolve("test.xml"), "<root><child>hello</child></root>");
        CompareOptions opts = new CompareOptions();
        Map<String, Object> results = XmlCompare.compareDirs(d1.toString(), d2.toString(), opts, false);
        assertFalse(results.isEmpty());
        results.values().forEach(v -> {
            assertTrue(v instanceof List);
            assertTrue(((List<?>) v).isEmpty());
        });
    }

    @Test
    void testCompareDirsMissingFile(@TempDir Path tempDir) throws Exception {
        Path d1 = tempDir.resolve("d1");
        Path d2 = tempDir.resolve("d2");
        Files.createDirectories(d1);
        Files.createDirectories(d2);
        Files.writeString(d1.resolve("test.xml"), "<root/>");
        CompareOptions opts = new CompareOptions();
        Map<String, Object> results = XmlCompare.compareDirs(d1.toString(), d2.toString(), opts, false);
        assertEquals(1, results.size());
        Object val = results.values().iterator().next();
        assertTrue(val instanceof List);
        List<?> diffs = (List<?>) val;
        assertFalse(diffs.isEmpty());
        assertEquals("missing", ((Difference) diffs.get(0)).kind);
    }

    @Test
    void testCompareDirsRecursive(@TempDir Path tempDir) throws Exception {
        Path d1 = tempDir.resolve("d1");
        Path d2 = tempDir.resolve("d2");
        Path sub1 = d1.resolve("sub");
        Path sub2 = d2.resolve("sub");
        Files.createDirectories(sub1);
        Files.createDirectories(sub2);
        Files.writeString(sub1.resolve("deep.xml"), "<root><v>1</v></root>");
        Files.writeString(sub2.resolve("deep.xml"), "<root><v>1</v></root>");
        CompareOptions opts = new CompareOptions();
        Map<String, Object> results = XmlCompare.compareDirs(d1.toString(), d2.toString(), opts, true);
        assertFalse(results.isEmpty());
        results.values().forEach(v -> {
            assertTrue(v instanceof List);
            assertTrue(((List<?>) v).isEmpty());
        });
    }

    // --- formatTextReport ---

    @Test
    void testFormatTextReportEqual() {
        String report = XmlCompare.formatTextReport(List.of(), "file1.xml", "file2.xml");
        assertTrue(report.contains("Files are equal"));
    }

    @Test
    void testFormatTextReportWithDiffs() {
        List<Difference> diffs = List.of(
            new Difference("root/child", "text", "Text mismatch at 'root/child': 'hello' != 'world'", "hello", "world")
        );
        String report = XmlCompare.formatTextReport(diffs, "file1.xml", "file2.xml");
        assertTrue(report.contains("[TEXT]"));
        assertTrue(report.contains("hello"));
        assertTrue(report.contains("world"));
    }

    // --- formatJsonReport ---

    @Test
    void testFormatJsonReport() throws Exception {
        Map<String, Object> results = new java.util.LinkedHashMap<>();
        results.put("test.xml", List.of());
        String json = XmlCompare.formatJsonReport(results);
        assertTrue(json.contains("\"equal\""));
        assertTrue(json.contains("true"));
    }

    @Test
    void testFormatJsonReportWithError() {
        Map<String, Object> results = new java.util.LinkedHashMap<>();
        results.put("bad.xml", "Parse error");
        String json = XmlCompare.formatJsonReport(results);
        assertTrue(json.contains("\"error\""));
        assertTrue(json.contains("Parse error"));
    }

    // --- formatHtmlReport ---

    @Test
    void testFormatHtmlReportEqual() {
        Map<String, Object> results = new java.util.LinkedHashMap<>();
        results.put("test.xml", List.of());
        String html = XmlCompare.formatHtmlReport(results);
        assertTrue(html.contains("class=\"equal\""));
        assertTrue(html.contains("EQUAL"));
    }

    @Test
    void testFormatHtmlReportWithDiffs() {
        Map<String, Object> results = new java.util.LinkedHashMap<>();
        results.put("test.xml", List.of(
            new Difference("root", "text", "Text mismatch", "a", "b")
        ));
        String html = XmlCompare.formatHtmlReport(results);
        assertTrue(html.contains("class=\"diff\""));
        assertTrue(html.contains("[TEXT]"));
    }

    @Test
    void testFormatHtmlReportWithError() {
        Map<String, Object> results = new java.util.LinkedHashMap<>();
        results.put("bad.xml", "Parse error occurred");
        String html = XmlCompare.formatHtmlReport(results);
        assertTrue(html.contains("class=\"error\""));
        assertTrue(html.contains("Parse error occurred"));
    }

    // --- Config loading ---

    @Test
    void testLoadConfigJson(@TempDir Path tempDir) throws Exception {
        Path configFile = tempDir.resolve("config.json");
        Files.writeString(configFile, "{\"tolerance\": 0.5, \"ignore_case\": true, \"unordered\": true}");
        CompareOptions opts = new CompareOptions();
        opts.tolerance = 0.5;
        opts.ignoreCase = true;
        assertTrue(XmlCompare.valuesEqual("1.0", "1.4", opts));
        assertTrue(XmlCompare.valuesEqual("Hello", "hello", opts));
    }

    @Test
    void testWhitespaceNormalization() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root><child>  hello   world  </child></root>";
        String xml2 = "<root><child>hello world</child></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testNumericTrailingZeros() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root><value>1.0</value></root>";
        String xml2 = "<root><value>1.00</value></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testNestedElements() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root><a><b><c>deep</c></b></a></root>";
        String xml2 = "<root><a><b><c>deep</c></b></a></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void testNestedElementsDifferent() throws Exception {
        CompareOptions opts = new CompareOptions();
        String xml1 = "<root><a><b><c>deep1</c></b></a></root>";
        String xml2 = "<root><a><b><c>deep2</c></b></a></root>";
        List<Difference> diffs = compareStrings(xml1, xml2, opts);
        assertFalse(diffs.isEmpty());
        assertEquals("root/a/b/c", diffs.get(0).path);
    }
}
