#!/usr/bin/env python3
"""
Benchmarking suite for xmlcompare performance.
Tests comparison speed and memory usage across various file sizes.
Generates baseline for performance regression tracking.
"""

import time
import tempfile
import os
from pathlib import Path
from xml.etree import ElementTree as ET

from xmlcompare import compare_xml_files, CompareOptions
from parse_streaming import get_stream_stats


def generate_large_xml(size_mb, filename=None):
    """
    Generate a large XML file for benchmarking.

    Args:
        size_mb: Target file size in MB
        filename: Output filename (optional, uses temp if not provided)

    Returns:
        Path to generated file
    """
    if filename is None:
        filename = f"test_large_{size_mb}mb.xml"

    filepath = Path(filename)
    target_bytes = size_mb * 1024 * 1024
    current_size = 0

    # Start XML
    with open(filepath, 'w') as f:
        f.write('<?xml version="1.0"?>\n<root>\n')
        current_size += 20

        # Add elements until target size
        item_num = 0
        while current_size < target_bytes:
            item = (
                f'  <item id="{item_num}">\n'
                f'    <name>Item {item_num}</name>\n'
                f'    <description>This is a test item for benchmarking xmlcompare '
                f'performance on large files with multiple elements and attributes.</description>\n'
                f'    <value>{item_num * 3.14159:.4f}</value>\n'
                f'    <timestamp>2026-04-04T12:00:00Z</timestamp>\n'
                f'  </item>\n'
            )
            f.write(item)
            current_size += len(item.encode('utf-8'))
            item_num += 1

        # Close XML
        f.write('</root>\n')

    actual_size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"Generated {filepath.name}: {actual_size_mb:.1f} MB ({item_num} items)")

    return filepath


def benchmark_comparison(file1, file2, label=""):
    """
    Benchmark a single comparison.

    Args:
        file1: Path to first XML file
        file2: Path to second XML file
        label: Benchmark label/description

    Returns:
        BenchmarkResult with timing and metrics
    """
    try:
        # Warm up
        compare_xml_files(str(file1), str(file2))

        # Actual benchmark
        start_time = time.time()
        diffs = compare_xml_files(str(file1), str(file2))
        elapsed = time.time() - start_time

        file1_size_mb = file1.stat().st_size / (1024 * 1024)
        file2_size_mb = file2.stat().st_size / (1024 * 1024)

        result = BenchmarkResult(
            label=label,
            file1_size_mb=file1_size_mb,
            file2_size_mb=file2_size_mb,
            elapsed_seconds=elapsed,
            diff_count=len(diffs),
            status="OK",
        )
        return result

    except Exception as e:
        return BenchmarkResult(
            label=label,
            file1_size_mb=0,
            file2_size_mb=0,
            elapsed_seconds=0,
            diff_count=0,
            status=f"ERROR: {str(e)}",
        )


def benchmark_streaming(file1, file2, label=""):
    """Benchmark streaming (iterparse) comparison."""
    from parse_streaming import compare_xml_files_streaming
    opts = CompareOptions()
    try:
        compare_xml_files_streaming(str(file1), str(file2), opts)
        start = time.time()
        diffs = compare_xml_files_streaming(str(file1), str(file2), opts)
        elapsed = time.time() - start
        size_mb = file1.stat().st_size / (1024 * 1024)
        return BenchmarkResult(label, size_mb, size_mb, elapsed, len(diffs), "OK")
    except Exception as e:
        return BenchmarkResult(label, 0, 0, 0, 0, f"ERROR: {e}")


def benchmark_parallel(file1, file2, label="", threads=0):
    """Benchmark parallel (multiprocessing) comparison."""
    from parallel import compare_xml_files_parallel
    opts = CompareOptions()
    try:
        compare_xml_files_parallel(str(file1), str(file2), opts, num_processes=threads)
        start = time.time()
        diffs = compare_xml_files_parallel(str(file1), str(file2), opts, num_processes=threads)
        elapsed = time.time() - start
        size_mb = file1.stat().st_size / (1024 * 1024)
        return BenchmarkResult(label, size_mb, size_mb, elapsed, len(diffs), "OK")
    except Exception as e:
        return BenchmarkResult(label, 0, 0, 0, 0, f"ERROR: {e}")


def run_benchmark_suite():
    """Run full benchmarking suite across multiple file sizes."""
    print("=" * 70)
    print("xmlcompare Performance Benchmark Suite")
    print("=" * 70)

    results = []

    # Test sizes (in MB)
    sizes = [1, 10, 50]

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\nGenerating test files in {tmpdir}...")

        # Generate test files
        test_files = {}
        for size_mb in sizes:
            file_path = generate_large_xml(
                size_mb,
                os.path.join(tmpdir, f"test_{size_mb}mb.xml")
            )
            test_files[size_mb] = file_path

        print("\nRunning benchmarks...")
        print("-" * 70)

        # Run benchmarks: DOM, streaming, and parallel for each size
        for size_mb in sizes:
            file1 = test_files[size_mb]
            file2 = test_files[size_mb]  # Same file (0 differences)

            result = benchmark_comparison(
                file1, file2,
                label=f"{size_mb:3d}MB DOM"
            )
            results.append(result)
            print(result)

            result_stream = benchmark_streaming(
                file1, file2,
                label=f"{size_mb:3d}MB STREAM"
            )
            results.append(result_stream)
            print(result_stream)

            result_parallel = benchmark_parallel(
                file1, file2,
                label=f"{size_mb:3d}MB PARALLEL"
            )
            results.append(result_parallel)
            print(result_parallel)

        print("-" * 70)

    # Print summary
    print("\nBenchmark Summary:")
    print("-" * 70)
    for result in results:
        if result.status == "OK":
            throughput = result.file1_size_mb / result.elapsed_seconds
            print(f"{result.label:40s}: {result.elapsed_seconds:6.2f}s "
                  f"({throughput:6.1f} MB/s)")


class BenchmarkResult:
    """Result of a single benchmark run."""

    def __init__(self, label, file1_size_mb, file2_size_mb,
                 elapsed_seconds, diff_count, status):
        self.label = label
        self.file1_size_mb = file1_size_mb
        self.file2_size_mb = file2_size_mb
        self.elapsed_seconds = elapsed_seconds
        self.diff_count = diff_count
        self.status = status

    def __str__(self):
        if self.status == "OK":
            throughput = self.file1_size_mb / self.elapsed_seconds if self.elapsed_seconds > 0 else 0
            return (
                f"{self.label:40s}: "
                f"{self.elapsed_seconds:6.2f}s ({throughput:6.1f} MB/s) "
                f"- {self.diff_count} diffs"
            )
        else:
            return f"{self.label:40s}: {self.status}"


if __name__ == "__main__":
    run_benchmark_suite()
