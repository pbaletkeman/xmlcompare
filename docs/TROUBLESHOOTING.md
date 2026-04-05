---
post_title: Troubleshooting Guide
author1: xmlcompare
post_slug: troubleshooting
microsoft_alias: ""
featured_image: ""
categories: []
tags: [troubleshooting, faq, debugging, performance]
ai_note: false
summary: Common errors, debugging steps, performance tips, and platform-specific guidance for xmlcompare.
post_date: 2026-04-04
---

## Common Errors

### "Out of Memory" / Java heap space exhausted

**Cause:** File is too large for DOM parsing (typically >500 MB).

**Solutions:**

Use the streaming parser (constant memory regardless of file size):

```bash
# Python
python xmlcompare.py --files huge1.xml huge2.xml --stream

# Java
java -jar xmlcompare.jar --files huge1.xml huge2.xml --stream
```

Increase the Java heap as a last resort:

```bash
java -Xmx8G -jar xmlcompare.jar --files file1.xml file2.xml
```

**Rule of thumb:** use `--stream` for files larger than 200 MB.

---

### "File not found" when path contains spaces

**Cause:** Shell splits the path at the space.

**Fix:** Quote the path:

```bash
python xmlcompare.py --files "c:\path with spaces\file1.xml" "c:\other path\file2.xml"
java -jar xmlcompare.jar --files "/path with spaces/file1.xml" "/other/file2.xml"
```

---

### "Invalid XML at line N" (ParseError)

**Cause:** Malformed XML — the file is not well-formed.

**Debug steps:**

```bash
# Linux/macOS: validate with xmllint
xmllint --noout file.xml

# Show the problem area
sed -n '$((N-2)),$((N+2))p' file.xml

# Windows (PowerShell): basic check
[xml](Get-Content file.xml)
```

Common culprits:
- Unescaped `&` (must be `&amp;`)
- Unescaped `<` inside text (must be `&lt;`)
- Mismatched or unclosed tags
- Byte-order mark (BOM) at the start of the file

---

### "Invalid XPath expression"

**Cause:** The expression passed to `--filter` uses syntax not supported by
the built-in XPath engine.

**With Python:** install `lxml` to enable full XPath 1.0:

```bash
pip install lxml
```

Without `lxml`, ElementTree supports a useful subset:

```bash
# These work without lxml
--filter "//order"
--filter "//item[@status='active']"
--filter "//record[2]"

# These require lxml
--filter "//item[position() > 5]"
--filter "//error[contains(.,'timeout')]"
--filter "//tx[@amount > 1000]"
```

---

### "Schema validation failed"

**Cause:** One or both XML files do not conform to the XSD schema provided
with `--schema`.

**Debug steps:**

```bash
# Validate a single file against the schema
python -c "
from validate_xsd import get_validation_errors
errors = get_validation_errors('file.xml', 'schema.xsd')
for e in (errors or []):
    print(e)
"

# Java equivalent
java -jar xmlcompare.jar --files file1.xml file2.xml --schema schema.xsd --verbose
```

If validation should be skipped intentionally, omit `--schema`.

---

### Comparison returns no differences when differences are expected

**Check these options first:**

| Option | What it hides |
|--------|--------------|
| `--ignore-case` | Text case differences |
| `--ignore-namespaces` | Namespace differences |
| `--ignore-attributes` | All attribute differences |
| `--structure-only` | All text and attribute values |
| `--tolerance N` | Numeric differences ≤ N |

Double-check the active configuration:

```bash
# Verify with --verbose (Python)
python xmlcompare.py --files a.xml b.xml --verbose

# Java
java -jar xmlcompare.jar --files a.xml b.xml --verbose
```

Also confirm you are comparing the correct files — especially when using a
config file where `files:` may be set.

---

### Comparison is very slow (> 30 seconds for large files)

**Investigation:**

```bash
# Check file sizes first
# Linux/macOS
ls -lh file1.xml file2.xml

# Windows PowerShell
Get-Item file1.xml, file2.xml | Select Name, Length
```

**Quick wins:**
- `--fail-fast`: stop at the first difference (great for CI)
- `--summary`: skip detailed output rendering
- `--parallel`: use all CPU cores for large subtree comparisons

```bash
# Python - parallel on all available cores
python xmlcompare.py --files a.xml b.xml --parallel

# Java - explicit thread count
java -jar xmlcompare.jar --files a.xml b.xml --parallel --threads 8
```

**For very large files (>500 MB), combine streaming + parallel:**

```bash
# Python
python xmlcompare.py --files huge1.xml huge2.xml --stream --parallel

# Java
java -jar xmlcompare.jar --files huge1.xml huge2.xml --stream --parallel --threads 8
```

---

### Parallel comparison gives different results than serial

**Cause (Python):** Plugins that are not importable inside worker processes
are silently skipped. Plugins that maintain shared state may also behave
differently.

**Fix:** Avoid stateful plugins or test with `--plugins` disabled when using
`--parallel`.

**Cause (Java):** Using `-Djava.util.concurrent.ForkJoinPool.common.parallelism`
system property may affect thread counts unexpectedly. Prefer `--threads`.

---

### "No module named 'lxml'" (Python)

`lxml` is optional but enables full XPath 1.0. Install it when needed:

```bash
pip install lxml

# Or via project extras when available
pip install "xmlcompare[lxml]"
```

---

### "UnsupportedClassVersionError" (Java)

**Cause:** You are running the JAR with a JVM older than Java 21.

**Fix:**

```bash
# Check current Java version
java -version

# Use sdkman or brew to install Java 21+
sdk install java 21-tem
```

---

## Frequently Asked Questions

### What is the maximum file size for --stream?

Unlimited — tested to 5 GB+. Peak memory stays around 50 MB because
elements are freed immediately after comparison.

### When does --parallel help most?

- Directory comparisons with many files (e.g. 100+ XML files)
- Single files whose root element has many independent children

The parallelism overhead makes it slower for small files (<10 MB) with
few top-level children. The tool falls back to serial automatically when
splitting would not be beneficial.

### Can I compare SOAP/REST XML with namespaces?

Yes — use `--ignore-namespaces` to strip all namespace prefixes before
comparison:

```bash
python xmlcompare.py --files soap1.xml soap2.xml --ignore-namespaces
```

### How do I compare only specific elements?

Use `--filter` with an XPath expression:

```bash
# Compare only <order> elements
python xmlcompare.py --files a.xml b.xml --filter "//order"

# Compare only active orders (requires lxml)
python xmlcompare.py --files a.xml b.xml --filter "//order[@status='active']"
```

### Should I use JSON, HTML or text output?

| Format | Best for |
|--------|---------|
| `text` (default) | Terminal quick checks |
| `json` | CI/CD pipelines, scripting |
| `html` | Human review, audit reports |
| `unified-diff` | Patch generation, version control |
| `html-diff` | Side-by-side browser review |

### How do I suppress identical files from directory output?

```bash
# Show only files with differences (quiet + json)
python xmlcompare.py --dirs dir1 dir2 --output-format json \
  | python -c "import sys,json; d=json.load(sys.stdin); \
    [print(k) for k,v in d.items() if not v.get('equal')]"
```

---

## Performance Tuning by File Size

### Small files (< 10 MB)

No special options needed — comparison completes in milliseconds.

### Medium files (10–200 MB)

```bash
--fail-fast      # Stop immediately on first difference
--summary        # Skip detailed output rendering
```

### Large files (200 MB – 2 GB)

```bash
--stream                   # Constant memory usage
--parallel --threads 4     # Multi-core acceleration
```

### Very large files (> 2 GB)

```bash
--stream --parallel --threads $(nproc)   # Linux/macOS

# Java: increase heap too
java -Xmx4G -jar xmlcompare.jar --files f1.xml f2.xml --stream --parallel
```

---

## Platform-Specific Tips

### Windows

- Use forward slashes or quoted backslashes in paths:

  ```cmd
  xmlcompare --files "C:\data\file1.xml" "C:\data\file2.xml"
  ```

- On Windows, the Python `--parallel` flag spawns new processes using
  `spawn` (not `fork`). Ensure all imports are inside `if __name__ == '__main__':`.

- Use `build.bat` instead of `build.sh` for the Java build.

### macOS

- Ensure write permissions for the output directory:
  ```bash
  chmod 755 /output/dir
  ```

- Install Java 21+ via Homebrew: `brew install openjdk@21`
- Install Python 3.8+: `brew install python@3.11`

### Linux

- Make build scripts executable: `chmod +x build.sh`
- Use `$(nproc)` to pass all CPU cores to `--threads`

---

## Getting More Help

- Check [FEATURES.md](../FEATURES.md) for the full feature list
- Check [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for configuration examples
- Check [PLUGINS.md](../PLUGINS.md) for plugin development
- Open a GitHub issue with the output of `--verbose` attached
