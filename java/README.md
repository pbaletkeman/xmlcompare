# xmlcompare — Java Edition

A Java 21 port of the Python `xmlcompare` tool for comparing XML files and directories.

## Table of Contents

- [xmlcompare — Java Edition](#xmlcompare--java-edition)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Building](#building)
    - [With Gradle (recommended)](#with-gradle-recommended)
    - [With Maven](#with-maven)
    - [With the build script (both Gradle and Maven)](#with-the-build-script-both-gradle-and-maven)
  - [Building a Fat JAR](#building-a-fat-jar)
    - [Dedicated fat JAR scripts](#dedicated-fat-jar-scripts)
    - [Output locations](#output-locations)
    - [Examples](#examples)
  - [Running](#running)
  - [CLI Options](#cli-options)
  - [Sample Commands](#sample-commands)
  - [Config File Format](#config-file-format)
  - [Exit Codes](#exit-codes)
  - [Running Tests](#running-tests)

---

## Prerequisites

- Java 21 or later
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
.\build.ps1       # PowerShell
```

---

## Building a Fat JAR

A fat JAR (uber JAR) bundles the application and all its dependencies into a single self-contained `.jar` file.

Both build tools are pre-configured:
- **Maven** uses `maven-shade-plugin` (runs automatically during `mvn package`)
- **Gradle** uses a custom `jar` task with `configurations.runtimeClasspath`

### Dedicated fat JAR scripts

| Script | Platform | Usage |
|--------|----------|-------|
| `fatjar.sh` | Linux / macOS | `./fatjar.sh [maven\|gradle]` |
| `fatjar.bat` | Windows CMD | `fatjar.bat [maven\|gradle]` |
| `fatjar.ps1` | Windows PowerShell | `.\fatjar.ps1 [-BuildTool maven\|gradle]` |

The default build tool is **maven**. Pass `gradle` as the argument to use Gradle instead.

### Output locations

| Build tool | Fat JAR path |
|------------|-------------|
| Maven | `target/xmlcompare-1.0.0.jar` |
| Gradle | `build/libs/xmlcompare-1.0.0.jar` |

### Examples

```bash
# Maven (default)
./fatjar.sh
fatjar.bat
.\fatjar.ps1

# Gradle
./fatjar.sh gradle
fatjar.bat gradle
.\fatjar.ps1 -BuildTool gradle
```

---

## Running

After building, run with:

```bash
# Maven fat JAR
java -jar target/xmlcompare-1.0.0.jar [OPTIONS]

# Gradle fat JAR
java -jar build/libs/xmlcompare-1.0.0.jar [OPTIONS]
```

Or use the run script (after building):

```bash
./run.sh [OPTIONS]          # Linux/macOS
run.bat [OPTIONS]           # Windows CMD
./run.ps1 [OPTIONS]         # PowerShell
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--files FILE1 FILE2` | Compare two XML files |
| `--dirs DIR1 DIR2` | Compare two directories of XML files |
| `--recursive` | Recurse into subdirectories (with `--dirs`) |
| `--config FILE` | Load options from a JSON or YAML config file |
| `--tolerance FLOAT` | Numeric tolerance for value comparison (default: 0.0) |
| `--ignore-case` | Case-insensitive text comparison |
| `--unordered` | Compare child elements in any order |
| `--ignore-namespaces` | Ignore XML namespace URIs |
| `--ignore-attributes` | Ignore XML attributes entirely |
| `--skip-keys PATH,...` | Skip elements by path or `//tagname` |
| `--skip-pattern REGEX` | Skip elements whose tag matches a regex |
| `--filter XPATH` | Compare only elements matching an XPath expression |
| `--output-format FORMAT` | Output format: `text` (default), `json`, `html` |
| `--output-file FILE` | Write output to a file instead of stdout |
| `--summary` | Print a summary line only |
| `--verbose` | Print verbose comparison details to stderr |
| `--quiet` | Suppress all output |
| `--fail-fast` | Stop on first difference found |
| `-h`, `--help` | Show help message |
| `-V`, `--version` | Print version information |

## Sample Commands

```bash
# Compare two XML files
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml

# Compare with numeric tolerance
java -jar build/libs/xmlcompare-1.0.0.jar --files a.xml b.xml --tolerance 0.001

# Compare directories, ignoring element order
java -jar build/libs/xmlcompare-1.0.0.jar --dirs dir1/ dir2/ --unordered

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

JSON:
```json
{
  "tolerance": 0.001,
  "ignore_case": true,
  "unordered": false,
  "ignore_namespaces": false,
  "ignore_attributes": false,
  "skip_keys": ["//timestamp", "root/version"],
  "skip_pattern": "temp.*",
  "output_format": "text",
  "fail_fast": false
}
```

YAML:
```yaml
tolerance: 0.001
ignore_case: true
unordered: false
skip_keys:
  - //timestamp
  - root/version
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Files/directories are equal |
| 1 | Differences found |
| 2 | Error (file not found, invalid XML, etc.) |

## Running Tests

```bash
./gradlew test
```

Test reports are generated in `build/reports/tests/test/index.html`.

Maven tests run automatically during `mvn package`; to run tests only:

```bash
mvn test
```
