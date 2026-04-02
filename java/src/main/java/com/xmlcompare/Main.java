package com.xmlcompare;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;

@Command(name = "xmlcompare",
    description = "Compare XML files or directories.",
    mixinStandardHelpOptions = true,
    version = "xmlcompare 1.0.0")
public class Main implements Callable<Integer> {

    @Option(names = "--files", description = "Two XML files to compare", arity = "2", paramLabel = "FILE")
    private String[] files;

    @Option(names = "--dirs", description = "Two directories to compare", arity = "2", paramLabel = "DIR")
    private String[] dirs;

    @Option(names = "--recursive", description = "Recurse into subdirectories (with --dirs)")
    private boolean recursive;

    @Option(names = "--config", description = "Config file (JSON or YAML)", paramLabel = "FILE")
    private File config;

    @Option(names = "--tolerance", description = "Numeric tolerance", paramLabel = "FLOAT")
    private Double tolerance;

    @Option(names = "--ignore-case", description = "Case-insensitive text comparison")
    private boolean ignoreCase;

    @Option(names = "--unordered", description = "Compare children in any order")
    private boolean unordered;

    @Option(names = "--ignore-namespaces", description = "Ignore XML namespaces")
    private boolean ignoreNamespaces;

    @Option(names = "--ignore-attributes", description = "Ignore XML attributes")
    private boolean ignoreAttributes;

    @Option(names = "--structure-only", description = "Compare only XML structure, ignore text and attribute values")
    private boolean structureOnly;

    @Option(names = "--max-depth", description = "Maximum depth for comparison", paramLabel = "INT")
    private Integer maxDepth;

    @Option(names = "--skip-keys", description = "Paths or //tags to skip", split = ",", paramLabel = "PATH")
    private List<String> skipKeys;

    @Option(names = "--skip-pattern", description = "Regex pattern of tags to skip", paramLabel = "REGEX")
    private String skipPattern;

    @Option(names = "--filter", description = "XPath filter", paramLabel = "XPATH")
    private String filter;

    @Option(names = "--output-format", description = "Output format: text, json, html", paramLabel = "FORMAT")
    private String outputFormat;

    @Option(names = "--output-file", description = "Write output to file", paramLabel = "FILE")
    private File outputFile;

    @Option(names = "--summary", description = "Print summary only")
    private boolean summary;

    @Option(names = "--verbose", description = "Verbose output")
    private boolean verbose;

    @Option(names = "--quiet", description = "Suppress output")
    private boolean quiet;

    @Option(names = "--fail-fast", description = "Stop on first difference")
    private boolean failFast;

    public static void main(String[] args) {
        int exitCode = new CommandLine(new Main()).execute(args);
        System.exit(exitCode);
    }

    @Override
    public Integer call() {
        CompareOptions opts = new CompareOptions();

        // Load config file first, then override with CLI options
        if (config != null) {
            try {
                loadConfig(opts, config);
            } catch (IOException e) {
                System.err.println("Error loading config: " + e.getMessage());
                return 2;
            }
        }

        // CLI overrides
        if (tolerance != null) opts.tolerance = tolerance;
        if (ignoreCase) opts.ignoreCase = true;
        if (unordered) opts.unordered = true;
        if (ignoreNamespaces) opts.ignoreNamespaces = true;
        if (ignoreAttributes) opts.ignoreAttributes = true;
        if (skipKeys != null && !skipKeys.isEmpty()) opts.skipKeys = skipKeys;
        if (skipPattern != null) opts.skipPattern = skipPattern;
        if (filter != null) opts.filterXpath = filter;
        if (outputFormat != null) opts.outputFormat = outputFormat;
        if (outputFile != null) opts.outputFile = outputFile.getPath();
        if (summary) opts.summary = true;
        if (verbose) opts.verbose = true;
        if (quiet) opts.quiet = true;
        if (failFast) opts.failFast = true;
        if (structureOnly) opts.structureOnly = true;
        if (maxDepth != null) opts.maxDepth = maxDepth;

        try {
            if (files != null) {
                return compareFiles(files[0], files[1], opts);
            } else if (dirs != null) {
                return compareDirs(dirs[0], dirs[1], opts);
            } else {
                System.err.println("Error: specify --files or --dirs");
                return 2;
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            return 2;
        }
    }

    private int compareFiles(String file1, String file2, CompareOptions opts) {
        try {
            List<Difference> diffs = XmlCompare.compareXmlFiles(file1, file2, opts);
            Map<String, Object> allResults = new LinkedHashMap<>();
            allResults.put(file1 + " vs " + file2, diffs);
            String report = generateReport(allResults, opts, file1, file2);
            writeOutput(report, opts);
            return diffs.isEmpty() ? 0 : 1;
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
            return 2;
        }
    }

    private int compareDirs(String dir1, String dir2, CompareOptions opts) {
        Map<String, Object> results = XmlCompare.compareDirs(dir1, dir2, opts, recursive);
        String report = generateReport(results, opts, null, null);
        writeOutput(report, opts);
        boolean hasDiffs = results.values().stream().anyMatch(v -> {
            if (v instanceof String) return true;
            if (v instanceof List<?> list) return !list.isEmpty();
            return false;
        });
        return hasDiffs ? 1 : 0;
    }

    @SuppressWarnings("unchecked")
    private String generateReport(Map<String, Object> allResults, CompareOptions opts, String label1, String label2) {
        if (opts.summary) {
            StringBuilder sb = new StringBuilder();
            int equalCount = 0, diffCount = 0, errorCount = 0;
            for (Object val : allResults.values()) {
                if (val instanceof String) errorCount++;
                else if (((List<Difference>) val).isEmpty()) equalCount++;
                else diffCount++;
            }
            sb.append("Summary: ").append(equalCount).append(" equal, ")
              .append(diffCount).append(" with differences, ")
              .append(errorCount).append(" errors");
            return sb.toString();
        }

        return switch (opts.outputFormat) {
            case "json" -> XmlCompare.formatJsonReport(allResults);
            case "html" -> XmlCompare.formatHtmlReport(allResults);
            default -> {
                if (label1 != null && label2 != null && allResults.size() == 1) {
                    Object val = allResults.values().iterator().next();
                    List<Difference> diffs = val instanceof List ? (List<Difference>) val : Collections.emptyList();
                    yield XmlCompare.formatTextReport(diffs, label1, label2);
                } else {
                    StringBuilder sb = new StringBuilder();
                    for (Map.Entry<String, Object> entry : allResults.entrySet()) {
                        Object val = entry.getValue();
                        if (val instanceof String) {
                            sb.append(entry.getKey()).append(": ERROR - ").append(val).append("\n");
                        } else {
                            List<Difference> diffs = (List<Difference>) val;
                            sb.append(XmlCompare.formatTextReport(diffs, entry.getKey(), null)).append("\n");
                        }
                    }
                    yield sb.toString().stripTrailing();
                }
            }
        };
    }

    private void writeOutput(String report, CompareOptions opts) {
        if (opts.quiet) return;
        if (opts.outputFile != null) {
            try {
                Files.writeString(java.nio.file.Path.of(opts.outputFile), report + "\n");
            } catch (IOException e) {
                System.err.println("Error writing output file: " + e.getMessage());
            }
        } else {
            System.out.println(report);
        }
    }

    @SuppressWarnings("unchecked")
    private void loadConfig(CompareOptions opts, File configFile) throws IOException {
        String name = configFile.getName().toLowerCase();
        ObjectMapper mapper;
        if (name.endsWith(".yaml") || name.endsWith(".yml")) {
            mapper = new ObjectMapper(new YAMLFactory());
        } else {
            mapper = new ObjectMapper();
        }
        Map<String, Object> cfg = mapper.readValue(configFile, Map.class);
        if (cfg.containsKey("tolerance")) opts.tolerance = ((Number) cfg.get("tolerance")).doubleValue();
        if (cfg.containsKey("ignore_case")) opts.ignoreCase = (Boolean) cfg.get("ignore_case");
        if (cfg.containsKey("unordered")) opts.unordered = (Boolean) cfg.get("unordered");
        if (cfg.containsKey("ignore_namespaces")) opts.ignoreNamespaces = (Boolean) cfg.get("ignore_namespaces");
        if (cfg.containsKey("ignore_attributes")) opts.ignoreAttributes = (Boolean) cfg.get("ignore_attributes");
        if (cfg.containsKey("skip_keys")) opts.skipKeys = (List<String>) cfg.get("skip_keys");
        if (cfg.containsKey("skip_pattern")) opts.skipPattern = (String) cfg.get("skip_pattern");
        if (cfg.containsKey("filter_xpath")) opts.filterXpath = (String) cfg.get("filter_xpath");
        if (cfg.containsKey("output_format")) opts.outputFormat = (String) cfg.get("output_format");
        if (cfg.containsKey("fail_fast")) opts.failFast = (Boolean) cfg.get("fail_fast");
        if (cfg.containsKey("structure_only")) opts.structureOnly = (Boolean) cfg.get("structure_only");
        if (cfg.containsKey("max_depth")) opts.maxDepth = ((Number) cfg.get("max_depth")).intValue();
    }
}
