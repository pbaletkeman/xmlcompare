# Contributing to xmlcompare

Thank you for your interest in contributing to xmlcompare! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- **Python 3.8+** for Python implementation
- **Java 21+** for Java implementation
- **Git** for version control
- **Docker** (optional, for containerized testing)

### Cloning and Setup

```bash
git clone https://github.com/pbaletkeman/xmlcompare.git
cd xmlcompare
```

#### Python Setup

```bash
cd python
./build.sh          # Linux/macOS
# or
build.bat           # Windows CMD
# or
.\build.ps1         # Windows PowerShell
```

#### Java Setup

```bash
cd java
./build.sh          # Linux/macOS
# or
build.bat           # Windows CMD
# or
.\build.ps1         # Windows PowerShell
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/your-bug-fix
```

Use descriptive branch names:

- `feature/namespace-handling` ✓
- `bugfix/tolerance-rounding` ✓
- `docs/update-readme` ✓
- `f1` ✗ (too vague)

### 2. Make Your Changes

Follow the code style and standards:

#### Python Code

- **Linting**: Follows [Ruff](https://github.com/astral-sh/ruff) rules with 120-character line limit
- **Style**: PEP 8 compliant
- **Tests**: Add tests in `python/tests/` for all new features

Run validation before committing:

```bash
cd python
python -m ruff check . --fix    # Auto-fix issues
pytest tests/ -v               # Run all tests
```

#### Java Code

- **Style**: Google Java Style with 120-character line limit
- **Linting**: Enforced by Checkstyle
- **Tests**: Add tests in `java/src/test/java/` for all new features
- **Build**: Both Gradle and Maven must pass

Run validation before committing:

```bash
cd java

# Gradle
./gradlew build               # Build and test
./gradlew checkstyleMain checkstyleTest  # Check style

# Maven
mvn clean package             # Build and test
mvn checkstyle:check          # Check style
```

### 3. Write Tests

Both implementations must have comprehensive tests:

- **Unit tests**: Test individual functions/methods in isolation
- **Integration tests**: Test feature end-to-end
- **Edge cases**: Test boundary conditions and error handling

Example Python test:

```python
def test_tolerance_exceeded(self, tmp_path):
    f1 = write(tmp_path / 'a.xml', '<r><v>1.0</v></r>')
    f2 = write(tmp_path / 'b.xml', '<r><v>2.0</v></r>')
    opts = CompareOptions()
    opts.tolerance = 0.001
    diffs = xmlcompare.compare_xml_files(f1, f2, opts)
    assert len(diffs) > 0
    assert diffs[0].kind == 'text'
```

Example Java test:

```java
@Test
void testToleranceExceeded() throws IOException {
    String f1 = write("a.xml", "<r><v>1.0</v></r>");
    String f2 = write("b.xml", "<r><v>2.0</v></r>");
    opts.tolerance = 0.001;
    List<Difference> diffs = XmlCompare.compareFiles(f1, f2, opts);
    assertFalse(diffs.isEmpty());
}
```

### 4. Update Documentation

- Update [README.md](README.md) if adding features or changing behavior
- Add docstrings/JavaDoc for public functions and classes
- Update [CHANGELOG.md](CHANGELOG.md) with your changes

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add XPath filter support for selective comparison"
# or
git commit -m "fix: correct numeric tolerance rounding edge case"
# or
git commit -m "docs: add examples for --structure-only flag"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring without feature changes
- `perf:` Performance improvements
- `test:` Adding or updating tests
- `chore:` Build process, dependencies, etc.

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- **Title**: Short description (matches first commit message)
- **Description**: Explain what changed, why, and how to test
- **Screenshots**: For UI changes (if applicable)
- **Related Issues**: Reference any related issues (#123)

Example PR description:

## Description

Adds support for XPath filtering to allow users to compare only specific XML subtrees.

## Changes

- Added `--filter XPATH` command-line option
- Implemented XPath evaluation in both Python and Java
- Added 15 new test cases covering various XPath expressions

## Testing

```bash
./run.sh --files a.xml b.xml --filter "//order"
```

## Related Issues

Closes #45

## Code Review Process

1. **Automated checks**: All PRs must pass:
   - Python linting (Ruff)
   - Java linting (Checkstyle)
   - All unit tests (pytest for Python, JUnit for Java)
   - Code coverage thresholds (≥50%)

2. **Manual review**: At least one maintainer review required

3. **Feedback**: Address review comments by committing additional changes

4. **Approval**: PR merged after approval and all checks pass

## Testing

### Running Tests Locally

#### Python

```bash
cd python

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_xmlcompare.py -v

# Run with coverage
pytest tests/ --cov=xmlcompare --cov-report=html
```

#### Java

```bash
cd java

# Gradle
./gradlew test
./gradlew jacocoTestReport  # Generate coverage report

# Maven
mvn test
mvn jacoco:report  # Generate coverage report
```

### Test Data

Use the sample XML files in `samples/` for testing:

- `orders_expected.xml` — Reference document
- `orders_actual_equal.xml` — Normalizes to equal
- `orders_actual_diff.xml` — Contains intentional differences
- `catalog_ns_a.xml` / `catalog_ns_b.xml` — Namespace testing
- `readings_a.xml` / `readings_b.xml` — Numeric tolerance testing

## Reporting Issues

Use [GitHub Issues](https://github.com/pbaletkeman/xmlcompare/issues) to report bugs or suggest features.

### Bug Report

Include:

- **Description**: What went wrong?
- **Steps to reproduce**: Exact commands and inputs
- **Expected behavior**: What should happen?
- **Actual behavior**: What actually happened?
- **Environment**: OS, Python/Java version, xmlcompare version
- **Error logs**: Full error messages and stack traces
- **Sample files**: Minimal XML examples that trigger the bug

### Feature Request

Include:

- **Description**: What would you like?
- **Use case**: Why do you need it?
- **Proposed solution**: How should it work?
- **Alternatives**: Any alternative approaches?

## Project Structure

```shell
xmlcompare/
├── python/
│   ├── xmlcompare.py        # Main implementation
│   ├── validate_xsd.py      # XSD validation
│   ├── pyproject.toml       # Python package config
│   ├── ruff.toml            # Ruff linting config
│   ├── tests/
│   │   ├── test_xmlcompare.py
│   │   ├── test_xsd_validation.py
│   │   └── schema.xsd
│   └── samples/             # Sample XML files
├── java/
│   ├── build.gradle         # Gradle build config
│   ├── pom.xml              # Maven build config
│   ├── checkstyle.xml       # Code style config
│   ├── src/
│   │   ├── main/java/com/xmlcompare/
│   │   │   ├── Main.java
│   │   │   ├── XmlCompare.java
│   │   │   ├── XsdValidator.java
│   │   │   ├── CompareOptions.java
│   │   │   └── Difference.java
│   │   └── test/java/com/xmlcompare/
│   └── samples/             # Sample XML files
├── samples/                 # Shared sample files
├── .github/workflows/       # GitHub Actions CI
└── README.md
```

## Code Style Guide

### Python

- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use type hints where possible
- Docstrings for all public functions
- Use descriptive variable names

```python
def compare_elements(elem1: Element, elem2: Element, opts: CompareOptions) -> List[Difference]:
    """
    Compare two XML elements and return differences.

    Args:
        elem1: First element to compare
        elem2: Second element to compare
        opts: Comparison options

    Returns:
        List of differences found
    """
```

### Java

- Use 2 spaces for indentation
- Maximum line length: 120 characters
- Use [Google Java Style](https://google.github.io/styleguide/javaguide.html)
- Javadoc for all public classes and methods
- Use descriptive variable names

```java
/**
 * Compares two XML elements and returns differences.
 *
 * @param elem1 First element to compare
 * @param elem2 Second element to compare
 * @param opts Comparison options
 * @return List of differences found
 */
public static List<Difference> compareElements(
    Element elem1, Element elem2, CompareOptions opts) {
```

## Performance Considerations

- **Memory**: Handle large XML files with streaming where possible
- **Time complexity**: O(n) is acceptable, O(n²) should be avoided
- **Caching**: Cache computation results when appropriate
- **Profiling**: Profile code for performance-critical paths

## Security Considerations

- **Input validation**: Validate all XML and file inputs
- **Error handling**: Never expose internal paths or implementation details in error messages
- **Dependencies**: Keep dependencies up-to-date
- **XML bombs**: Handle XXE and other XML security vulnerabilities

## License

By contributing to xmlcompare, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## Questions?

- Check existing [issues](https://github.com/pbaletkeman/xmlcompare/issues)
- Review [README.md](README.md) and [Java README](java/README.md) / [Python README](python/README.md)
- Open a [discussion](https://github.com/pbaletkeman/xmlcompare/discussions)

Thank you for contributing! 🙏
