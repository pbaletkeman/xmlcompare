# xmlcompare – Python

Python 3.8+ implementation of xmlcompare with flexible XML comparison options.

---

## Quick Navigation

- **[Master Features Guide](../docs/FEATURES.md)** - All features and examples
- **[Complete CLI Reference](docs/CLI_REFERENCE.md)** - All switches documented
- **[Advanced Features](docs/FEATURES.md)** - Interactive mode, streaming, plugins
- **[Root README](../README.md)** - Project overview
- **[Java Implementation](../java/README.md)** - Java version

---

## Quick Start

**Prerequisites:** Python 3.8+

```bash
# Build: create venv, install deps, run 167 tests
./build.sh          # Linux / macOS
build.bat           # Windows CMD
.\build.ps1         # Windows PowerShell

# Run examples
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml
./run.sh --files samples/readings_a.xml samples/readings_b.xml --tolerance 0.005
```

---

## Build and Run Scripts

| Script | Platform | Purpose |
|--------|----------|---------|
| `build.sh / build.bat / build.ps1` | All | Setup venv, install deps, run tests |
| `run.sh / run.bat / run.ps1` | All | Activate venv and run xmlcompare |

**Usage:**
```bash
./run.sh --files file1.xml file2.xml [OPTIONS]
./run.sh --dirs dir1/ dir2/ --recursive [OPTIONS]
```

---

## Building a Wheel

Create a distributable Python package:

```bash
./wheel.sh          # Linux / macOS  → dist/xmlcompare-1.0.0-py3-none-any.whl
wheel.bat           # Windows CMD
.\wheel.ps1         # Windows PowerShell

# Install and use globally
pip install dist/xmlcompare-1.0.0-py3-none-any.whl
xmlcompare --files file1.xml file2.xml
```

---

## Command Reference

**Input (choose one):**
- `--files FILE1 FILE2` - Compare two files
- `--dirs DIR1 DIR2` - Compare directories
- `--recursive` - Include subdirectories

**Comparison options:**
- `--tolerance FLOAT` - Numeric variation (default: 0.0)
- `--ignore-case` - Case-insensitive text
- `--unordered` - Ignore element order
- `--ignore-namespaces` - Strip XML namespaces
- `--ignore-attributes` - Skip attribute comparison
- `--structure-only` - Compare structure only
- `--max-depth INT` - Limit comparison depth

**Filtering:**
- `--skip-keys XPATH…` - Skip specific elements
- `--skip-pattern REGEX` - Skip elements matching regex
- `--filter XPATH` - Compare only matching elements

**Output:**
- `--output-format text|json|html` - Report format (default: text)
- `--output-file FILE` - Write to file
- `--summary` - Count only
- `--verbose` - Trace output
- `--quiet` - Suppress output
- `--fail-fast` - Stop at first difference

**Configuration:**
- `--config FILE` - Load from YAML/JSON config file

**Full reference:** See [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md)

---

## Exit Codes

| Code | Meaning |
|------|---------|
| **0** | Files are equal |
| **1** | Files differ |
| **2** | Error (file not found, invalid XML, etc.) |

---

## Configuration Files

Load settings from JSON or YAML:

**Example config.json:**
```json
{
  "tolerance": 0.001,
  "ignoreCase": true,
  "unordered": true,
  "ignoreNamespaces": true,
  "skipKeys": ["//timestamp"],
  "outputFormat": "json"
}
```

**Usage:**
```bash
./run.sh --files file1.xml file2.xml --config config.json
```

See [../config.json.example](../config.json.example) for more examples.

---

## Sample XML Files

| File | Description |
|------|-------------|
| `samples/orders_expected.xml` | Reference document |
| `samples/orders_actual_equal.xml` | Equal (normalized) |
| `samples/orders_actual_diff.xml` | With differences |
| `samples/catalog_ns_*.xml` | Namespace examples |
| `samples/readings_*.xml` | Numeric tolerance examples |

---

## Examples

```bash
# Basic comparison
./run.sh --files file1.xml file2.xml

# Flexible matching
./run.sh --files file1.xml file2.xml --ignore-case --unordered --tolerance 0.001

# Directory with filters
./run.sh --dirs dir1/ dir2/ --recursive --skip-pattern "^_.*"

# JSON report
./run.sh --files file1.xml file2.xml --output-format json --output-file result.json

# HTML report
./run.sh --files file1.xml file2.xml --output-format html --output-file report.html

# Configuration file
./run.sh --files file1.xml file2.xml --config config.json
```

---

## Testing

```bash
# Run all tests (167 tests)
pytest tests/

# Verbose with coverage
pytest tests/ -v --cov=xmlcompare --cov-report=term-missing

# Run specific test file
pytest tests/test_xsd_validation.py -v
```

---

## Code Quality

### Ruff Linting

Python code style is enforced with [Ruff](https://github.com/astral-sh/ruff):

```bash
# Check all code
python -m ruff check .

# Auto-fix issues
python -m ruff check . --fix
```

**Configuration:** `ruff.toml` - Uses flake8-compatible rules, 120-character line length.

### XSD Validation

Schema validation is available and tested:

```bash
# Run schema validation tests
pytest tests/test_xsd_validation.py -v

# Use programmatically
from validate_xsd import validate_xml
validate_xml("document.xml", "schema.xsd")  # Raises ValueError if invalid
```

---

## Documentation

- **[Complete Features Guide](../docs/FEATURES.md)** - All features with examples
- **[CLI Reference](docs/CLI_REFERENCE.md)** - All switches and examples
- **[Advanced Features](docs/FEATURES.md)** - Interactive mode, streaming, plugins, benchmarks
- **[Configuration Guide](../docs/CONFIG_GUIDE.md)** - Config file guide
- **[Root README](../README.md)** - Project overview

---

## Next Steps

- 📘 See [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md) for all command options with examples
- 🚀 See [docs/FEATURES.md](docs/FEATURES.md) for advanced features (interactive mode, streaming, plugins)
- ☕ Check [../java/README.md](../java/README.md) for Java implementation
- 📋 See [../CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines

---

**Python Tests:** 167 passing
**Tools:** pytest, Ruff, XSD validation
**License:** MIT
