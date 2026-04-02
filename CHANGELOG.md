# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-04-02

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

## [Unreleased]

### Planned Features
- [ ] Diff-style output format (side-by-side)
- [ ] Performance optimizations for large files
- [ ] Custom comparison rules via plugins
- [ ] Docker container distribution
- [ ] Maven Central Repository publishing
- [ ] Interactive mode for CLI exploration
- [ ] Schema-aware comparison

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
