package com.xmlcompare;

import java.util.ArrayList;
import java.util.List;

public class CompareOptions {
    public double tolerance = 0.0;
    public boolean ignoreCase = false;
    public boolean unordered = false;
    public boolean ignoreNamespaces = false;
    public boolean ignoreAttributes = false;
    public List<String> skipKeys = new ArrayList<>();
    public String skipPattern = null;
    public String filterXpath = null;
    public String outputFormat = "text";
    public String outputFile = null;
    public boolean summary = false;
    public boolean verbose = false;
    public boolean quiet = false;
    public boolean failFast = false;
    public boolean structureOnly = false;
    public Integer maxDepth = null;
    // Phase 1 additions
    /** Path to XSD schema file for pre-validation and type hints. */
    public String schema = null;
    /** Enable type-aware comparison using schema hints. */
    public boolean typeAware = false;
    /** List of fully-qualified plugin class names to load. */
    public List<String> plugins = new ArrayList<>();
}
