# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-15

### Added

- **Python – Streaming Parser** (`--stream`)
  - Memory-efficient iterparse-based comparison via `parse_streaming.py`
  - `compare_xml_files_streaming()` function integrated into CLI dispatch
  - Handles large XML files without loading the full tree into memory

- **Python – Parallel Processing** (`--parallel`, `--threads`)
  - `multiprocessing.Pool`-based concurrent element comparison via `parallel.py`
  - `compare_xml_files_parallel()` function integrated into CLI dispatch
  - Automatic load distribution across available CPU cores

- **Python – Interactive CLI** (`--interactive`)
  - Full-featured menu-driven interface in `interactive_cli.py`
  - File selection, option configuration, XPath filter, skip keys
  - Export results to text/JSON/HTML directly from the menu
  - Show statistics and performance info (options 8 and 9)

- **Python – Plugin System**
  - `FormatterPlugin`, `DifferenceFilter` interfaces in `plugin_interface.py`
  - `PluginRegistry` for entry-point-based discovery

- **Python – Schema / Type-Aware Comparison**
  - `schema_analyzer.py` with XSD pre-validation via `lxml`
  - `--schema`, `--type-aware` flags using type hints from XSD

- **Python – Performance Benchmarking**
  - `benchmark.py` with timing comparisons across DOM, streaming, and parallel engines

- **Python – HTML Side-by-Side & Unified Diff Output**
  - `HtmlSideBySideFormatter` and `UnifiedDiffFormatter` in `xmlcompare.py`
  - `--output-format html` and `--output-format unified-diff`

- **Java – Streaming Parser** (`--stream`)
  - StAX dual-file streaming comparison via `parse/StreamingXmlParser.java`
  - Low memory footprint for files too large for DOM

- **Java – Parallel Processing** (`--parallel`, `--threads`)
  - Subtree-parallel comparison via `ForkJoinPool` in `parallel/ParallelComparison.java`
  - Directory-level parallelism via `ExecutorService`

- **Java – Interactive Mode** (`--interactive`)
  - Console `Scanner`-based menu in `interactive/InteractiveMode.java`
  - 7 configuration options including streaming, parallel, XPath filter, skip keys, thread count

- **Java – Schema / Type-Aware Comparison**
  - `schema/SchemaAnalyzer.java` — XSD validation + type-hint extraction
  - `--schema FILE` and `--type-aware` flags

- **Java – Plugin System (SPI)**
  - `plugin/FormatterPlugin.java`, `plugin/DifferenceFilter.java` interfaces
  - `--plugins com.example.MyPlugin` flag

- **Java – Performance Benchmarking**
  - `benchmark/BenchmarkSuite.java` — DOM vs streaming vs parallel timing
  - Run via `java -cp xmlcompare.jar com.xmlcompare.benchmark.BenchmarkSuite`

- **Java – HTML Side-by-Side & Unified Diff Output**
  - `format/HtmlSideBySideFormatter.java` — colour-coded side-by-side diff
  - `format/UnifiedDiffFormatter.java` — standard `@@` hunk format
  - `--output-format html` and `--output-format unified-diff`

### Fixed

- **Python** – `interactive_cli.py` `_rerun_comparison()` now correctly dispatches to
  `compare_xml_files_streaming()` / `compare_xml_files_parallel()` when those modes
  are enabled (previously always called the plain DOM function, silently ignoring flags)
- **Java** – `InteractiveMode.java` XPath filter option double-called `readLine()`,
  discarding the first value; now reads into a variable correctly
- **Java** – `StreamingXmlParser.java` Difference `kind` names normalised to match
  formatter switch cases (`"tag"`, `"text"`, `"missing"`, `"extra"`, `"attr"`) — previously
  used long forms like `"tag_mismatch"` that fell through to unstyled `"context"` in HTML
- **Java** – `ParallelComparison.java` same Difference `kind` normalisation applied

### Technical Details

- Python test suite: 167 tests, all passing
- Java test suite: 93 tests, all passing
- Java target: JDK 25 (Amazon Corretto), picocli 4.7.5, Jackson 2.17.0

---

## [1.0.0] - 2026-04-02

### Added

- **Python Implementation** (Python 3.8+)
  - XML file and directory comparison
  - Numeric tolerance with configurable thresholds
  - Whitespace normalization
  - Case-insensitive comparison mode
  - Namespace handling (ignore or strict)
  - Element order flexibility (ordered/unordered)
  - Skip elements by path or pattern
  - XPath filtering
  - Multiple output formats (text, JSON, HTML)
  - Config file support (YAML/JSON)
  - XSD schema validation
  - Python wheel distribution

- **Java Implementation** (Java 21+)
  - Full feature parity with Python
  - Gradle and Maven build support
  - Checkstyle code style enforcement
  - Fat JAR distribution
  - JaCoCo code coverage reporting
  - Both Maven and Gradle build systems

- **Quality Assurance**
  - Comprehensive test suites (Python pytest + Java JUnit)
  - Ruff linting for Python (120-character line limit)
  - Checkstyle enforcement for Java (120-character line limit)
  - Code coverage verification (≥50% minimum)

- **Documentation**
  - Root README with feature overview
  - Python-specific README with examples
  - Java-specific README with examples
  - Sample XML files for testing
  - Contributing guidelines
  - GitHub issue templates (bug report, feature request)
  - GitHub Actions CI/CD workflow

- **Features**
  - `--files FILE1 FILE2` — Compare two XML files
  - `--dirs DIR1 DIR2` — Compare directories
  - `--recursive` — Recurse into subdirectories
  - `--tolerance FLOAT` — Numeric tolerance
  - `--ignore-case` — Case-insensitive text
  - `--unordered` — Child elements in any order
  - `--ignore-namespaces` — Strip namespace URIs
  - `--ignore-attributes` — Skip attributes
  - `--structure-only` — Compare structure only
  - `--max-depth INT` — Limit comparison depth
  - `--skip-keys PATH` — Skip by path/tag
  - `--skip-pattern REGEX` — Skip by pattern
  - `--filter XPATH` — Filter by XPath
  - `--output-format text|json|html` — Output format
  - `--output-file FILE` — Write to file
  - `--summary` — Summary count only
  - `--verbose` — Verbose output
  - `--quiet` — Suppress output
  - `--fail-fast` — Stop on first difference
  - `--config FILE` — Load from config file

### Technical Details

#### Exit Codes

- `0` — Files are equal
- `1` — Differences found
- `2` — Error (file not found, invalid XML, etc.)

#### Numeric Normalization

- `10.10` == `10.1` (trailing zero)
- `10.0` == `10` (integer vs float)
- `1.001` ≈ `1.002` with tolerance

#### Whitespace Normalization

- Leading/trailing whitespace is trimmed
- Multiple spaces are normalized to single space
- Newlines are normalized

#### Namespace Handling

- By default, namespaces are compared
- With `--ignore-namespaces`, stripped before comparison
- QName prefixes are handled correctly

#### Ordering

- By default, child elements must be in same order
- With `--unordered`, order is ignored
- Attributes are unordered by default

### Known Limitations

- XPath filtering limited to basic expressions
- Large files (>1GB) may require streaming optimization
- Performance not optimized for deeply nested XML (100+ levels)

## Support

- **Issues**: [GitHub Issues](https://github.com/pbaletkeman/xmlcompare/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pbaletkeman/xmlcompare/discussions)
- **License**: MIT

## Contributors

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
