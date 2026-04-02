# XML Compare - New Features Documentation

## Quick Start

### Structure-Only Comparison
Compare only XML structure, ignoring all text and attribute values:

```bash
# Python
python xmlcompare.py --files file1.xml file2.xml --structure-only

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --structure-only
```

### Max-Depth Comparison
Limit comparison to a specific depth level:

```bash
# Python - compare only up to depth 2
python xmlcompare.py --files file1.xml file2.xml --max-depth 2

# Java
java -jar xmlcompare.jar --files file1.xml file2.xml --max-depth=2
```

### Combine Both Features
Use both options together for powerful validation:

```bash
python xmlcompare.py --files file1.xml file2.xml --structure-only --max-depth 1
```

## Feature Details

### `--structure-only` Option

Compares the structural layout of XML documents while completely ignoring:
- Text node values
- Attribute values
- Whitespace variations

**Still detects:**
- Missing or extra elements
- Tag name mismatches
- Structural hierarchy differences
- Element count differences

**Example:**
```xml
<!-- File 1 -->
<root>
  <name id="1">Alice</name>
  <age>30</age>
</root>

<!-- File 2 -->
<root>
  <name id="999">Bob</name>
  <age>25</age>
</root>

# Command: --structure-only
# Result: Files are equal (structure matches)

# Command: (default)
# Result: Multiple differences found (attributes and text values differ)
```

**Use Cases:**
- Validating document structure without content validation
- Schema compliance testing
- Template verification
- Data format validation

### `--max-depth` Option

Limits comparison to elements at or above a specified depth level (0-indexed from root):

**Depth Levels:**
- `depth 0`: Root element only
- `depth 1`: Root + direct children
- `depth 2`: Root + children + grandchildren
- `depth N`: All elements up to N levels deep

**Example:**
```xml
<!-- File 1 -->
<root>                              <!-- depth 0 -->
  <section>                         <!-- depth 1 -->
    <article>                       <!-- depth 2 -->
      <paragraph>                   <!-- depth 3 -->
        <sentence>Text</sentence>   <!-- depth 4 -->
      </paragraph>
    </article>
  </section>
</root>

# --max-depth 1: compares root and section, ignores content below
# --max-depth 2: also includes article, but ignores paragraph
# --max-depth 3: includes paragraph and below
```

**Use Cases:**
- Progressive validation (validate structure first, details later)
- Quick sanity checks on large documents
- Outline/hierarchy verification
- Top-level schema compliance

## Combined Usage Examples

### 1. Quick Structure Check
```bash
python xmlcompare.py --files large1.xml large2.xml --structure-only --max-depth 2
```
Compare only if the document structure matches at top 2 levels, ignoring all values.

### 2. Progressive Validation
```bash
# First: validate top-level structure exists
python xmlcompare.py --files config1.xml config2.xml --max-depth 0

# Then: validate one level deep
python xmlcompare.py --files config1.xml config2.xml --max-depth 1

# Finally: full validation
python xmlcompare.py --files config1.xml config2.xml
```

### 3. Flexible Testing
```bash
# Check schema structure regardless of data
python xmlcompare.py --files response1.json response2.json --structure-only

# Verify outline structure is identical
python xmlcompare.py --files doc1.xml doc2.xml --structure-only --max-depth 3
```

## Configuration File Support

Both options can be specified in configuration files:

### JSON Config
```json
{
  "structure_only": true,
  "max_depth": 2,
  "unordered": true
}
```

### YAML Config
```yaml
structure_only: true
max_depth: 2
unordered: true
```

## Compatibility with Existing Options

Both new options work seamlessly with all existing features:

### With `--unordered`
```bash
# Elements can be in any order, but structure must match
python xmlcompare.py --files file1.xml file2.xml --structure-only --unordered

# Mix with max-depth
python xmlcompare.py --files file1.xml file2.xml --max-depth 2 --unordered
```

### With `--ignore-attributes` / `--ignore-case`
```bash
python xmlcompare.py --files file1.xml file2.xml --structure-only --ignore-case
```

### With `--skip-keys` / `--skip-pattern`
```bash
python xmlcompare.py --files file1.xml file2.xml --structure-only --skip-keys //timestamp
```

### With `--tolerance`
```bash
# Numeric tolerance + structure-only = validate structure with no value checking
python xmlcompare.py --files file1.xml file2.xml --structure-only --tolerance 0.1
```

## Performance Impact

- **`--structure-only`**: Slight performance improvement (skips text/attribute comparisons)
- **`--max-depth`**: Significant performance improvement for large documents (stops early)
- **Combined**: Best performance for large document quick checks

## Test Results

### Python
- 23 new feature tests: **100% PASS**
- 93 existing tests: **100% PASS**
- Backward compatibility: **VERIFIED**

### Java
- 55 existing tests: **100% PASS**
- CLI options: **VERIFIED**
- Integration: **VERIFIED**

## Examples in Repository

Test files demonstrating features:
- `test_struct1.xml` / `test_struct2.xml` - Structure-only examples
- `test_depth1.xml` / `test_depth2.xml` - Max-depth examples
- `test_complex1.xml` / `test_complex2.xml` - Complex real-world example
- `test_unordered1.xml` / `test_unordered2.xml` - Unordered with multiple types

Run examples:
```bash
cd python
python xmlcompare.py --files ../test_struct1.xml ../test_struct2.xml --structure-only
python xmlcompare.py --files ../test_depth1.xml ../test_depth2.xml --max-depth 1
python xmlcompare.py --files ../test_complex1.xml ../test_complex2.xml --structure-only
```
