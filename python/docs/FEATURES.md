# xmlcompare Python - Features & Advanced Topics

This document describes the advanced features and detailed capabilities of the Python implementation.

## Overview

The Python implementation includes:

- **Multiple output formats** (text, JSON, HTML, unified diff)
- **Interactive mode** with menu-driven interface
- **Streaming parser** for memory-efficient large file handling
- **Plugin system** for extensibility
- **Schema-aware comparison** with XSD validation
- **Performance benchmarking** utilities

---

- [xmlcompare Python - Features \& Advanced Topics](#xmlcompare-python---features--advanced-topics)
  - [Overview](#overview)
  - [Output Formatters](#output-formatters)
    - [Text Format (Default)](#text-format-default)
    - [JSON Format](#json-format)
    - [HTML Format](#html-format)
    - [Unified Diff Format](#unified-diff-format)
  - [Interactive Mode](#interactive-mode)
    - [Launching Interactive Mode](#launching-interactive-mode)
    - [Features](#features)
    - [Example Session](#example-session)
  - [Example: Streaming Parser](#example-streaming-parser)
  - [Example: Schema Validation](#example-schema-validation)
  - [Example: Plugin System](#example-plugin-system)
  - [Example: XPath Filtering](#example-xpath-filtering)
  - [Example: Type-Aware Comparison](#example-type-aware-comparison)
  - [Example: Output Formats](#example-output-formats)
  - [Example: Config File](#example-config-file)
  - [Example: Directory Comparison](#example-directory-comparison)
  - [Example: Structure-Only Mode](#example-structure-only-mode)
  - [Example: Attribute Filtering](#example-attribute-filtering)
  - [Example: Element Filtering](#example-element-filtering)
  - [Example: Depth Limiting](#example-depth-limiting)
  - [Example: Performance Benchmarks](#example-performance-benchmarks)
  - [Access type information](#access-type-information)
  - [Plugin System](#plugin-system)
    - [Creating a Plugin](#creating-a-plugin)
    - [Using Plugins](#using-plugins)
    - [Plugin Types](#plugin-types)
    - [Plugin Registry](#plugin-registry)
  - [Performance Benchmarking](#performance-benchmarking)
    - [Running Benchmarks](#running-benchmarks)
    - [What Gets Measured](#what-gets-measured)
    - [Benchmark Output](#benchmark-output)
    - [Interpreting Results](#interpreting-results)
    - [Optimization Tips](#optimization-tips)
  - [Command Examples](#command-examples)
    - [Example 1: Flexible Development Comparison](#example-1-flexible-development-comparison)
    - [Example 2: Strict Production Testing](#example-2-strict-production-testing)
    - [Example 3: Generate HTML Report](#example-3-generate-html-report)
    - [Example 4: Skip Metadata Fields](#example-4-skip-metadata-fields)
    - [Example 5: Filter Specific Elements](#example-5-filter-specific-elements)
    - [Example 6: Batch Comparison with Config](#example-6-batch-comparison-with-config)
    - [Example 7: Interactive Mode Workflow](#example-7-interactive-mode-workflow)
  - [Advanced Configuration](#advanced-configuration)
    - [Config File Best Practices](#config-file-best-practices)
    - [Environment Variables](#environment-variables)
  - [Troubleshooting](#troubleshooting)
    - ["Out of memory" with large files](#out-of-memory-with-large-files)
    - [Slow performance](#slow-performance)
    - [Plugin loading fails](#plugin-loading-fails)
  - [See Also](#see-also)

---

## Output Formatters

### Text Format (Default)

Human-readable text output with color support for TTY terminals.

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format text
```

**Output Example:**

```plaintext
Comparing: file1.xml vs file2.xml
------------------------------------------------------------
  [ATTR] Path: /root/item/@id - attribute 'id' value mismatch
    Expected : 123
    Actual   : 456
  [TEXT] Path: /root/item/price - text value mismatch
    Expected : 99.99
    Actual   : 89.99
```

**Features:**

- Color-coded output (red for differences, green for context)
- Clear path indication for each difference
- Side-by-side value comparison
- Disabled automatically when piping output

### JSON Format

Machine-readable JSON output for programmatic processing.

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format json
```

**Output Example:**

```json
{
  "file1.xml vs file2.xml": {
    "equal": false,
    "differences": [
      {
        "path": "/root/item",
        "kind": "attr",
        "message": "attribute 'id' value mismatch",
        "expected": "123",
        "actual": "456"
      },
      {
        "path": "/root/item/price",
        "kind": "text",
        "message": "text value mismatch",
        "expected": "99.99",
        "actual": "89.99"
      }
    ]
  }
}
```

**Use Cases:**

- Parsing output in shell scripts
- Analysis by other tools
- CI/CD integration
- Reporting and dashboards

### HTML Format

Interactive HTML report with side-by-side comparison view.

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format html --output-file report.html
```

**Features:**

- Two-column layout (expected vs actual)
- Color-coded differences (red for removed, green for added)
- Line numbers
- Self-contained CSS (works offline)
- Collapsible sections for large reports
- Summary statistics

**Perfect for:**

- Stakeholder reviews
- Documentation
- Archive storage
- Automated reports

### Unified Diff Format

Standard unified diff format compatible with `diff`, `patch`, and version control systems.

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format unified-diff
```

**Output Example:**

```shell
--- file1.xml
+++ file2.xml
@@ /root/item @@
- <id>123</id>
+ <id>456</id>
@@ /root/item/price @@
- <value>99.99</value>
+ <value>89.99</value>
```

**Use Cases:**

- Pattern recognition in diffs
- Integration with version control
- Patch creation and verification
- Diff analysis tools

---

## Interactive Mode

Interactive mode provides a menu-driven interface for exploring comparison results.

### Launching Interactive Mode

```bash
python interactive_cli.py
```

### Features

1. **File Comparison Menu**
   - Select two XML files to compare
   - Apply comparison options interactively
   - View results immediately

2. **Options Configuration**
   - Set tolerance, case sensitivity, ordering
   - Toggle namespace/attribute handling
   - Configure skip patterns and filters

3. **Result Exploration**
   - View differences one by one
   - Navigation through large result sets
   - Filter and search capabilities

4. **Batch Operations**
   - Compare multiple file pairs
   - Apply template configurations
   - Save comparison sessions

### Example Session

```shell
xmlcompare Interactive Mode
================================

Main Menu:
1. Compare Files
2. Configure Options
3. Load Config File
4. Exit

Choose option: 1

Enter first file: samples/orders_expected.xml
Enter second file: samples/orders_actual_diff.xml

Comparison Options:
1. Default (strict)
2. Flexible (ignore namespaces, case, order)
# xmlcompare (Python) – Features

## Quick Navigation

- [CLI_REFERENCE.md](CLI_REFERENCE.md) – Command-line usage
- [../docs/CONFIG_GUIDE.md](../../docs/CONFIG_GUIDE.md) – Configuration guide
- [../docs/FEATURES.md](../../docs/FEATURES.md) – Master feature matrix

---

## Python-Specific Features

| Feature                | Description                                 |
|------------------------|---------------------------------------------|
| Parallel processing    | Multi-core comparison for large datasets    |
| Streaming parser       | Handles large XML files with low memory     |
| Schema validation      | XSD schema support                          |
| Plugin system          | Custom comparison logic via plugins         |
| XPath filtering        | Compare only elements matching XPath        |
| Type-aware comparison  | Numeric/date type hints                     |
| Output formats         | text, JSON, HTML, diff                      |
| Config file support    | JSON/YAML config                            |
| Directory comparison   | Recursively compare directories             |
| Structure-only mode    | Compare only structure                      |
| Attribute filtering    | Ignore or match specific attributes         |
| Element filtering      | Skip specific elements                      |
| Depth limiting         | Limit comparison depth                      |
| Performance benchmarks | Built-in benchmarking                       |

## Example: Parallel Processing

```bash
python xmlcompare.py --files file1.xml file2.xml --parallel
```

## Example: Streaming Parser

```bash
python xmlcompare.py --files large1.xml large2.xml --stream
```

## Example: Schema Validation

```bash
python xmlcompare.py --files file1.xml file2.xml --schema schema.xsd
```

## Example: Plugin System

```bash
python xmlcompare.py --files file1.xml file2.xml --plugin myplugin.py
```

## Example: XPath Filtering

```bash
python xmlcompare.py --files file1.xml file2.xml --xpath "/root/item"
```

## Example: Type-Aware Comparison

```bash
python xmlcompare.py --files file1.xml file2.xml --type-aware
```

## Example: Output Formats

```bash
python xmlcompare.py --files file1.xml file2.xml --output json
python xmlcompare.py --files file1.xml file2.xml --output html
python xmlcompare.py --files file1.xml file2.xml --output diff
```

## Example: Config File

```bash
python xmlcompare.py --files file1.xml file2.xml --config config.json
```

## Example: Directory Comparison

```bash
python xmlcompare.py --dir dir1 dir2
```

## Example: Structure-Only Mode

```bash
python xmlcompare.py --files file1.xml file2.xml --structure-only
```

## Example: Attribute Filtering

```bash
python xmlcompare.py --files file1.xml file2.xml --ignore-attributes timestamp id
```

## Example: Element Filtering

```bash
python xmlcompare.py --files file1.xml file2.xml --skip-elements meta debug
```

## Example: Depth Limiting

```bash
python xmlcompare.py --files file1.xml file2.xml --max-depth 3
```

## Example: Performance Benchmarks

```bash
python xmlcompare.py --benchmark --files file1.xml file2.xml
```

analyzer = SchemaAnalyzer()
metadata = analyzer.analyze('schema.xsd')

## Access type information

```shell
if metadata:
    print(metadata.get_type('/root/date'))  # Returns 'xs:date'
    print(metadata.is_numeric('/root/price'))  # Returns True
```

---

## Plugin System

Extensibility framework for custom comparison logic and filters.

### Creating a Plugin

Plugins implement the `ComparisonPlugin` interface:

```python
from plugin_interface import ComparisonPlugin, DifferenceFilter, FormatterPlugin

class CustomFilter(DifferenceFilter):
    """Custom filter to skip XML comments."""

    def should_skip(self, path: str, tag: str) -> bool:
        """Return True if element should be skipped."""
        return tag.startswith('_meta_')

    def filter_differences(self, diffs: List[Difference]) -> List[Difference]:
        """Filter out specific differences."""
        return [d for d in diffs if not d.path.contains('temp')]
```

### Using Plugins

```bash
# Load a plugin via --plugins option
python xmlcompare.py --files file1.xml file2.xml --plugins "mymodule.CustomFilter"

# Multiple plugins
python xmlcompare.py --files file1.xml file2.xml --plugins "filter1.CustomFilter,formatter.ReportFormatter"
```

### Plugin Types

1. **DifferenceFilter**
   - Filter elements to skip
   - Filter final differences
   - Transform comparison results

2. **FormatterPlugin**
   - Custom output formatting
   - Report generation
   - Result aggregation

3. **ComparisonPlugin**
   - Custom comparison logic
   - Type-specific handling
   - Domain-specific rules

### Plugin Registry

Built-in plugins in `plugin_interface.py`:

```python
registry = PluginRegistry()
registry.load_plugin('mymodule.CustomPlugin')
plugins = registry.get_all_plugins()
```

---

## Performance Benchmarking

Built-in benchmarking and performance analysis tools.

### Running Benchmarks

```bash
python benchmark.py

# Or directly
python -c "from benchmark import run_benchmarks; run_benchmarks()"
```

### What Gets Measured

- File parsing time
- Comparison time
- Memory usage
- Memory efficiency ratio
- Performance with various file sizes

### Benchmark Output

```shell
XML Comparison Benchmarks
========================

1. Small file (1KB)
   - Parse time: 0.5ms
   - Compare time: 1.2ms
   - Memory used: 512KB

2. Medium file (1MB)
   - Parse time: 45ms
   - Compare time: 89ms
   - Memory used: 8.5MB

3. Large file (100MB)
   - Parse time: 2500ms
   - Compare time: 4200ms
   - Memory used: 256MB
```

### Interpreting Results

- **Parse time**: XML parsing overhead
- **Compare time**: Actual comparison algorithm performance
- **Memory used**: Peak memory consumption
- **Trend analysis**: Performance scaling with file size

### Optimization Tips

1. For files < 10MB: Use default DOM parser
2. For files > 100MB: Consider streaming parser
3. For repeated comparisons: Cache parsed trees
4. For parallel workloads: Use multiprocessing

---

## Command Examples

### Example 1: Flexible Development Comparison

```bash
# Ignore namespaces, order, and case - perfect for development
python xmlcompare.py \
  --files expected.xml actual.xml \
  --unordered \
  --ignore-namespaces \
  --ignore-case \
  --tolerance 0.001 \
  --output-format text
```

### Example 2: Strict Production Testing

```bash
# Zero tolerance - strict matching for production validation
python xmlcompare.py \
  --files test1.xml test2.xml \
  --tolerance 0.0 \
  --ignore-case false \
  --unordered false \
  --ignore-namespaces false \
  --output-format json \
  --output-file test-results.json
```

### Example 3: Generate HTML Report

```bash
# Create interactive comparison report
python xmlcompare.py \
  --files baseline.xml current.xml \
  --output-format html \
  --output-file comparison-report.html \
  --verbose
```

### Example 4: Skip Metadata Fields

```bash
# Compare data while ignoring technical metadata
python xmlcompare.py \
  --files file1.xml file2.xml \
  --skip-keys "//timestamp" "//uuid" "//version" "//checksum" \
  --output-format json \
  --summary
```

### Example 5: Filter Specific Elements

```bash
# Compare only active orders
python xmlcompare.py \
  --files order1.xml order2.xml \
  --filter "//orders/order[status='active']" \
  --tolerance 0.01 \
  --streaming
```

### Example 6: Batch Comparison with Config

```bash
# Create config file
cat > batch-config.json <<EOF
{
  "tolerance": 0.001,
  "ignoreNamespaces": true,
  "skipKeys": ["//timestamp", "//uuid"],
  "outputFormat": "json"
}
EOF

# Use config for multiple comparisons
for file1 in expected/*.xml; do
  file2="actual/$(basename "$file1")"
  python xmlcompare.py --files "$file1" "$file2" --config batch-config.json
done
```

### Example 7: Interactive Mode Workflow

```bash
# Launch interactive CLI
python interactive_cli.py

# Follow prompts:
# 1. Compare Files
# 2. Select file1.xml and file2.xml
# 3. Choose "Flexible" template
# 4. View results with detailed breakdown
# 5. Export to JSON if needed
```

---

## Advanced Configuration

### Config File Best Practices

```json
{
  "comment": "Production comparison config",
  "tolerance": 0.001,
  "ignore_case": false,
  "unordered": true,
  "ignore_namespaces": true,
  "ignore_attributes": false,
  "skip_keys": [
    "//timestamp",
    "//transactionId",
    "//processId",
    "/root/metadata/version"
  ],
  "skip_pattern": "^(_internal|__debug).*$",
  "output_format": "json",
  "output_file": "comparison-results.json",
  "summary": false,
  "verbose": true,
  "fail_fast": false
}
```

### Environment Variables

```bash
# Enable debug output
export XMLCOMPARE_DEBUG=1

# Set custom temp directory
export XMLCOMPARE_TMPDIR=/var/tmp

# Run with Python optimization
PYTHONOPTIMIZE=2 python xmlcompare.py --files file1.xml file2.xml
```

---

## Troubleshooting

### "Out of memory" with large files

Solution: Use streaming parser or split large files:

```bash
# Using streaming (partial support)
python parse_streaming.py file1.xml file2.xml

# Or split files by elements
# Then compare parts individually
```

### Slow performance

Solutions:

1. Use `--fail-fast` for quick checks
2. Apply `--filter` to reduce scope
3. Use `--skip-keys` to skip unnecessary elements
4. Consider `--structure-only` for schema validation

### Plugin loading fails

```bash
# Check Python path
export PYTHONPATH=$PYTHONPATH:/path/to/plugins

# Verbose loading
python xmlcompare.py --files file1.xml file2.xml --plugins "mymodule.Plugin" --verbose
```

---

## See Also

- [CLI Reference Guide](CLI_REFERENCE.md) - Complete command-line documentation
- [Python README](../README.md) - Installation and setup
- [Root README](/README.md) - Project overview
- [config.json.example](/config.json.example) - Configuration examples
