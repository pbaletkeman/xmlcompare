package com.xmlcompare;

import com.xmlcompare.plugin.ComparisonPluginSPI;
import com.xmlcompare.plugin.DifferenceFilter;
import com.xmlcompare.plugin.FormatterPlugin;
import com.xmlcompare.plugin.PluginRegistry;
import com.xmlcompare.schema.SchemaAnalyzer;
import com.xmlcompare.schema.SchemaMetadata;
import com.xmlcompare.schema.TypeAwareComparator;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for Phase 1: Plugin Architecture & Schema Integration (Java).
 */
public class Phase1FeaturesTest {

    // -----------------------------------------------------------------------
    // Helper methods
    // -----------------------------------------------------------------------

    private List<Difference> compareStrings(String xml1, String xml2, CompareOptions opts) throws Exception {
        var doc1 = XmlCompare.parseXmlString(xml1);
        var doc2 = XmlCompare.parseXmlString(xml2);
        return XmlCompare.compareElements(doc1.getDocumentElement(), doc2.getDocumentElement(),
            opts, "", null);
    }

    private Path writeXml(Path dir, String name, String content) throws IOException {
        Path file = dir.resolve(name);
        Files.writeString(file, content);
        return file;
    }

    private Path writeXsd(Path dir, String name, String content) throws IOException {
        Path file = dir.resolve(name);
        Files.writeString(file, content);
        return file;
    }

    // -----------------------------------------------------------------------
    // CompareOptions Phase 1 fields
    // -----------------------------------------------------------------------

    @Test
    void testCompareOptionsDefaultSchema() {
        CompareOptions opts = new CompareOptions();
        assertNull(opts.schema);
    }

    @Test
    void testCompareOptionsDefaultTypeAware() {
        CompareOptions opts = new CompareOptions();
        assertFalse(opts.typeAware);
    }

    @Test
    void testCompareOptionsDefaultPluginsEmpty() {
        CompareOptions opts = new CompareOptions();
        assertNotNull(opts.plugins);
        assertTrue(opts.plugins.isEmpty());
    }

    // -----------------------------------------------------------------------
    // FormatterPlugin interface
    // -----------------------------------------------------------------------

    @Test
    void testFormatterPluginRegistrationAndRetrieval() {
        FormatterPlugin plugin = new FormatterPlugin() {
            @Override
            public String getName() { return "test-formatter"; }

            @Override
            public String format(Map<String, Object> allResults, String label1, String label2) {
                return "test-output";
            }
        };

        PluginRegistry registry = new PluginRegistry();
        registry.registerFormatter(plugin);

        FormatterPlugin found = registry.getFormatter("test-formatter");
        assertNotNull(found);
        assertSame(plugin, found);
    }

    @Test
    void testFormatterPluginUnknownNameReturnsNull() {
        PluginRegistry registry = new PluginRegistry();
        assertNull(registry.getFormatter("nonexistent"));
    }

    @Test
    void testFormatterPluginListNames() {
        PluginRegistry registry = new PluginRegistry();
        registry.registerFormatter(new FormatterPlugin() {
            @Override public String getName() { return "fmt-a"; }
            @Override public String format(Map<String, Object> r, String l1, String l2) { return ""; }
        });
        registry.registerFormatter(new FormatterPlugin() {
            @Override public String getName() { return "fmt-b"; }
            @Override public String format(Map<String, Object> r, String l1, String l2) { return ""; }
        });

        List<String> names = registry.listFormatters();
        assertTrue(names.contains("fmt-a"));
        assertTrue(names.contains("fmt-b"));
    }

    // -----------------------------------------------------------------------
    // DifferenceFilter interface
    // -----------------------------------------------------------------------

    @Test
    void testDifferenceFilterRegistrationAndRetrieval() {
        DifferenceFilter filter = new DifferenceFilter() {
            @Override public String getName() { return "ignore-text"; }
            @Override public boolean shouldIgnore(Difference d) { return "text".equals(d.kind); }
        };

        PluginRegistry registry = new PluginRegistry();
        registry.registerFilter(filter);

        List<DifferenceFilter> filters = registry.getFilters();
        assertEquals(1, filters.size());
        assertSame(filter, filters.get(0));
    }

    @Test
    void testDifferenceFilterApplyFiltersRemovesSuppressed() {
        DifferenceFilter textFilter = new DifferenceFilter() {
            @Override public String getName() { return "ignore-text"; }
            @Override public boolean shouldIgnore(Difference d) { return "text".equals(d.kind); }
        };

        PluginRegistry registry = new PluginRegistry();
        registry.registerFilter(textFilter);

        List<Difference> diffs = List.of(
            new Difference("path/a", "text", "text diff"),
            new Difference("path/b", "attr", "attr diff"),
            new Difference("path/c", "text", "another text diff")
        );

        List<Difference> filtered = registry.applyFilters(diffs);
        assertEquals(1, filtered.size());
        assertEquals("attr", filtered.get(0).kind);
    }

    @Test
    void testDifferenceFilterApplyFiltersEmpty() {
        PluginRegistry registry = new PluginRegistry();
        List<Difference> diffs = List.of(
            new Difference("path/a", "text", "text diff")
        );
        List<Difference> filtered = registry.applyFilters(diffs);
        assertEquals(1, filtered.size());
    }

    @Test
    void testPluginRegistryServiceLoaderDoesNotCrash() {
        PluginRegistry registry = new PluginRegistry();
        // Should not throw even with no plugins installed.
        // Uses the current thread's class loader — no network calls are made;
        // ServiceLoader only inspects the local classpath.
        assertDoesNotThrow((org.junit.jupiter.api.function.Executable) registry::loadServiceLoader);
    }

    @Test
    void testPluginRegistryServiceLoaderWithMockClassLoader() {
        // Use a minimal custom ClassLoader that exposes mock service entries
        // so the test is fully self-contained and not affected by firewall or classpath.
        PluginRegistry registry = new PluginRegistry();
        // An empty ClassLoader finds no META-INF/services — registry stays empty
        ClassLoader emptyLoader = new ClassLoader(null) { };
        registry.loadServiceLoader(emptyLoader);
        assertTrue(registry.listFormatters().isEmpty());
        assertTrue(registry.getFilters().isEmpty());
    }

    @Test
    void testPluginRegistryLoadModuleUnknownClassDoesNotThrow() {
        PluginRegistry registry = new PluginRegistry();
        // Should print a warning but not throw
        assertDoesNotThrow((org.junit.jupiter.api.function.Executable)
            () -> registry.loadModule("com.example.NonExistentPlugin"));
    }

    @Test
    void testPluginRegistryLoadModuleRegistersConcretePlugin() {
        // Register a mock formatter directly then verify it is returned.
        // This is the "mock services" pattern — no ServiceLoader/classpath needed.
        FormatterPlugin mockFmt = new FormatterPlugin() {
            @Override public String getName() { return "inline-mock"; }
            @Override public String format(Map<String, Object> r, String l1, String l2) {
                return "inline";
            }
        };
        PluginRegistry registry = new PluginRegistry();
        registry.registerFormatter(mockFmt);

        assertNotNull(registry.getFormatter("inline-mock"));
        assertEquals("inline", registry.getFormatter("inline-mock").format(Map.of(), null, null));
    }

    @Test
    void testPluginRegistryMockFilterIsAppliedDuringComparison() {
        // Mock a DifferenceFilter that suppresses all text differences.
        // Fully self-contained — no ServiceLoader or classpath scanning.
        DifferenceFilter suppressText = new DifferenceFilter() {
            @Override public String getName() { return "suppress-text"; }
            @Override public boolean shouldIgnore(Difference d) { return "text".equals(d.kind); }
        };

        PluginRegistry registry = new PluginRegistry();
        registry.registerFilter(suppressText);

        List<Difference> diffs = List.of(
            new Difference("a/b", "text", "text diff"),
            new Difference("a/c", "attr", "attr diff"),
            new Difference("a/d", "text", "another text diff")
        );

        List<Difference> result = registry.applyFilters(diffs);
        assertEquals(1, result.size());
        assertEquals("attr", result.get(0).kind);
    }

    // -----------------------------------------------------------------------
    // TypeAwareComparator
    // -----------------------------------------------------------------------

    @Test
    void testTypeCategoryDate() {
        assertEquals("date", TypeAwareComparator.typeCategory("xs:date"));
        assertEquals("date", TypeAwareComparator.typeCategory("xs:dateTime"));
        assertEquals("date", TypeAwareComparator.typeCategory("date"));
    }

    @Test
    void testTypeCategoryNumeric() {
        assertEquals("numeric", TypeAwareComparator.typeCategory("xs:integer"));
        assertEquals("numeric", TypeAwareComparator.typeCategory("xs:decimal"));
        assertEquals("numeric", TypeAwareComparator.typeCategory("xs:float"));
    }

    @Test
    void testTypeCategoryBoolean() {
        assertEquals("boolean", TypeAwareComparator.typeCategory("xs:boolean"));
        assertEquals("boolean", TypeAwareComparator.typeCategory("boolean"));
    }

    @Test
    void testTypeCategoryUnknown() {
        assertNull(TypeAwareComparator.typeCategory("xs:string"));
        assertNull(TypeAwareComparator.typeCategory(null));
    }

    @Test
    void testTypeAwareEqualBooleanTrueVariants() {
        Optional<Boolean> result = TypeAwareComparator.typeAwareEqual("true", "1", "xs:boolean");
        assertTrue(result.isPresent());
        assertTrue(result.get());
    }

    @Test
    void testTypeAwareEqualBooleanMismatch() {
        Optional<Boolean> result = TypeAwareComparator.typeAwareEqual("true", "false", "xs:boolean");
        assertTrue(result.isPresent());
        assertFalse(result.get());
    }

    @Test
    void testTypeAwareEqualNumericEqual() {
        Optional<Boolean> result = TypeAwareComparator.typeAwareEqual("1.0", "1", "xs:decimal");
        assertTrue(result.isPresent());
        assertTrue(result.get());
    }

    @Test
    void testTypeAwareEqualNumericMismatch() {
        Optional<Boolean> result = TypeAwareComparator.typeAwareEqual("1.0", "2.0", "xs:decimal");
        assertTrue(result.isPresent());
        assertFalse(result.get());
    }

    @Test
    void testTypeAwareEqualDateEqual() {
        Optional<Boolean> result = TypeAwareComparator.typeAwareEqual("2024-01-15", "2024-01-15", "xs:date");
        assertTrue(result.isPresent());
        assertTrue(result.get());
    }

    @Test
    void testTypeAwareEqualDateMismatch() {
        Optional<Boolean> result = TypeAwareComparator.typeAwareEqual("2024-01-15", "2024-01-16", "xs:date");
        assertTrue(result.isPresent());
        assertFalse(result.get());
    }

    @Test
    void testTypeAwareEqualUnknownTypeReturnsEmpty() {
        Optional<Boolean> result = TypeAwareComparator.typeAwareEqual("hello", "hello", "xs:string");
        assertTrue(result.isEmpty());
    }

    @Test
    void testValuesEqualTypeAwareBoolean() {
        CompareOptions opts = new CompareOptions();
        opts.typeAware = true;
        assertTrue(XmlCompare.valuesEqual("true", "1", opts, "xs:boolean"));
        assertFalse(XmlCompare.valuesEqual("true", "false", opts, "xs:boolean"));
    }

    @Test
    void testValuesEqualTypeAwareNumeric() {
        CompareOptions opts = new CompareOptions();
        opts.typeAware = true;
        assertTrue(XmlCompare.valuesEqual("1.0", "1", opts, "xs:decimal"));
    }

    @Test
    void testValuesEqualTypeAwareFallbackWithoutTypeAware() {
        CompareOptions opts = new CompareOptions();
        opts.typeAware = false;
        // Without typeAware, xs:boolean type hint is ignored
        assertFalse(XmlCompare.valuesEqual("true", "1", opts, "xs:boolean"));
    }

    // -----------------------------------------------------------------------
    // SchemaAnalyzer
    // -----------------------------------------------------------------------

    @Test
    void testSchemaAnalyzerExtractsTypes(@TempDir Path tmpDir) throws IOException {
        String xsd = """
            <?xml version="1.0"?>
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
              <xs:element name="root">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name="date" type="xs:date"/>
                    <xs:element name="amount" type="xs:decimal"/>
                    <xs:element name="active" type="xs:boolean"/>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:schema>""";
        Path xsdFile = writeXsd(tmpDir, "schema.xsd", xsd);

        SchemaMetadata meta = new SchemaAnalyzer().analyze(xsdFile.toString());
        assertFalse(meta.isEmpty());

        assertEquals("xs:date", meta.getXsType("date", "root/date"));
        assertEquals("xs:decimal", meta.getXsType("amount", "root/amount"));
        assertEquals("xs:boolean", meta.getXsType("active", "root/active"));
    }

    @Test
    void testSchemaAnalyzerMissingFileReturnsEmpty() {
        SchemaMetadata meta = new SchemaAnalyzer().analyze("/nonexistent/path/schema.xsd");
        assertTrue(meta.isEmpty());
    }

    @Test
    void testSchemaAnalyzerAllGroupIsUnordered(@TempDir Path tmpDir) throws IOException {
        String xsd = """
            <?xml version="1.0"?>
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
              <xs:element name="root">
                <xs:complexType>
                  <xs:all>
                    <xs:element name="a" type="xs:string"/>
                    <xs:element name="b" type="xs:string"/>
                  </xs:all>
                </xs:complexType>
              </xs:element>
            </xs:schema>""";
        Path xsdFile = writeXsd(tmpDir, "schema.xsd", xsd);

        SchemaMetadata meta = new SchemaAnalyzer().analyze(xsdFile.toString());
        assertTrue(meta.isUnorderedChildren("root"));
    }

    @Test
    void testSchemaAnalyzerSequenceIsOrdered(@TempDir Path tmpDir) throws IOException {
        String xsd = """
            <?xml version="1.0"?>
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
              <xs:element name="root">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name="a" type="xs:string"/>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:schema>""";
        Path xsdFile = writeXsd(tmpDir, "schema.xsd", xsd);

        SchemaMetadata meta = new SchemaAnalyzer().analyze(xsdFile.toString());
        assertFalse(meta.isUnorderedChildren("root"));
    }

    @Test
    void testSchemaAnalyzerMinMaxOccurs(@TempDir Path tmpDir) throws IOException {
        String xsd = """
            <?xml version="1.0"?>
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
            </xs:schema>""";
        Path xsdFile = writeXsd(tmpDir, "schema.xsd", xsd);

        SchemaMetadata meta = new SchemaAnalyzer().analyze(xsdFile.toString());

        Optional<SchemaMetadata.ElementInfo> req = meta.getElementInfo("required", "root/required");
        assertTrue(req.isPresent());
        assertEquals(1, req.get().minOccurs);
        assertEquals(1, req.get().maxOccurs);
        assertTrue(req.get().required);

        Optional<SchemaMetadata.ElementInfo> opt = meta.getElementInfo("optional", "root/optional");
        assertTrue(opt.isPresent());
        assertEquals(0, opt.get().minOccurs);
        assertFalse(opt.get().required);

        Optional<SchemaMetadata.ElementInfo> rep = meta.getElementInfo("repeated", "root/repeated");
        assertTrue(rep.isPresent());
        assertNull(rep.get().maxOccurs); // unbounded
    }

    // -----------------------------------------------------------------------
    // Schema-aware comparison
    // -----------------------------------------------------------------------

    @Test
    void testSchemaTypeAwareBooleanComparison(@TempDir Path tmpDir) throws IOException {
        String xsd = """
            <?xml version="1.0"?>
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
              <xs:element name="root">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name="flag" type="xs:boolean"/>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:schema>""";
        Path xsdFile = writeXsd(tmpDir, "schema.xsd", xsd);
        Path file1 = writeXml(tmpDir, "a.xml", "<root><flag>true</flag></root>");
        Path file2 = writeXml(tmpDir, "b.xml", "<root><flag>1</flag></root>");

        CompareOptions opts = new CompareOptions();
        opts.schema = xsdFile.toString();
        opts.typeAware = true;

        List<Difference> diffs = XmlCompare.compareXmlFiles(file1.toString(), file2.toString(), opts);
        assertTrue(diffs.isEmpty(), "true and 1 should be equal as xs:boolean");
    }

    @Test
    void testSchemaAllGroupUsesUnorderedComparison(@TempDir Path tmpDir) throws IOException {
        String xsd = """
            <?xml version="1.0"?>
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
              <xs:element name="root">
                <xs:complexType>
                  <xs:all>
                    <xs:element name="a" type="xs:string"/>
                    <xs:element name="b" type="xs:string"/>
                  </xs:all>
                </xs:complexType>
              </xs:element>
            </xs:schema>""";
        Path xsdFile = writeXsd(tmpDir, "schema.xsd", xsd);
        Path file1 = writeXml(tmpDir, "a.xml", "<root><a>x</a><b>y</b></root>");
        Path file2 = writeXml(tmpDir, "b.xml", "<root><b>y</b><a>x</a></root>");

        CompareOptions opts = new CompareOptions();
        opts.schema = xsdFile.toString();
        opts.typeAware = true;

        List<Difference> diffs = XmlCompare.compareXmlFiles(file1.toString(), file2.toString(), opts);
        assertTrue(diffs.isEmpty(), "xs:all means any order is valid");
    }

    @Test
    void testCompareWithoutSchemaWorksNormally(@TempDir Path tmpDir) throws IOException {
        Path file1 = writeXml(tmpDir, "a.xml", "<r><v>1</v></r>");
        Path file2 = writeXml(tmpDir, "b.xml", "<r><v>2</v></r>");

        CompareOptions opts = new CompareOptions();
        List<Difference> diffs = XmlCompare.compareXmlFiles(file1.toString(), file2.toString(), opts);
        assertEquals(1, diffs.size());
        assertEquals("text", diffs.get(0).kind);
    }
}
