# xmlcompare – Python

A command-line tool for comparing XML files and directories, with flexible options for numeric tolerance, whitespace normalisation, namespace handling, attribute comparison, and more.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Build and Run Scripts](#build-and-run-scripts)
3. [All Switches Reference](#all-switches-reference)
4. [Sample Files](#sample-files)
5. [Exit Codes](#exit-codes)
6. [Config File Support](#config-file-support)
7. [Running the Tests](#running-the-tests)

---

## Quick Start

### Prerequisites

- Python 3.8 or newer

```bash
# Install dependencies and run tests
./build.sh          # Linux / macOS
build.bat           # Windows Command Prompt
.\build.ps1         # Windows PowerShell

# Run the tool
./run.sh --files samples/orders_expected.xml samples/orders_actual_equal.xml
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml --summary
```

---

## Build and Run Scripts

### Linux / macOS (bash)

| Script | Purpose |
|--------|---------|
| `build.sh` | Creates `.venv`, installs dependencies, runs tests |
| `run.sh [ARGS]` | Activates `.venv` and runs `xmlcompare.py` with given arguments |

### Windows Command Prompt (batch)

| Script | Purpose |
|--------|---------|
| `build.bat` | Creates `.venv`, installs dependencies, runs tests |
| `run.bat [ARGS]` | Activates `.venv` and runs `xmlcompare.py` with given arguments |

### Windows PowerShell

| Script | Purpose |
|--------|---------|
| `build.ps1` | Creates `.venv`, installs dependencies, runs tests |
| `run.ps1 [ARGS]` | Activates `.venv` and runs `xmlcompare.py` with given arguments |

### Example run commands

```bash
# Linux / macOS
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml --output-format json
./run.sh --dirs samples/ samples/ --summary
./run.sh --files samples/catalog_ns_a.xml samples/catalog_ns_b.xml --ignore-namespaces
./run.sh --files samples/readings_a.xml samples/readings_b.xml --skip-pattern "timestamp" --tolerance 0.005
```

```bat
REM Windows Command Prompt
run.bat --files samples\orders_expected.xml samples\orders_actual_diff.xml
run.bat --dirs samples\ samples\ --summary
```

```powershell
# Windows PowerShell
.\run.ps1 --files samples\orders_expected.xml samples\orders_actual_diff.xml
.\run.ps1 --dirs samples\ samples\ --summary
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
| `--config` | `FILE` | Load comparison options from a YAML or JSON file |

### Comparison Behaviour

| Switch | Argument | Default | Description |
|--------|----------|---------|-------------|
| `--tolerance` | `FLOAT` | `0.0` | Allow numeric values to differ by up to this amount |
| `--ignore-case` | — | off | Treat text content as case-insensitive |
| `--unordered` | — | off | Compare child elements as an unordered set |
| `--ignore-namespaces` | — | off | Strip XML namespace URIs before comparing tag names |
| `--ignore-attributes` | — | off | Skip attribute comparison entirely |

### Skip / Filter

| Switch | Argument | Description |
|--------|----------|-------------|
| `--skip-keys` | `PATH …` | XPath-style paths to skip (`//tag` or `parent/tag`) |
| `--skip-pattern` | `REGEX` | Skip elements whose tag name matches the regex |
| `--filter` | `XPATH` | Compare only elements matching this XPath expression |

### Output

| Switch | Argument | Default | Description |
|--------|----------|---------|-------------|
| `--output-format` | `text\|json\|html` | `text` | Format of the comparison report |
| `--output-file` | `FILE` | stdout | Write the report to a file |
| `--summary` | — | off | Print only a one-line pass/fail count |
| `--verbose` | — | off | Print each element path as it is compared (stderr) |
| `--quiet` | — | off | Suppress all output |
| `--fail-fast` | — | off | Stop after the first difference is found |

---

## Sample Files

| File | Description |
|------|-------------|
| `samples/orders_expected.xml` | Reference order document |
| `samples/orders_actual_equal.xml` | Same data as expected (normalises to equal) |
| `samples/orders_actual_diff.xml` | Modified copy with intentional differences |
| `samples/catalog_ns_a.xml` | Product catalogue using namespace `v1` |
| `samples/catalog_ns_b.xml` | Same catalogue using namespace `v2` |
| `samples/readings_a.xml` | Sensor readings at 12:00 |
| `samples/readings_b.xml` | Same sensors at 12:05 with slightly different values |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All compared files are equal |
| `1` | One or more differences were found |
| `2` | An error occurred (file not found, invalid XML, bad arguments) |

---

## Config File Support

```yaml
# config.yaml
tolerance: 0.01
ignore_case: true
skip_keys:
  - //timestamp
  - //createdAt
output_format: json
```

```json
{
  "tolerance": 0.01,
  "ignore_case": true,
  "skip_keys": ["//timestamp", "//createdAt"],
  "output_format": "json"
}
```

```bash
./run.sh --files file1.xml file2.xml --config config.yaml
```

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
# Install test dependencies (first time)
pip install -r requirements.txt
pip install pytest-cov

# Run all tests
pytest tests/

# Verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=xmlcompare --cov-report=term-missing
```
