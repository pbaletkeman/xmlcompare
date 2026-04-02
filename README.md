# xmlcompare

- [xmlcompare](#xmlcompare)
  - [Repository Structure](#repository-structure)
  - [Quick Start](#quick-start)
    - [Python](#python)
      - [Build a wheel](#build-a-wheel)
    - [Java](#java)
      - [Build a fat JAR](#build-a-fat-jar)
  - [Features](#features)
      - [Option Details](#option-details)
  - [Exit Codes](#exit-codes)
  - [Sample Files](#sample-files)
  - [Example Commands](#example-commands)
  - [Config File Support](#config-file-support)
  - [Code Quality Standards](#code-quality-standards)
    - [Java: Checkstyle](#java-checkstyle)
    - [Python: Ruff](#python-ruff)
    - [XSD Schema Validation](#xsd-schema-validation)
  - [Edge Cases and Advanced Topics](#edge-cases-and-advanced-topics)
    - [Numeric Normalization](#numeric-normalization)
    - [Large Files](#large-files)
    - [Complex Namespaces](#complex-namespaces)
    - [Deeply Nested XML](#deeply-nested-xml)
    - [Special Characters and Encoding](#special-characters-and-encoding)
    - [Mixed Content](#mixed-content)
    - [Config File with Complex Options](#config-file-with-complex-options)
    - [Performance Tips](#performance-tips)
    - [Error Handling](#error-handling)
    - [XML Security (XXE Prevention)](#xml-security-xxe-prevention)
  - [Contributing](#contributing)
  - [License](#license)


---

[![CI](https://github.com/pbaletkeman/xmlcompare/workflows/CI/badge.svg)](https://github.com/pbaletkeman/xmlcompare/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pbaletkeman/xmlcompare/branch/main/graph/badge.svg)](https://codecov.io/gh/pbaletkeman/xmlcompare)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Java 21+](https://img.shields.io/badge/Java-21+-orange.svg)](https://www.oracle.com/java/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A command-line tool for comparing XML files and directories, available in both **Python** and **Java 21** implementations with identical behaviour.

---

## Repository Structure

```
xmlcompare/
├── python/          # Python 3.8+ implementation
│   ├── xmlcompare.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── tests/
│   ├── samples/
│   ├── build.sh  / build.bat  / build.ps1
│   ├── wheel.sh  / wheel.bat  / wheel.ps1
│   ├── run.sh    / run.bat    / run.ps1
│   └── README.md
├── java/            # Java 21 implementation (Gradle + Maven)
│   ├── src/
│   ├── samples/
│   ├── build.gradle / pom.xml
│   ├── build.sh    / build.bat    / build.ps1
│   ├── fatjar.sh   / fatjar.bat   / fatjar.ps1
│   ├── run.sh      / run.bat      / run.ps1
│   └── README.md
└── samples/         # Original shared XML sample files
```

---

## Quick Start

### Python

```bash
cd python

# Linux / macOS
./build.sh                      # create venv, install deps, run tests
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml

# Windows Command Prompt
build.bat
run.bat --files samples\orders_expected.xml samples\orders_actual_diff.xml

# Windows PowerShell
.\build.ps1
.\run.ps1 --files samples\orders_expected.xml samples\orders_actual_diff.xml
```

#### Build a wheel

```bash
cd python

./wheel.sh          # Linux / macOS  → dist/xmlcompare-1.0.0-py3-none-any.whl
wheel.bat           # Windows CMD
.\wheel.ps1         # Windows PowerShell
```

See [`python/README.md`](python/README.md) for full Python documentation.

---

### Java

```bash
cd java

# Linux / macOS
./build.sh                      # compile + test with both Gradle and Maven
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml

# Windows Command Prompt
build.bat
run.bat --files samples\orders_expected.xml samples\orders_actual_diff.xml

# Windows PowerShell
.\build.ps1
.\run.ps1 --files samples\orders_expected.xml samples\orders_actual_diff.xml
```

#### Build a fat JAR

```bash
cd java

# Maven (default) — target/xmlcompare-1.0.0.jar
./fatjar.sh             # Linux / macOS
fatjar.bat              # Windows CMD
.\fatjar.ps1            # Windows PowerShell

# Gradle — build/libs/xmlcompare-1.0.0.jar
./fatjar.sh gradle
fatjar.bat gradle
.\fatjar.ps1 -BuildTool gradle
```

See [`java/README.md`](java/README.md) for full Java documentation.

---


## Features

Both implementations share the same feature set:

| Feature | Switch |
|---------|--------|
| Compare two XML files | `--files FILE1 FILE2` |
| Compare directories | `--dirs DIR1 DIR2` |
| Recursive directory traversal | `--recursive` |
| Numeric tolerance | `--tolerance FLOAT` |
| Case-insensitive comparison | `--ignore-case` |
| Unordered child elements | `--unordered` |
| Strip XML namespaces | `--ignore-namespaces` |
| Skip attribute comparison | `--ignore-attributes` |
| Skip specific elements | `--skip-keys PATH…` |
| Skip by tag pattern | `--skip-pattern REGEX` |
| Filter by XPath | `--filter XPATH` |
| Text / JSON / HTML output | `--output-format text\|json\|html` |
| Write report to file | `--output-file FILE` |
| Summary count only | `--summary` |
| Verbose trace | `--verbose` |
| Quiet mode | `--quiet` |
| Stop on first difference | `--fail-fast` |
| Load options from config file | `--config FILE` |
| Structure-only comparison | `--structure-only` |
| Limit comparison depth | `--max-depth INT` |

---


---

#### Option Details

- `--structure-only`: Compares only XML element structure, ignoring all text and attribute values. Detects missing/extra elements, tag mismatches, and hierarchy differences.
    - Example:
      ```bash
      python xmlcompare.py --files file1.xml file2.xml --structure-only
      java -jar xmlcompare.jar --files file1.xml file2.xml --structure-only
      ```

- `--max-depth INT`: Limits comparison to elements at or above the specified depth (0=root only, 1=root+children, etc). Still validates values/structure at the depth limit.
    - Example:
      ```bash
      python xmlcompare.py --files file1.xml file2.xml --max-depth 2
      java -jar xmlcompare.jar --files file1.xml file2.xml --max-depth=2
      ```

- Combine both:
    - Example:
      ```bash
      python xmlcompare.py --files file1.xml file2.xml --structure-only --max-depth 1
      ```

- Works with unordered:
    - Example:
      ```bash
      python xmlcompare.py --files file1.xml file2.xml --unordered --max-depth 2
      ```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All compared files are equal |
| `1` | One or more differences were found |
| `2` | An error occurred (file not found, invalid XML, bad arguments) |

---

## Sample Files

The `samples/` directory (mirrored in `python/samples/` and `java/samples/`) contains ready-to-use XML files:

| File | Description |
|------|-------------|
| `orders_expected.xml` | Reference order document |
| `orders_actual_equal.xml` | Same data as expected (normalises to equal) |
| `orders_actual_diff.xml` | Modified copy with intentional differences |
| `catalog_ns_a.xml` | Product catalogue using namespace `v1` |
| `catalog_ns_b.xml` | Same catalogue using namespace `v2` |
| `readings_a.xml` | Sensor readings at 12:00 |
| `readings_b.xml` | Same sensors at 12:05 with slightly different values |

---

## Example Commands

```bash
# No differences (numeric trailing-zero and whitespace normalisation)
./run.sh --files samples/orders_expected.xml samples/orders_actual_equal.xml

# Multiple differences in text format
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml

# Differences as JSON
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml --output-format json

# Save HTML report
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml \
    --output-format html --output-file report.html

# Ignore namespaces
./run.sh --files samples/catalog_ns_a.xml samples/catalog_ns_b.xml --ignore-namespaces

# Sensor readings with tolerance and skip
./run.sh --files samples/readings_a.xml samples/readings_b.xml \
    --skip-pattern "timestamp" --tolerance 0.005

# Directory compare
./run.sh --dirs samples/ samples/ --summary

# Quiet mode (exit code only)
./run.sh --files samples/orders_expected.xml samples/orders_actual_equal.xml \
    --quiet && echo "PASS" || echo "FAIL"
```

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
  "skip_keys": ["//timestamp"],
  "output_format": "json"
}
```

Run with:
```bash
./run.sh --files file1.xml file2.xml --config config.yaml
java -jar xmlcompare.jar --files file1.xml file2.xml --config config.yaml
```

---

## Code Quality Standards

Both implementations maintain high code quality through automated style checking, linting, and validation.

### Java: Checkstyle

The Java implementation enforces **Google-style** code standards with a **120-character line length limit** via [Checkstyle](https://checkstyle.sourceforge.io/).

**Run code style checks:**

Using Maven:
```bash
cd java
mvn checkstyle:check
```

Using Gradle:
```bash
cd java
./gradlew checkstyleMain checkstyleTest
```

**Configuration:**
- File: `java/checkstyle.xml` (Google style ruleset)
- Suppresses: `java/suppressions.xml` (specific exclusions)
- Key checks: imports (no wildcards), naming conventions, whitespace, indentation (2 spaces), line length (120 chars)

### Python: Ruff

The Python implementation uses [Ruff](https://github.com/astral-sh/ruff) for fast linting with **flake8-compatible rules** and a **120-character line length limit**.

**Run code style checks:**

```bash
cd python

# Lint all code
python -m ruff check .

# Fix common issues automatically
python -m ruff check . --fix
```

**Configuration:**
- File: `python/ruff.toml`
- Rule sets: `E` (pycodestyle errors), `F` (Pyflakes), `W` (warnings), `C90` (McCabe complexity)
- Line length: 120 characters (flake8 default is 79)
- Detects: unused imports, complex functions, trailing whitespace, and more

### XSD Schema Validation

Both implementations include XSD (XML Schema Definition) validation to verify XML documents conform to a schema. This is tested as part of the standard test suite.

**Java XSD Validation:**

- Class: `XsdValidator` (`src/main/java/com/xmlcompare/XsdValidator.java`)
- Tests: `src/test/java/XsdValidatorTest.java`
- Schemas: `src/test/resources/schema.xsd`

Run tests:
```bash
cd java
./gradlew test --tests XsdValidatorTest   # Gradle
mvn test -Dtest=XsdValidatorTest         # Maven
```

**Python XSD Validation:**

- Module: `validate_xsd.py` (`python/validate_xsd.py`)
- Tests: `python/tests/test_xsd_validation.py`
- Schemas: `python/tests/schema.xsd`

Run tests:
```bash
cd python
pytest tests/test_xsd_validation.py -v
```

**Usage (Programmatic):**

Java:
```java
XsdValidator validator = new XsdValidator("schema.xsd");
validator.validate("document.xml");  // Throws IOException if invalid
```

Python:
```python
from validate_xsd import validate_xml
validate_xml("document.xml", "schema.xsd")  # Raises ValueError if invalid
```

---

## Edge Cases and Advanced Topics

### Numeric Normalization

xmlcompare normalizes numeric values for robust comparison:

```bash
# These are considered equal (trailing zeros ignored)
./run.sh --files <(echo '<r><v>1.0</v></r>') <(echo '<r><v>1</v></r>')

# Floating-point precision is handled
./run.sh --files <(echo '<r><v>0.1 + 0.2</v></r>') <(echo '<r><v>0.30000001</v></r>') --tolerance 0.00001
```

### Large Files

For very large XML files (>100MB), consider:

```bash
# Use structure-only comparison to skip text values
./run.sh --files large1.xml large2.xml --structure-only

# Limit depth to avoid deep recursion
./run.sh --files large1.xml large2.xml --max-depth 5

# Use fail-fast to stop at first difference
./run.sh --files large1.xml large2.xml --fail-fast
```

### Complex Namespaces

When dealing with multiple namespace prefixes:

```bash
# Default: namespace-aware (will report differences)
./run.sh --files ns1.xml ns2.xml  # May fail if ns prefixes differ

# With --ignore-namespaces: all namespace URIs stripped
./run.sh --files ns1.xml ns2.xml --ignore-namespaces  # Will pass
```

### Deeply Nested XML

For XML with deep nesting (100+ levels), use `--max-depth`:

```bash
# Compare only first 3 levels of hierarchy
./run.sh --files deep1.xml deep2.xml --max-depth 3
```

### Special Characters and Encoding

- **UTF-8**: Fully supported
- **XML entities**: `&lt;`, `&gt;`, `&amp;` handled correctly
- **CDATA sections**: Treated as text content
- **Comments**: Ignored by default (not compared)

```bash
# CDATA is compared as text
./run.sh --files <(echo '<r><![CDATA[test]]></r>') <(echo '<r><![CDATA[test]]></r>')
```

### Mixed Content

Elements with mixed text and child elements:

```xml
<!-- file1.xml -->
<p>Hello <b>world</b>!</p>

<!-- file2.xml -->
<p>Hello<b>world</b>!</p>
```

Differences in whitespace between mixed content will be detected (unless whitespace normalization applies).

### Config File with Complex Options

```yaml
# config.yaml
structure_only: false
max_depth: 10
unordered: true
tolerance: 0.001
ignore_case: true
ignore_namespaces: true
ignore_attributes: false
skip_keys:
  - //timestamp
  - //random-id
skip_pattern: "temp.*"
output_format: json
output_file: report.json
fail_fast: true
```

```bash
./run.sh --files file1.xml file2.xml --config config.yaml
```

### Performance Tips

1. **Skip unnecessary checks**: Use `--ignore-attributes`, `--ignore-namespaces` if not needed
2. **Use `--structure-only`**: Much faster than full comparison
3. **Limit depth**: `--max-depth 2` for top-level comparison only
4. **Pattern matching**: Use efficient regex patterns in `--skip-pattern`
5. **Directory comparison**: Use `--summary` for large directory comparisons

### Error Handling

All implementations use consistent exit codes:

```bash
./run.sh --files file1.xml file2.xml
echo "Exit code: $?"  # 0 = equal, 1 = different, 2 = error
```

### XML Security (XXE Prevention)

Both implementations are secure by default:
- XXE (XML External Entity) attacks are prevented
- Billion laughs attack protection enabled
- External DTDs are not loaded

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Setting up development environment
- Writing tests
- Code style standards
- Submitting pull requests
- Reporting bugs and suggesting features

**Community Standards**: This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors, maintainers, and community members to treat each other with respect and kindness.

---

## Security

We take security seriously. If you discover a security vulnerability, please report it responsibly:

- **Do NOT** create a public issue
- See [SECURITY.md](SECURITY.md) for responsible disclosure procedures
- Includes information on supported versions, how to report vulnerabilities, and security best practices

---

## License

This project is licensed under the [MIT License](LICENSE).
