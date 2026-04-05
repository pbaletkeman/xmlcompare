package com.xmlcompare.benchmark;

import java.io.File;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import com.xmlcompare.XmlCompare;
import com.xmlcompare.CompareOptions;
import com.xmlcompare.Difference;

/**
 * Benchmarking suite for xmlcompare performance.
 * Tests comparison speed and memory usage across various file sizes.
 */
public class BenchmarkSuite {

  /**
   * Generate a large XML file for benchmarking.
   * @param sizeMb Target file size in MB
   * @param filename Output filename
   * @return Path to generated file
   */
  public static Path generateLargeXml(int sizeMb, String filename) throws Exception {
    Path filepath = Paths.get(filename);
    long targetBytes = (long) sizeMb * 1024 * 1024;
    long currentSize = 0;

    try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(filepath))) {
      writer.println("<?xml version=\"1.0\"?>");
      writer.println("<root>");
      currentSize += 35;

      int itemNum = 0;
      while (currentSize < targetBytes) {
        String item = String.format(
            "  <item id=\"%%d\">\n"
                + "    <name>Item %%d</name>\n"
                + "    <description>This is a test item for benchmarking xmlcompare "
                + "performance on large files with multiple elements and attributes.</description>\n"
                + "    <value>%%.4f</value>\n"
                + "    <timestamp>2026-04-04T12:00:00Z</timestamp>\n"
                + "  </item>\n",
            itemNum, itemNum, itemNum * 3.14159);
        writer.print(item);
        currentSize += item.getBytes().length;
        itemNum++;
      }

      writer.println("</root>");
    }

    double actualSizeMb = Files.size(filepath) / (1024.0 * 1024.0);
    System.out.printf("Generated %s: %.1f MB%n", filename, actualSizeMb);

    return filepath;
  }

  /**
   * Benchmark a single comparison.
   */
  public static BenchmarkResult benchmarkComparison(
      File file1, File file2, String label) {
    try {
      // Warm up
      XmlCompare.compareXmlFiles(
          file1.getAbsolutePath(), file2.getAbsolutePath(), new CompareOptions());

      // Actual benchmark
      long startTime = System.currentTimeMillis();
      List<Difference> diffs = XmlCompare.compareXmlFiles(
          file1.getAbsolutePath(), file2.getAbsolutePath(), new CompareOptions());
      long elapsed = System.currentTimeMillis() - startTime;

      double file1SizeMb = file1.length() / (1024.0 * 1024.0);
      double file2SizeMb = file2.length() / (1024.0 * 1024.0);

      return new BenchmarkResult(
          label, file1SizeMb, file2SizeMb, elapsed / 1000.0,
          diffs.size(), "OK");
    } catch (Exception e) {
      return new BenchmarkResult(
          label, 0, 0, 0, 0,
          "ERROR: " + e.getMessage());
    }
  }

  /**
   * Benchmark a streaming comparison.
   */
  public static BenchmarkResult benchmarkStreamingComparison(
      File file1, File file2, String label) {
    try {
      CompareOptions opts = new CompareOptions();
      // Warm up
      com.xmlcompare.parse.StreamingXmlParser.compareXmlFilesStreaming(file1, file2, opts);
      long startTime = System.currentTimeMillis();
      List<Difference> diffs =
          com.xmlcompare.parse.StreamingXmlParser.compareXmlFilesStreaming(file1, file2, opts);
      long elapsed = System.currentTimeMillis() - startTime;
      double sizeMb = file1.length() / (1024.0 * 1024.0);
      return new BenchmarkResult(label, sizeMb, sizeMb, elapsed / 1000.0, diffs.size(), "OK");
    } catch (Exception e) {
      return new BenchmarkResult(label, 0, 0, 0, 0, "ERROR: " + e.getMessage());
    }
  }

  /**
   * Benchmark a parallel comparison.
   */
  public static BenchmarkResult benchmarkParallelComparison(
      File file1, File file2, String label) {
    try {
      CompareOptions opts = new CompareOptions();
      int threads = Runtime.getRuntime().availableProcessors();
      // Warm up
      com.xmlcompare.parallel.ParallelComparison.compareXmlFilesParallel(file1, file2, opts, threads);
      long startTime = System.currentTimeMillis();
      List<Difference> diffs =
          com.xmlcompare.parallel.ParallelComparison.compareXmlFilesParallel(file1, file2, opts, threads);
      long elapsed = System.currentTimeMillis() - startTime;
      double sizeMb = file1.length() / (1024.0 * 1024.0);
      return new BenchmarkResult(label, sizeMb, sizeMb, elapsed / 1000.0, diffs.size(), "OK");
    } catch (Exception e) {
      return new BenchmarkResult(label, 0, 0, 0, 0, "ERROR: " + e.getMessage());
    }
  }

  /**
   * Run full benchmarking suite.
   */
  public static void runBenchmarkSuite() throws Exception {
    System.out.println("=".repeat(70));
    System.out.println("xmlcompare Performance Benchmark Suite");
    System.out.println("=".repeat(70));

    List<BenchmarkResult> results = new ArrayList<>();
    int[] sizes = {1, 10, 50};

    // Create temporary files
    System.out.println("\nGenerating test files...");
    java.util.Map<Integer, Path> testFiles = new java.util.HashMap<>();

    for (int sizeMb : sizes) {
      String filename = String.format("test_%dmb.xml", sizeMb);
      Path path = generateLargeXml(sizeMb, filename);
      testFiles.put(sizeMb, path);
    }

    System.out.println("\nRunning benchmarks...");
    System.out.println("-".repeat(70));

    // Run benchmarks: DOM, streaming, and parallel for each size
    for (int sizeMb : sizes) {
      Path filePath = testFiles.get(sizeMb);
      File file = filePath.toFile();

      BenchmarkResult result = benchmarkComparison(
          file, file, String.format("%3dMB DOM", sizeMb));
      results.add(result);
      System.out.println(result);

      BenchmarkResult resultStream = benchmarkStreamingComparison(
          file, file, String.format("%3dMB STREAM", sizeMb));
      results.add(resultStream);
      System.out.println(resultStream);

      BenchmarkResult resultParallel = benchmarkParallelComparison(
          file, file, String.format("%3dMB PARALLEL", sizeMb));
      results.add(resultParallel);
      System.out.println(resultParallel);
    }

    System.out.println("-".repeat(70));

    // Print summary
    System.out.println("\nBenchmark Summary:");
    System.out.println("-".repeat(70));
    for (BenchmarkResult result : results) {
      if ("OK".equals(result.status)) {
        double throughput = result.file1SizeMb / result.elapsedSeconds;
        System.out.printf("%40s: %6.2f s (%6.1f MB/s)%n",
            result.label, result.elapsedSeconds, throughput);
      }
    }

    // Cleanup
    System.out.println("\nCleaning up test files...");
    for (Path path : testFiles.values()) {
      Files.delete(path);
    }
  }

  /**
   * Benchmark result data class.
   */
  public static class BenchmarkResult {
    public String label;
    public double file1SizeMb;
    public double file2SizeMb;
    public double elapsedSeconds;
    public int diffCount;
    public String status;

    public BenchmarkResult(String label, double file1SizeMb, double file2SizeMb,
        double elapsedSeconds, int diffCount, String status) {
      this.label = label;
      this.file1SizeMb = file1SizeMb;
      this.file2SizeMb = file2SizeMb;
      this.elapsedSeconds = elapsedSeconds;
      this.diffCount = diffCount;
      this.status = status;
    }

    @Override
    public String toString() {
      if ("OK".equals(status)) {
        double throughput = elapsedSeconds > 0 ? file1SizeMb / elapsedSeconds : 0;
        return String.format(
            "%40s: %6.2f s (%6.1f MB/s) - %d diffs",
            label, elapsedSeconds, throughput, diffCount);
      } else {
        return String.format("%40s: %s", label, status);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    runBenchmarkSuite();
  }
}
