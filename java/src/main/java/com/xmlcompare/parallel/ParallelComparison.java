package com.xmlcompare.parallel;

import com.xmlcompare.CompareOptions;
import com.xmlcompare.Difference;
import com.xmlcompare.XmlCompare;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.Future;
import java.util.concurrent.RecursiveTask;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

/**
 * Parallel XML comparison using ForkJoinPool for subtree-level parallelism and
 * ExecutorService for directory-level parallelism.
 */
public class ParallelComparison {

    private static final int DEFAULT_THREADS = Runtime.getRuntime().availableProcessors();

    /**
     * Compare two XML files in parallel by splitting root children into subtrees.
     * Each subtree pair is compared by a ForkJoin worker task.
     */
    public static List<Difference> compareXmlFilesParallel(
            File file1, File file2, CompareOptions options, int threadCount) throws Exception {

        if (threadCount <= 0) {
            threadCount = DEFAULT_THREADS;
        }

        Document doc1 = parseDocument(file1);
        Document doc2 = parseDocument(file2);
        Element root1 = doc1.getDocumentElement();
        Element root2 = doc2.getDocumentElement();

        List<Element> children1 = getChildElements(root1);
        List<Element> children2 = getChildElements(root2);

        // Fall back to serial if there's nothing to parallelize meaningfully
        if (children1.size() < 2 || threadCount < 2) {
            return XmlCompare.compareXmlFiles(file1.getAbsolutePath(), file2.getAbsolutePath(), options);
        }

        int pairCount = Math.min(children1.size(), children2.size());
        ForkJoinPool pool = new ForkJoinPool(threadCount);
        try {
            List<ForkJoinTask<List<Difference>>> tasks = new ArrayList<>();
            for (int i = 0; i < pairCount; i++) {
                Element c1 = children1.get(i);
                Element c2 = children2.get(i);
                String path = XmlCompare.getTag(c1, options);
                tasks.add(pool.submit(new SubtreeCompareTask(c1, c2, path, options)));
            }

            List<Difference> allDiffs = new ArrayList<>();

            // Report root-level tag mismatch if roots differ
            String rootTag1 = XmlCompare.getTag(root1, options);
            String rootTag2 = XmlCompare.getTag(root2, options);
            if (!rootTag1.equals(rootTag2)) {
                allDiffs.add(new Difference("", "tag",
                        "Root tag mismatch: <" + rootTag1 + "> vs <" + rootTag2 + ">",
                        rootTag1, rootTag2));
            }

            // Elements present in file1 but not in file2
            for (int i = pairCount; i < children1.size(); i++) {
                String tag = XmlCompare.getTag(children1.get(i), options);
                allDiffs.add(new Difference(rootTag1 + "/" + tag, "missing",
                        "Child <" + tag + "> present in file1 but not in file2"));
            }
            // Elements present in file2 but not in file1
            for (int i = pairCount; i < children2.size(); i++) {
                String tag = XmlCompare.getTag(children2.get(i), options);
                allDiffs.add(new Difference(rootTag1 + "/" + tag, "extra",
                        "Child <" + tag + "> present in file2 but not in file1"));
            }

            for (ForkJoinTask<List<Difference>> task : tasks) {
                allDiffs.addAll(task.get());
                if (options.failFast && !allDiffs.isEmpty()) break;
            }

            // Sort by path for deterministic output order
            allDiffs.sort((a, b) -> a.path.compareTo(b.path));
            return allDiffs;
        } finally {
            pool.shutdown();
        }
    }

    /**
     * Compare two directories in parallel — each file pair is processed by a worker thread.
     */
    public static Map<String, Object> compareDirsParallel(
            String dir1, String dir2, CompareOptions options, int threadCount, boolean recursive)
            throws Exception {

        if (threadCount <= 0) {
            threadCount = DEFAULT_THREADS;
        }

        // Collect file pairs using the same logic as XmlCompare.compareDirs
        Path d1 = Path.of(dir1);
        Path d2 = Path.of(dir2);
        java.util.Set<String> files1 = collectXmlFiles(d1, recursive);
        java.util.Set<String> files2 = collectXmlFiles(d2, recursive);
        java.util.Set<String> allFiles = new java.util.TreeSet<>();
        allFiles.addAll(files1);
        allFiles.addAll(files2);

        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        Map<String, Future<Object>> futures = new LinkedHashMap<>();

        for (String fname : allFiles) {
            final boolean inDir1 = files1.contains(fname);
            final boolean inDir2 = files2.contains(fname);
            futures.put(fname, executor.submit(() -> {
                if (!inDir1) return (Object) ("only in " + dir2);
                if (!inDir2) return (Object) ("only in " + dir1);
                try {
                    return (Object) XmlCompare.compareXmlFiles(
                            d1.resolve(fname).toString(),
                            d2.resolve(fname).toString(),
                            options);
                } catch (Exception e) {
                    return (Object) ("Error: " + e.getMessage());
                }
            }));
        }

        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.MINUTES);

        Map<String, Object> results = new LinkedHashMap<>();
        for (Map.Entry<String, Future<Object>> entry : futures.entrySet()) {
            try {
                results.put(entry.getKey(), entry.getValue().get());
            } catch (Exception e) {
                results.put(entry.getKey(), "Error: " + e.getMessage());
            }
        }
        return results;
    }

    @SuppressWarnings("unchecked")
    private static java.util.Set<String> collectXmlFiles(Path dir, boolean recursive) {
        java.util.Set<String> result = new java.util.TreeSet<>();
        try {
            Stream<Path> stream = recursive ? Files.walk(dir) : Files.list(dir);
            stream.filter(p -> p.toString().endsWith(".xml") && Files.isRegularFile(p))
                    .forEach(p -> result.add(dir.relativize(p).toString()));
        } catch (Exception ignored) {
        }
        return result;
    }

    private static Document parseDocument(File file) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        // Disable external entity processing (XXE prevention)
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        DocumentBuilder builder = factory.newDocumentBuilder();
        return builder.parse(file);
    }

    private static List<Element> getChildElements(Element parent) {
        List<Element> result = new ArrayList<>();
        NodeList children = parent.getChildNodes();
        for (int i = 0; i < children.getLength(); i++) {
            if (children.item(i).getNodeType() == org.w3c.dom.Node.ELEMENT_NODE) {
                result.add((Element) children.item(i));
            }
        }
        return result;
    }

    public static int getRecommendedThreadCount() {
        return Math.max(1, DEFAULT_THREADS - 1);
    }

    public static ParallelStats getParallelStats() {
        ParallelStats stats = new ParallelStats();
        stats.availableCores = DEFAULT_THREADS;
        stats.recommendedThreads = getRecommendedThreadCount();
        stats.expectedSpeedup = Math.min(4.0, stats.recommendedThreads / 1.0);
        return stats;
    }

    public static class ParallelStats {
        public int availableCores;
        public int recommendedThreads;
        public double expectedSpeedup;

        @Override
        public String toString() {
            return String.format(
                    "Cores: %d | Recommended Threads: %d | Expected Speedup: %.1fx",
                    availableCores, recommendedThreads, expectedSpeedup);
        }
    }

    /**
     * ForkJoin task that compares a single subtree pair.
     */
    private static class SubtreeCompareTask extends RecursiveTask<List<Difference>> {
        private final Element elem1;
        private final Element elem2;
        private final String path;
        private final CompareOptions opts;

        SubtreeCompareTask(Element elem1, Element elem2, String path, CompareOptions opts) {
            this.elem1 = elem1;
            this.elem2 = elem2;
            this.path = path;
            this.opts = opts;
        }

        @Override
        protected List<Difference> compute() {
            List<Element> children1 = getChildElements(elem1);
            List<Element> children2 = getChildElements(elem2);

            // Fork sub-tasks for grandchildren if worth splitting
            if (children1.size() >= 4) {
                int half = children1.size() / 2;
                int pairCount = Math.min(children1.size(), children2.size());
                int splitAt = Math.min(half, pairCount);

                List<SubtreeCompareTask> subTasks = new ArrayList<>();
                for (int i = 0; i < splitAt; i++) {
                    String childPath = path + "/" + XmlCompare.getTag(children1.get(i), opts);
                    subTasks.add(new SubtreeCompareTask(children1.get(i), children2.get(i), childPath, opts));
                }
                invokeAll(subTasks);

                List<Difference> diffs = new ArrayList<>();
                compareThisElement(diffs);
                for (SubtreeCompareTask t : subTasks) {
                    diffs.addAll(t.join());
                }
                // Handle remaining pairs beyond split
                for (int i = splitAt; i < pairCount; i++) {
                    String childPath = path + "/" + XmlCompare.getTag(children1.get(i), opts);
                    new SubtreeCompareTask(children1.get(i), children2.get(i), childPath, opts)
                            .compute().forEach(diffs::add);
                }
                return diffs;
            }

            // Few children — compute directly
            List<Difference> diffs = new ArrayList<>();
            compareThisElement(diffs);
            return diffs;
        }

        private void compareThisElement(List<Difference> diffs) {
            diffs.addAll(XmlCompare.compareElements(elem1, elem2, opts, path, new ArrayList<>(), 0, null));
        }
    }
}
