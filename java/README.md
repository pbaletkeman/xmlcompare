# xmlcompare — Java Edition

A Java 21 port of the Python `xmlcompare` tool for comparing XML files and directories.

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

- Java 21 or later (Gradle 8.x requires Java 21+ for compatibility)
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
# xmlcompare (Java)

High-performance XML comparison tool (Java implementation)

## Quick Navigation

- [FEATURES.md](docs/FEATURES.md) – Java-specific features
- [CLI_REFERENCE.md](docs/CLI_REFERENCE.md) – Command-line usage
- [../docs/CONFIG_GUIDE.md](../docs/CONFIG_GUIDE.md) – Configuration guide
- [../docs/FEATURES.md](../docs/FEATURES.md) – Master feature matrix

---

## Overview

xmlcompare (Java) is a fast, extensible XML comparison tool for data validation, regression testing, and automated QA. It supports large files, fuzzy matching, and advanced filtering.

**Key Features:**
- Parallel processing for large datasets
- Streaming parser for low memory usage
- Schema validation (XSD)
- Plugin system for custom logic
- Multiple output formats: text, JSON, HTML, diff

## Installation

```bash
# Using Maven
mvn clean install

# Using Gradle
gradle build
```

## Usage

### Basic file comparison

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml
```

### Directory comparison

```bash
java -jar xmlcompare.jar --dir dir1 dir2
```

### With configuration file

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --config config.json
```

### Output formats

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --output json
java -jar xmlcompare.jar --files file1.xml file2.xml --output html
java -jar xmlcompare.jar --files file1.xml file2.xml --output diff
```

## Command-Line Reference

See [CLI_REFERENCE.md](docs/CLI_REFERENCE.md) for all options and examples.

## Configuration

See [../docs/CONFIG_GUIDE.md](../docs/CONFIG_GUIDE.md) for all config options and examples.

## Features

See [FEATURES.md](docs/FEATURES.md) for a full list of Java-specific features.

## Testing

```bash
# Run all tests
mvn test
# or
gradle test
```

## Contributing

1. Fork the repo
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

## License

MIT

## Sample Commands

```bash
# Compare two XML files
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml

# Structure-only comparison
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --structure-only

# Max-depth limiting
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --max-depth 2

# Combine both
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --structure-only --max-depth 1

# Compare with numeric tolerance
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --tolerance 0.001

# Compare directories, ignoring element order
java -jar build/libs/xmlcompare-1.0.0.jar --dirs dir1/ dir2/ --unordered

# Unordered with max-depth
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --unordered --max-depth 2

# Recursive directory comparison
java -jar build/libs/xmlcompare-1.0.0.jar --dirs dir1/ dir2/ --recursive

# JSON output
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --output-format json

# HTML report
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --output-format html --output-file report.html

# Skip specific elements
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --skip-keys //timestamp,//version

# Case-insensitive, ignore namespaces
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --ignore-case --ignore-namespaces

# Load from config file
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --config myconfig.json
```

## Config File Format

All options (including `structure_only` and `max_depth`) are standard and can be set in JSON or YAML config files:

**JSON Example:**

```json
{
  "structure_only": true,
  "max_depth": 2,
  "unordered": true,
  "tolerance": 0.001,
  "ignore_case": true,
  "skip_keys": ["//timestamp", "root/version"],
  "skip_pattern": "temp.*",
  "output_format": "text",
  "fail_fast": false
}
```

**YAML Example:**

```yaml
structure_only: true
max_depth: 2
unordered: true
tolerance: 0.001
ignore_case: true
skip_keys:
  - //timestamp
  - root/version
```

## Exit Codes

| Code  | Meaning                                   |
| ----- | ----------------------------------------- |
| 0     | Files/directories are equal               |
| 1     | Differences found                         |
| 2     | Error (file not found, invalid XML, etc.) |

## Running Tests

```bash
./gradlew test
```

Test reports are generated in `build/reports/tests/test/index.html`.

Maven tests run automatically during `mvn package`; to run tests only:

```bash
mvn test
```

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
