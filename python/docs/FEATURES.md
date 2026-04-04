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

## Table of Contents

1. [Output Formatters](#output-formatters)
2. [Interactive Mode](#interactive-mode)
3. [Streaming Parser](#streaming-parser)
4. [Schema Analysis & Validation](#schema-analysis--validation)
5. [Plugin System](#plugin-system)
6. [Performance Benchmarking](#performance-benchmarking)
7. [Command Examples](#command-examples)

---

## Output Formatters

### Text Format (Default)

Human-readable text output with color support for TTY terminals.

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format text
```

**Output Example:**
```
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
```
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

```
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
3. Custom
Choose: 2

Comparing...

Results:
- Total differences: 5
- Attribute differences: 2
- Text differences: 3

View detailed differences? (y/n): y
```

---

## Streaming Parser

Memory-efficient parser for large XML files using SAX (event-based) parsing.

### Features

```bash
# Not yet integrated into main CLI, but available in parse_streaming.py
python -c "from parse_streaming import compare_streaming; compare_streaming('large1.xml', 'large2.xml')"
```

**Advantages:**
- Constant memory usage regardless of file size
- Process multi-gigabyte files efficiently
- Event-based processing model

**Trade-offs:**
- Slower than DOM parsing
- Different API than standard comparison

### Use Cases

- Processing very large XML files (> 1GB)
- Streaming data processing
- Memory-constrained environments
- Real-time log file analysis

---

## Schema Analysis & Validation

Schema-aware comparison using XSD (XML Schema Definition) files.

### Basic Usage

```bash
python xmlcompare.py --files data1.xml data2.xml --schema schema.xsd --type-aware
```

### Features

1. **Type-Aware Comparison**
   - Date fields: Normalize formats before comparison
   - Numeric types: Apply schema-defined precision
   - Boolean types: Normalize true/false variants
   - Enum types: Validate against allowed values

2. **Schema Validation**
   - Validate XML against schema
   - Report validation errors
   - Enforce structure compliance

3. **Type Hints**
   - Comparison logic adapts to field types
   - Special handling for known types
   - Collation support for locale-aware strings

### Type-Aware Comparison Examples

**Date Comparison:**
```xml
<!-- file1.xml -->
<date>2024-01-15</date>

<!-- file2.xml -->
<date>01/15/2024</date>

<!-- With schema XSD that defines xs:date type -->
<!-- Result: EQUAL (date formats normalized) -->
```

**Numeric Precision:**
```xml
<!-- file1.xml -->
<price type="xs:decimal">99.99</price>

<!-- file2.xml -->
<price type="xs:decimal">99.990</price>

<!-- With schema defining 2-decimal precision -->
<!-- Result: EQUAL (trailing zero ignored) -->
```

**Boolean Normalization:**
```xml
<!-- file1.xml -->
<active>true</active>

<!-- file2.xml -->
<active>1</active>

<!-- With schema defining xs:boolean type -->
<!-- Result: EQUAL (1 and true are equivalent booleans) -->
```

### Schema Validation API

```python
from schema_analyzer import SchemaAnalyzer

analyzer = SchemaAnalyzer()
metadata = analyzer.analyze('schema.xsd')

# Access type information
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

```
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
