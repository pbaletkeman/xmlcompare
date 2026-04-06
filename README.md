# Overview

- [Overview](#overview)
  - [Quick Navigation](#quick-navigation)
  - [Repository Structure](#repository-structure)
  - [Quick Start](#quick-start)
    - [🐍 Python](#-python)
      - [Build and test (Linux/macOS)](#build-and-test-linuxmacos)
      - [Build and test (Windows)](#build-and-test-windows)
    - [☕ Java](#-java)
  - [Feature Matrix](#feature-matrix)
  - [Basic Usage](#basic-usage)
    - [Simple File Comparison](#simple-file-comparison)
    - [Flexible Comparison](#flexible-comparison)
    - [Directory Comparison](#directory-comparison)
    - [Generate Report](#generate-report)
    - [Configuration File](#configuration-file)
  - [Command Reference](#command-reference)
  - [Exit Codes](#exit-codes)
  - [Configuration Files](#configuration-files)
  - [Performance](#performance)
    - [Python](#python)
    - [Java](#java)
  - [Code Quality](#code-quality)
    - [Python: Ruff Linting](#python-ruff-linting)
    - [Java: Checkstyle](#java-checkstyle)
  - [Testing](#testing)
  - [Documentation](#documentation)
  - [Common Use Cases](#common-use-cases)
  - [Getting Help](#getting-help)
  - [Contributing](#contributing)
  - [License](#license)

A powerful command-line tool for comparing XML files and directories with flexible options, available in both **Python 3.8+** and **Java 25** implementations with identical behavior.

[![CI](https://github.com/pbaletkeman/xmlcompare/workflows/CI/badge.svg)](https://github.com/pbaletkeman/xmlcompare/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pbaletkeman/xmlcompare/branch/main/graph/badge.svg)](https://codecov.io/gh/pbaletkeman/xmlcompare)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Java 25+](https://img.shields.io/badge/Java-25+-orange.svg)](https://www.oracle.com/java/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quick Navigation

## Repository Structure

```shell
xmlcompare/
├── python/              # Python 3.8+ implementation
│   ├── xmlcompare.py   # Main comparison engine
│   ├── docs/           # Python-specific documentation
│   ├── tests/          # 333 pytest tests
│   ├── README.md       # Python setup guide
│   └── build.sh|.bat|.ps1
│
├── java/                # Java 25 implementation
│   ├── src/            # picocli-based CLI
│   ├── docs/           # Java-specific documentation
│   ├── tests/          # 154 JUnit5 tests
│   ├── README.md       # Java setup guide
│   └── build.sh|.bat|.ps1
│
├── docs/                # Master documentation
│   ├── FEATURES.md     # Complete feature guide
│   ├── CLI_REFERENCE.md # (Symlinks to implementation versions)
│   └── CONFIG_GUIDE.md
│
├── config.json.example  # Documented config examples
├── samples/             # Sample XML files
├── CONTRIBUTING.md      # Contribution guidelines
├── PLUGINS.md          # Plugin development
├── PERFORMANCE.md      # Performance tuning
└── README.md           # This file
```

## Quick Start

### 🐍 Python

cd python

#### Build and test (Linux/macOS)

```shell
./build.sh
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml
```

#### Build and test (Windows)

```shell
build.bat
run.bat --files samples\orders_expected.xml samples\orders_actual_diff.xml
```

**Build a wheel:**

```bash
./wheel.sh              # dist/xmlcompare-1.0.0-py3-none-any.whl
```

See [Python README](python/README.md) for full documentation.

---

### ☕ Java

```bash
cd java

# Build and test (Linux/macOS)
./build.sh
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml

# Build and test (Windows)
build.bat
run.bat --files samples\orders_expected.xml samples\orders_actual_diff.xml
```

**Build a fat JAR:**

```bash
./fatjar.sh             # Maven (default)
./fatjar.sh gradle      # Gradle
```

See [Java README](java/README.md) for full documentation.

---

## Feature Matrix

| Feature                   | Python | Java | Details                            |
| ------------------------- | ------ | ---- | ---------------------------------  |
| File comparison           | ✅     | ✅   | Compare two XML files              |
| Directory comparison      | ✅     | ✅   | Compare all files in directories   |
| Numeric tolerance         | ✅     | ✅   | Fuzzy numeric matching (0.001)     |
| Case-insensitive          | ✅     | ✅   | Ignore letter case in text         |
| Unordered elements        | ✅     | ✅   | Compare in any order               |
| Namespace handling        | ✅     | ✅   | Ignore or normalize namespaces     |
| Skip elements             | ✅     | ✅   | Skip by tag, pattern, or XPath     |
| Text / JSON / HTML output | ✅     | ✅   | Multiple output formats            |
| Unified diff / HTML diff  | ✅     | ✅   | Standard and side-by-side diff     |
| Config file support       | ✅     | ✅   | JSON/YAML configuration            |
| Schema validation         | ✅     | ✅   | XSD pre-validation + type hints    |
| Type-aware comparison     | ✅     | ✅   | Date/numeric type matching         |
| Interactive CLI           | ✅     | ✅   | Menu-driven interface              |
| Parallel processing       | ✅     | ✅   | Multi-process/threaded comparison  |
| Streaming parser          | ✅     | ✅   | Memory-efficient large file mode   |
| Plugin system             | ✅     | ✅   | Extend via entry-points / SPI      |
| Performance benchmarks    | ✅     | ✅   | Built-in benchmarking suite        |
| Attribute-key unordered   | ✅     | ✅   | `--match-attr` for repeated elements |
| Diff-only output          | ✅     | ✅   | `--diff-only` suppress equal-pair output |
| Canonicalize              | ✅     | ✅   | `--canonicalize` strip comments/PIs |
| XSLT preprocessing        | ✅     | ✅   | `--xslt` transform before comparison |
| Incremental cache         | ✅     | ✅   | `--cache` skip unchanged pairs |
| REST API server           | ✅     | ❌   | Flask HTTP service (`api_server.py`) |
| ANSI color output         | ✅     | ✅   | Color-coded TTY text report |
| Swap direction            | ✅     | ✅   | `--swap` reverse expected/actual |
| No-color flag             | ✅     | ✅   | `--no-color` force disable color |
| .xmlignore auto-load      | ✅     | ✅   | Skip patterns from `.xmlignore` |

---

## Basic Usage

### Simple File Comparison

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml
```

### Flexible Comparison

```bash
# Ignore case and element order, allow 0.1% numeric variation
python xmlcompare.py --files file1.xml file2.xml \
  --ignore-case --unordered --tolerance 0.001
```

### Directory Comparison

```bash
# Compare all XML files in directories (recursive)
python xmlcompare.py --dirs dir1/ dir2/ --recursive --summary
```

### Generate Report

```bash
# Output as JSON to file
python xmlcompare.py --files file1.xml file2.xml \
  --output-format json --output-file result.json

# Generate interactive HTML report
python xmlcompare.py --files file1.xml file2.xml \
  --output-format html --output-file report.html
```

### Configuration File

```bash
# Create config.json
cat > config.json <<EOF
{
  "tolerance": 0.001,
  "ignore_case": true,
  "ignore_namespaces": true,
  "skip_keys": ["//timestamp", "//uuid"]
}
EOF

# Use configuration
python xmlcompare.py --files file1.xml file2.xml --config config.json
```

See [config.json.example](config.json.example) for more examples.

---

## Command Reference

**Quick Reference:**

```plaintext
--files FILE1 FILE2           Compare two files
--dirs DIR1 DIR2              Compare directories
--recursive                   Recursive directory scan
--tolerance FLOAT             Numeric variation (0.001)
--ignore-case                 Case-insensitive text
--unordered                   Ignore element order
--ignore-namespaces           Strip XML namespaces
--ignore-attributes           Skip attribute comparison
--skip-keys XPATH…            Skip specific elements
--skip-pattern REGEX          Skip elements matching regex
--filter XPATH                Compare only matching elements
--output-format FORMAT        text | json | html | unified-diff
--output-file FILE            Write report to file
--config FILE                 Load from config file
--structure-only              Compare structure only
--max-depth INT               Limit comparison depth
--summary                     Show count only
--fail-fast                   Stop at first difference
--verbose                     Detailed trace output
--quiet                       Suppress output
--match-attr ATTR             Attribute match key for --unordered
--diff-only                   Suppress equal-pair output
--canonicalize                Strip XML comments and PIs
--xslt FILE                   Apply XSLT transform before compare
--cache FILE                  Incremental cache for --dirs
--swap                        Swap file1/file2 direction
--no-color                    Disable ANSI color output
--help                        Show help
```

**Full reference:**

- [Python CLI Reference](python/docs/CLI_REFERENCE.md)
- [Java CLI Reference](java/docs/CLI_REFERENCE.md)

---

## Exit Codes

| Code  | Meaning                                   |
| ----- | ----------------------------------------- |
| **0** | Files are equal                           |
| **1** | Files differ                              |
| **2** | Error (file not found, invalid XML, etc.) |

---

## Configuration Files

Load settings from JSON or YAML config files:

**Example config.json:**

```json
{
  "tolerance": 0.001,
  "ignore_case": false,
  "unordered": true,
  "ignore_namespaces": true,
  "skip_keys": ["//timestamp", "//uuid"],
  "output_format": "json"
}
```

**Run with config:**

```bash
python xmlcompare.py --files file1.xml file2.xml --config config.json
java -jar xmlcompare.jar --files file1.xml file2.xml --config config.json
```

See [Configuration Guide](docs/CONFIG_GUIDE.md) for detailed examples.

---

## Performance

### Python

- **Speed:** 50-200ms for small files; scales with complexity
- **Memory:** ~10x file size
- **Ideal for:** Development, scripting, flexibility

### Java

- **Speed:** 100-300ms for small files (includes JVM startup)
- **Parallel Mode:** 2-3x faster on multi-core systems
- **Memory:** Configurable; parallel mode ~10x file size
- **Ideal for:** Production, large files, high throughput

**Recommendation:** Use Java for large files and frequent comparisons; Python for ad-hoc testing and scripting.

---

## Code Quality

### Python: Ruff Linting

- Fast linting with flake8-compatible rules
- 120-character line length limit
- Detects: unused imports, complexity, style issues

Run checks:

```bash
cd python && python -m ruff check .
```

### Java: Checkstyle

- Google-style code standards
- 120-character line length limit
- Enforced via Maven/Gradle

Run checks:

```bash
cd java && mvn checkstyle:check
# or
cd java && ./gradlew checkstyle
```

---

## Testing

**Python:** 333 passing tests (91% coverage)
**Java:** 154 passing tests
**Total:** 487 test cases

Run tests:

```bash
# Python
cd python && python -m pytest tests/

# Java
cd java && mvn test
# or
cd java && ./gradlew test
```

---

## Documentation

| Document                                                    | Purpose                              |
| ----------------------------------------------------------- | ------------------------------------ |
| [FEATURES.md](docs/FEATURES.md)                             | Complete feature guide with examples |
| [Python README](python/README.md)                           | Python setup and quick start         |
| [Java README](java/README.md)                               | Java setup and quick start           |
| [Python CLI Reference](python/docs/CLI_REFERENCE.md)        | All Python options and examples      |
| [Java CLI Reference](java/docs/CLI_REFERENCE.md)            | All Java options and examples        |
| [Configuration Guide](docs/CONFIG_GUIDE.md)                 | How to use config files              |
| [config.json.example](config.json.example)                  | Working config examples              |
| [CONTRIBUTING.md](CONTRIBUTING.md)                          | How to contribute                    |
| [PLUGINS.md](PLUGINS.md)                                    | Plugin development guide             |
| [PERFORMANCE.md](PERFORMANCE.md)                            | Performance optimization             |

---

## Common Use Cases

✅ **Test Automation** - Compare expected vs actual XML in test suites

✅ **Data Validation** - Verify XML data matches schema/expected format

✅ **ETL Verification** - Compare data before/after transformation

✅ **Config Management** - Detect changes in config files

✅ **Document Comparison** - Compare generated vs reference documents

✅ **CI/CD Integration** - Automated XML validation in pipelines

---

## Getting Help

- **GitHub Issues:** [pbaletkeman/xmlcompare](https://github.com/pbaletkeman/xmlcompare/issues)
- **Feature Requests:** Open an issue (see [CONTRIBUTING.md](CONTRIBUTING.md))
- **Questions:** Check [FEATURES.md](docs/FEATURES.md) or implementation READMEs

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas for contribution:**

- Bug reports and fixes
- Feature requests and implementations
- Documentation improvements
- Performance optimizations
- Plugin development

---

## License

MIT License - see [LICENSE](LICENSE) file.
