# xmlcompare Python - Complete CLI Reference Guide

This guide documents all command-line options and switches for the Python implementation of xmlcompare.

## Quick Navigation

- [FEATURES.md](FEATURES.md) – Python-specific features
- [../docs/CONFIG_GUIDE.md](../../docs/CONFIG_GUIDE.md) – Configuration guide
- [../docs/FEATURES.md](../../docs/FEATURES.md) – Master feature matrix

---

## Usage

```bash
python xmlcompare.py --files file1.xml file2.xml [options]
```

## Options

| Flag                              | Default     | Description                                             |
| --------------------------------- | ----------- | ------------------------------------------------------- |
| `--files FILE1 FILE2`             |             | Compare two XML files                                   |
| `--dirs DIR1 DIR2`                |             | Compare two directories                                 |
| `--recursive`                     | false       | Recurse into subdirectories (with `--dirs`)             |
| `--config FILE`                   |             | Load settings from JSON/YAML config file                |
| `--tolerance FLOAT`               | 0.0         | Numeric tolerance ±δ for value comparison               |
| `--ignore-case`                   | false       | Case-insensitive text comparison                        |
| `--unordered`                     | false       | Ignore element order                                    |
| `--ignore-namespaces`             | false       | Ignore XML namespace URIs                               |
| `--ignore-attributes`             | false       | Ignore all XML attributes                               |
| `--structure-only`                | false       | Compare structure only (ignore text values)             |
| `--max-depth INT`                 | unlimited   | Limit traversal depth                                   |
| `--skip-keys PATH [PATH...]`      |             | Skip elements by path or tag name                       |
| `--skip-pattern REGEX`            |             | Skip elements whose tag matches regex                   |
| `--filter XPATH`                  |             | Compare only nodes matching XPath expression            |
| `--output-format FORMAT`          | text        | Output: `text`, `json`, `html`, `unified-diff`          |
| `--output-file FILE`              | stdout      | Write output to file                                    |
| `--summary`                       | false       | Print only difference count                             |
| `--verbose`                       | false       | Detailed element-by-element trace                       |
| `--quiet`                         | false       | Suppress all output (exit code only)                    |
| `--fail-fast`                     | false       | Stop on first detected difference                       |
| `--stream`                        | false       | Streaming parser (memory-efficient for large files)     |
| `--parallel`                      | false       | Parallel subtree comparison                             |
| `--threads INT`                   | CPU count-1 | Worker process count (with `--parallel`)                |
| `--interactive`                   | false       | Menu-driven interactive mode                            |
| `--schema FILE`                   |             | XSD schema file for pre-validation and type hints       |
| `--type-aware`                    | false       | Schema type hints for smarter comparison (needs `--schema`) |
| `--plugins MODULE [MODULE...]`    |             | Python module paths for custom plugins                  |
| `--match-attr ATTR`               |             | Attribute name used as match key for `--unordered`      |
| `--diff-only`                     | false       | Suppress output for equal file pairs                    |
| `--canonicalize`                  | false       | Strip XML comments and processing instructions          |
| `--xslt FILE`                     |             | Apply XSLT transform to both documents (requires lxml)  |
| `--cache FILE`                    |             | Incremental cache file for `--dirs` mode                |
| `--swap`                          | false       | Swap file1 and file2 (reverse expected/actual)          |
| `--no-color`                      | false       | Disable ANSI color output                               |
| `--help`                          |             | Show help message                                       |

## Examples

### Compare two files

```bash
python xmlcompare.py --files a.xml b.xml
```

### Compare directories

```bash
python xmlcompare.py --dirs old/ new/
```

### Compare directories recursively

```bash
python xmlcompare.py --dirs old/ new/ --recursive
```

### Use a config file

```bash
python xmlcompare.py --files a.xml b.xml --config config.json
```

### Output as JSON

```bash
python xmlcompare.py --files a.xml b.xml --output-format json
```

### Output as HTML report

```bash
python xmlcompare.py --files a.xml b.xml --output-format html --output-file report.html
```

### Parallel processing

```bash
python xmlcompare.py --files a.xml b.xml --parallel --threads 4
```

### Streaming parser

```bash
python xmlcompare.py --files a.xml b.xml --stream
```

### Schema validation

```bash
python xmlcompare.py --files a.xml b.xml --schema schema.xsd
```

### Custom plugins

```bash
python xmlcompare.py --files a.xml b.xml --plugins mypkg.myplugin
```

### XPath filter

```bash
python xmlcompare.py --files a.xml b.xml --filter "//orders/order[status='active']"
```

### Skip elements

```bash
python xmlcompare.py --files a.xml b.xml --skip-keys "//timestamp" "//uuid"
```

### Skip by regex pattern

```bash
python xmlcompare.py --files a.xml b.xml --skip-pattern "^(temp|debug).*$"
```

### Ignore attributes

```bash
python xmlcompare.py --files a.xml b.xml --ignore-attributes
```

### Structure-only mode

```bash
python xmlcompare.py --files a.xml b.xml --structure-only
```

### Limit depth

```bash
python xmlcompare.py --files a.xml b.xml --max-depth 3
```

### Interactive mode

```bash
python xmlcompare.py --interactive
```

---

### `--ignore-case`

Compare text values case-insensitively.

**Default:** `false` (case-sensitive)

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --ignore-case
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
python xmlcompare.py --files file1.xml file2.xml --unordered
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
python xmlcompare.py --files file1.xml file2.xml --ignore-namespaces
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
python xmlcompare.py --files file1.xml file2.xml --ignore-attributes
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
python xmlcompare.py --files file1.xml file2.xml --structure-only
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

**Default:** `null` (unlimited)

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --max-depth 5
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
python xmlcompare.py --files file1.xml file2.xml --skip-keys "//timestamp" "//uuid" "/root/metadata/version"
```

**Examples:**

```bash
# Skip timestamp elements anywhere
python xmlcompare.py --files file1.xml file2.xml --skip-keys "//timestamp"

# Skip multiple elements
python xmlcompare.py --files file1.xml file2.xml --skip-keys "//timestamp" "//uuid" "//transactionId"

# Skip by exact path
python xmlcompare.py --files file1.xml file2.xml --skip-keys "/root/metadata/lastModified"

# Mix both approaches
python xmlcompare.py --files file1.xml file2.xml --skip-keys "//temp" "/root/debug/info"
```

---

### `--skip-pattern REGEX`

Regular expression pattern to skip elements by tag name.

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --skip-pattern "^(temp|debug|test).*$"
```

**Examples:**

```bash
# Skip tags starting with underscore
python xmlcompare.py --files file1.xml file2.xml --skip-pattern "^_.*"

# Skip numeric tags
python xmlcompare.py --files file1.xml file2.xml --skip-pattern "^\\d+$"

# Skip tags containing specific word
python xmlcompare.py --files file1.xml file2.xml --skip-pattern ".*meta.*"
```

---

### `--filter XPATH`

XPath expression to filter which elements to compare.

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --filter "//orders/order[status='active']"
```

**Examples:**

```bash
# Compare only active orders
python xmlcompare.py --files file1.xml file2.xml --filter "//order[status='active']"

# Compare orders with total > 1000
python xmlcompare.py --files file1.xml file2.xml --filter "//order[total > 1000]"

# Compare specific user's data
python xmlcompare.py --files file1.xml file2.xml --filter "//users/user[@id='user123']"
```

---

## Output Options

### `--output-format FORMAT`

Output format for comparison results.

**Options:** `text` (default), `json`, `html`, `html-diff`, `unified-diff`

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format json
```

#### `text` (default)

Human-readable text output with color (if TTY).

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format text
```

Output:

```shell
[ATTR] Path: /root/item - attribute 'id' mismatch
  Expected : 123
  Actual   : 456
```

#### `json`

Structured JSON output for programmatic processing.

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format json
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
python xmlcompare.py --files file1.xml file2.xml --output-format html --output-file report.html
```

Features:

- Two-column layout (expected vs actual)
- Color-coded differences
- Line numbers
- Collapsible sections
- Works offline

#### `unified-diff`

Standard unified diff format (like `git diff --unified`).

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format unified-diff
```

Output:

```shell
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
python xmlcompare.py --files file1.xml file2.xml --output-file results.txt
python xmlcompare.py --files file1.xml file2.xml --output-format json --output-file results.json
```

---

### `--summary`

Print only summary (difference count) instead of detailed differences.

**Default:** `false` (print all differences)

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --summary
```

Output:

```shell
Total differences: 3
```

---

### `--verbose`

Enable verbose output with additional diagnostic information.

**Default:** `false`

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --verbose
```

---

### `--quiet`

Suppress all output except exit code.

**Default:** `false`

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --quiet
echo $?  # Exit code only
```

---

## Flow Control Options

### `--fail-fast`

Stop comparison on the first difference found.

**Default:** `false` (compare entire documents)

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --fail-fast
```

**Use case:** Quick check to see if files differ without analyzing all differences.

---

## Advanced Options (Phase 1 Features)

### `--schema FILE`

Path to XSD schema file for schema-aware comparison.

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --schema schema.xsd
```

---

### Type-Aware Comparison

Comparison using schema type hints (currently in `schema_analyzer.py`).

**Features:**

- Date value normalization
- Numeric type handling
- Boolean comparison
- Enum validation

---

## Config File Examples

### Example 1: Basic Production Config

```json
{
  "tolerance": 0.001,
  "ignore_case": false,
  "unordered": true,
  "ignore_namespaces": true,
  "skip_keys": ["//timestamp", "//transactionId"],
  "output_format": "json",
  "output_file": "results.json"
}
```

Command: `python xmlcompare.py --files test1.xml test2.xml --config config.json`

---

### Example 2: Flexible Development Config

```json
{
  "tolerance": 0.01,
  "ignore_case": true,
  "unordered": true,
  "ignore_namespaces": true,
  "ignore_attributes": false,
  "skip_pattern": "^(temp|debug).*$",
  "verbose": true,
  "summary": false
}
```

---

### Example 3: Strict Testing Config

```json
{
  "tolerance": 0.0,
  "ignore_case": false,
  "unordered": false,
  "ignore_namespaces": false,
  "ignore_attributes": false,
  "structure_only": false,
  "fail_fast": true
}
```

---

## Exit Codes

| Code  | Meaning                                                |
| ----- | ------------------------------------------------------ |
| 0     | Files are equal                                        |
| 1     | Files differ; differences found                        |
| 2     | Error (file not found, invalid XML, invalid arguments) |

---

## Common Patterns

### Skip all metadata elements

```bash
python xmlcompare.py --files file1.xml file2.xml --skip-keys "//metadata" "//timestamp" "//version"
```

### Compare only structure

```bash
python xmlcompare.py --files file1.xml file2.xml --structure-only --ignore-attributes
```

### Flexible comparison

```bash
python xmlcompare.py --files file1.xml file2.xml --tolerance 0.001 --ignore-case --unordered --ignore-namespaces
```

### Generate machine-readable report

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format json --output-file report.json --quiet
```

### Interactive HTML report

```bash
python xmlcompare.py --files file1.xml file2.xml --output-format html --output-file comparison.html
```

---

## Troubleshooting

### "File not found error"

Ensure the file path is correct and relative to your current working directory or use absolute paths.

```bash
# Relative path
python xmlcompare.py --files samples/test.xml samples/test2.xml

# Absolute path
python xmlcompare.py --files /absolute/path/test.xml /absolute/path/test2.xml
```

### "Invalid XML" error

The XML file is malformed. Check syntax using an XML validator:

```bash
xmllint test.xml  # Requires libxml2
```

### Config file not loading

Ensure JSON/YAML syntax is valid:

```bash
python -m json.tool config.json  # Validate JSON
```

---

## See Also

- [Python README](../README.md) - Installation and quick start
- [Root README](/README.md) - Project overview
- [FEATURES.md](FEATURES.md) - Advanced features including interactive mode and plugins
- [config.json.example](/config.json.example) - Configuration file reference
