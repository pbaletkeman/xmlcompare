package com.xmlcompare;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.xmlcompare.schema.SchemaAnalyzer;
import com.xmlcompare.schema.SchemaMetadata;
import com.xmlcompare.schema.TypeAwareComparator;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;
import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class XmlCompare {

    public static String stripNamespace(String tag) {
        if (tag != null && tag.startsWith("{")) {
            int idx = tag.indexOf('}');
            if (idx >= 0) {
                return tag.substring(idx + 1);
            }
        }
        return tag;
    }

    public static String getTag(Element elem, CompareOptions opts) {
        String tag = elem.getLocalName();
        if (tag == null) {
            tag = elem.getNodeName();
        }
        if (!opts.ignoreNamespaces && elem.getNamespaceURI() != null) {
            tag = "{" + elem.getNamespaceURI() + "}" + tag;
        }
        return tag;
    }

    public static String normalizeText(String text) {
        if (text == null) return "";
        return String.join(" ", text.trim().split("\\s+")).trim();
    }

    public static Optional<Double> toNumeric(String text) {
        if (text == null || text.isEmpty()) return Optional.empty();
        try {
            return Optional.of(Double.parseDouble(text));
        } catch (NumberFormatException e) {
            return Optional.empty();
        }
    }

    public static boolean valuesEqual(String a, String b, CompareOptions opts) {
        return valuesEqual(a, b, opts, null);
    }

    /**
     * Compare two string values with optional XSD type awareness.
     *
     * @param a      first value
     * @param b      second value
     * @param opts   comparison options
     * @param xsType XSD simple type (e.g. {@code "xs:date"}), or {@code null}
     * @return {@code true} if the values are considered equal
     */
    public static boolean valuesEqual(String a, String b, CompareOptions opts, String xsType) {
        // Type-aware comparison via schema hints
        if (xsType != null && opts.typeAware) {
            Optional<Boolean> result = TypeAwareComparator.typeAwareEqual(a, b, xsType);
            if (result.isPresent()) return result.get();
        }

        String na = normalizeText(a);
        String nb = normalizeText(b);
        Optional<Double> fa = toNumeric(na);
        Optional<Double> fb = toNumeric(nb);
        if (fa.isPresent() && fb.isPresent()) {
            return Math.abs(fa.get() - fb.get()) <= opts.tolerance;
        }
        if (opts.ignoreCase) {
            return na.equalsIgnoreCase(nb);
        }
        return na.equals(nb);
    }

    public static String buildPath(String parent, String tag) {
        if (parent == null || parent.isEmpty()) return tag;
        return parent + "/" + tag;
    }

    public static boolean shouldSkip(String path, String tag, CompareOptions opts) {
        for (String skipKey : opts.skipKeys) {
            if (skipKey.startsWith("//")) {
                String skTag = skipKey.substring(2);
                if (tag.equals(skTag)) return true;
            } else {
                if (path.equals(skipKey)) return true;
            }
        }
        if (opts.skipPattern != null) {
            try {
                if (Pattern.compile(opts.skipPattern).matcher(tag).find()) return true;
            } catch (PatternSyntaxException e) {
                // ignore bad pattern
            }
        }
        return false;
    }

    private static List<Element> getChildElements(Element elem) {
        List<Element> children = new ArrayList<>();
        NodeList nodes = elem.getChildNodes();
        for (int i = 0; i < nodes.getLength(); i++) {
            Node n = nodes.item(i);
            if (n.getNodeType() == Node.ELEMENT_NODE) {
                children.add((Element) n);
            }
        }
        return children;
    }

    private static String getDirectTextContent(Element elem) {
        StringBuilder sb = new StringBuilder();
        NodeList nodes = elem.getChildNodes();
        for (int i = 0; i < nodes.getLength(); i++) {
            Node n = nodes.item(i);
            if (n.getNodeType() == Node.TEXT_NODE || n.getNodeType() == Node.CDATA_SECTION_NODE) {
                sb.append(n.getNodeValue());
            }
        }
        return sb.toString();
    }

    public static List<Difference> compareElements(Element elem1, Element elem2, CompareOptions opts, String path, List<Difference> diffs) {
        return compareElements(elem1, elem2, opts, path, diffs, 0, null);
    }

    public static List<Difference> compareElements(Element elem1, Element elem2, CompareOptions opts, String path, List<Difference> diffs, int depth) {
        return compareElements(elem1, elem2, opts, path, diffs, depth, null);
    }

    /**
     * Recursively compare two XML elements, optionally using schema metadata.
     *
     * @param elem1      first element
     * @param elem2      second element
     * @param opts       comparison options
     * @param path       current XPath-style path
     * @param diffs      accumulator list for differences
     * @param depth      current recursion depth
     * @param schemaMeta optional {@link SchemaMetadata} for type-aware comparison
     * @return the {@code diffs} list
     */
    public static List<Difference> compareElements(Element elem1, Element elem2,
            CompareOptions opts, String path, List<Difference> diffs, int depth,
            SchemaMetadata schemaMeta) {
        if (diffs == null) diffs = new ArrayList<>();

        String tag1 = getTag(elem1, opts);
        String tag2 = getTag(elem2, opts);
        String currentPath = (path == null || path.isEmpty()) ? tag1 : path;

        if (opts.verbose) {
            System.err.println("  Comparing: " + currentPath + " (depth=" + depth + ")");
        }

        // Check if we've exceeded max depth
        if (opts.maxDepth != null && depth > opts.maxDepth) {
            return diffs;
        }

        if (!tag1.equals(tag2)) {
            diffs.add(new Difference(currentPath, "tag",
                "Tag mismatch: '" + tag1 + "' != '" + tag2 + "'", tag1, tag2));
            return diffs;
        }

        // Resolve XSD type for type-aware comparison
        String xsType = null;
        if (schemaMeta != null && opts.typeAware) {
            xsType = schemaMeta.getXsType(tag1, currentPath);
        }

        // Text content (skip if structure_only)
        if (!opts.structureOnly) {
            String text1 = normalizeText(getDirectTextContent(elem1));
            String text2 = normalizeText(getDirectTextContent(elem2));
            if (!valuesEqual(text1, text2, opts, xsType)) {
                diffs.add(new Difference(currentPath, "text",
                    "Text mismatch at '" + currentPath + "': '" + text1 + "' != '" + text2 + "'",
                    text1, text2));
                if (opts.failFast) return diffs;
            }
        }

        // Attributes (skip if structure_only)
        if (!opts.ignoreAttributes && !opts.structureOnly) {
            Map<String, String> attrs1 = getAttributes(elem1, opts);
            Map<String, String> attrs2 = getAttributes(elem2, opts);
            List<String> allKeys = new ArrayList<>(new TreeSet<>(
                Stream.concat(attrs1.keySet().stream(), attrs2.keySet().stream()).collect(Collectors.toSet())));
            for (String key : allKeys) {
                if (!attrs1.containsKey(key)) {
                    diffs.add(new Difference(currentPath, "attr",
                        "Attribute '" + key + "' missing in first element at '" + currentPath + "'",
                        null, attrs2.get(key)));
                    if (opts.failFast) return diffs;
                } else if (!attrs2.containsKey(key)) {
                    diffs.add(new Difference(currentPath, "attr",
                        "Attribute '" + key + "' missing in second element at '" + currentPath + "'",
                        attrs1.get(key), null));
                    if (opts.failFast) return diffs;
                } else if (!valuesEqual(attrs1.get(key), attrs2.get(key), opts)) {
                    diffs.add(new Difference(currentPath, "attr",
                        "Attribute '" + key + "' mismatch at '" + currentPath + "': '" + attrs1.get(key) + "' != '" + attrs2.get(key) + "'",
                        attrs1.get(key), attrs2.get(key)));
                    if (opts.failFast) return diffs;
                }
            }
        }

        if (opts.failFast && !diffs.isEmpty()) return diffs;

        // Only compare children if we haven't reached max depth limit
        if (opts.maxDepth == null || depth < opts.maxDepth) {
            final String cp = currentPath;
            List<Element> children1 = getChildElements(elem1).stream()
                .filter(c -> {
                    String ctag = getTag(c, opts);
                    String cpath = buildPath(cp, ctag);
                    return !shouldSkip(cpath, ctag, opts);
                }).collect(Collectors.toList());

            List<Element> children2 = getChildElements(elem2).stream()
                .filter(c -> {
                    String ctag = getTag(c, opts);
                    String cpath = buildPath(cp, ctag);
                    return !shouldSkip(cpath, ctag, opts);
                }).collect(Collectors.toList());

            // Use schema-driven ordering hint when available
            boolean schemaUnordered = schemaMeta != null && opts.typeAware
                && schemaMeta.isUnorderedChildren(currentPath);
            if (opts.unordered || schemaUnordered) {
                compareUnordered(children1, children2, opts, currentPath, diffs, depth, schemaMeta);
            } else {
                compareOrdered(children1, children2, opts, currentPath, diffs, depth, schemaMeta);
            }
        }

        return diffs;
    }

    private static Map<String, String> getAttributes(Element elem, CompareOptions opts) {
        Map<String, String> attrs = new LinkedHashMap<>();
        NamedNodeMap nnm = elem.getAttributes();
        for (int i = 0; i < nnm.getLength(); i++) {
            Node attr = nnm.item(i);
            String name = attr.getNodeName();
            // skip xmlns declarations
            if (name.equals("xmlns") || name.startsWith("xmlns:")) continue;
            if (opts.ignoreNamespaces) {
                name = stripNamespace(attr.getLocalName() != null ? attr.getLocalName() : name);
            }
            attrs.put(name, attr.getNodeValue());
        }
        return attrs;
    }

    public static void compareOrdered(List<Element> children1, List<Element> children2, CompareOptions opts, String path, List<Difference> diffs) {
        compareOrdered(children1, children2, opts, path, diffs, 0, null);
    }

    public static void compareOrdered(List<Element> children1, List<Element> children2, CompareOptions opts, String path, List<Difference> diffs, int depth) {
        compareOrdered(children1, children2, opts, path, diffs, depth, null);
    }

    public static void compareOrdered(List<Element> children1, List<Element> children2,
            CompareOptions opts, String path, List<Difference> diffs, int depth,
            SchemaMetadata schemaMeta) {
        int maxLen = Math.max(children1.size(), children2.size());
        for (int i = 0; i < maxLen; i++) {
            if (i >= children1.size()) {
                String tag = getTag(children2.get(i), opts);
                diffs.add(new Difference(buildPath(path, tag), "missing",
                    "Element '" + tag + "' missing in first document at position " + i));
                if (opts.failFast) return;
            } else if (i >= children2.size()) {
                String tag = getTag(children1.get(i), opts);
                diffs.add(new Difference(buildPath(path, tag), "extra",
                    "Element '" + tag + "' missing in second document at position " + i));
                if (opts.failFast) return;
            } else {
                String childPath = buildPath(path, getTag(children1.get(i), opts));
                compareElements(children1.get(i), children2.get(i), opts, childPath, diffs,
                    depth + 1, schemaMeta);
                if (opts.failFast && !diffs.isEmpty()) return;
            }
        }
    }

    public static void compareUnordered(List<Element> children1, List<Element> children2, CompareOptions opts, String path, List<Difference> diffs) {
        compareUnordered(children1, children2, opts, path, diffs, 0, null);
    }

    public static void compareUnordered(List<Element> children1, List<Element> children2, CompareOptions opts, String path, List<Difference> diffs, int depth) {
        compareUnordered(children1, children2, opts, path, diffs, depth, null);
    }

    private static String groupKey(Element elem, CompareOptions opts) {
        String tag = getTag(elem, opts);
        if (opts.matchAttr != null && !opts.matchAttr.isEmpty()) {
            return tag + "[@" + opts.matchAttr + "='" + elem.getAttribute(opts.matchAttr) + "']";
        }
        return tag;
    }

    public static void compareUnordered(List<Element> children1, List<Element> children2,
            CompareOptions opts, String path, List<Difference> diffs, int depth,
            SchemaMetadata schemaMeta) {
        Map<String, List<Element>> groups1 = new LinkedHashMap<>();
        Map<String, List<Element>> groups2 = new LinkedHashMap<>();

        for (Element c : children1) {
            groups1.computeIfAbsent(groupKey(c, opts), k -> new ArrayList<>()).add(c);
        }
        for (Element c : children2) {
            groups2.computeIfAbsent(groupKey(c, opts), k -> new ArrayList<>()).add(c);
        }

        Set<String> allTags = new TreeSet<>();
        allTags.addAll(groups1.keySet());
        allTags.addAll(groups2.keySet());

        for (String tag : allTags) {
            List<Element> elems1 = groups1.getOrDefault(tag, Collections.emptyList());
            List<Element> elems2 = groups2.getOrDefault(tag, Collections.emptyList());
            String childPath = buildPath(path, tag);
            int maxLen = Math.max(elems1.size(), elems2.size());
            for (int i = 0; i < maxLen; i++) {
                if (i >= elems1.size()) {
                    diffs.add(new Difference(childPath, "missing",
                        "Element '" + tag + "' occurrence " + (i + 1) + " missing in first document"));
                    if (opts.failFast) return;
                } else if (i >= elems2.size()) {
                    diffs.add(new Difference(childPath, "extra",
                        "Element '" + tag + "' occurrence " + (i + 1) + " missing in second document"));
                    if (opts.failFast) return;
                } else {
                    compareElements(elems1.get(i), elems2.get(i), opts, childPath, diffs,
                        depth + 1, schemaMeta);
                    if (opts.failFast && !diffs.isEmpty()) return;
                }
            }
        }
    }

    private static DocumentBuilder newDocumentBuilder() throws ParserConfigurationException {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        return factory.newDocumentBuilder();
    }

    public static Document parseXmlFile(String filePath) throws IOException, SAXException, ParserConfigurationException {
        DocumentBuilder builder = newDocumentBuilder();
        return builder.parse(new File(filePath));
    }

    public static Document parseXmlString(String xml) throws IOException, SAXException, ParserConfigurationException {
        DocumentBuilder builder = newDocumentBuilder();
        return builder.parse(new InputSource(new StringReader(xml)));
    }

    private static void stripNonElements(Element elem) {
        List<Node> toRemove = new ArrayList<>();
        NodeList children = elem.getChildNodes();
        for (int i = 0; i < children.getLength(); i++) {
            Node n = children.item(i);
            if (n.getNodeType() == Node.COMMENT_NODE
                    || n.getNodeType() == Node.PROCESSING_INSTRUCTION_NODE) {
                toRemove.add(n);
            } else if (n.getNodeType() == Node.ELEMENT_NODE) {
                stripNonElements((Element) n);
            }
        }
        for (Node n : toRemove) {
            elem.removeChild(n);
        }
    }

    private static Document applyXslt(Document doc, String xsltPath) throws Exception {
        javax.xml.transform.TransformerFactory tf =
            javax.xml.transform.TransformerFactory.newInstance();
        javax.xml.transform.Transformer transformer =
            tf.newTransformer(new javax.xml.transform.stream.StreamSource(new File(xsltPath)));
        DocumentBuilder builder = newDocumentBuilder();
        Document result = builder.newDocument();
        transformer.transform(
            new javax.xml.transform.dom.DOMSource(doc),
            new javax.xml.transform.dom.DOMResult(result));
        return result;
    }

    private static boolean useAnsiColor() {
        return useAnsiColor(false);
    }

    private static boolean useAnsiColor(boolean noColor) {
        if (noColor) return false;
        return System.console() != null
            && System.getenv("NO_COLOR") == null
            && !"false".equalsIgnoreCase(System.getenv("XMLCOMPARE_COLOR"));
    }

    public static List<Difference> compareXmlFiles(String file1, String file2, CompareOptions opts) throws IOException {
        if (opts.swap) {
            String tmp = file1;
            file1 = file2;
            file2 = tmp;
        }
        // Load schema metadata if specified
        SchemaMetadata schemaMeta = null;
        if (opts.schema != null && !opts.schema.isEmpty()) {
            schemaMeta = new SchemaAnalyzer().analyze(opts.schema);
        }

        Document doc1, doc2;
        try {
            doc1 = parseXmlFile(file1);
        } catch (SAXException e) {
            throw new IOException("Failed to parse " + file1 + ": " + e.getMessage(), e);
        } catch (ParserConfigurationException e) {
            throw new IOException("Parser configuration error: " + e.getMessage(), e);
        }
        try {
            doc2 = parseXmlFile(file2);
        } catch (SAXException e) {
            throw new IOException("Failed to parse " + file2 + ": " + e.getMessage(), e);
        } catch (ParserConfigurationException e) {
            throw new IOException("Parser configuration error: " + e.getMessage(), e);
        }

        Element root1 = doc1.getDocumentElement();
        Element root2 = doc2.getDocumentElement();

        // Pre-processing: XSLT transform
        if (opts.xsltPath != null && !opts.xsltPath.isEmpty()) {
            try {
                doc1 = applyXslt(doc1, opts.xsltPath);
                doc2 = applyXslt(doc2, opts.xsltPath);
                root1 = doc1.getDocumentElement();
                root2 = doc2.getDocumentElement();
            } catch (Exception e) {
                throw new IOException("XSLT transform failed: " + e.getMessage(), e);
            }
        }

        // Pre-processing: canonicalize (strip comments and processing instructions)
        if (opts.canonicalize) {
            stripNonElements(root1);
            stripNonElements(root2);
        }

        if (opts.filterXpath != null && !opts.filterXpath.isEmpty()) {
            try {
                XPath xpath = XPathFactory.newInstance().newXPath();
                NodeList nl1 = (NodeList) xpath.evaluate(opts.filterXpath, root1, XPathConstants.NODESET);
                NodeList nl2 = (NodeList) xpath.evaluate(opts.filterXpath, root2, XPathConstants.NODESET);
                List<Element> elems1 = nodeListToElements(nl1);
                List<Element> elems2 = nodeListToElements(nl2);
                List<Difference> diffs = new ArrayList<>();
                compareOrdered(elems1, elems2, opts, "", diffs, 0, schemaMeta);
                return diffs;
            } catch (XPathExpressionException e) {
                throw new IOException("Invalid filter XPath '" + opts.filterXpath + "': " + e.getMessage(), e);
            }
        }

        return compareElements(root1, root2, opts, "", new ArrayList<>(), 0, schemaMeta);
    }

    private static List<Element> nodeListToElements(NodeList nl) {
        List<Element> list = new ArrayList<>();
        for (int i = 0; i < nl.getLength(); i++) {
            Node n = nl.item(i);
            if (n.getNodeType() == Node.ELEMENT_NODE) {
                list.add((Element) n);
            }
        }
        return list;
    }

    // Returns Map<String, Object> where values are List<Difference> or String (error message)
    public static Map<String, Object> compareDirs(String dir1, String dir2, CompareOptions opts, boolean recursive) {
        Map<String, Object> results = new LinkedHashMap<>();
        Path dir1Path = Path.of(dir1);
        Path dir2Path = Path.of(dir2);

        Set<String> files1 = collectXmlFiles(dir1Path, recursive);
        Set<String> files2 = collectXmlFiles(dir2Path, recursive);

        Set<String> allFiles = new TreeSet<>();
        allFiles.addAll(files1);
        allFiles.addAll(files2);

        com.xmlcompare.cache.CacheManager cacheManager = null;
        if (opts.cacheFile != null && !opts.cacheFile.isEmpty()) {
            cacheManager = new com.xmlcompare.cache.CacheManager(opts.cacheFile);
        }

        for (String fname : allFiles) {
            if (!files1.contains(fname)) {
                results.put(fname, List.of(new Difference(fname, "missing",
                    "File '" + fname + "' missing in " + dir1)));
            } else if (!files2.contains(fname)) {
                results.put(fname, List.of(new Difference(fname, "missing",
                    "File '" + fname + "' missing in " + dir2)));
            } else {
                File f1 = dir1Path.resolve(fname).toFile();
                File f2 = dir2Path.resolve(fname).toFile();
                if (cacheManager != null && cacheManager.isCachedEqual(f1, f2)) {
                    results.put(fname, new ArrayList<>());
                } else {
                    try {
                        List<Difference> diffs = compareXmlFiles(f1.getAbsolutePath(), f2.getAbsolutePath(), opts);
                        results.put(fname, diffs);
                        if (cacheManager != null) {
                            cacheManager.update(f1, f2, diffs.isEmpty());
                        }
                    } catch (IOException e) {
                        results.put(fname, e.getMessage());
                    }
                }
            }

            if (opts.failFast) {
                Object val = results.get(fname);
                if (val instanceof List<?> list && !list.isEmpty()) break;
                if (val instanceof String) break;
            }
        }

        if (cacheManager != null) {
            try {
                cacheManager.save();
            } catch (IOException ignored) {
                // non-fatal: cache save failure does not affect comparison results
            }
        }

        return results;
    }

    private static Set<String> collectXmlFiles(Path dir, boolean recursive) {
        Set<String> files = new LinkedHashSet<>();
        if (!Files.isDirectory(dir)) return files;
        try {
            if (recursive) {
                try (Stream<Path> stream = Files.walk(dir)) {
                    stream.filter(p -> p.toString().endsWith(".xml") && Files.isRegularFile(p))
                        .forEach(p -> files.add(dir.relativize(p).toString()));
                }
            } else {
                try (Stream<Path> stream = Files.list(dir)) {
                    stream.filter(p -> p.toString().endsWith(".xml") && Files.isRegularFile(p))
                        .forEach(p -> files.add(p.getFileName().toString()));
                }
            }
        } catch (IOException e) {
            // ignore
        }
        return files;
    }

    public static String formatTextReport(List<Difference> diffs, String label1, String label2) {
        return formatTextReport(diffs, label1, label2, false);
    }

    public static String formatTextReport(List<Difference> diffs, String label1, String label2, boolean noColor) {
        boolean color = useAnsiColor(noColor);
        StringBuilder sb = new StringBuilder();
        if (label1 != null && label2 != null) {
            sb.append("Comparing: ").append(label1).append(" vs ").append(label2).append("\n");
            sb.append("-".repeat(60)).append("\n");
        }
        if (diffs == null || diffs.isEmpty()) {
            String msg = "Files are equal";
            sb.append(color ? "\033[92m" + msg + "\033[0m" : msg);
        } else {
            for (Difference diff : diffs) {
                String line = "  [" + diff.kind.toUpperCase() + "] " + diff.msg;
                sb.append(color ? "\033[91m" + line + "\033[0m" : line).append("\n");
                if (diff.expected != null) {
                    sb.append("    Expected : ").append(diff.expected).append("\n");
                }
                if (diff.actual != null) {
                    sb.append("    Actual   : ").append(diff.actual).append("\n");
                }
            }
            // Remove trailing newline to match Python behavior
            if (sb.length() > 0 && sb.charAt(sb.length() - 1) == '\n') {
                sb.setLength(sb.length() - 1);
            }
        }
        return sb.toString();
    }

    @SuppressWarnings("unchecked")
    public static String formatJsonReport(Map<String, Object> allResults) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> output = new LinkedHashMap<>();
            for (Map.Entry<String, Object> entry : allResults.entrySet()) {
                String key = entry.getKey();
                Object val = entry.getValue();
                if (val instanceof String) {
                    Map<String, Object> errMap = new LinkedHashMap<>();
                    errMap.put("error", val);
                    output.put(key, errMap);
                } else {
                    List<Difference> diffs = (List<Difference>) val;
                    Map<String, Object> resultMap = new LinkedHashMap<>();
                    resultMap.put("equal", diffs.isEmpty());
                    resultMap.put("differences", diffs.stream().map(Difference::toMap).collect(Collectors.toList()));
                    output.put(key, resultMap);
                }
            }
            return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(output);
        } catch (Exception e) {
            return "{}";
        }
    }

    @SuppressWarnings("unchecked")
    public static String formatHtmlReport(Map<String, Object> allResults) {
        StringBuilder sb = new StringBuilder();
        sb.append("<html><head><title>XML Compare Report</title>\n");
        sb.append("<style>\n");
        sb.append("body { font-family: monospace; }\n");
        sb.append(".equal { color: green; }\n");
        sb.append(".diff  { color: red;   }\n");
        sb.append(".error { color: orange; }\n");
        sb.append("</style></head><body>\n");
        sb.append("<h1>XML Compare Report</h1>\n");
        for (Map.Entry<String, Object> entry : allResults.entrySet()) {
            String key = entry.getKey();
            Object val = entry.getValue();
            if (val instanceof String) {
                sb.append("<h2 class=\"error\">").append(key).append(": ERROR</h2>\n");
                sb.append("<p class=\"error\">").append(val).append("</p>\n");
            } else {
                List<Difference> diffs = (List<Difference>) val;
                if (diffs.isEmpty()) {
                    sb.append("<h2 class=\"equal\">").append(key).append(": EQUAL</h2>\n");
                } else {
                    sb.append("<h2 class=\"diff\">").append(key).append(": ").append(diffs.size()).append(" difference(s)</h2><ul>\n");
                    for (Difference d : diffs) {
                        String detail = "";
                        if (d.expected != null || d.actual != null) {
                            detail = " &mdash; expected: " + d.expected + ", actual: " + d.actual;
                        }
                        sb.append("<li class=\"diff\">[").append(d.kind.toUpperCase()).append("] ")
                          .append(d.msg).append(detail).append("</li>\n");
                    }
                    sb.append("</ul>\n");
                }
            }
        }
        sb.append("</body></html>");
        return sb.toString();
    }
}
