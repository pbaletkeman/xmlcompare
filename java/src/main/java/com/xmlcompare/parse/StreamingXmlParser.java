package com.xmlcompare.parse;

import com.xmlcompare.CompareOptions;
import com.xmlcompare.Difference;
import com.xmlcompare.XmlCompare;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Streaming XML parser using StAX for memory-efficient processing of large files.
 * Memory usage is proportional to tree depth, not total document size.
 */
public class StreamingXmlParser {

    private static XMLInputFactory createSecureFactory() {
        XMLInputFactory factory = XMLInputFactory.newInstance();
        // Disable external entity resolution to prevent XXE
        factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
        factory.setProperty(XMLInputFactory.SUPPORT_DTD, false);
        return factory;
    }

    /**
     * Compare two XML files using StAX streaming parser.
     * Falls back to DOM comparison for unordered mode (requires full tree).
     */
    public static List<Difference> compareXmlFilesStreaming(
            File file1, File file2, CompareOptions options) throws Exception {

        if (options.unordered || options.schema != null) {
            // Unordered and schema-aware comparison require the full DOM
            return XmlCompare.compareXmlFiles(
                    file1.getAbsolutePath(), file2.getAbsolutePath(), options);
        }

        XMLInputFactory factory = createSecureFactory();
        try (FileInputStream fis1 = new FileInputStream(file1);
             FileInputStream fis2 = new FileInputStream(file2)) {

            XMLStreamReader reader1 = factory.createXMLStreamReader(fis1);
            XMLStreamReader reader2 = factory.createXMLStreamReader(fis2);
            try {
                return streamCompare(reader1, reader2, options);
            } finally {
                reader1.close();
                reader2.close();
            }
        }
    }

    private static List<Difference> streamCompare(
            XMLStreamReader r1, XMLStreamReader r2, CompareOptions opts) throws XMLStreamException {

        List<Difference> diffs = new ArrayList<>();
        Deque<String> pathStack = new ArrayDeque<>();
        StringBuilder text1 = new StringBuilder();
        StringBuilder text2 = new StringBuilder();
        int diffCount = 0;

        // Advance both readers past document start to first meaningful event
        while (r1.hasNext() && r1.getEventType() != XMLStreamConstants.START_ELEMENT) {
            r1.next();
        }
        while (r2.hasNext() && r2.getEventType() != XMLStreamConstants.START_ELEMENT) {
            r2.next();
        }

        while (r1.hasNext() && r2.hasNext()) {
            int e1 = r1.getEventType();
            int e2 = r2.getEventType();

            if (e1 == XMLStreamConstants.START_ELEMENT && e2 == XMLStreamConstants.START_ELEMENT) {
                text1.setLength(0);
                text2.setLength(0);

                String tag1 = resolveTag(r1, opts);
                String tag2 = resolveTag(r2, opts);
                String currentPath = buildPath(pathStack, tag1);

                if (opts.maxDepth != null && pathStack.size() >= opts.maxDepth) {
                    skipToMatchingEnd(r1);
                    skipToMatchingEnd(r2);
                    advancePastEnd(r1);
                    advancePastEnd(r2);
                    continue;
                }

                if (XmlCompare.shouldSkip(currentPath, tag1, opts)) {
                    skipToMatchingEnd(r1);
                    skipToMatchingEnd(r2);
                    advancePastEnd(r1);
                    advancePastEnd(r2);
                    continue;
                }

                if (!tag1.equals(tag2)) {
                    diffs.add(new Difference(currentPath, "tag",
                            "Tag mismatch: expected <" + tag1 + "> but found <" + tag2 + ">",
                            tag1, tag2));
                    if (opts.failFast) return diffs;
                    diffCount++;
                }

                if (!opts.ignoreAttributes && !opts.structureOnly) {
                    compareAttributes(r1, r2, currentPath, opts, diffs);
                    if (opts.failFast && !diffs.isEmpty() && diffs.size() > diffCount) return diffs;
                    diffCount = diffs.size();
                }

                pathStack.push(tag1);
                r1.next();
                r2.next();

            } else if (e1 == XMLStreamConstants.END_ELEMENT && e2 == XMLStreamConstants.END_ELEMENT) {
                String normText1 = XmlCompare.normalizeText(text1.toString());
                String normText2 = XmlCompare.normalizeText(text2.toString());
                String currentPath = currentPath(pathStack);

                if (!opts.structureOnly && !normText1.equals(normText2)) {
                    if (!XmlCompare.valuesEqual(normText1, normText2, opts)) {
                        diffs.add(new Difference(currentPath, "text",
                                "Text mismatch at <" + r1.getLocalName() + ">",
                                normText1, normText2));
                        if (opts.failFast) return diffs;
                    }
                }

                if (!pathStack.isEmpty()) pathStack.pop();
                text1.setLength(0);
                text2.setLength(0);
                r1.next();
                r2.next();

            } else if (e1 == XMLStreamConstants.CHARACTERS || e1 == XMLStreamConstants.CDATA) {
                text1.append(r1.getText());
                r1.next();
                if (e2 == XMLStreamConstants.CHARACTERS || e2 == XMLStreamConstants.CDATA) {
                    text2.append(r2.getText());
                    r2.next();
                }
            } else if (e2 == XMLStreamConstants.CHARACTERS || e2 == XMLStreamConstants.CDATA) {
                text2.append(r2.getText());
                r2.next();
            } else if (e1 == XMLStreamConstants.END_DOCUMENT || e2 == XMLStreamConstants.END_DOCUMENT) {
                break;
            } else {
                // Skip comments, processing instructions, etc.
                r1.next();
                r2.next();
            }
        }

        // If one file has more elements than the other
        while (r1.hasNext() && r1.getEventType() != XMLStreamConstants.END_DOCUMENT) {
            if (r1.getEventType() == XMLStreamConstants.START_ELEMENT) {
                diffs.add(new Difference(currentPath(pathStack), "missing",
                        "Element <" + resolveTag(r1, opts) + "> present in file1 but not in file2"));
                if (opts.failFast) return diffs;
            }
            r1.next();
        }
        while (r2.hasNext() && r2.getEventType() != XMLStreamConstants.END_DOCUMENT) {
            if (r2.getEventType() == XMLStreamConstants.START_ELEMENT) {
                diffs.add(new Difference(currentPath(pathStack), "extra",
                        "Element <" + resolveTag(r2, opts) + "> present in file2 but not in file1"));
                if (opts.failFast) return diffs;
            }
            r2.next();
        }

        return diffs;
    }

    private static String resolveTag(XMLStreamReader r, CompareOptions opts) {
        String local = r.getLocalName();
        if (!opts.ignoreNamespaces) {
            String ns = r.getNamespaceURI();
            if (ns != null && !ns.isEmpty()) {
                return "{" + ns + "}" + local;
            }
        }
        return local;
    }

    private static String buildPath(Deque<String> stack, String tag) {
        if (stack.isEmpty()) return tag;
        return String.join("/", new ArrayList<>(stack)) + "/" + tag;
    }

    private static String currentPath(Deque<String> stack) {
        if (stack.isEmpty()) return "";
        return String.join("/", new ArrayList<>(stack));
    }

    private static void compareAttributes(
            XMLStreamReader r1, XMLStreamReader r2, String path,
            CompareOptions opts, List<Difference> diffs) {

        Map<String, String> attrs1 = readAttributes(r1, opts);
        Map<String, String> attrs2 = readAttributes(r2, opts);

        for (Map.Entry<String, String> entry : attrs1.entrySet()) {
            String key = entry.getKey();
            String val1 = entry.getValue();
            if (!attrs2.containsKey(key)) {
                diffs.add(new Difference(path + "/@" + key, "attr",
                        "Attribute '" + key + "' missing in file2", val1, null));
            } else if (!XmlCompare.valuesEqual(val1, attrs2.get(key), opts)) {
                diffs.add(new Difference(path + "/@" + key, "attr",
                        "Attribute '" + key + "' differs",
                        val1, attrs2.get(key)));
            }
        }
        for (String key : attrs2.keySet()) {
            if (!attrs1.containsKey(key)) {
                diffs.add(new Difference(path + "/@" + key, "attr",
                        "Attribute '" + key + "' extra in file2", null, attrs2.get(key)));
            }
        }
    }

    private static Map<String, String> readAttributes(XMLStreamReader r, CompareOptions opts) {
        Map<String, String> map = new LinkedHashMap<>();
        for (int i = 0; i < r.getAttributeCount(); i++) {
            String ns = r.getAttributeNamespace(i);
            String local = r.getAttributeLocalName(i);
            String key = (!opts.ignoreNamespaces && ns != null && !ns.isEmpty())
                    ? "{" + ns + "}" + local : local;
            map.put(key, r.getAttributeValue(i));
        }
        return map;
    }

    private static void skipToMatchingEnd(XMLStreamReader r) throws XMLStreamException {
        int depth = 1;
        while (r.hasNext() && depth > 0) {
            int event = r.next();
            if (event == XMLStreamConstants.START_ELEMENT) depth++;
            else if (event == XMLStreamConstants.END_ELEMENT) depth--;
        }
    }

    private static void advancePastEnd(XMLStreamReader r) throws XMLStreamException {
        if (r.hasNext()) r.next();
    }

    /**
     * Get statistics about a file's suitability for streaming.
     */
    public static StreamingStats getStreamStats(File file) throws Exception {
        long fileSize = file.length();
        long fileSizeMB = fileSize / (1024 * 1024);
        long estimatedDomMemory = fileSize * 10 / (1024 * 1024);

        ElementCountingHandler handler = new ElementCountingHandler();
        parseWithHandler(file, handler);

        StreamingStats stats = new StreamingStats();
        stats.fileSizeMB = fileSizeMB;
        stats.estimatedDomMemoryMB = estimatedDomMemory;
        stats.elementCount = handler.elementCount;
        stats.suitableForStreaming = fileSizeMB > 50;
        return stats;
    }

    private static void parseWithHandler(File file, DefaultHandler handler) throws Exception {
        SAXParserFactory factory = SAXParserFactory.newInstance();
        SAXParser parser = factory.newSAXParser();
        parser.parse(file, handler);
    }

    public static class StreamingStats {
        public long fileSizeMB;
        public long estimatedDomMemoryMB;
        public long elementCount;
        public boolean suitableForStreaming;

        @Override
        public String toString() {
            return String.format(
                    "File: %dMB | Est. DOM Memory: %dMB | Elements: %d | Streaming: %s",
                    fileSizeMB, estimatedDomMemoryMB, elementCount,
                    suitableForStreaming ? "RECOMMENDED" : "not needed");
        }
    }

    private static class ElementCountingHandler extends DefaultHandler {
        long elementCount = 0;

        @Override
        public void startElement(String uri, String localName, String qName, Attributes attributes)
                throws SAXException {
            elementCount++;
        }
    }
}
