# xmlcompare – Python

Python 3.8+ implementation of xmlcompare with flexible XML comparison options.

---

## Quick Navigation

- **[Root README](../README.md)** — Project overview and feature matrix
- **[Java Implementation](../java/README.md)** — Java version
- **[FEATURES.md](../FEATURES.md)** — Advanced features guide
- **[PLUGINS.md](../PLUGINS.md)** — Plugin development guide

---

## Table of Contents

- [Quick Start](#quick-start)
- [Usage](#usage)
  - [File comparison](#file-comparison)
  - [Directory comparison](#directory-comparison)
  - [REST API server](#rest-api-server)
- [Command-Line Reference](#command-line-reference)
- [Configuration](#configuration)
  - [Config file JSON/YAML](#config-file-jsonyaml)
  - [.xmlignore file](#xmlignore-file)
  - [config.schema.json](#configschemajson)
- [Features](#features)
- [Output Formats](#output-formats)
- [Streaming Mode](#streaming-mode)
- [Parallel Mode](#parallel-mode)
- [Caching](#caching)
- [XSLT Transforms](#xslt-transforms)
- [XSD Validation](#xsd-validation)
- [Plugin System](#plugin-system)
- [REST API](#rest-api)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Performance Benchmarks](#performance-benchmarks)
- [Sample Files](#sample-files)

---

## Quick Start

**Prerequisites:** Python 3.8+

```bash
# Build: create venv, install deps, run 333 tests
./build.sh          # Linux / macOS
./build.bat         # Windows CMD
./build.ps1         # Windows PowerShell
```

After build, compare two files:

```bash
./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml
# Windows: run.bat or run.ps1
```

---

## Usage

### File comparison

```bash
# Basic
./run.sh --files file1.xml file2.xml

# Numeric tolerance (allow up to 0.1% difference)
./run.sh --files file1.xml file2.xml --tolerance 0.001

# Case-insensitive, unordered children, ignore namespaces
./run.sh --files file1.xml file2.xml --ignore-case --unordered --ignore-namespaces

# Structure only (tag names, ignore text and attributes)
./run.sh --files file1.xml file2.xml --structure-only

# Limit recursion depth
./run.sh --files file1.xml file2.xml --max-depth 3

# Skip elements by XPath key list or regex
./run.sh --files file1.xml file2.xml --skip-keys //timestamp,//version
./run.sh --files file1.xml file2.xml --skip-pattern "^_.*"

# Swap expected/actual direction
./run.sh --files file1.xml file2.xml --swap

# Canonicalize (remove comments, normalize whitespace) before compare
./run.sh --files file1.xml file2.xml --canonicalize

# Apply XSLT transform before comparing (requires lxml)
./run.sh --files file1.xml file2.xml --xslt transform.xsl

# Validate against XSD schema during comparison
./run.sh --files doc.xml doc2.xml --schema schema.xsd

# Show only differences (suppress equal-file messages)
./run.sh --files file1.xml file2.xml --diff-only

# Disable ANSI colour output
./run.sh --files file1.xml file2.xml --no-color

# Stop at first difference
./run.sh --files file1.xml file2.xml --fail-fast

# Generation HTML report
./run.sh --files a.xml b.xml --output-format html --output-file report.html

# JSON output
./run.sh --files a.xml b.xml --output-format json | python -m json.tool
```

### Directory comparison

```bash
# Compare all XML files in two directories
./run.sh --dirs dir1/ dir2/

# Recursive
./run.sh --dirs dir1/ dir2/ --recursive

# Recursive with parallel multi-process
./run.sh --dirs dir1/ dir2/ --recursive --parallel

# With diff-only and cache (skip unchanged pairs)
./run.sh --dirs dir1/ dir2/ --cache .xmlcache.json --diff-only

# Unordered matching keyed on 'id' attribute
./run.sh --dirs dir1/ dir2/ --unordered --match-attr id

# Skip files matching pattern
./run.sh --dirs dir1/ dir2/ --skip-pattern "^_|backup"

# JSON summary
./run.sh --dirs dir1/ dir2/ --output-format json --output-file results.json
```

### REST API server

```bash
# Start server (default: 127.0.0.1:5000)
python api_server.py

# Custom host/port
python api_server.py --host 0.0.0.0 --port 8080

# Health check
curl http://localhost:5000/health

# Compare by file path
curl -s -X POST http://localhost:5000/compare/files \
     -H 'Content-Type: application/json' \
     -d '{"file1": "a.xml", "file2": "b.xml"}'

# Compare XML content directly
curl -s -X POST http://localhost:5000/compare/content \
     -H 'Content-Type: application/json' \
     -d '{"xml1": "<root><v>1</v></root>", "xml2": "<root><v>2</v></root>"}'

# With options
curl -s -X POST http://localhost:5000/compare/files \
     -H 'Content-Type: application/json' \
     -d '{"file1":"a.xml","file2":"b.xml","options":{"tolerance":0.01,"unordered":true}}'
```

---

## Command-Line Reference

```
usage: xmlcompare [--files FILE1 FILE2 | --dirs DIR1 DIR2] [OPTIONS]
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
| `--tolerance N` | `0.0` | Allow numeric differences up to N (e.g. `0.001`) |
| `--ignore-case` | off | Case-insensitive text comparison |
| `--unordered` | off | Allow child elements in any order |
| `--ignore-namespaces` | off | Strip namespace prefixes before comparing |
| `--ignore-attributes` | off | Ignore all attribute differences |
| `--skip-keys XPATHS` | — | Comma-separated list of XPath keys to skip |
| `--skip-pattern REGEX` | — | Skip elements whose tag matches this regex |
| `--filter-xpath XPATH` | — | Compare only elements matching this XPath |
| `--structure-only` | off | Compare tag names only (ignore text/attrs) |
| `--type-aware` | off | Coerce types before comparing (e.g. int vs float) |
| `--fail-fast` | off | Stop after first difference |
| `--max-depth N` | unlimited | Limit comparison depth to N levels |
| `--match-attr ATTR` | — | Attribute used as identity key for unordered matching |
| `--schema FILE` | — | Validate each file against this XSD schema |
| `--schema-dir DIR` | — | Validate against per-file XSD schemas in a directory |
| `--canonicalize` | off | Canonicalize XML before comparing |
| `--xslt FILE` | — | Apply XSLT transform before comparing (requires `lxml`) |
| `--swap` | off | Swap file1/file2 direction |

### Output control

| Flag | Default | Description |
|------|---------|-------------|
| `--output-format FMT` | `text` | One of: `text`, `json`, `html`, `unified` |
| `--output-file FILE` | — | Write output to file instead of stdout |
| `--verbose` | off | Show detailed per-element information |
| `--quiet` | off | Suppress progress messages |
| `--summary` | off | Print summary counts only |
| `--diff-only` | off | Only show files/pairs with differences |
| `--no-color` | off | Disable ANSI colour (also: `NO_COLOR=1` env var) |

### Performance

| Flag | Default | Description |
|------|---------|-------------|
| `--stream` | off | Use streaming iterparse parser for large files |
| `--parallel` | off | Process directory pairs in parallel (multi-process) |
| `--cache FILE` | — | JSON cache; skip pairs unchanged since last run |

### Interactive

| Flag | Description |
|------|-------------|
| `--interactive` | Launch interactive menu-driven UI |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Equal (no differences) |
| `1` | Differences found |
| `2` | Error (file not found, invalid XML, etc.) |

---

## Configuration

### Config file JSON/YAML

```json
{
  "tolerance": 0.001,
  "ignore_case": true,
  "unordered": true,
  "skip_keys": ["//timestamp", "//version"],
  "output_format": "html",
  "diff_only": true,
  "no_color": false,
  "cache": ".xmlcache.json"
}
```

```bash
./run.sh --files a.xml b.xml --config config.json
```

YAML is also supported (requires `pyyaml`):

```yaml
tolerance: 0.001
ignore_case: true
skip_keys:
  - //timestamp
  - //version
```

See `config.json.example` at the project root for a complete example.

### .xmlignore file

Place a `.xmlignore` file in a directory to exclude files from directory comparison:

```
# Comments supported
*.bak
temp_*.xml
legacy/
```

Patterns use glob syntax and are evaluated before any file is queued for comparison.

### config.schema.json

`config.schema.json` at the project root is a JSON Schema describing every supported configuration key. Use it in VS Code or JetBrains IDEs for autocompletion and validation when editing `config.json`.

---

## Features

| Feature | Flag(s) | Notes |
|---------|---------|-------|
| Text comparison | default | Tags, text content, attributes |
| Numeric tolerance | `--tolerance` | Absolute difference threshold |
| Case-insensitive | `--ignore-case` | All text values |
| Unordered children | `--unordered` | Order-independent matching |
| Ignore namespaces | `--ignore-namespaces` | Strips `ns:` prefixes |
| Skip elements | `--skip-keys`, `--skip-pattern` | XPath list or regex |
| XPath filter | `--filter-xpath` | Scope to subtree |
| Structure-only | `--structure-only` | Tag hierarchy only |
| Type-aware | `--type-aware` | Coerce `"1"` == `1` |
| Schema validation | `--schema` | XSD via lxml |
| Depth limiting | `--max-depth` | Stop at depth N |
| Streaming parser | `--stream` | Low-memory large-file mode |
| Parallel dirs | `--parallel` | Multi-process directory scan |
| Caching | `--cache` | Skip unchanged pairs |
| XSLT transform | `--xslt` | Pre-process before compare |
| Canonicalize | `--canonicalize` | Normalize XML first |
| Match attribute | `--match-attr` | Identity key for unordered sets |
| Diff-only | `--diff-only` | Suppress equal pairs |
| Swap direction | `--swap` | Flip expected/actual |
| No colour | `--no-color` | Plain text output |
| ANSI colours | automatic | TTY-detected; `FORCE_COLOR=1`/`NO_COLOR=1` |
| REST API | `api_server.py` | Flask HTTP service |
| Interactive UI | `--interactive` | Menu-driven CLI |
| Plugins | `--plugins` | Custom formatters and filters |
| .xmlignore | automatic | Per-directory exclusion list |

---

## Output Formats

| Format | Flag | Use case |
|--------|------|----------|
| Text (default) | `--output-format text` | Human review, terminal |
| JSON | `--output-format json` | CI parsing, scripts |
| HTML | `--output-format html` | Side-by-side browser diff |
| Unified diff | `--output-format unified` | Patch-style review |

```bash
# HTML report to file
./run.sh --files a.xml b.xml --output-format html --output-file report.html

# JSON piped to jq
./run.sh --files a.xml b.xml --output-format json | jq '.differences[].kind'

# Unified diff
./run.sh --files a.xml b.xml --output-format unified
```

---

## Streaming Mode

For large XML files (> 50 MB), use `--stream` to process with the iterparse streaming parser:

```bash
./run.sh --files large1.xml large2.xml --stream
```

Unordered and schema-guided comparisons fall back to DOM automatically.

---

## Parallel Mode

Distributes file pairs across CPU cores for large directory trees:

```bash
./run.sh --dirs dir1/ dir2/ --recursive --parallel
```

Thread count auto-selected as `min(cpu_count, 8)`.

---

## Caching

Skip file pairs that have not changed since the last run:

```bash
# First run: compare all and write cache
./run.sh --dirs dir1/ dir2/ --cache .xmlcache.json

# Second run: only compare changed files
./run.sh --dirs dir1/ dir2/ --cache .xmlcache.json
```

Cache entries are invalidated when a file's size or modification time changes.

---

## XSLT Transforms

```bash
./run.sh --files a.xml b.xml --xslt normalize.xsl
```

Requires `lxml` (`pip install lxml`). Useful for normalising timestamps or extracting subsections before comparison.

---

## XSD Validation

```bash
# Combined with comparison
./run.sh --files doc.xml doc2.xml --schema schema.xsd

# Standalone validator
python validate_xsd.py document.xml schema.xsd
echo $?   # 0 = valid, 1 = invalid, 2 = lxml missing
```

---

## Plugin System

**Custom formatter:**

```python
from plugin_interface import FormatterPlugin, get_registry

class CsvFormatter(FormatterPlugin):
    @property
    def name(self): return 'csv'

    def format(self, diffs, label1='file1', label2='file2', **kwargs):
        lines = ['kind,path,message']
        for d in diffs:
            lines.append(f'{d.kind},{d.path},{d.message}')
        return '\n'.join(lines)

get_registry().register_formatter(CsvFormatter())
```

**Custom difference filter:**

```python
from plugin_interface import DifferenceFilter, get_registry

class IgnoreTimestamps(DifferenceFilter):
    @property
    def name(self): return 'ignore-timestamps'

    def should_ignore(self, diff):
        return 'timestamp' in diff.path.lower()

get_registry().register_filter(IgnoreTimestamps())
```

```bash
./run.sh --files a.xml b.xml --plugins mypackage.myplugin
```

See [PLUGINS.md](../PLUGINS.md) for entry-point based packaging.

---

## REST API

Requires Flask (`pip install flask`):

```bash
python api_server.py [--host HOST] [--port PORT] [--debug]
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `POST` | `/compare/files` | Compare two files by filesystem path |
| `POST` | `/compare/content` | Compare two XML strings directly |

Response format:

```json
{
  "equal": false,
  "differences": [
    {"kind": "text", "path": "/root/price", "message": "text mismatch: '10.00' vs '10.01'"}
  ]
}
```

---

## Testing

```bash
# Run all 333 tests
pytest tests/

# With coverage
pytest tests/ --cov=. --cov-report=term-missing

# Specific file
pytest tests/test_xmlcompare.py -v

# Matching keyword
pytest tests/ -k "streaming or parallel"
```

**Coverage:** 91% overall.

---

## Code Quality

```bash
# Ruff lint check
python -m ruff check .

# Auto-fix
python -m ruff check . --fix
```

Configuration: `ruff.toml` — 120-character line length, flake8-compatible rules.

---

## Performance Benchmarks

```bash
python benchmark.py
```

Generates XML test files (1–50 MB) and reports throughput in MB/s for DOM, streaming, and parallel modes.

---

## Sample Files

| File | Description |
|------|-------------|
| `samples/orders_expected.xml` | Reference document |
| `samples/orders_actual_equal.xml` | Equal (normalised) |
| `samples/orders_actual_diff.xml` | With differences |
| `samples/catalog_ns_*.xml` | Namespace examples |
| `samples/readings_*.xml` | Numeric tolerance examples |

---

**Python Tests:** 333 passing
**Coverage:** 91%
**Tools:** pytest, pytest-cov, Ruff, lxml (optional)
**License:** MIT
