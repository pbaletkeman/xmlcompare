# xmlcompare Java - Complete CLI Reference Guide

This guide documents all command-line options and switches for the Java implementation of xmlcompare.

## Quick Reference

```bash
# Basic file comparison
java -jar xmlcompare.jar --files file1.xml file2.xml

# Directory comparison
java -jar xmlcompare.jar --dirs dir1/ dir2/ --recursive

# With config file
java -jar xmlcompare.jar --files file1.xml file2.xml --config config.json

# Generate JSON output
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format json

# Generate HTML report
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format html --output-file report.html

# Parallel comparison (experimental)
java -jar xmlcompare.jar --files file1.xml file2.xml --parallel --threads 8

# Help
java -jar xmlcompare.jar --help
```

---

## Input Options

### `--files FILE FILE` (required, unless using --dirs)
Compare two XML files.

**Usage:**
```bash
java -jar xmlcompare.jar --files expected.xml actual.xml
java -jar xmlcompare.jar --files /path/to/file1.xml /path/to/file2.xml
```

**Examples:**
- `--files file1.xml file2.xml`
- `--files samples/orders_expected.xml samples/orders_actual.xml`

---

### `--dirs DIR DIR` (required, unless using --files)
Compare two directories containing XML files.

**Usage:**
```bash
java -jar xmlcompare.jar --dirs dir1/ dir2/
java -jar xmlcompare.jar --dirs /path/to/dir1 /path/to/dir2
```

**Options with --dirs:**
- Combine with `--recursive` to traverse all subdirectories
- Only `.xml` files are compared
- Exit with status 1 if any file differs

---

### `--recursive`
When using `--dirs`, recurse into all subdirectories.

**Usage:**
```bash
java -jar xmlcompare.jar --dirs configs1/ configs2/ --recursive
```

**Without --recursive (default):**
- Only compares XML files in the top level of specified directories

**With --recursive:**
- Compares XML files in all subdirectories preserving relative paths

---

### `--config FILE`
Load comparison options from a JSON or YAML configuration file.

**Supported formats:**
- JSON: `config.json`
- YAML: `config.yaml`

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --config config.json
```

**Config file structure:**
```json
{
  "tolerance": 0.01,
  "ignoreCase": true,
  "unordered": true,
  "skipKeys": ["//timestamp"],
  "outputFormat": "json"
}
```

**Note:** Command-line options override config file values.

---

## Comparison Behavior Options

### `--tolerance FLOAT`
Numeric tolerance for comparing numeric values.

**Default:** `0.0` (exact match required)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --tolerance 0.01
```

**Examples:**
- `--tolerance 0.0` - Exact numeric match
- `--tolerance 0.001` - 0.1% tolerance
- `--tolerance 0.01` - 1% tolerance
- `--tolerance 0.1` - 10% tolerance

**How it works:**
- For values `a` and `b`, they are equal if `|a - b| <= tolerance`
- Text values are not affected; only numeric values

**Example values:**
- file1.xml: `<price>100.00</price>`
- file2.xml: `<price>100.50</price>`
- With `--tolerance 1.0`: Equal
- With `--tolerance 0.1`: Not equal

---

### `--ignore-case`
Compare text values case-insensitively.

**Default:** `false` (case-sensitive)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --ignore-case
```

**Examples:**

With `--ignore-case`:
```xml
<!-- file1.xml -->
<status>Active</status>

<!-- file2.xml -->
<status>ACTIVE</status>

<!-- Result: EQUAL -->
```

Without `--ignore-case`:
```xml
<!-- Same XML files -->
<!-- Result: NOT EQUAL (case mismatch) -->
```

---

### `--unordered`
Compare child elements in any order (not position-dependent).

**Default:** `false` (order matters)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --unordered
```

**Examples:**

With `--unordered`:
```xml
<!-- file1.xml -->
<root>
  <item>A</item>
  <item>B</item>
</root>

<!-- file2.xml -->
<root>
  <item>B</item>
  <item>A</item>
</root>

<!-- Result: EQUAL -->
```

Without `--unordered`:
```xml
<!-- Same XML files -->
<!-- Result: NOT EQUAL (different order) -->
```

---

### `--ignore-namespaces`
Ignore XML namespace URIs when comparing elements and attributes.

**Default:** `false` (namespaces matter)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --ignore-namespaces
```

**Examples:**

With `--ignore-namespaces`:
```xml
<!-- file1.xml -->
<root xmlns="http://example.com/v1">
  <name>John</name>
</root>

<!-- file2.xml -->
<root xmlns="http://example.com/v2">
  <name>John</name>
</root>

<!-- Result: EQUAL (namespace URIs ignored) -->
```

Without `--ignore-namespaces`:
```xml
<!-- Same XML files -->
<!-- Result: NOT EQUAL (different namespace URIs) -->
```

---

### `--ignore-attributes`
Ignore all XML attributes; compare only element structure and text content.

**Default:** `false` (attributes matter)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --ignore-attributes
```

**Examples:**

With `--ignore-attributes`:
```xml
<!-- file1.xml -->
<item id="1" status="active">Widget</item>

<!-- file2.xml -->
<item id="2" status="inactive">Widget</item>

<!-- Result: EQUAL (attributes ignored) -->
```

Without `--ignore-attributes`:
```xml
<!-- Same XML files -->
<!-- Result: NOT EQUAL (attribute differences detected) -->
```

---

### `--structure-only`
Compare only XML structure and element names; ignore text content and attributes.

**Default:** `false`

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --structure-only
```

**Examples:**

With `--structure-only`:
```xml
<!-- file1.xml -->
<root>
  <user id="1">Alice</user>
  <score>95</score>
</root>

<!-- file2.xml -->
<root>
  <user id="2">Bob</user>
  <score>87</score>
</root>

<!-- Result: EQUAL (same structure) -->
```

---

### `--max-depth INT`
Limit comparison depth (useful for deeply nested XML).

**Default:** unlimited

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --max-depth 5
```

**Examples:**
- `--max-depth 1` - Only compare root element
- `--max-depth 2` - Compare root and one level of children
- `--max-depth 5` - Compare up to 5 levels deep

---

## Filtering Options

### `--skip-keys PATH [PATH ...]`
Skip specific elements by path or tag name.

**Syntax:**
- `//tagname` - Skip elements with this tag name anywhere in the document
- `/path/to/element` - Skip element at this exact path

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-keys "//timestamp" "//uuid" "/root/metadata/version"
```

**Examples:**
```bash
# Skip timestamp elements anywhere
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-keys "//timestamp"

# Skip multiple elements (comma-separated for command line)
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-keys "//timestamp,//uuid,//transactionId"

# Skip by exact path
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-keys "/root/metadata/lastModified"
```

---

### `--skip-pattern REGEX`
Regular expression pattern to skip elements by tag name.

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-pattern "^(temp|debug|test).*$"
```

**Examples:**
```bash
# Skip tags starting with underscore
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-pattern "^_.*"

# Skip numeric tags
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-pattern "^\\d+$"

# Skip tags containing specific word
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-pattern ".*meta.*"
```

---

### `--filter XPATH`
XPath 1.0 expression to filter which elements to compare.

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --filter "//orders/order[status='active']"
```

**Examples:**
```bash
# Compare only active orders
java -jar xmlcompare.jar --files file1.xml file2.xml --filter "//order[status='active']"

# Compare specific node group
java -jar xmlcompare.jar --files file1.xml file2.xml --filter "//users/user[@id='user123']"
```

---

## Output Options

### `--output-format FORMAT`
Output format for comparison results.

**Options:** `text` (default), `json`, `html`, `html-diff`, `unified-diff`

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format json
```

#### `text` (default)
Human-readable text output with optional color.

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format text
```

Output:
```
[ATTR] Path: /root/item - attribute 'id' mismatch
  Expected : 123
  Actual   : 456
```

#### `json`
Structured JSON output for programmatic processing.

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format json
```

Output:
```json
{
  "file1.xml vs file2.xml": {
    "equal": false,
    "differences": [
      {
        "path": "/root/item",
        "kind": "attr",
        "message": "attribute 'id' mismatch",
        "expected": "123",
        "actual": "456"
      }
    ]
  }
}
```

#### `html` or `html-diff`
Interactive HTML report with side-by-side comparison.

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format html --output-file report.html
```

Features:
- Two-column layout (expected vs actual)
- Color-coded differences (red/green)
- Line numbers
- Collapsible sections
- Works offline

#### `unified-diff`
Standard unified diff format (like `git diff --unified`).

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format unified-diff
```

Output:
```
--- file1.xml
+++ file2.xml
@@ /root/item @@
- Expected value
+ Actual value
```

---

### `--output-file FILE`
Write output to a file instead of stdout.

**Default:** stdout

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-file results.txt
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format json --output-file results.json
```

---

### `--summary`
Print only summary (difference count) instead of detailed differences.

**Default:** `false` (print all differences)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --summary
```

Output:
```
Total differences: 3
```

---

### `--verbose`
Enable verbose output with additional diagnostic information.

**Default:** `false`

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --verbose
```

---

### `--quiet`
Suppress all output except exit code.

**Default:** `false`

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --quiet
echo $?  # Exit code only
```

---

## Flow Control Options

### `--fail-fast`
Stop comparison on the first difference found.

**Default:** `false` (compare entire documents)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --fail-fast
```

**Use case:** Quick check to see if files differ without analyzing all differences.

---

## Performance Options (Experimental)

### `--stream`
Use streaming parser for large files.

**Default:** `false` (standard DOM parsing)

**Usage:**
```bash
java -jar xmlcompare.jar --files large1.xml large2.xml --stream
```

**Benefits:**
- Reduced memory usage for large files
- Constant memory regardless of file size

**Trade-offs:**
- Slower processing than DOM parsing
- Currently a placeholder; full streaming implementation in progress

---

### `--parallel`
Use parallel processing for comparison.

**Default:** `false`

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --parallel
```

**Best for:**
- Large files (multi-GB)
- Multi-core systems

**Note:** Experimental feature; behavior may change.

---

### `--threads INT`
Number of threads for parallel processing.

**Default:** `4` (auto-detected based on available cores)

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --parallel --threads 8
```

**Note:** Only effective with `--parallel` flag.

---

## Advanced Options

### `--schema FILE`
Path to XSD schema file for schema-aware comparison.

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --schema schema.xsd
```

---

### `--plugins CLASS [CLASS ...]`
Load custom plugin classes at runtime.

**Usage:**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --plugins "com.example.CustomFilter"
```

**Multiple plugins (comma-separated):**
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --plugins "com.example.CustomFilter,com.example.Validator"
```

---

## Config File Examples

### Example 1: Basic Production Config
```json
{
  "tolerance": 0.001,
  "ignoreCase": false,
  "unordered": true,
  "ignoreNamespaces": true,
  "skipKeys": ["//timestamp", "//transactionId"],
  "outputFormat": "json",
  "outputFile": "results.json"
}
```

Command: `java -jar xmlcompare.jar --files test1.xml test2.xml --config config.json`

---

### Example 2: High-Performance Config
```json
{
  "tolerance": 0.001,
  "ignoreCase": true,
  "unordered": true,
  "ignoreNamespaces": true,
  "parallel": true,
  "threads": 8,
  "failFast": true
}
```

---

### Example 3: Strict Testing Config
```json
{
  "tolerance": 0.0,
  "ignoreCase": false,
  "unordered": false,
  "ignoreNamespaces": false,
  "ignoreAttributes": false,
  "structureOnly": false,
  "failFast": true,
  "outputFormat": "json"
}
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Files are equal |
| 1 | Files differ; differences found |
| 2 | Error (file not found, invalid XML, invalid arguments) |

---

## Help and Version

### `--help`
Display help message with all available options.

```bash
java -jar xmlcompare.jar --help
```

### `--version`
Display version information.

```bash
java -jar xmlcompare.jar --version
```

---

## Common Patterns

### Skip all metadata elements
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --skip-keys "//metadata,//timestamp,//version"
```

### Compare only structure
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --structure-only --ignore-attributes
```

### Flexible comparison
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --tolerance 0.001 --ignore-case --unordered --ignore-namespaces
```

### Generate machine-readable report
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format json --output-file report.json --quiet
```

### Interactive HTML report
```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output-format html --output-file comparison.html
```

### High-performance comparison
```bash
java -jar xmlcompare.jar --files huge1.xml huge2.xml --parallel --threads 16 --fail-fast
```

---

## Troubleshooting

### "File not found error"
Ensure the file path is correct and relative to your current working directory or use absolute paths.

```bash
# Relative path
java -jar xmlcompare.jar --files samples/test.xml samples/test2.xml

# Absolute path
java -jar xmlcompare.jar --files /absolute/path/test.xml /absolute/path/test2.xml
```

### "Invalid XML" error
The XML file is malformed. Check syntax using an XML validator:
```bash
xmllint test.xml  # Requires libxml2
```

### Config file not loading
Ensure JSON/YAML syntax is valid. Use an online JSON validator or:
```bash
python -c "import json; json.load(open('config.json'))"
```

### Parallel comparison not working
Ensure `--threads` value is reasonable for your system. Use `java.lang.Runtime.getRuntime().availableProcessors()` to determine optimal value.

---

## See Also

- [Java README](../README.md) - Installation and quick start
- [Root README](/README.md) - Project overview
- [FEATURES.md](FEATURES.md) - Advanced features including plugins and performance
- [config.json.example](/config.json.example) - Configuration file reference
