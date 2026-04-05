# xmlcompare – Complete Features Guide

Master features guide covering both Python and Java implementations of xmlcompare.

- [xmlcompare – Complete Features Guide](#xmlcompare--complete-features-guide)
  - [Quick Navigation](#quick-navigation)
  - [Feature Matrix: Python vs Java](#feature-matrix-python-vs-java)
    - [Core Comparison Features](#core-comparison-features)
    - [Output Formats](#output-formats)
    - [Advanced Features - Table](#advanced-features---table)
  - [Core Features Explained](#core-features-explained)
    - [1. File Comparison](#1-file-comparison)
    - [2. Directory Comparison](#2-directory-comparison)
    - [3. Flexible Comparison Options](#3-flexible-comparison-options)
      - [Numeric Tolerance](#numeric-tolerance)
      - [Case Insensitivity](#case-insensitivity)
      - [Unordered Comparison](#unordered-comparison)
      - [Namespace Handling](#namespace-handling)
    - [4. Element Filtering \& Skipping](#4-element-filtering--skipping)
      - [Skip Elements by Tag](#skip-elements-by-tag)
      - [Skip Elements by Pattern](#skip-elements-by-pattern)
      - [XPath Filtering](#xpath-filtering)
    - [5. Output Formats](#5-output-formats)
      - [Text (Default)](#text-default)
      - [JSON](#json)
      - [HTML](#html)
      - [Unified Diff](#unified-diff)
    - [6. Configuration Files](#6-configuration-files)
  - [Advanced Features](#advanced-features)
    - [Python Features](#python-features)
      - [Interactive Mode](#interactive-mode)
      - [Streaming Parser (Experimental)](#streaming-parser-experimental)
      - [Plugin System](#plugin-system)
      - [Performance Benchmarking](#performance-benchmarking)
    - [Java Features](#java-features)
      - [Parallel Processing (Experimental)](#parallel-processing-experimental)
      - [Streaming Parser (Experimental) SAX-based](#streaming-parser-experimental-sax-based)
      - [Plugin System (SPI)](#plugin-system-spi)
      - [High Performance](#high-performance)
  - [Schema-Aware Comparison](#schema-aware-comparison)
    - [Basic Usage](#basic-usage)
    - [Type-Aware Features](#type-aware-features)
  - [Exit Codes](#exit-codes)
  - [Common Use Cases \& Examples](#common-use-cases--examples)
    - [Use Case 1: Development/Testing](#use-case-1-developmenttesting)
    - [Use Case 2: Production Validation](#use-case-2-production-validation)
    - [Use Case 3: Batch Processing](#use-case-3-batch-processing)
    - [Use Case 4: CI/CD Integration](#use-case-4-cicd-integration)
    - [Use Case 5: Large File Comparison (Java)](#use-case-5-large-file-comparison-java)
    - [Use Case 6: Generate HTML Report](#use-case-6-generate-html-report)
  - [Comparison Language Support](#comparison-language-support)
  - [Performance Characteristics](#performance-characteristics)
    - [Python](#python)
    - [Java](#java)
  - [Integration Examples](#integration-examples)
    - [Shell Scripting](#shell-scripting)
    - [CI/CD Pipeline (GitHub Actions)](#cicd-pipeline-github-actions)
    - [Python Script Integration](#python-script-integration)
  - [Documentation](#documentation)
  - [Support \& Questions](#support--questions)

## Quick Navigation

- **[Python Features](../python/docs/FEATURES.md)** – Python-specific advanced features
- **[Java Features](../java/docs/FEATURES.md)** – Java-specific advanced features
- **[Python CLI Reference](../python/docs/CLI_REFERENCE.md)** – Complete Python command reference
- **[Java CLI Reference](../java/docs/CLI_REFERENCE.md)** – Complete Java command reference
- **[Configuration Guide](CONFIG_GUIDE.md)** – How to use configuration files
- **[config.json.example](../config.json.example)** – Configuration examples

---

## Feature Matrix: Python vs Java

### Core Comparison Features

| Feature                  | Python | Java | Notes                           |
|--------------------------|--------|------|---------------------------------|
| File comparison          | ✅     | ✅   | Compare two XML files           |
| Directory comparison     | ✅     | ✅   | Compare directory contents      |
| Recursive directory scan | ✅     | ✅   | Process subdirectories          |
| Numeric tolerance        | ✅     | ✅   | Fuzzy numeric matching          |
| Case-insensitive         | ✅     | ✅   | Ignore letter case              |
| Ordering flexibility     | ✅     | ✅   | Compare elements in any order   |
| Namespace handling       | ✅     | ✅   | Ignore or normalize namespaces  |
| Attribute comparison     | ✅     | ✅   | Compare or skip attributes      |
| Element filtering        | ✅     | ✅   | Skip specific elements          |
| XPath filtering          | ✅     | ✅   | Filter by XPath expression      |
| Depth limiting           | ✅     | ✅   | Limit comparison depth          |
| Structure-only mode      | ✅     | ✅   | Compare only structure          |
| Config file support      | ✅     | ✅   | Load settings from JSON/YAML    |

### Output Formats

| Format        | Python | Java | Purpose                          |
|---------------|--------|------|--------------------------------- |
| Text          | ✅     | ✅   | Human-readable with color        |
| JSON          | ✅     | ✅   | Machine-readable, scripting      |
| HTML          | ✅     | ✅   | Interactive side-by-side report  |
| Unified Diff  | ✅     | ✅   | Standard diff format             |

### Advanced Features - Table

| Feature                | Python | Java | Notes                        |
|------------------------|--------|------|----------------------------- |
| Interactive CLI        | ✅     | ✅   | Menu-driven interface        |
| Streaming parser       | ✅     | ✅   | Large file optimization      |
| Parallel processing    | ✅     | ✅   | Multi-threaded comparison    |
| Schema validation      | ✅     | ✅   | XSD schema support           |
| Type-aware comparison  | ✅     | ✅   | Date/numeric type hints      |
| Plugin system          | ✅     | ✅   | Extend via plugins/SPI       |
| Performance benchmarks | ✅     | ✅   | Built-in benchmarking        |

**Legend:** ✅ = Implemented

---

## Core Features Explained

### 1. File Comparison

Compare two XML files and detect all differences.

**Python:**

```bash
python xmlcompare.py --files file1.xml file2.xml
```

**Java:**

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml
```

**Detects:**

- Missing/extra elements
- Text content differences
- Attribute mismatches
- Structural changes

---

### 2. Directory Comparison

Compare all XML files in two directories.

**Python:**

```bash
python xmlcompare.py --dirs dir1/ dir2/ --recursive
```

**Java:**

```bash
java -jar xmlcompare.jar --dirs dir1/ dir2/ --recursive
```

**Features:**

- Recursive directory support
- File-by-file comparison
- Relative path preservation
- Summary statistics

---

### 3. Flexible Comparison Options

#### Numeric Tolerance

Handle minor numeric variations.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --tolerance 0.01

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --tolerance 0.01
```

**Example:**

- File1: `<value>99.99</value>`
- File2: `<value>100.00</value>`
- With `--tolerance 0.01`: EQUAL ✅

#### Case Insensitivity

Compare text ignoring letter case.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --ignore-case

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --ignore-case
```

**Example:**

- File1: `<status>Active</status>`
- File2: `<status>ACTIVE</status>`
- With `--ignore-case`: EQUAL ✅

#### Unordered Comparison

Compare child elements regardless of order.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --unordered

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --unordered
```

**Example:**

```xml
<!-- File 1 -->
<root>
  <item>A</item>
  <item>B</item>
</root>

<!-- File 2 -->
<root>
  <item>B</item>
  <item>A</item>
</root>

<!-- With --unordered: EQUAL ✅ -->
```

#### Namespace Handling

Ignore or normalize XML namespace URIs.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --ignore-namespaces

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --ignore-namespaces
```

---

### 4. Element Filtering & Skipping

#### Skip Elements by Tag

Skip comparison of specific elements matching tag names.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --skip-keys "//timestamp" "//uuid"

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-keys "//timestamp,//uuid"
```

#### Skip Elements by Pattern

Use regex to skip matching elements.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --skip-pattern "^(_|debug|temp).*"

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-pattern "^(_|debug|temp).*"
```

#### XPath Filtering

Compare only elements matching XPath expression.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --filter "//orders/order[status='active']"

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --filter "//orders/order[status='active']"
```

---

### 5. Output Formats

#### Text (Default)

Human-readable output with optional colors.

```plaintext
[ATTR] Path: /root/item/@id - attribute 'id' value mismatch
  Expected : 123
  Actual   : 456
```

#### JSON

Machine-readable structured output.

```json
{
  "equal": false,
  "differences": [
    {
      "path": "/root/item",
      "kind": "attr",
      "message": "attribute 'id' value mismatch"
    }
  ]
}
```

#### HTML

Interactive side-by-side comparison report.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --output-format html --output-file report.html

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format html --output-file report.html
```

#### Unified Diff

Standard diff format for integration with tools.

```shell
--- file1.xml
+++ file2.xml
@@ /root/item @@
- <id>123</id>
+ <id>456</id>
```

---

### 6. Configuration Files

Load settings from JSON or YAML config files.

**Python:**

```bash
python xmlcompare.py --files file1.xml file2.xml --config config.json
```

**Java:**

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --config config.json
```

**Example config.json:**

```json
{
  "tolerance": 0.001,
  "ignoreCase": false,
  "unordered": true,
  "ignoreNamespaces": true,
  "skipKeys": ["//timestamp", "//uuid"],
  "outputFormat": "json"
}
```

**See:** [Configuration Guide](CONFIG_GUIDE.md) for detailed examples.

---

## Advanced Features

### Python Features

#### Interactive Mode

Menu-driven interface for interactive comparisons.

```bash
python interactive_cli.py
```

- Select files/directories
- Configure options in real-time
- View results with navigation
- Save sessions and configurations

**See:** [Python FEATURES](../python/docs/FEATURES.md#interactive-mode)

#### Streaming Parser (Experimental)

Memory-efficient processing of large files.

- Constant memory regardless of file size
- SAX event-based parsing
- Trade-off: Slower than DOM parsing

**See:** [Python FEATURES](../python/docs/FEATURES.md#streaming-parser)

#### Plugin System

Extend comparison with Python modules.

```python
class CustomFilter(DifferenceFilter):
    def should_skip(self, path: str, tag: str) -> bool:
        return tag.startswith('_meta_')
```

**See:** [Python FEATURES](../python/docs/FEATURES.md#plugin-system)

#### Performance Benchmarking

Built-in benchmark suite for performance analysis.

```bash
python benchmark.py
```

**See:** [Python FEATURES](../python/docs/FEATURES.md#performance-benchmarking)

---

### Java Features

#### Parallel Processing (Experimental)

Multi-threaded comparison for improved performance.

```bash
java -jar xmlcompare.jar --files huge1.xml huge2.xml --parallel --threads 8
```

**Performance:** 2-3x speedup on multi-core systems for large files.

**See:** [Java FEATURES](../java/docs/FEATURES.md#parallel-processing-experimental)

#### Streaming Parser (Experimental) SAX-based

SAX-based streaming for constant memory usage.

```bash
java -jar xmlcompare.jar --files large.xml large2.xml --stream
```

**See:** [Java FEATURES](../java/docs/FEATURES.md#streaming-parser-experimental)

#### Plugin System (SPI)

Extend via Java Service Provider Interface.

```java
public class CustomPlugin implements ComparisonPluginSPI {
    public List<Difference> compareElements(Element e1, Element e2, ...) {
        // Custom logic
    }
}
```

**See:** [Java FEATURES](../java/docs/FEATURES.md#plugin-system)

#### High Performance

- Parallel processing
- Multi-core support
- Configurable memory
- Benchmark suite

**See:** [Java FEATURES](../java/docs/FEATURES.md#benchmarking)

---

## Schema-Aware Comparison

Both implementations support XSD schema-aware comparison with type hints.

### Basic Usage

**Python:**

```bash
python xmlcompare.py --files data1.xml data2.xml --schema schema.xsd
```

**Java:**

```bash
java -jar xmlcompare.jar --files data1.xml data2.xml --schema schema.xsd
```

### Type-Aware Features

1. **Date Normalization**

   ```shell
   2024-01-15 vs 01/15/2024 → EQUAL
   ```

2. **Numeric Precision**

   ```shell
   99.99 vs 99.990 → EQUAL (with xs:decimal)
   ```

3. **Boolean Normalization**

   ```shell
   true vs 1 → EQUAL (with xs:boolean)
   ```

4. **Enum Validation**

   ```shell
   Validates against allowed values
   ```

**See:**

- [Python Schema Analysis](../python/docs/FEATURES.md#schema-analysis--validation)
- [Java Schema Analysis](../java/docs/FEATURES.md#schema-analysis--validation)

---

## Exit Codes

Both implementations follow standard exit codes:

| Code  | Meaning                                   |
|------ | ----------------------------------------- |
| 0     | Files are equal                           |
| 1     | Files differ                              |
| 2     | Error (file not found, invalid XML, etc.) |

---

## Common Use Cases & Examples

### Use Case 1: Development/Testing

Flexible comparison during development.

```bash
# Python
python xmlcompare.py --files expected.xml actual.xml \
  --ignore-case --unordered --ignore-namespaces --tolerance 0.001

# Java
java -jar xmlcompare.jar --files expected.xml actual.xml \
  --ignore-case --unordered --ignore-namespaces --tolerance 0.001
```

### Use Case 2: Production Validation

Strict testing in production environments.

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml \
  --tolerance 0.0 --fail-fast --output-format json

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml \
  --tolerance 0.0 --fail-fast --output-format json
```

### Use Case 3: Batch Processing

Compare multiple files using configuration.

```bash
# Create config
cat > batch.json <<EOF
{
  "tolerance": 0.001,
  "ignoreNamespaces": true,
  "skipKeys": ["//timestamp"]
}
EOF

# Python: Compare all files
for file in expected/*.xml; do
  python xmlcompare.py --files "$file" "actual/$(basename $file)" --config batch.json
done

# Java: Compare all files
for file in expected/*.xml; do
  java -jar xmlcompare.jar --files "$file" "actual/$(basename $file)" --config batch.json
done
```

### Use Case 4: CI/CD Integration

Generate machine-readable JSON for CI/CD pipelines.

```bash
# Python
python xmlcompare.py --files test1.xml test2.xml --output-format json --output-file results.json

# Java
java -jar xmlcompare.jar --files test1.xml test2.xml --output-format json --output-file results.json
```

### Use Case 5: Large File Comparison (Java)

High-performance comparison with multiple cores.

```bash
java -Xmx4G -jar xmlcompare.jar \
  --files huge1.xml huge2.xml \
  --parallel --threads 8 \
  --summary
```

### Use Case 6: Generate HTML Report

Interactive comparison report for stakeholders.

```bash
# Python
python xmlcompare.py --files test1.xml test2.xml \
  --output-format html --output-file report.html

# Java
java -jar xmlcompare.jar --files test1.xml test2.xml \
  --output-format html --output-file report.html
```

---

## Comparison Language Support

- **Both Python & Java:** Identical behavior and output
- **Compatibility:** Cross-language comparison results are consistent
- **Performance:** Java typically 2-3x faster; Python more flexible

**Choose based on:**

- **Python:** Flexibility, plugins, development, easy scripting
- **Java:** Performance, parallelization, deployment stability

---

## Performance Characteristics

### Python

- **Small files (< 10MB):** 50-200ms
- **Medium files (10-100MB):** 500ms-2s
- **Large files:** Efficiency depends on configuration
- **Memory:** ~10x file size

### Java

- **Small files:** 100-300ms (JVM startup + comparison)
- **Medium files:** 500ms-1s (parallel): 200-400ms)
- **Large files:** 2-5x faster with parallel mode
- **Memory:** Configurable; parallel mode ~10x file size

**Recommendation:** Use Java for large/frequent comparisons; Python for ad-hoc/scripted use.

---

## Integration Examples

### Shell Scripting

```bash
#!/bin/bash

# Compare and generate report
python xmlcompare.py --files "$1" "$2" \
  --output-format json \
  --output-file result.json

# Check exit code
if [ $? -eq 0 ]; then
  echo "✓ Files are equal"
else
  echo "✗ Files differ"
  jq . result.json  # Pretty-print JSON
fi
```

### CI/CD Pipeline (GitHub Actions)

```yaml
- name: Compare XML Files
  run: |
    java -jar xmlcompare.jar \
      --files expected.xml actual.xml \
      --output-format json \
      --output-file comparison.json

- name: Check Results
  run: |
    if [ $? -ne 0 ]; then
      echo "XML validation failed"
      cat comparison.json
      exit 1
    fi
```

### Python Script Integration

```python
import subprocess
import json

result = subprocess.run(
    ['java', '-jar', 'xmlcompare.jar',
     '--files', 'test1.xml', 'test2.xml',
     '--output-format', 'json'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Files are equal")
else:
    data = json.loads(result.stdout)
    for diff in data['differences']:
        print(f"Difference: {diff['path']}")
```

---

## Documentation

- **[Python README](../python/README.md)** - Python-specific setup
- **[Java README](../java/README.md)** - Java-specific setup
- **[Root README](../README.md)** - Project overview
- **[Python CLI Reference](../python/docs/CLI_REFERENCE.md)** - All Python options
- **[Java CLI Reference](../java/docs/CLI_REFERENCE.md)** - All Java options
- **[Python Features](../python/docs/FEATURES.md)** - Advanced Python features
- **[Java Features](../java/docs/FEATURES.md)** - Advanced Java features
- **[Configuration Guide](CONFIG_GUIDE.md)** - Config file guide
- **[config.json.example](../config.json.example)** - Config examples

---

## Support & Questions

For issues, feature requests, or questions:

- GitHub Issues: [pbaletkeman/xmlcompare](https://github.com/pbaletkeman/xmlcompare/issues)
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines

---

**Version:** 1.0.0
**Last Updated:** 2026-04-04
**License:** MIT
