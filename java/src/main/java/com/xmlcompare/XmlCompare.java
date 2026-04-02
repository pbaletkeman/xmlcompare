package com.xmlcompare;

import com.fasterxml.jackson.databind.ObjectMapper;
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
        return compareElements(elem1, elem2, opts, path, diffs, 0);
    }

    public static List<Difference> compareElements(Element elem1, Element elem2, CompareOptions opts, String path, List<Difference> diffs, int depth) {
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

        // Text content (skip if structure_only)
        if (!opts.structureOnly) {
            String text1 = normalizeText(getDirectTextContent(elem1));
            String text2 = normalizeText(getDirectTextContent(elem2));
            if (!valuesEqual(text1, text2, opts)) {
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

            if (opts.unordered) {
                compareUnordered(children1, children2, opts, currentPath, diffs, depth);
            } else {
                compareOrdered(children1, children2, opts, currentPath, diffs, depth);
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
        compareOrdered(children1, children2, opts, path, diffs, 0);
    }

    public static void compareOrdered(List<Element> children1, List<Element> children2, CompareOptions opts, String path, List<Difference> diffs, int depth) {
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
                compareElements(children1.get(i), children2.get(i), opts, childPath, diffs, depth + 1);
                if (opts.failFast && !diffs.isEmpty()) return;
            }
        }
    }

    public static void compareUnordered(List<Element> children1, List<Element> children2, CompareOptions opts, String path, List<Difference> diffs) {
        compareUnordered(children1, children2, opts, path, diffs, 0);
    }

    public static void compareUnordered(List<Element> children1, List<Element> children2, CompareOptions opts, String path, List<Difference> diffs, int depth) {
        Map<String, List<Element>> groups1 = new LinkedHashMap<>();
        Map<String, List<Element>> groups2 = new LinkedHashMap<>();

        for (Element c : children1) {
            groups1.computeIfAbsent(getTag(c, opts), k -> new ArrayList<>()).add(c);
        }
        for (Element c : children2) {
            groups2.computeIfAbsent(getTag(c, opts), k -> new ArrayList<>()).add(c);
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
                    compareElements(elems1.get(i), elems2.get(i), opts, childPath, diffs, depth + 1);
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

    public static List<Difference> compareXmlFiles(String file1, String file2, CompareOptions opts) throws IOException {
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

        if (opts.filterXpath != null && !opts.filterXpath.isEmpty()) {
            try {
                XPath xpath = XPathFactory.newInstance().newXPath();
                NodeList nl1 = (NodeList) xpath.evaluate(opts.filterXpath, root1, XPathConstants.NODESET);
                NodeList nl2 = (NodeList) xpath.evaluate(opts.filterXpath, root2, XPathConstants.NODESET);
                List<Element> elems1 = nodeListToElements(nl1);
                List<Element> elems2 = nodeListToElements(nl2);
                List<Difference> diffs = new ArrayList<>();
                compareOrdered(elems1, elems2, opts, "", diffs);
                return diffs;
            } catch (XPathExpressionException e) {
                throw new IOException("Invalid filter XPath '" + opts.filterXpath + "': " + e.getMessage(), e);
            }
        }

        return compareElements(root1, root2, opts, "", new ArrayList<>());
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

        for (String fname : allFiles) {
            if (!files1.contains(fname)) {
                results.put(fname, List.of(new Difference(fname, "missing",
                    "File '" + fname + "' missing in " + dir1)));
            } else if (!files2.contains(fname)) {
                results.put(fname, List.of(new Difference(fname, "missing",
                    "File '" + fname + "' missing in " + dir2)));
            } else {
                try {
                    results.put(fname, compareXmlFiles(
                        dir1Path.resolve(fname).toString(),
                        dir2Path.resolve(fname).toString(), opts));
                } catch (IOException e) {
                    results.put(fname, e.getMessage());
                }
            }

            if (opts.failFast) {
                Object val = results.get(fname);
                if (val instanceof List<?> list && !list.isEmpty()) break;
                if (val instanceof String) break;
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
        StringBuilder sb = new StringBuilder();
        if (label1 != null && label2 != null) {
            sb.append("Comparing: ").append(label1).append(" vs ").append(label2).append("\n");
            sb.append("-".repeat(60)).append("\n");
        }
        if (diffs == null || diffs.isEmpty()) {
            sb.append("Files are equal");
        } else {
            for (Difference diff : diffs) {
                sb.append("  [").append(diff.kind.toUpperCase()).append("] ").append(diff.msg).append("\n");
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
