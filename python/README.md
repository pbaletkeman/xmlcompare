# xmlcompare – Python

Python 3.8+ implementation of xmlcompare with flexible XML comparison options.

---

## Quick Navigation

- **[Master Features Guide](../docs/FEATURES.md)** - All features and examples
- **[Complete CLI Reference](docs/CLI_REFERENCE.md)** - All switches documented
- **[Advanced Features](docs/FEATURES.md)** - Interactive mode, streaming, plugins
- **[Root README](../README.md)** - Project overview
- **[Java Implementation](../java/README.md)** - Java version

- [xmlcompare – Python](#xmlcompare--python)
  - [Quick Navigation](#quick-navigation)
  - [Quick Start](#quick-start)
  - [Usage](#usage)
    - [Basic file comparison](#basic-file-comparison)
    - [Directory comparison](#directory-comparison)
    - [With configuration file](#with-configuration-file)
    - [Output formats](#output-formats)
  - [Command-Line Reference](#command-line-reference)
  - [Configuration](#configuration)
  - [Features](#features)
  - [Testing](#testing)
  - [Contributing](#contributing)
  - [License](#license)
  - [Sample XML Files](#sample-xml-files)
  - [Examples](#examples)
  - [Testing with Python](#testing-with-python)
  - [Code Quality](#code-quality)
    - [Ruff Linting](#ruff-linting)
    - [XSD Validation](#xsd-validation)
  - [Documentation](#documentation)
  - [Next Steps](#next-steps)

---

## Quick Start

**Prerequisites:** Python 3.8+

```bash
# Build: create venv, install deps, run 167 tests
./build.sh          # Linux / macOS
./build.bat         # Windows
```

## Sample XML Files

| File                              | Description                |
| --------------------------------- | -------------------------- |
| `samples/orders_expected.xml`     | Reference document         |
| `samples/orders_actual_equal.xml` | Equal (normalized)         |
| `samples/orders_actual_diff.xml`  | With differences           |
| `samples/catalog_ns_*.xml`        | Namespace examples         |
| `samples/readings_*.xml`          | Numeric tolerance examples |

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

## Testing with Python

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
