# xmlcompare — Java Edition

A Java 25 port of the Python `xmlcompare` tool for comparing XML files and directories.

---

## Quick Navigation

- **[Master Features Guide](../docs/FEATURES.md)** - All features and examples
- **[Complete CLI Reference](docs/CLI_REFERENCE.md)** - All switches documented
- **[Advanced Features](docs/FEATURES.md)** - Parallel processing, streaming, plugins
- **[Root README](../README.md)** - Project overview
- **[Python Implementation](../python/README.md)** - Python version

---

## Table of Contents

- [xmlcompare — Java Edition](#xmlcompare--java-edition)
  - [Quick Navigation](#quick-navigation)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Building](#building)
    - [With Gradle (recommended)](#with-gradle-recommended)
    - [With Maven](#with-maven)
    - [With the build script (both Gradle and Maven)](#with-the-build-script-both-gradle-and-maven)
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
  - [Sample Commands](#sample-commands)
  - [Config File Format](#config-file-format)
  - [Exit Codes](#exit-codes)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
    - [Checkstyle (Code Style Validation)](#checkstyle-code-style-validation)
    - [XSD Validation](#xsd-validation)

---

## Prerequisites

- Java 25 or later (Gradle 8.x requires Java 21+ for compatibility)
- Gradle 8.x (or use the included `gradlew` wrapper)
- Maven 3.8+ (optional, for Maven builds)

## Building

### With Gradle (recommended)

```bash
./gradlew build
```

### With Maven

```bash
mvn clean package
```

### With the build script (both Gradle and Maven)

```bash
./build.sh        # Linux/macOS
build.bat         # Windows CMD
```

## Sample Commands

Define `JAR=build/libs/xmlcompare-1.0.0.jar` for brevity.

```bash
# Basic file comparison
java -jar $JAR --files a.xml b.xml

# Numeric tolerance
java -jar $JAR --files a.xml b.xml --tolerance 0.001

# Case-insensitive, unordered children
java -jar $JAR --files a.xml b.xml --ignore-case --unordered

# Unordered with attribute identity key
java -jar $JAR --files a.xml b.xml --unordered --match-attr id

# Structure only (ignore text/attrs)
java -jar $JAR --files a.xml b.xml --structure-only

# Ignore namespaces
java -jar $JAR --files a.xml b.xml --ignore-namespaces

# Max depth
java -jar $JAR --files a.xml b.xml --max-depth 2

# Skip elements by XPath
java -jar $JAR --files a.xml b.xml --skip-keys //timestamp,//version

# Fail fast
java -jar $JAR --files a.xml b.xml --fail-fast

# Directory comparison
java -jar $JAR --dirs dir1/ dir2/

# Recursive directory comparison
java -jar $JAR --dirs dir1/ dir2/ --recursive

# Parallel directory scan
java -jar $JAR --dirs dir1/ dir2/ --recursive --parallel

# Diff-only (suppress equal pairs)
java -jar $JAR --dirs dir1/ dir2/ --diff-only

# Swap expected/actual direction
java -jar $JAR --files a.xml b.xml --swap

# Canonicalize before compare
java -jar $JAR --files a.xml b.xml --canonicalize

# Disable ANSI colour
java -jar $JAR --files a.xml b.xml --no-color

# Cache for incremental directory runs
java -jar $JAR --dirs dir1/ dir2/ --cache .xmlcache.json

# JSON output
java -jar $JAR --files a.xml b.xml --output-format json

# HTML side-by-side report
java -jar $JAR --files a.xml b.xml --output-format html --output-file report.html

# Unified diff format
java -jar $JAR --files a.xml b.xml --output-format unified

# Summary counts only
java -jar $JAR --dirs dir1/ dir2/ --summary

# XSD schema validation
java -jar $JAR --files doc.xml doc2.xml --schema schema.xsd

# Load from config file
java -jar $JAR --files a.xml b.xml --config myconfig.json
```

## Command-Line Reference

```
usage: java -jar xmlcompare.jar [--files FILE1 FILE2 | --dirs DIR1 DIR2] [OPTIONS]
```

### Input selection

| Flag | Description |
|------|-------------|
| `--files FILE1 FILE2` | Compare two XML files |
| `--dirs DIR1 DIR2` | Compare matching XML files in two directories |
| `--recursive` | Recurse into subdirectories (with `--dirs`) |
| `--config FILE` | Load options from JSON or YAML config file |

### Comparison behaviour

| Flag | Default | Description |
|------|---------|-------------|
| `--tolerance N` | `0.0` | Allow numeric differences up to N |
| `--ignore-case` | off | Case-insensitive text comparison |
| `--unordered` | off | Allow child elements in any order |
| `--ignore-namespaces` | off | Strip namespace prefixes |
| `--ignore-attributes` | off | Ignore all attribute differences |
| `--skip-keys XPATHS` | — | Comma-separated XPath keys to skip |
| `--skip-pattern REGEX` | — | Skip elements matching this regex |
| `--filter-xpath XPATH` | — | Compare only elements matching this XPath |
| `--structure-only` | off | Compare tag names only |
| `--type-aware` | off | Coerce types before comparing |
| `--fail-fast` | off | Stop at first difference |
| `--max-depth N` | unlimited | Limit comparison depth |
| `--match-attr ATTR` | — | Attribute used as identity key for unordered matching |
| `--schema FILE` | — | Validate each file against this XSD schema |
| `--canonicalize` | off | Canonicalize XML before comparing |
| `--swap` | off | Swap file1/file2 direction |

### Output control

| Flag | Default | Description |
|------|---------|-------------|
| `--output-format FMT` | `text` | One of: `text`, `json`, `html`, `unified` |
| `--output-file FILE` | — | Write output to file |
| `--verbose` | off | Detailed per-element information |
| `--quiet` | off | Suppress progress messages |
| `--summary` | off | Print summary counts only |
| `--diff-only` | off | Only show files/pairs with differences |
| `--no-color` | off | Disable ANSI colour |

### Performance

| Flag | Default | Description |
|------|---------|-------------|
| `--stream` | off | Streaming StAX parser for large files |
| `--parallel` | off | Parallel directory scan |
| `--cache FILE` | — | JSON cache; skip unchanged pairs |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Equal (no differences) |
| `1` | Differences found |
| `2` | Error (file not found, invalid XML, etc.) |

---

## Config File Format

```json
{
  "structure_only": true,
  "max_depth": 2,
  "unordered": true,
  "tolerance": 0.001,
  "ignore_case": true,
  "skip_keys": ["//timestamp", "root/version"],
  "skip_pattern": "temp.*",
  "output_format": "html",
  "diff_only": true,
  "no_color": false,
  "cache": ".xmlcache.json",
  "fail_fast": false
}
```

YAML is also supported:

```yaml
tolerance: 0.001
unordered: true
match_attr: id
diff_only: true
cache: .xmlcache.json
```

---

## .xmlignore File

When using `--dirs`, place a `.xmlignore` file in the directory to exclude files:

```
# Glob patterns
*.bak
temp_*.xml
legacy/
```

---

## Features

| Feature | Flag(s) | Notes |
|---------|---------|-------|
| Text comparison | default | Tags, text, attributes |
| Numeric tolerance | `--tolerance` | Absolute threshold |
| Case-insensitive | `--ignore-case` | All text values |
| Unordered children | `--unordered` | Order-independent |
| Ignore namespaces | `--ignore-namespaces` | Strips `ns:` prefixes |
| Skip elements | `--skip-keys`, `--skip-pattern` | XPath or regex |
| Structure-only | `--structure-only` | Tag hierarchy only |
| Type-aware | `--type-aware` | Coerce `"1"` == `1` |
| Schema validation | `--schema` | XSD validation |
| Depth limiting | `--max-depth` | Stop at depth N |
| Streaming parser | `--stream` | StAX low-memory mode |
| Parallel dirs | `--parallel` | Multi-thread directory scan |
| Caching | `--cache` | Skip unchanged pairs |
| Canonicalize | `--canonicalize` | Normalize XML first |
| Match attribute | `--match-attr` | Identity key for sets |
| Diff-only | `--diff-only` | Suppress equal pairs |
| Swap direction | `--swap` | Flip expected/actual |
| No colour | `--no-color` | Plain text output |
| ANSI colours | automatic | Terminal-detected |

---

## Running Tests

```bash
# Gradle (154 JUnit5 tests)
./gradlew test

# Maven
mvn test
```

Test reports: `build/reports/tests/test/index.html`

---

## Code Quality

### Checkstyle (Code Style Validation)

The project enforces Google-style coding standards with a 120-character line length limit via [Checkstyle](https://checkstyle.sourceforge.io/).

**Run Checkstyle:**

Using Maven:

```bash
mvn checkstyle:check
```

Using Gradle:

```bash
./gradlew checkstyleMain checkstyleTest
```

**Configuration:**

- `checkstyle.xml` — Main Google-style ruleset
- `suppressions.xml` — Suppresses specific violations for third-party or generated code
- Line length: 120 characters (Google style default is 80; configured to 120 for readability)
- Indentation: 2 spaces (Google style standard)

**Violations reported by Checkstyle:**

- Import statement issues (wildcard imports forbidden)
- Naming conventions (TypeName, MethodName, ParameterName, etc.)
- Whitespace rules (spacing around operators, method params, casts, etc.)
- File-level rules (tabs forbidden, trailing whitespace, etc.)

All production and test code must pass Checkstyle checks.

### XSD Validation

XSD (XML Schema Definition) validation is available as part of the testing suite. The `XsdValidator` class provides schema validation for both production and test code.

**Test XSD validation:**

Using Maven:

```bash
mvn clean test -Dtest=XsdValidatorTest
```

Using Gradle:

```bash
./gradlew test --tests XsdValidatorTest
```

**XSD Validation Files:**

- `src/test/resources/schema.xsd` — Example XSD schema
- `src/test/resources/valid.xml` — Example XML valid against the schema
- `src/test/resources/invalid.xml` — Example XML invalid against the schema

The `XsdValidator` class can be used programmatically:

```java
XsdValidator validator = new XsdValidator("path/to/schema.xsd");
validator.validate("path/to/document.xml");  // Throws IOException if invalid
```
