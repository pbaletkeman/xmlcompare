package com.xmlcompare.schema;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

/**
 * Aggregated XSD metadata returned by {@link SchemaAnalyzer}.
 *
 * <p>Holds per-element information such as XSD type, cardinality, and ordering
 * constraints, indexed both by bare element name and by full element path.
 */
public class SchemaMetadata {

    // -----------------------------------------------------------------------
    // Inner class
    // -----------------------------------------------------------------------

    /**
     * Metadata about a single XSD element declaration.
     */
    public static class ElementInfo {

        /** Element tag name. */
        public final String name;
        /** Minimum occurrences (default: 1). */
        public final int minOccurs;
        /** Maximum occurrences ({@code null} = unbounded, default: 1). */
        public final Integer maxOccurs;
        /** XSD simple type, e.g. {@code "xs:date"}, {@code "xs:integer"}, or {@code null}. */
        public final String xsType;
        /** {@code true} if minOccurs &gt; 0. */
        public final boolean required;

        public ElementInfo(String name, int minOccurs, Integer maxOccurs,
                           String xsType, boolean required) {
            this.name = name;
            this.minOccurs = minOccurs;
            this.maxOccurs = maxOccurs;
            this.xsType = xsType;
            this.required = required;
        }

        @Override
        public String toString() {
            return "ElementInfo{name=" + name + ", type=" + xsType
                + ", minOccurs=" + minOccurs + ", maxOccurs=" + maxOccurs + "}";
        }
    }

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /** element name → ElementInfo (for globally named elements) */
    private final Map<String, ElementInfo> elements = new HashMap<>();

    /** full path (parent/child) → ElementInfo */
    private final Map<String, ElementInfo> pathElements = new HashMap<>();

    /** paths whose children are unordered (xs:all) */
    private final Set<String> unorderedPaths = new java.util.HashSet<>();

    // -----------------------------------------------------------------------
    // Package-private mutators (used by SchemaAnalyzer)
    // -----------------------------------------------------------------------

    void putElement(String name, String path, ElementInfo info) {
        elements.put(name, info);
        pathElements.put(path, info);
    }

    void markUnordered(String parentPath) {
        unorderedPaths.add(parentPath);
    }

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------

    /**
     * Look up element metadata by path first, then by bare name.
     *
     * @param name element tag name
     * @param path full element path (e.g. {@code "root/child"})
     * @return {@link Optional} containing the info, or empty if not found
     */
    public Optional<ElementInfo> getElementInfo(String name, String path) {
        if (path != null && !path.isEmpty() && pathElements.containsKey(path)) {
            return Optional.of(pathElements.get(path));
        }
        return Optional.ofNullable(elements.get(name));
    }

    /**
     * Return the XSD simple type string for the element, or {@code null}.
     *
     * @param name element tag name
     * @param path full element path
     * @return XSD type string (e.g. {@code "xs:date"}) or {@code null}
     */
    public String getXsType(String name, String path) {
        return getElementInfo(name, path).map(i -> i.xsType).orElse(null);
    }

    /**
     * Return {@code true} if the children of the element at {@code parentPath}
     * are declared as {@code xs:all} (i.e. may appear in any order).
     *
     * @param parentPath full path of the parent element
     * @return {@code true} if children are unordered
     */
    public boolean isUnorderedChildren(String parentPath) {
        return unorderedPaths.contains(parentPath);
    }

    /**
     * Return {@code true} if this metadata contains at least one element entry.
     *
     * @return {@code true} if non-empty
     */
    public boolean isEmpty() {
        return elements.isEmpty();
    }

    /**
     * Return the map of all globally-named elements.
     * Intended for testing and introspection.
     *
     * @return unmodifiable map
     */
    public Map<String, ElementInfo> getElements() {
        return Map.copyOf(elements);
    }
}
