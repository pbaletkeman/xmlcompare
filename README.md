# xmlcompare

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

```yaml
# config.yaml
tolerance: 0.01
ignore_case: true
skip_keys:
  - //timestamp
output_format: json
```

```bash
./run.sh --files file1.xml file2.xml --config config.yaml
```

---

## License

This project is licensed under the [MIT License](LICENSE).
