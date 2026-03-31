# xmlcompare

A command-line tool for comparing XML files and directories, with flexible options for numeric tolerance, whitespace normalisation, namespace handling, attribute comparison, and more.

---

## Table of Contents

1. [Five-Minute Quickstart](#five-minute-quickstart)
2. [Getting Started with a Virtual Environment](#getting-started-with-a-virtual-environment)
3. [All Switches Reference](#all-switches-reference)
4. [Sample Files](#sample-files)
5. [Exit Codes](#exit-codes)
6. [Config File Support](#config-file-support)
7. [Running the Tests](#running-the-tests)

---

## Five-Minute Quickstart

### Prerequisites

- Python 3.8 or newer

### Install and run

```bash
# 1. Clone the repository
git clone https://github.com/pbaletkeman/xmlcompare.git
cd xmlcompare

# 2. Install dependencies
pip install -r requirements.txt

# 3. Compare two XML files (uses the bundled sample files)
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_equal.xml
# → Files are equal

python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_diff.xml
# → Lists all differences

# 4. Compare with --summary for a quick pass/fail count
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_diff.xml --summary
# → Total: 1 | Equal: 0 | Different: 1 | Errors: 0

# 5. Compare two directories
python xmlcompare.py --dirs samples/ samples/ --summary
# → Total: 7 | Equal: 7 | Different: 0 | Errors: 0
```

---

## Getting Started with a Virtual Environment

Using a virtual environment (venv) keeps dependencies isolated from the rest of your system.

```bash
# 1. Create a virtual environment named .venv
python -m venv .venv

# 2. Activate the environment
#    macOS / Linux:
source .venv/bin/activate
#    Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
#    Windows (Command Prompt):
.\.venv\Scripts\activate.bat

# 3. Install dependencies inside the venv
pip install -r requirements.txt

# 4. Run the tool
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_diff.xml

# 5. Deactivate when you are done
deactivate
```

---

## All Switches Reference

### Primary Input (one required)

| Switch | Argument | Description |
|--------|----------|-------------|
| `--files` | `FILE1 FILE2` | Compare two XML files side-by-side |
| `--dirs` | `DIR1 DIR2` | Compare every `.xml` file found in both directories |

### Directory Options

| Switch | Description |
|--------|-------------|
| `--recursive` | Recurse into sub-directories when using `--dirs` |

### Configuration File

| Switch | Argument | Description |
|--------|----------|-------------|
| `--config` | `FILE` | Load comparison options from a YAML or JSON file (see [Config File Support](#config-file-support)) |

### Comparison Behaviour

| Switch | Argument | Default | Description |
|--------|----------|---------|-------------|
| `--tolerance` | `FLOAT` | `0.0` | Allow numeric values to differ by up to this amount (e.g. `--tolerance 0.01`) |
| `--ignore-case` | — | off | Treat text content as case-insensitive |
| `--unordered` | — | off | Compare child elements as an unordered set (order-independent) |
| `--ignore-namespaces` | — | off | Strip XML namespace URIs before comparing tag names |
| `--ignore-attributes` | — | off | Skip attribute comparison entirely |

### Skip / Filter

| Switch | Argument | Description |
|--------|----------|-------------|
| `--skip-keys` | `PATH …` | One or more XPath-style paths to skip. Use `//tag` to skip a tag anywhere in the tree, or `parent/tag` for an exact path match |
| `--skip-pattern` | `REGEX` | Skip any element whose tag name matches the given regular expression |
| `--filter` | `XPATH` | Compare **only** elements that match this XPath expression (applied to both roots) |

### Output

| Switch | Argument | Default | Description |
|--------|----------|---------|-------------|
| `--output-format` | `text\|json\|html` | `text` | Format of the comparison report |
| `--output-file` | `FILE` | stdout | Write the report to a file instead of stdout |
| `--summary` | — | off | Print only a one-line pass/fail count |
| `--verbose` | — | off | Print each element path as it is compared (written to stderr) |
| `--quiet` | — | off | Suppress all output (useful in scripts — check the exit code instead) |
| `--fail-fast` | — | off | Stop after the first difference is found |

---

## Sample Files

The `samples/` directory contains ready-to-use XML files that demonstrate each major feature.

| File | Description |
|------|-------------|
| `orders_expected.xml` | Reference order document |
| `orders_actual_equal.xml` | Same data as expected (minor numeric/whitespace variations that normalise to equal) |
| `orders_actual_diff.xml` | Modified copy with intentional differences (status, email, qty, total) |
| `catalog_ns_a.xml` | Product catalogue using namespace `http://example.com/catalog/v1` |
| `catalog_ns_b.xml` | Same catalogue content using namespace `http://example.com/catalog/v2` |
| `readings_a.xml` | Sensor readings taken at 12:00 |
| `readings_b.xml` | Same sensors taken at 12:05 with slightly different values and timestamps |

### Example commands

```bash
# 1. No differences (numeric trailing-zero and whitespace normalisation)
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_equal.xml

# 2. Multiple differences shown in text format
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_diff.xml

# 3. Differences as JSON
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_diff.xml \
    --output-format json

# 4. Differences saved to an HTML report
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_diff.xml \
    --output-format html --output-file report.html

# 5. Namespaces cause tag mismatches by default …
python xmlcompare.py --files samples/catalog_ns_a.xml samples/catalog_ns_b.xml

# 6. … but --ignore-namespaces makes them equal
python xmlcompare.py --files samples/catalog_ns_a.xml samples/catalog_ns_b.xml \
    --ignore-namespaces

# 7. Sensor readings — skip timestamps, allow 0.005 tolerance on values
python xmlcompare.py --files samples/readings_a.xml samples/readings_b.xml \
    --skip-pattern "timestamp" --tolerance 0.005

# 8. Directory compare (self vs self — always equal)
python xmlcompare.py --dirs samples/ samples/ --summary

# 9. Unordered child comparison
python xmlcompare.py --files samples/readings_a.xml samples/readings_b.xml \
    --unordered --skip-pattern "timestamp" --tolerance 0.005

# 10. Quiet mode — use exit code in a shell script
python xmlcompare.py --files samples/orders_expected.xml samples/orders_actual_equal.xml \
    --quiet && echo "PASS" || echo "FAIL"
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All compared files are equal |
| `1` | One or more differences were found |
| `2` | An error occurred (file not found, invalid XML, bad arguments) |

---

## Config File Support

You can store comparison options in a YAML or JSON file and pass it with `--config`.

**Example `config.yaml`:**

```yaml
tolerance: 0.01
ignore_case: true
skip_keys:
  - //timestamp
  - //createdAt
output_format: json
```

**Example `config.json`:**

```json
{
  "tolerance": 0.01,
  "ignore_case": true,
  "skip_keys": ["//timestamp", "//createdAt"],
  "output_format": "json"
}
```

**Usage:**

```bash
python xmlcompare.py --files file1.xml file2.xml --config config.yaml
```

> **Note:** YAML config support requires the `pyyaml` package (included in `requirements.txt`).

Supported config keys mirror the CLI switches:

| Key | Type | CLI equivalent |
|-----|------|----------------|
| `tolerance` | float | `--tolerance` |
| `ignore_case` | bool | `--ignore-case` |
| `unordered` | bool | `--unordered` |
| `ignore_namespaces` | bool | `--ignore-namespaces` |
| `ignore_attributes` | bool | `--ignore-attributes` |
| `skip_keys` | list of strings | `--skip-keys` |
| `skip_pattern` | string | `--skip-pattern` |
| `filter` | string | `--filter` |
| `output_format` | string | `--output-format` |
| `output_file` | string | `--output-file` |
| `summary` | bool | `--summary` |
| `verbose` | bool | `--verbose` |
| `quiet` | bool | `--quiet` |
| `fail_fast` | bool | `--fail-fast` |

---

## Running the Tests

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pip install pytest-cov
pytest tests/ --cov=xmlcompare --cov-report=term-missing
```
