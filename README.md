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
  - [License](#license)


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

## License

This project is licensed under the [MIT License](LICENSE).
