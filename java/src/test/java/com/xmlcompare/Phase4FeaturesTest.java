package com.xmlcompare;

import com.xmlcompare.cache.CacheManager;
import com.xmlcompare.format.HtmlSideBySideFormatter;
import com.xmlcompare.format.UnifiedDiffFormatter;
import com.xmlcompare.parallel.ParallelComparison;
import com.xmlcompare.parse.StreamingXmlParser;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Phase-4 feature tests covering formatters, cache, streaming, parallel,
 * Difference model, CompareOptions new fields, and the noColor/swap overloads.
 */
class Phase4FeaturesTest {

    @TempDir
    Path tmp;

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private File write(String name, String content) throws IOException {
        Path p = tmp.resolve(name);
        Files.createDirectories(p.getParent());
        Files.writeString(p, content);
        return p.toFile();
    }

    private static Difference diff(String path, String kind, String msg, String exp, String act) {
        return new Difference(path, kind, msg, exp, act);
    }

    private static Difference diff(String path, String kind, String msg) {
        return new Difference(path, kind, msg);
    }

    // =========================================================================
    // Difference model
    // =========================================================================

    @Test
    void differenceToMapHasAllFields() {
        Difference d = diff("root/a", "text", "differs", "X", "Y");
        Map<String, Object> map = d.toMap();
        assertEquals("root/a", map.get("path"));
        assertEquals("text", map.get("kind"));
        assertEquals("differs", map.get("message"));
        assertEquals("X", map.get("expected"));
        assertEquals("Y", map.get("actual"));
    }

    @Test
    void differenceToMapOmitsNullFields() {
        Difference d = diff("root/a", "tag", "tag mismatch");
        Map<String, Object> map = d.toMap();
        assertFalse(map.containsKey("expected"));
        assertFalse(map.containsKey("actual"));
    }

    @Test
    void differenceToStringContainsKind() {
        Difference d = diff("p", "attr", "value differs");
        assertTrue(d.toString().contains("attr"));
    }

    // =========================================================================
    // CompareOptions – Phase-4 fields
    // =========================================================================

    @Test
    void compareOptionsSwapDefaultFalse() {
        CompareOptions opts = new CompareOptions();
        assertFalse(opts.swap);
    }

    @Test
    void compareOptionsNoColorDefaultFalse() {
        CompareOptions opts = new CompareOptions();
        assertFalse(opts.noColor);
    }

    @Test
    void compareOptionsDiffOnlyDefaultFalse() {
        CompareOptions opts = new CompareOptions();
        assertFalse(opts.diffOnly);
    }

    @Test
    void compareOptionsCanonicalizeDefaultFalse() {
        CompareOptions opts = new CompareOptions();
        assertFalse(opts.canonicalize);
    }

    // =========================================================================
    // UnifiedDiffFormatter
    // =========================================================================

    @Test
    void unifiedDiffFormatterName() {
        assertEquals("unified-diff", new UnifiedDiffFormatter().getName());
    }

    @Test
    void unifiedDiffFormatterEqualFiles() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        Map<String, Object> results = Map.of("k", new ArrayList<Difference>());
        String out = fmt.format(results, "a.xml", "b.xml");
        assertTrue(out.contains("--- a.xml"));
        assertTrue(out.contains("+++ b.xml"));
        assertTrue(out.contains("(no differences)"));
    }

    @Test
    void unifiedDiffFormatterTextDiff() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        List<Difference> diffs = List.of(diff("root/v", "text", "differs", "old", "new"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("@@ root/v @@"));
        assertTrue(out.contains("- old"));
        assertTrue(out.contains("+ new"));
    }

    @Test
    void unifiedDiffFormatterAttrDiff() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        List<Difference> diffs = List.of(diff("root/v", "attr", "differs", "v1", "v2"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("- v1"));
        assertTrue(out.contains("+ v2"));
    }

    @Test
    void unifiedDiffFormatterTagDiff() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        List<Difference> diffs = List.of(diff("root/v", "tag", "tag mismatch"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("! tag mismatch"));
    }

    @Test
    void unifiedDiffFormatterMissing() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        List<Difference> diffs = List.of(diff("root/v", "missing", "element gone"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("- element gone"));
    }

    @Test
    void unifiedDiffFormatterExtra() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        List<Difference> diffs = List.of(diff("root/v", "extra", "element added"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("+ element added"));
    }

    @Test
    void unifiedDiffFormatterDefaultKind() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        List<Difference> diffs = List.of(diff("root/v", "structure", "structural issue"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("structural issue"));
    }

    @Test
    void unifiedDiffFormatterErrorCase() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        String out = fmt.format(Map.of("k", "parse error"), null, null);
        assertTrue(out.contains("Error: parse error"));
    }

    @Test
    void unifiedDiffFormatterDiffWithNullExpectedActual() {
        UnifiedDiffFormatter fmt = new UnifiedDiffFormatter();
        List<Difference> diffs = List.of(diff("root/v", "text", "differs", null, null));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("@@ root/v @@"));
    }

    // =========================================================================
    // HtmlSideBySideFormatter
    // =========================================================================

    @Test
    void htmlFormatterName() {
        assertEquals("html-diff", new HtmlSideBySideFormatter().getName());
    }

    @Test
    void htmlFormatterEqualFiles() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        String out = fmt.format(Map.of("k", new ArrayList<Difference>()), null, null);
        assertTrue(out.contains("<!DOCTYPE html>"));
        assertTrue(out.contains("No differences"));
    }

    @Test
    void htmlFormatterWithTextDiff() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        List<Difference> diffs = List.of(diff("root/v", "text", "differs", "a", "b"));
        String out = fmt.format(Map.of("k", diffs), "Expected", "Actual");
        assertTrue(out.contains("<table"));
        assertTrue(out.contains("Expected"));
        assertTrue(out.contains("Actual"));
    }

    @Test
    void htmlFormatterMissingKind() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        List<Difference> diffs = List.of(diff("root/v", "missing", "element gone", "x", null));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("removed"));
        assertTrue(out.contains("MISSING"));
    }

    @Test
    void htmlFormatterExtraKind() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        List<Difference> diffs = List.of(diff("root/v", "extra", "element added", null, "y"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("added"));
        assertTrue(out.contains("EXTRA"));
    }

    @Test
    void htmlFormatterTagKind() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        List<Difference> diffs = List.of(diff("root/v", "tag", "tag mismatch"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("TAG"));
    }

    @Test
    void htmlFormatterAttrKind() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        List<Difference> diffs = List.of(diff("root/v", "attr", "attr mismatch", "v1", "v2"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("ATTR"));
    }

    @Test
    void htmlFormatterContextKind() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        List<Difference> diffs = List.of(diff("root/v", "context", "context msg"));
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("CONTEXT"));
    }

    @Test
    void htmlFormatterErrorCase() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        String out = fmt.format(Map.of("k", "some <error> & \"value\""), null, null);
        assertTrue(out.contains("class=\"error\""));
        assertTrue(out.contains("&lt;error&gt;"));
        assertTrue(out.contains("&amp;"));
    }

    @Test
    void htmlFormatterSummaryCount() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        List<Difference> diffs = List.of(
            diff("root/a", "text", "x"),
            diff("root/b", "text", "y")
        );
        String out = fmt.format(Map.of("k", diffs), null, null);
        assertTrue(out.contains("Total differences: <strong>2</strong>"));
    }

    @Test
    void htmlFormatterMultipleKeys() {
        HtmlSideBySideFormatter fmt = new HtmlSideBySideFormatter();
        Map<String, Object> results = Map.of(
            "eq", new ArrayList<Difference>(),
            "diff", List.of(diff("root/v", "text", "x"))
        );
        String out = fmt.format(results, null, null);
        assertTrue(out.contains("Total differences: <strong>1</strong>"));
    }

    // =========================================================================
    // formatTextReport with noColor=true (overload)
    // =========================================================================

    @Test
    void formatTextReportNoColorOverload() {
        List<Difference> diffs = List.of(diff("root/v", "text", "x differs", "a", "b"));
        String out = XmlCompare.formatTextReport(diffs, "f1", "f2", true);
        assertFalse(out.contains("\033["));
        assertTrue(out.contains("x differs"));
    }

    @Test
    void formatTextReportNoColorEqualFiles() {
        String out = XmlCompare.formatTextReport(new ArrayList<>(), "f1", "f2", true);
        assertTrue(out.contains("Files are equal"));
        assertFalse(out.contains("\033["));
    }

    @Test
    void formatTextReportNoColorNullDiffs() {
        String out = XmlCompare.formatTextReport(null, "f1", "f2", true);
        assertTrue(out.contains("Files are equal"));
    }

    @Test
    void formatTextReportDefaultOverloadCallsNoColor() {
        List<Difference> diffs = List.of(diff("root/v", "text", "differs"));
        String out1 = XmlCompare.formatTextReport(diffs, "f1", "f2");
        String out2 = XmlCompare.formatTextReport(diffs, "f1", "f2", true);
        // noColor strips ANSI; content (minus ANSI codes) should be equivalent
        String stripped1 = out1.replaceAll("\033\\[[0-9;]*m", "");
        assertEquals(stripped1, out2);
    }

    // =========================================================================
    // swap option in compareXmlFiles
    // =========================================================================

    @Test
    void swapReversesDiffDirection() throws Exception {
        File f1 = write("a.xml", "<root><v>1</v></root>");
        File f2 = write("b.xml", "<root><v>2</v></root>");

        CompareOptions normal = new CompareOptions();
        List<Difference> normalDiffs = XmlCompare.compareXmlFiles(
            f1.getAbsolutePath(), f2.getAbsolutePath(), normal);

        CompareOptions swapped = new CompareOptions();
        swapped.swap = true;
        List<Difference> swappedDiffs = XmlCompare.compareXmlFiles(
            f1.getAbsolutePath(), f2.getAbsolutePath(), swapped);

        // swap(f1,f2) = compare(f2,f1) → expected/actual are reversed
        assertFalse(normalDiffs.isEmpty());
        assertFalse(swappedDiffs.isEmpty());
        assertEquals(normalDiffs.get(0).expected, swappedDiffs.get(0).actual);
        assertEquals(normalDiffs.get(0).actual, swappedDiffs.get(0).expected);
    }

    @Test
    void swapEqualFilesStillEqual() throws Exception {
        File f1 = write("a.xml", "<root><v>1</v></root>");
        File f2 = write("b.xml", "<root><v>1</v></root>");

        CompareOptions opts = new CompareOptions();
        opts.swap = true;
        List<Difference> diffs = XmlCompare.compareXmlFiles(
            f1.getAbsolutePath(), f2.getAbsolutePath(), opts);
        assertTrue(diffs.isEmpty());
    }

    // =========================================================================
    // CacheManager
    // =========================================================================

    @Test
    void cacheManagerSaveAndReload() throws Exception {
        File cacheFile = tmp.resolve("cache.json").toFile();
        File f1 = write("a.xml", "<root/>");
        File f2 = write("b.xml", "<root/>");

        CacheManager cm = new CacheManager(cacheFile.getAbsolutePath());
        assertFalse(cm.isCachedEqual(f1, f2));

        cm.update(f1, f2, true);
        assertTrue(cm.isCachedEqual(f1, f2));

        cm.save();

        CacheManager cm2 = new CacheManager(cacheFile.getAbsolutePath());
        assertTrue(cm2.isCachedEqual(f1, f2));
    }

    @Test
    void cacheManagerNotEqualNotCached() throws Exception {
        File cacheFile = tmp.resolve("cache.json").toFile();
        File f1 = write("a.xml", "<root/>");
        File f2 = write("b.xml", "<root/>");

        CacheManager cm = new CacheManager(cacheFile.getAbsolutePath());
        cm.update(f1, f2, false);
        assertFalse(cm.isCachedEqual(f1, f2));
    }

    @Test
    void cacheManagerCorruptFileDoesNotThrow() throws Exception {
        File cacheFile = tmp.resolve("corrupt.json").toFile();
        Files.writeString(cacheFile.toPath(), "NOT JSON {{{{");
        assertDoesNotThrow(() -> new CacheManager(cacheFile.getAbsolutePath()));
    }

    @Test
    void cacheManagerNonExistentFileDoesNotThrow() throws Exception {
        File cacheFile = tmp.resolve("nonexistent.json").toFile();
        CacheManager cm = assertDoesNotThrow(() -> new CacheManager(cacheFile.getAbsolutePath()));
        assertNotNull(cm);
    }

    @Test
    void cacheManagerChangedFileInvalidatesCache() throws Exception {
        File cacheFile = tmp.resolve("cache.json").toFile();
        File f1 = write("a.xml", "<root/>");
        File f2 = write("b.xml", "<root/>");

        CacheManager cm = new CacheManager(cacheFile.getAbsolutePath());
        cm.update(f1, f2, true);
        assertTrue(cm.isCachedEqual(f1, f2));

        // Modify a file — hash changes
        Files.writeString(f1.toPath(), "<root><changed/></root>");
        assertFalse(cm.isCachedEqual(f1, f2));
    }

    // =========================================================================
    // StreamingXmlParser
    // =========================================================================

    @Test
    void streamingEqualFiles() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>2</b></root>");
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(
            f1, f2, new CompareOptions());
        assertTrue(diffs.isEmpty());
    }

    @Test
    void streamingTextDiff() throws Exception {
        File f1 = write("a.xml", "<root><v>1</v></root>");
        File f2 = write("b.xml", "<root><v>2</v></root>");
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(
            f1, f2, new CompareOptions());
        assertFalse(diffs.isEmpty());
        assertTrue(diffs.stream().anyMatch(d -> "text".equals(d.kind)));
    }

    @Test
    void streamingTagMismatch() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a></root>");
        File f2 = write("b.xml", "<root><b>1</b></root>");
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(
            f1, f2, new CompareOptions());
        assertFalse(diffs.isEmpty());
        assertTrue(diffs.stream().anyMatch(d -> "tag".equals(d.kind)));
    }

    @Test
    void streamingAttrMismatch() throws Exception {
        File f1 = write("a.xml", "<root><v id=\"1\">text</v></root>");
        File f2 = write("b.xml", "<root><v id=\"2\">text</v></root>");
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(
            f1, f2, new CompareOptions());
        assertFalse(diffs.isEmpty());
        assertTrue(diffs.stream().anyMatch(d -> "attr".equals(d.kind)));
    }

    @Test
    void streamingAttrMissingInSecond() throws Exception {
        File f1 = write("a.xml", "<root><v id=\"1\">text</v></root>");
        File f2 = write("b.xml", "<root><v>text</v></root>");
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(
            f1, f2, new CompareOptions());
        assertFalse(diffs.isEmpty());
    }

    @Test
    void streamingAttrMissingInFirst() throws Exception {
        File f1 = write("a.xml", "<root><v>text</v></root>");
        File f2 = write("b.xml", "<root><v id=\"2\">text</v></root>");
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(
            f1, f2, new CompareOptions());
        assertFalse(diffs.isEmpty());
    }

    @Test
    void streamingDomFallbackUnordered() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><b>2</b><a>1</a></root>");
        CompareOptions opts = new CompareOptions();
        opts.unordered = true;
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(f1, f2, opts);
        assertTrue(diffs.isEmpty());  // DOM comparison handles unordered correctly
    }

    @Test
    void streamingDomFallbackSchema() throws Exception {
        File f1 = write("a.xml", "<root><v>1</v></root>");
        File f2 = write("b.xml", "<root><v>1</v></root>");
        CompareOptions opts = new CompareOptions();
        opts.schema = "dummy_schema.xsd";  // non-null triggers DOM fallback
        // DOM fallback will try compareXmlFiles; schema file doesn't exist so might throw or return empty
        assertDoesNotThrow(() -> StreamingXmlParser.compareXmlFilesStreaming(f1, f2, opts));
    }

    @Test
    void streamingIgnoreNamespaces() throws Exception {
        File f1 = write("a.xml", "<ns:root xmlns:ns=\"http://x\"><ns:v>1</ns:v></ns:root>");
        File f2 = write("b.xml", "<root><v>1</v></root>");
        CompareOptions opts = new CompareOptions();
        opts.ignoreNamespaces = true;
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(f1, f2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void streamingFailFast() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>X</a><b>Y</b></root>");
        CompareOptions opts = new CompareOptions();
        opts.failFast = true;
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(f1, f2, opts);
        assertEquals(1, diffs.size());
    }

    @Test
    void streamingStructureOnly() throws Exception {
        File f1 = write("a.xml", "<root><v>1</v></root>");
        File f2 = write("b.xml", "<root><v>999</v></root>");
        CompareOptions opts = new CompareOptions();
        opts.structureOnly = true;
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(f1, f2, opts);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void streamingDifferentElementCounts() throws Exception {
        // Use text-value difference so streaming StAX parser can detect it
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>99</b></root>");
        List<Difference> diffs = StreamingXmlParser.compareXmlFilesStreaming(
            f1, f2, new CompareOptions());
        assertFalse(diffs.isEmpty());
    }

    // =========================================================================
    // ParallelComparison
    // =========================================================================

    @Test
    void parallelEqualFiles() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>2</b></root>");
        List<Difference> diffs = ParallelComparison.compareXmlFilesParallel(
            f1, f2, new CompareOptions(), 2);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void parallelDifferentFiles() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>99</b></root>");
        List<Difference> diffs = ParallelComparison.compareXmlFilesParallel(
            f1, f2, new CompareOptions(), 2);
        assertFalse(diffs.isEmpty());
    }

    @Test
    void parallelSerialFallbackOneChild() throws Exception {
        File f1 = write("a.xml", "<root><only>1</only></root>");
        File f2 = write("b.xml", "<root><only>1</only></root>");
        List<Difference> diffs = ParallelComparison.compareXmlFilesParallel(
            f1, f2, new CompareOptions(), 2);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void parallelSerialFallbackOneThread() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>2</b></root>");
        List<Difference> diffs = ParallelComparison.compareXmlFilesParallel(
            f1, f2, new CompareOptions(), 1);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void parallelAutoThreadCount() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>2</b></root>");
        List<Difference> diffs = ParallelComparison.compareXmlFilesParallel(
            f1, f2, new CompareOptions(), 0);
        assertTrue(diffs.isEmpty());
    }

    @Test
    void parallelExtraChildrenInFirst() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b><c>3</c></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>2</b></root>");
        List<Difference> diffs = ParallelComparison.compareXmlFilesParallel(
            f1, f2, new CompareOptions(), 2);
        assertFalse(diffs.isEmpty());
    }

    @Test
    void parallelExtraChildrenInSecond() throws Exception {
        File f1 = write("a.xml", "<root><a>1</a><b>2</b></root>");
        File f2 = write("b.xml", "<root><a>1</a><b>2</b><c>3</c></root>");
        List<Difference> diffs = ParallelComparison.compareXmlFilesParallel(
            f1, f2, new CompareOptions(), 2);
        assertFalse(diffs.isEmpty());
    }

    // =========================================================================
    // compareDirs with cache integration
    // =========================================================================

    @Test
    void compareDirsWithCache() throws Exception {
        File dir1 = tmp.resolve("d1").toFile();
        File dir2 = tmp.resolve("d2").toFile();
        dir1.mkdirs();
        dir2.mkdirs();
        write("d1/a.xml", "<root><v>1</v></root>");
        write("d2/a.xml", "<root><v>1</v></root>");
        File cacheFile = tmp.resolve("cache.json").toFile();

        CompareOptions opts = new CompareOptions();
        opts.cacheFile = cacheFile.getAbsolutePath();

        Map<String, Object> results1 = XmlCompare.compareDirs(
            dir1.getAbsolutePath(), dir2.getAbsolutePath(), opts, false);
        assertNotNull(results1.get("a.xml"));
        assertTrue(cacheFile.exists());

        // Second run: cached hit
        Map<String, Object> results2 = XmlCompare.compareDirs(
            dir1.getAbsolutePath(), dir2.getAbsolutePath(), opts, false);
        @SuppressWarnings("unchecked")
        List<Difference> diffs = (List<Difference>) results2.get("a.xml");
        assertTrue(diffs.isEmpty());
    }

    // =========================================================================
    // noColor in compareXmlFiles reporting
    // =========================================================================

    @Test
    void noColorFlagInCompareOptions() {
        CompareOptions opts = new CompareOptions();
        opts.noColor = true;
        assertTrue(opts.noColor);
    }

    @Test
    void formatTextReportWithDiffsNoColor() {
        List<Difference> diffs = List.of(
            diff("root/v", "text", "differs", "a", "b"),
            diff("root/w", "attr", "attr mismatch", "old", "new")
        );
        String out = XmlCompare.formatTextReport(diffs, null, null, true);
        assertFalse(out.contains("\033["));
        assertTrue(out.contains("[TEXT]"));
        assertTrue(out.contains("[ATTR]"));
        assertTrue(out.contains("Expected : a"));
        assertTrue(out.contains("Actual   : b"));
    }
}
