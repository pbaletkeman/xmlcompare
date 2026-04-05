package com.xmlcompare.interactive;

import com.xmlcompare.CompareOptions;
import com.xmlcompare.Difference;
import com.xmlcompare.XmlCompare;
import com.xmlcompare.parallel.ParallelComparison;
import com.xmlcompare.parse.StreamingXmlParser;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

/**
 * Console-based interactive mode for xmlcompare.
 * Provides a menu-driven interface for file selection, option configuration, and result browsing.
 */
public class InteractiveMode {

    private final Scanner scanner = new Scanner(System.in);
    private String file1 = null;
    private String file2 = null;
    private String dir1 = null;
    private String dir2 = null;
    private CompareOptions opts = new CompareOptions();
    private List<Difference> lastResult = null;
    private boolean compareMode = true; // true = files, false = dirs

    public static void run() {
        new InteractiveMode().mainLoop();
    }

    private void mainLoop() {
        printBanner();
        while (true) {
            printMenu();
            String choice = readLine("Choice").trim();
            switch (choice) {
                case "1" -> selectFiles();
                case "2" -> selectDirs();
                case "3" -> configureOptions();
                case "4" -> runComparison();
                case "5" -> browseResults();
                case "6" -> exportResults();
                case "7" -> showStats();
                case "0", "q", "quit", "exit" -> {
                    println("Goodbye.");
                    return;
                }
                default -> println("Unknown option. Enter 1-7 or 0 to quit.");
            }
        }
    }

    private void printBanner() {
        println("╔══════════════════════════════════════╗");
        println("║        xmlcompare interactive        ║");
        println("╚══════════════════════════════════════╝");
    }

    private void printMenu() {
        println("");
        println("Mode: " + (compareMode ? "files" : "dirs") +
                " | Stream: " + opts.streaming + " | Parallel: " + opts.parallel +
                " | Unordered: " + opts.unordered);
        if (compareMode) {
            println("File1: " + (file1 != null ? file1 : "(not set)"));
            println("File2: " + (file2 != null ? file2 : "(not set)"));
        } else {
            println("Dir1:  " + (dir1 != null ? dir1 : "(not set)"));
            println("Dir2:  " + (dir2 != null ? dir2 : "(not set)"));
        }
        if (lastResult != null) {
            println("Last:  " + lastResult.size() + " difference(s)");
        }
        println("─────────────────────────────────────");
        println("  1) Select XML files");
        println("  2) Select directories");
        println("  3) Configure options");
        println("  4) Run comparison");
        println("  5) Browse results");
        println("  6) Export results");
        println("  7) Show parallel/stream stats");
        println("  0) Quit");
    }

    private void selectFiles() {
        compareMode = true;
        file1 = readPathLine("File 1");
        file2 = readPathLine("File 2");
    }

    private void selectDirs() {
        compareMode = false;
        dir1 = readPathLine("Directory 1");
        dir2 = readPathLine("Directory 2");
    }

    private void configureOptions() {
        println("Current options:");
        println("  1) Tolerance:         " + opts.tolerance);
        println("  2) Ignore case:       " + opts.ignoreCase);
        println("  3) Unordered:         " + opts.unordered);
        println("  4) Ignore namespaces: " + opts.ignoreNamespaces);
        println("  5) Ignore attributes: " + opts.ignoreAttributes);
        println("  6) Structure only:    " + opts.structureOnly);
        println("  7) Streaming mode:    " + opts.streaming);
        println("  8) Parallel mode:     " + opts.parallel);
        println("  9) Thread count:      " + opts.parallelThreads);
        println("  10) XPath filter:     " + (opts.filterXpath != null ? opts.filterXpath : "(none)"));
        println("  11) Skip keys:        " + opts.skipKeys);
        println("  0) Back");
        String choice = readLine("Option").trim();
        switch (choice) {
            case "1" -> {
                String val = readLine("Tolerance (e.g. 0.01)");
                try { opts.tolerance = Double.parseDouble(val); } catch (NumberFormatException e) {
                    println("Invalid number.");
                }
            }
            case "2" -> opts.ignoreCase = !opts.ignoreCase;
            case "3" -> opts.unordered = !opts.unordered;
            case "4" -> opts.ignoreNamespaces = !opts.ignoreNamespaces;
            case "5" -> opts.ignoreAttributes = !opts.ignoreAttributes;
            case "6" -> opts.structureOnly = !opts.structureOnly;
            case "7" -> opts.streaming = !opts.streaming;
            case "8" -> opts.parallel = !opts.parallel;
            case "9" -> {
                String val = readLine("Thread count (0 = auto)");
                try { opts.parallelThreads = Integer.parseInt(val); } catch (NumberFormatException e) {
                    println("Invalid number.");
                }
            }
            case "10" -> {
                String val = readLine("XPath filter (blank to clear)").trim();
                opts.filterXpath = val.isEmpty() ? null : val;
            }
            case "11" -> {
                String keys = readLine("Skip keys (comma-separated, blank to clear)");
                opts.skipKeys = keys.isBlank() ? new java.util.ArrayList<>()
                        : java.util.Arrays.asList(keys.split(","));
            }
        }
        println("Options updated.");
    }

    private void runComparison() {
        if (compareMode) {
            runFileComparison();
        } else {
            runDirComparison();
        }
    }

    private void runFileComparison() {
        if (file1 == null || file2 == null) {
            println("Select files first (option 1).");
            return;
        }
        File f1 = new File(file1);
        File f2 = new File(file2);
        if (!f1.exists()) { println("File not found: " + file1); return; }
        if (!f2.exists()) { println("File not found: " + file2); return; }

        try {
            long start = System.currentTimeMillis();
            if (opts.streaming && !opts.unordered && opts.schema == null) {
                lastResult = StreamingXmlParser.compareXmlFilesStreaming(f1, f2, opts);
            } else if (opts.parallel) {
                int threads = opts.parallelThreads != null ? opts.parallelThreads : 0;
                lastResult = ParallelComparison.compareXmlFilesParallel(f1, f2, opts, threads);
            } else {
                lastResult = XmlCompare.compareXmlFiles(file1, file2, opts);
            }
            long elapsed = System.currentTimeMillis() - start;
            println("Done in " + elapsed + "ms. Found " + lastResult.size() + " difference(s).");
        } catch (Exception e) {
            println("Error: " + e.getMessage());
        }
    }

    private void runDirComparison() {
        if (dir1 == null || dir2 == null) {
            println("Select directories first (option 2).");
            return;
        }
        try {
            boolean recursive = yesNo("Recurse into subdirectories?");
            long start = System.currentTimeMillis();
            Map<String, Object> results = XmlCompare.compareDirs(dir1, dir2, opts, recursive);
            long elapsed = System.currentTimeMillis() - start;
            int total = results.values().stream().mapToInt(v -> {
                if (v instanceof List<?> l) return l.size();
                return 1;
            }).sum();
            println("Done in " + elapsed + "ms. " + results.size() + " file(s), " + total + " difference(s).");
            // Show per-file summary
            for (Map.Entry<String, Object> entry : results.entrySet()) {
                Object val = entry.getValue();
                if (val instanceof String s) {
                    println("  " + entry.getKey() + ": ERROR - " + s);
                } else if (val instanceof List<?> l) {
                    println("  " + entry.getKey() + ": " + l.size() + " diff(s)");
                }
            }
            // Set lastResult to combined list for browsing
            lastResult = new java.util.ArrayList<>();
            for (Object val : results.values()) {
                if (val instanceof List<?> list) {
                    for (Object d : list) {
                        if (d instanceof Difference diff) lastResult.add(diff);
                    }
                }
            }
        } catch (Exception e) {
            println("Error: " + e.getMessage());
        }
    }

    private void browseResults() {
        if (lastResult == null) {
            println("No results yet. Run a comparison first (option 4).");
            return;
        }
        if (lastResult.isEmpty()) {
            println("Files are identical — no differences.");
            return;
        }

        int pageSize = 10;
        int page = 0;
        while (true) {
            int start = page * pageSize;
            int end = Math.min(start + pageSize, lastResult.size());
            println("\nDifferences " + (start + 1) + " - " + end + " of " + lastResult.size() + ":");
            println("─────────────────────────────────────");
            for (int i = start; i < end; i++) {
                Difference d = lastResult.get(i);
                println((i + 1) + ". [" + d.kind + "] " + d.path);
                println("   " + d.msg);
                if (d.expected != null) println("   Expected: " + d.expected);
                if (d.actual != null) println("   Actual:   " + d.actual);
            }
            println("─────────────────────────────────────");
            println("[n]ext  [p]rev  [f]ilter by kind  [b]ack");
            String cmd = readLine("").trim().toLowerCase();
            switch (cmd) {
                case "n", "next" -> { if (end < lastResult.size()) page++; else println("Last page."); }
                case "p", "prev" -> { if (page > 0) page--; else println("First page."); }
                case "f", "filter" -> {
                    String kind = readLine("Kind to filter (e.g. text_mismatch)").trim();
                    List<Difference> filtered = lastResult.stream()
                            .filter(d -> d.kind.equals(kind)).toList();
                    println(filtered.size() + " difference(s) of kind '" + kind + "':");
                    filtered.forEach(d -> println("  " + d.path + " — " + d.msg));
                }
                case "b", "back", "" -> { return; }
                default -> println("Unknown command.");
            }
        }
    }

    private void exportResults() {
        if (lastResult == null) {
            println("No results to export.");
            return;
        }
        println("Export format: 1) Text  2) JSON  0) Cancel");
        String choice = readLine("Format").trim();
        if (choice.equals("0")) return;

        String outPath = readLine("Output file path").trim();
        if (outPath.isEmpty()) { println("No path given."); return; }

        try {
            String content;
            if (choice.equals("2")) {
                Map<String, Object> wrap = new java.util.LinkedHashMap<>();
                wrap.put("comparison", lastResult.stream().map(Difference::toMap).toList());
                content = new com.fasterxml.jackson.databind.ObjectMapper()
                        .writerWithDefaultPrettyPrinter().writeValueAsString(wrap);
            } else {
                StringBuilder sb = new StringBuilder();
                for (Difference d : lastResult) {
                    sb.append("[").append(d.kind).append("] ").append(d.path).append("\n");
                    sb.append("  ").append(d.msg).append("\n");
                    if (d.expected != null) sb.append("  Expected: ").append(d.expected).append("\n");
                    if (d.actual != null) sb.append("  Actual:   ").append(d.actual).append("\n");
                    sb.append("\n");
                }
                content = sb.toString();
            }
            Files.writeString(Path.of(outPath), content);
            println("Exported " + lastResult.size() + " difference(s) to " + outPath);
        } catch (Exception e) {
            println("Export failed: " + e.getMessage());
        }
    }

    private void showStats() {
        ParallelComparison.ParallelStats ps = ParallelComparison.getParallelStats();
        println("Parallel stats: " + ps);
        if (file1 != null) {
            try {
                StreamingXmlParser.StreamingStats ss = StreamingXmlParser.getStreamStats(new File(file1));
                println("Stream stats (file1): " + ss);
            } catch (Exception e) {
                println("Could not read stream stats: " + e.getMessage());
            }
        }
    }

    private String readLine(String prompt) {
        if (!prompt.isEmpty()) System.out.print(prompt + ": ");
        return scanner.hasNextLine() ? scanner.nextLine() : "";
    }

    private String readPathLine(String prompt) {
        String path = readLine(prompt).trim();
        // Strip surrounding quotes if present (common in copy-paste from Windows Explorer)
        if (path.startsWith("\"") && path.endsWith("\"") && path.length() > 1) {
            path = path.substring(1, path.length() - 1);
        }
        return path.isEmpty() ? null : path;
    }

    private boolean yesNo(String prompt) {
        String val = readLine(prompt + " [y/N]").trim().toLowerCase();
        return val.equals("y") || val.equals("yes");
    }

    private void println(String msg) {
        System.out.println(msg);
    }
}
