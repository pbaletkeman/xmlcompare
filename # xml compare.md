# XML Compare

Create a Python program that compares XML files and reports differences.

## Features

### Input / CLI

- Accept a `--files` argument to compare two XML files
- Accept a `--dirs` argument to compare two directories of XML files (matched by filename)
- Accept a `--recursive` flag to recurse into subdirectories when comparing directories
- Accept a `--config` argument to load options from a YAML/JSON config file instead of CLI flags

### Comparison Behaviour

- Numeric normalization: `10.10 == 10.1` and `10.0 == 10`
- Numeric tolerance threshold: e.g. `--tolerance 0.001` to allow small floating-point differences
- Whitespace normalization: treat collapsed and expanded text content as equal, e.g.
  ```xml
  <testing>true</testing>
  ```
  equals
  ```xml
  <testing>
      true
  </testing>
  ```
- Case-insensitive text comparison via `--ignore-case` flag
- Unordered (set-based) child element comparison via `--unordered` flag
- Strict (ordered) child element comparison (default)
- Namespace-aware comparison (default); `--ignore-namespaces` to strip namespaces before comparing
- Attribute comparison included by default; `--ignore-attributes` to skip all attributes

### Skipping / Filtering

- Skip specific XML element paths via `--skip-keys path1 path2 ...` (XPath-style, e.g. `//timestamp`)
- Skip elements matching a regex pattern via `--skip-pattern REGEX`
- Compare only elements matching a given XPath filter via `--filter XPATH`

### Output

- Human-readable diff to stdout by default
- `--output-format [text|json|html]` to select report format
- `--output-file FILE` to write the report to a file instead of stdout
- `--summary` flag to print only a pass/fail count rather than the full diff
- `--verbose` flag for detailed element-by-element trace
- `--quiet` flag to suppress all output (useful when only the exit code matters)
- Colour-coded terminal output where supported (differences highlighted in red/green)

### Exit Codes

- `0` — files/directories are equal
- `1` — differences found
- `2` — error (file not found, invalid XML, bad arguments, etc.)

### Error Handling

- Validate that input files are well-formed XML and report parse errors clearly
- When comparing directories, report files present in one directory but missing in the other
- Provide a `--fail-fast` flag to stop on the first detected difference
