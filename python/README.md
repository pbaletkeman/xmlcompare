# xmlcompare – Python

A command-line tool for comparing XML files and directories, with flexible options for numeric tolerance, whitespace normalisation, namespace handling, attribute comparison, and more.

---

- [xmlcompare – Python](#xmlcompare--python)
  - [Quick Start](#quick-start)
    - [Prerequisites](#prerequisites)
  - [Build and Run Scripts](#build-and-run-scripts)
    - [Linux / macOS (bash)](#linux--macos-bash)
    - [Windows Command Prompt (batch)](#windows-command-prompt-batch)
    - [Windows PowerShell](#windows-powershell)
    - [Example run commands](#example-run-commands)
  - [Building a Wheel](#building-a-wheel)
    - [Prerequisites](#prerequisites-1)
    - [Scripts](#scripts)
    - [Output](#output)
    - [Installing the wheel](#installing-the-wheel)
  - [All Switches Reference](#all-switches-reference)
    - [Primary Input (one required)](#primary-input-one-required)
    - [Directory Options](#directory-options)
    - [Configuration File](#configuration-file)
    - [Comparison Behaviour](#comparison-behaviour)
    - [Skip / Filter](#skip--filter)
    - [Output](#output-1)
  - [Sample Files](#sample-files)
  - [Exit Codes](#exit-codes)
  - [Config File Support](#config-file-support)
  - [Option Usage Examples](#option-usage-examples)
  - [Running the Tests](#running-the-tests)
  - [Code Quality](#code-quality)
    - [Ruff (Linting and Code Style)](#ruff-linting-and-code-style)
    - [XSD Validation](#xsd-validation)

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

## Building a Wheel

`pyproject.toml` defines the package metadata, entry point (`xmlcompare` CLI), and build backend. Use the dedicated wheel scripts to produce a distributable `.whl` file.

### Prerequisites

- Python 3.8 or newer
- Internet access on first run (to download `build` and `wheel` packages)

### Scripts

| Script | Platform | Usage |
|--------|----------|-------|
| `wheel.sh` | Linux / macOS | `./wheel.sh` |
| `wheel.bat` | Windows CMD | `wheel.bat` |
| `wheel.ps1` | Windows PowerShell | `.\wheel.ps1` |

Each script:
1. Creates (or reuses) a `.venv` virtual environment
2. Upgrades `pip`, `build`, and `wheel` inside the venv
3. Cleans any previous `dist/` and `xmlcompare.egg-info/` artefacts
4. Runs `python -m build --wheel`
5. Prints the path of the produced `.whl` file

### Output

```
dist/xmlcompare-1.0.0-py3-none-any.whl
```

### Installing the wheel

```bash
# Into the current Python environment
pip install dist/xmlcompare-1.0.0-py3-none-any.whl

# Then run directly
xmlcompare --files file1.xml file2.xml
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
| `--structure-only` | — | off | Compare only XML structure, ignoring text and attribute values |
| `--max-depth` | `INT` | unlimited | Limit comparison to elements at or above this depth (0=root only) |

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

All options (including `structure_only` and `max_depth`) can be set in YAML or JSON config files:

**YAML Example:**
```yaml
structure_only: true
max_depth: 2
unordered: true
tolerance: 0.01
ignore_case: true
skip_keys:
  - //timestamp
  - //createdAt
output_format: json
```

**JSON Example:**
```json
{
  "structure_only": true,
  "max_depth": 2,
  "unordered": true,
  "tolerance": 0.01,
  "ignore_case": true,
  "skip_keys": ["//timestamp", "//createdAt"],
  "output_format": "json"
}
```

Run with:
```bash
./run.sh --files file1.xml file2.xml --config config.yaml
```

---


---

## Option Usage Examples

- Structure-only comparison:
  ```bash
  ./run.sh --files file1.xml file2.xml --structure-only
  ```
- Max-depth limiting:
  ```bash
  ./run.sh --files file1.xml file2.xml --max-depth 2
  ```
- Combine both:
  ```bash
  ./run.sh --files file1.xml file2.xml --structure-only --max-depth 1
  ```
- With unordered:
  ```bash
  ./run.sh --files file1.xml file2.xml --unordered --max-depth 2
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

---

## Code Quality

### Ruff (Linting and Code Style)

The project uses [Ruff](https://github.com/astral-sh/ruff) for fast Python linting and code style validation with flake8-compatible rules and a 120-character line length limit.

**Run Ruff:**

```bash
# Lint the entire python/ directory
python -m ruff check python/

# Lint a specific file
python -m ruff check python/xmlcompare.py

# Auto-fix common issues (where possible)
python -m ruff check python/ --fix
```

**Configuration:**
- `ruff.toml` — Ruff configuration in the project root
- Enabled rule sets: `E` (pycodestyle errors), `F` (Pyflakes), `W` (pycodestyle warnings), `C90` (McCabe complexity)
- Line length: 120 characters (flake8 default is 79; configured to 120 for readability)
- Detects: unused imports, extraneous f-strings, code complexity, trailing whitespace, blank lines, and more

**Common violations:**
- `F401` — Unused imports
- `E701` — Multiple statements on one line
- `W291` — Trailing whitespace
- `C901` — Function too complex (McCabe complexity)

All production and test code must pass Ruff checks.

### XSD Validation

XSD (XML Schema Definition) validation is available as part of the testing suite. The `validate_xsd` module provides schema validation for both production and test code.

**Test XSD validation:**

```bash
# Run XSD validation tests
pytest tests/test_xsd_validation.py -v
```

**XSD Validation Files:**
- `tests/schema.xsd` — Example XSD schema
- `tests/valid.xml` — Example XML valid against the schema
- `tests/invalid.xml` — Example XML invalid against the schema

The `validate_xsd` module can be used programmatically:
```python
from validate_xsd import validate_xml

# Validates and raises ValueError if invalid
validate_xml("path/to/document.xml", "path/to/schema.xsd")
```
