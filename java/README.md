# xmlcompare — Java Edition

A Java 21 port of the Python `xmlcompare` tool for comparing XML files and directories.

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
./build.ps1       # PowerShell
```

## Running

After building, run with:

```bash
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
