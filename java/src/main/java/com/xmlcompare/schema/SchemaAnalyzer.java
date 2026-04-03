package com.xmlcompare.schema;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Parses XSD schema files and extracts element metadata for use by the
 * comparison engine.
 *
 * <p>Extracted metadata includes:
 * <ul>
 *   <li>Element names and simple types (e.g. {@code xs:date}, {@code xs:integer})</li>
 *   <li>Cardinality ({@code minOccurs}, {@code maxOccurs})</li>
 *   <li>Ordering constraints ({@code xs:all} → unordered children)</li>
 * </ul>
 *
 * <p>Usage:
 * <pre>
 *   SchemaAnalyzer analyzer = new SchemaAnalyzer();
 *   SchemaMetadata meta = analyzer.analyze("schema.xsd");
 *   Optional&lt;String&gt; type = meta.getXsType("amount", "root/amount");
 * </pre>
 */
public class SchemaAnalyzer {

    private static final String XSD_NS = "http://www.w3.org/2001/XMLSchema";

    /**
     * Parse the XSD at {@code xsdPath} and return its {@link SchemaMetadata}.
     * Returns an empty metadata object if the file cannot be parsed.
     *
     * @param xsdPath path to the XSD file
     * @return non-null {@link SchemaMetadata}
     */
    public SchemaMetadata analyze(String xsdPath) {
        SchemaMetadata meta = new SchemaMetadata();
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            factory.setNamespaceAware(true);
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(new File(xsdPath));
            Element root = doc.getDocumentElement();
            parseSchemaOrGroup(root, meta, "", "");
        } catch (ParserConfigurationException | SAXException | IOException e) {
            // Return empty metadata gracefully
        }
        return meta;
    }

    // ------------------------------------------------------------------
    // Private parsing helpers
    // ------------------------------------------------------------------

    private void parseSchemaOrGroup(Element node, SchemaMetadata meta,
                                    String parentPath, String parentTag) {
        String localName = node.getLocalName();
        if (localName == null) return;

        switch (localName) {
            case "schema" -> {
                NodeList children = node.getChildNodes();
                for (int i = 0; i < children.getLength(); i++) {
                    Node child = children.item(i);
                    if (child instanceof Element e && "element".equals(e.getLocalName())) {
                        parseElement(e, meta, "");
                    }
                }
            }
            case "all" -> {
                if (!parentPath.isEmpty()) {
                    meta.markUnordered(parentPath);
                }
                NodeList children = node.getChildNodes();
                for (int i = 0; i < children.getLength(); i++) {
                    Node child = children.item(i);
                    if (child instanceof Element e && "element".equals(e.getLocalName())) {
                        parseElement(e, meta, parentPath);
                    }
                }
            }
            case "sequence", "choice" -> {
                NodeList children = node.getChildNodes();
                for (int i = 0; i < children.getLength(); i++) {
                    Node child = children.item(i);
                    if (child instanceof Element e) {
                        String childLocal = e.getLocalName();
                        if ("element".equals(childLocal)) {
                            parseElement(e, meta, parentPath);
                        } else if ("sequence".equals(childLocal)
                            || "all".equals(childLocal)
                            || "choice".equals(childLocal)) {
                            parseSchemaOrGroup(e, meta, parentPath, parentTag);
                        }
                    }
                }
            }
            case "complexType", "complexContent", "simpleContent",
                 "extension", "restriction" -> {
                NodeList children = node.getChildNodes();
                for (int i = 0; i < children.getLength(); i++) {
                    Node child = children.item(i);
                    if (child instanceof Element e) {
                        String childLocal = e.getLocalName();
                        if ("sequence".equals(childLocal)
                            || "all".equals(childLocal)
                            || "choice".equals(childLocal)
                            || "complexContent".equals(childLocal)
                            || "simpleContent".equals(childLocal)
                            || "extension".equals(childLocal)
                            || "restriction".equals(childLocal)) {
                            parseSchemaOrGroup(e, meta, parentPath, parentTag);
                        }
                    }
                }
            }
            default -> { /* ignore unknown nodes */ }
        }
    }

    private void parseElement(Element elemNode, SchemaMetadata meta, String parentPath) {
        String name = elemNode.getAttribute("name");
        if (name == null || name.isEmpty()) return;

        String path = parentPath.isEmpty() ? name : parentPath + "/" + name;
        int minOccurs = parseMinOccurs(elemNode.getAttribute("minOccurs"));
        Integer maxOccurs = parseMaxOccurs(elemNode.getAttribute("maxOccurs"));
        String xsType = normalizeType(elemNode.getAttribute("type"));

        // Resolve inlined simpleType/restriction
        if (xsType == null || xsType.isEmpty()) {
            xsType = findInlineSimpleType(elemNode);
        }

        SchemaMetadata.ElementInfo info = new SchemaMetadata.ElementInfo(
            name, minOccurs, maxOccurs, xsType, minOccurs > 0);
        meta.putElement(name, path, info);

        // Recurse into complexType
        NodeList children = elemNode.getChildNodes();
        for (int i = 0; i < children.getLength(); i++) {
            Node child = children.item(i);
            if (child instanceof Element e && "complexType".equals(e.getLocalName())) {
                parseSchemaOrGroup(e, meta, path, name);
            }
        }
    }

    private String findInlineSimpleType(Element elemNode) {
        NodeList children = elemNode.getChildNodes();
        for (int i = 0; i < children.getLength(); i++) {
            Node child = children.item(i);
            if (child instanceof Element st && "simpleType".equals(st.getLocalName())) {
                NodeList stChildren = st.getChildNodes();
                for (int j = 0; j < stChildren.getLength(); j++) {
                    Node stChild = stChildren.item(j);
                    if (stChild instanceof Element r && "restriction".equals(r.getLocalName())) {
                        String base = ((Element) stChild).getAttribute("base");
                        if (base != null && !base.isEmpty()) {
                            return normalizeType(base);
                        }
                    }
                }
            }
        }
        return null;
    }

    private static int parseMinOccurs(String value) {
        if (value == null || value.isEmpty()) return 1;
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return 1;
        }
    }

    private static Integer parseMaxOccurs(String value) {
        if (value == null || value.isEmpty()) return 1;
        if ("unbounded".equals(value)) return null;
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return 1;
        }
    }

    private static String normalizeType(String type) {
        if (type == null || type.isEmpty()) return null;
        return type; // keep as-is, e.g. "xs:date", "xs:integer"
    }
}
