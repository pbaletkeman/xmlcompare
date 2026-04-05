# xmlcompare Advanced Features Guide

This document describes the advanced features available in xmlcompare, including output formatters, performance optimizations, interactive mode, and schema-aware comparison.

- [xmlcompare Advanced Features Guide](#xmlcompare-advanced-features-guide)
  - [Output Formatters](#output-formatters)
    - [Available Formatters](#available-formatters)
      - [1. Text Format (default)](#1-text-format-default)
      - [2. JSON Format](#2-json-format)
      - [3. HTML Format (Side-by-side)](#3-html-format-side-by-side)
      - [4. Unified Diff Format](#4-unified-diff-format)
  - [Interactive Mode](#interactive-mode)
    - [Starting Interactive Mode](#starting-interactive-mode)
    - [Menu Options](#menu-options)
    - [Example Interactive Session](#example-interactive-session)
  - [Streaming Parser](#streaming-parser)
    - [Why Use Streaming?](#why-use-streaming)
    - [Using Streaming Mode](#using-streaming-mode)
    - [Performance Comparison](#performance-comparison)
    - [Limitations](#limitations)
  - [Schema-Aware Comparison](#schema-aware-comparison)
    - [Features](#features)
    - [Using Schema-Aware Comparison](#using-schema-aware-comparison)
    - [Example](#example)
  - [Plugin System](#plugin-system)
    - [Creating a Custom Formatter Plugin](#creating-a-custom-formatter-plugin)
    - [Registering Plugins](#registering-plugins)
    - [Available Plugin Types](#available-plugin-types)
  - [Combining Features](#combining-features)
    - [Example: Large File with HTML Output and Filtering](#example-large-file-with-html-output-and-filtering)
    - [Example: Interactive Exploration with Schema Validation](#example-interactive-exploration-with-schema-validation)
  - [Performance Tips](#performance-tips)
  - [Troubleshooting](#troubleshooting)
    - ["File not found" in interactive mode](#file-not-found-in-interactive-mode)
    - [HTML report not rendering properly](#html-report-not-rendering-properly)
    - [Streaming mode seems slow](#streaming-mode-seems-slow)
    - [Schema validation errors](#schema-validation-errors)
  - [See Also](#see-also)

---

## Output Formatters

xmlcompare supports multiple output formats for different use cases. Use the `--output-format` option to select a formatter.

### Available Formatters

#### 1. Text Format (default)

Human-readable text output with color support (TTY only).

```bash
xmlcompare --files file1.xml file2.xml --output-format text
```

**Output example:**

```shell
[ATTR] Path: /root/element1 - attribute 'id' value mismatch
  Expected : id="123"
  Actual   : id="124"

[TEXT] Path: /root/element2 - text value mismatch
  Expected : Hello World
  Actual   : Hello there
```

#### 2. JSON Format

Structured JSON output suitable for programmatic processing.

```bash
xmlcompare --files file1.xml file2.xml --output-format json
```

**Output example:**

```json
{
  "file1 vs file2": {
    "equal": false,
    "differences": [
      {
        "path": "/root/element1",
        "kind": "attr",
        "msg": "attribute 'id' value mismatch",
        "expected": "123",
        "actual": "124"
      }
    ]
  }
}
```

#### 3. HTML Format (Side-by-side)

Interactive HTML report with side-by-side comparison view.

```bash
xmlcompare --files file1.xml file2.xml --output-format html-diff --output-file report.html
```

**Features:**

- Two-column layout (expected vs actual)
- Color-coded differences (red for removed, green for added)
- Line numbers
- Self-contained CSS (works offline)
- Collapsible sections
- Summary statistics

#### 4. Unified Diff Format

Standard unified diff format (like `git diff --unified`).

```bash
xmlcompare --files file1.xml file2.xml --output-format unified-diff
```

**Output example:**

```shell
--- file1.xml
+++ file2.xml
@@ /root/element1 @@
- Expected value
+ Actual value
```

---

## Interactive Mode

Interactive mode provides a menu-driven interface for exploring and filtering comparison results without command-line options.

### Starting Interactive Mode

```bash
# Start in interactive mode
xmlcompare --interactive

# Or use the interactive mode command
python xmlcompare.py --interactive
```

### Menu Options

1. **View Differences** — Display all filtered differences with context
2. **Filter by Type** — Show only specific difference types (text, attr, tag, missing, extra)
3. **Filter by Path** — Show only differences matching a path substring (case-insensitive)
4. **Reset Filters** — Return to showing all differences
5. **Export Results** — Save filtered differences to text or JSON file
6. **Select New Files** — Choose different XML files to compare
7. **Exit** — Quit the program

### Example Interactive Session

```shell
============================================================
XML Comparison - Interactive Mode
============================================================

Select files to compare:
---------- ------- File 1 [or 'q' to quit]: orders_expected.xml
File 2 [or 'q' to quit]: orders_actual.xml

Comparing:
  orders_expected.xml
  orders_actual.xml

Performing comparison...
Found 12 differences

============================================================
Files: orders_expected.xml vs orders_actual.xml
Differences: 12 (filtered from 12 total)
============================================================
1. View differences
2. Filter by type
3. Filter by path
4. Reset filters
5. Export results
6. Select new files
0. Exit
---------- -------
Choose option: 2

Available difference types: attr, extra, missing, tag, text
Filter by type (or 'all' to reset): text
Filtered to 8 differences of type 'text'
```

---

## Streaming Parser

The streaming parser enables efficient comparison of large XML files (10MB+) with minimal memory usage.

### Why Use Streaming?

- **Memory Efficient**: Uses <50MB for 1GB files (vs 5GB for DOM parsing)
- **Linear Time**: Processes files incrementally
- **Scalable**: Handle extremely large files on resource-constrained systems

### Using Streaming Mode

```bash
# Compare large files with streaming parser
xmlcompare --files large_file_1.xml large_file_2.xml --stream
```

### Performance Comparison

| File Size | Memory (DOM) | Memory (Stream) | Speedup |
| --------- | ------------ | --------------- | ------- |
| 10 MB     | 50 MB        | 5 MB            | ~10x    |
| 100 MB    | 500 MB       | 15 MB           | ~30x    |
| 1 GB      | 5 GB         | 50 MB           | ~100x   |

### Limitations

- Streaming is slightlly slower due to incremental processing
- Not all comparison options work with streaming (e.g., unordered element comparison)
- For optimal results, use streaming only for files > 10MB

---

## Schema-Aware Comparison

Integrate XSD schemas to enable smarter, type-aware XML comparison.

### Features

- **Pre-validation**: Ensures XML files conform to schema before comparison
- **Type-Aware Matching**: Compares numeric, date, and other typed values more intelligently
- **Cardinality Hints**: Uses schema metadata to better understand element relationships
- **Improved Accuracy**: Reduces false positives when comparing typed data

### Using Schema-Aware Comparison

```bash
# Specify schema for pre-validation and type hints
xmlcompare --files data1.xml data2.xml --schema schema.xsd

# Use type-aware comparison (enhanced matching for typed data)
xmlcompare --files data1.xml data2.xml --schema schema.xsd --type-aware
```

### Example

Without schema:

```shell
[TEXT] Path: /order/amount - text value mismatch
  Expected : 100.0
  Actual   : 100.00
```

With `--type-aware` and schema (amount defined as xs:decimal):

```shell
[MATCH] Path: /order/amount - values equal (decimal comparison)
```

---

## Plugin System

Extend xmlcompare with custom formatters and difference filters via the plugin system.

### Creating a Custom Formatter Plugin

**Python Example:**

```python
from plugin_interface import FormatterPlugin

class CustomFormatter(FormatterPlugin):
    @property
    def name(self):
        return "my-formatter"  # Use with --output-format my-formatter

    def format(self, all_results, **kwargs):
        """Format comparison results as needed."""
        parts = []
        for key, val in all_results.items():
            if isinstance(val, str):
                parts.append(f"ERROR: {val}")
            else:
                diffs = val
                parts.append(f"Found {len(diffs)} differences in {key}")
        return "\n".join(parts)
```

**Java Example:**

```java
package com.example;
import com.xmlcompare.plugin.FormatterPlugin;
import com.xmlcompare.Difference;
import java.util.*;

public class CustomFormatter implements FormatterPlugin {
    @Override
    public String getName() {
        return "my-formatter";
    }

    @Override
    public String format(Map<String, Object> allResults, String label1, String label2) {
        // Format results as needed
        return "...";
    }
}
```

### Registering Plugins

**Programmatically:**

```python
from plugin_interface import get_registry, FormatterPlugin

my_formatter = MyFormatter()
get_registry().register_formatter(my_formatter)
```

**Via CLI (Java):**

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --plugins com.example.CustomFormatter
```

### Available Plugin Types

1. **FormatterPlugin** — Custom output formatters
2. **DifferenceFilter** — Custom difference filtering rules

---

## Combining Features

### Example: Large File with HTML Output and Filtering

```bash
# Compare large files with streaming, filter by element, output as HTML
xmlcompare --files large_1.xml large_2.xml \
           --stream \
           --output-format html-diff \
           --output-file large_comparison.html \
           --skip-keys "timestamp" "revision" \   # Skip these elements
           --ignore-attributes  # Ignore all attributes
```

### Example: Interactive Exploration with Schema Validation

```bash
# Start interactive mode with schema validation
xmlcompare --interactive --schema schema.xsd --type-aware
```

---

## Performance Tips

1. **Use `--stream` for files > 10MB** — Reduces memory up to 100x
2. **Use `--ignore-case` sparingly** — Adds 5-10% overhead
3. **Use `--structure-only` for quick validation** — Skip text/attribute comparison
4. **Combine filters**  — `--skip-keys` and `--ignore-attributes` reduce processing
5. **Use `--fail-fast`** — Stop on first difference for quick validation

---

## Troubleshooting

### "File not found" in interactive mode

Ensure the path exists and is readable. Use absolute paths or relative paths from the current working directory.

### HTML report not rendering properly

The HTML formatter generates self-contained files with inline CSS. If styles don't show, clear browser cache and revisit the file.

### Streaming mode seems slow

Streaming has slight overhead for small files. Use streaming only for files > 10MB.

### Schema validation errors

Ensure the XSD schema is correct and the XML files conform to it. Run with `--schema` and check error messages.

---

## See Also

- [README.md](README.md) — Usage guide and feature overview
- [PLUGINS.md](PLUGINS.md) — Plugin development guide
- [PERFORMANCE.md](PERFORMANCE.md) — Performance benchmarking
