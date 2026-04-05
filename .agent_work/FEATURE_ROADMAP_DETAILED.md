# xmlcompare - Detailed Feature Enhancement Roadmap

## 🎯 Executive Priority Ranking

### 1. STREAMING PARSER (Critical) 🔴
**Status:** Placeholder implementation
**Blocker for:** Processing files >1GB
**User Impact:** HIGH - Common request for large XML processing
**Revenue Impact:** Could enable enterprise contracts
**Effort:** 2-3 days dev + 1 day testing
**ROI:** Very High

### 2. PARALLEL PROCESSING (Critical) 🔴
**Status:** Placeholder implementation
**Blocker for:** Performance on multi-core systems
**User Impact:** HIGH - Every user with 4+ cores
**Performance Gain:** 2-3x speedup
**Effort:** 2-3 days dev + 1 day testing
**ROI:** Very High

### 3. TROUBLESHOOTING GUIDE (Important) 🟡
**Status:** Missing documentation
**User Impact:** MEDIUM - Reduces support load
**Effort:** 1 day
**ROI:** High (support efficiency)

### 4. ADVANCED XPATH (Important) 🟡
**Status:** Limited to simple patterns
**User Impact:** MEDIUM - Enables complex filtering
**Effort:** 2-3 days
**ROI:** Medium-High

### 5. JAVA INTERACTIVE MODE (Nice-to-have) 🟡
**Status:** Python only
**User Impact:** MEDIUM - Feature parity
**Effort:** 2-3 days
**ROI:** Medium

---

## FEATURE DETAIL SPECIFICATIONS

### Feature #1: Real Streaming Parser Implementation

#### Problem Statement
Currently, the streaming parser is a stub that delegates to DOM parsing. This limitations:
- Can't process files >1GB (memory exhaustion)
- Uses 10x file size in memory (1GB file = 10GB RAM needed)
- Defeats purpose of `--stream` flag
- "Out of Memory" errors on large enterprise XML

#### Proposed Solution - Python

**Module:** `python/parse_streaming.py`

**Current Code:**
```python
def get_stream_stats(file_path):
    """Placeholder - just returns stats"""
    file_size_mb = os.path.getsize(file_path) / 1024 / 1024
    return StreamingStats(file_size_mb, suitable_for_streaming=file_size_mb > 100)
```

**Proposed Code:**
```python
def parse_streaming(file1_path, file2_path, options):
    """Compare massive XML files using iterparse."""
    import xml.etree.ElementTree as ET

    # Event-based parsing - constant memory regardless of file size
    parser1 = StreamingXmlComparator(file1_path)
    parser2 = StreamingXmlComparator(file2_path)

    differences = []

    for (event1, elem1), (event2, elem2) in zip(parser1.iter(), parser2.iter()):
        if compare_event(event1, elem1, event2, elem2, options):
            diffs = extract_differences(elem1, elem2, options)
            differences.extend(diffs)
            elem1.clear()  # Free memory immediately

        if options.fail_fast and differences:
            break

    return differences

class StreamingXmlComparator:
    """Event-based XML parser using iterparse."""
    def __init__(self, filepath):
        self.filepath = filepath

    def iter(self):
        """Yield (event, element) tuples."""
        for event, elem in ET.iterparse(self.filepath, events=['start', 'end']):
            yield event, elem
```

**Expected Results:**
- Memory usage: ~50MB (constant)
- Processing time: ~5 minutes for 5GB file
- Storage: No temporary files needed

#### Proposed Solution - Java

**File:** `java/src/main/java/com/xmlcompare/parse/StreamingXmlParser.java`

**Current Code:**
```java
public class StreamingXmlParser {
    public List<Difference> parse(String file1, String file2) {
        // Placeholder - delegates to DOM
        return XmlCompare.compare(file1, file2);
    }
}
```

**Proposed Code:**
```java
public class StreamingXmlParser {
    private static final XMLInputFactory factory = XMLInputFactory.newFactory();

    public List<Difference> compareStream(String file1, String file2)
            throws XMLStreamException {
        List<Difference> differences = new ArrayList<>();

        try (XMLStreamReader reader1 = createReader(file1);
             XMLStreamReader reader2 = createReader(file2)) {

            while (reader1.hasNext() || reader2.hasNext()) {
                int event1 = reader1.getEventType();
                int event2 = reader2.getEventType();

                if (!compareEvent(event1, event2, reader1, reader2)) {
                    recordDifference(differences, reader1, reader2);
                }

                reader1.next();
                reader2.next();
            }
        }

        return differences;
    }

    private XMLStreamReader createReader(String filepath) throws XMLStreamException {
        return factory.createXMLStreamReader(
            new FileInputStream(filepath)
        );
    }
}
```

**Benefits:**
- Constant memory usage (50MB)
- Processes unlimited file sizes
- No temporary files

#### Implementation Checklist
- [ ] Implement `python/parse_streaming.py` with iterparse
- [ ] Add tests for 500MB+ XML files
- [ ] Implement `java/parse/StreamingXmlParser.java` with StAX
- [ ] Add Java streaming tests
- [ ] Benchmark memory usage vs DOM
- [ ] Update documentation with guidance on when to use `--stream`
- [ ] Create troubleshooting guide for "Out of Memory" errors

---

### Feature #2: Real Parallel Processing Implementation

#### Problem Statement
The `--parallel` flag currently has no effect. Users with 4-core, 8-core, 16-core systems see single-threaded performance.

Expected benefit: **2-3x faster** on commodity hardware.

#### Proposed Solution - Python

**Module:** `python/parallel.py`

**Current Code:**
```python
def compare_xml_files_parallel(file1_path, file2_path, options=None, num_processes=0):
    """Just delegated to serial - no parallelization!"""
    differences = compare_xml_files(file1_path, file2_path, options)
    return differences
```

**Proposed Code:**
```python
from multiprocessing import Pool
from xml.etree import ElementTree as ET

def compare_xml_files_parallel(file1_path, file2_path, options=None, num_processes=0):
    """Compare XML trees using multiprocessing."""

    if num_processes <= 0:
        num_processes = get_recommended_process_count()

    # Parse XML into trees (DOM - one time cost)
    tree1 = ET.parse(file1_path)
    tree2 = ET.parse(file2_path)
    root1 = tree1.getroot()
    root2 = tree2.getroot()

    # Extract subtrees for parallel processing
    subtree_pairs = prepare_subtrees(root1, root2, max_depth=3)

    if len(subtree_pairs) <= 1:
        # Too small for parallelization overhead
        return compare_xml_files(file1_path, file2_path, options)

    # Compare subtrees in parallel
    with Pool(num_processes) as pool:
        partial_diffs = pool.starmap(
            compare_subtree_pair,
            [(st1, st2, options) for st1, st2 in subtree_pairs]
        )

    # Merge and sort results
    all_diffs = []
    for diffs in partial_diffs:
        all_diffs.extend(diffs)

    return sorted(all_diffs, key=lambda d: d.path)

def prepare_subtrees(elem1, elem2, max_depth=3):
    """Split trees into subtrees for parallel processing."""
    if max_depth <= 0:
        return [(elem1, elem2)]

    pairs = []
    for child1, child2 in zip(elem1, elem2):
        pairs.append((child1, child2))

    return pairs

def compare_subtree_pair(elem1, elem2, options):
    """Compare a pair of subtrees - runs in separate process."""
    return _compare_elements(elem1, elem2, options, path="", diffs=[])
```

**Performance Expectations:**
- 2-core system: ~1.5x
- 4-core system: ~2.5x
- 8-core system: ~3.0x
- 16+ core system: ~3.2x (diminishing returns)

#### Proposed Solution - Java

**File:** `java/src/main/java/com/xmlcompare/parallel/ParallelComparison.java`

**Proposed Code:**
```java
public class ParallelComparison {
    private static final int THRESHOLD = 1000; // Threshold for splitting
    private final ForkJoinPool pool;

    public ParallelComparison(int parallelism) {
        this.pool = new ForkJoinPool(parallelism);
    }

    public List<Difference> compare(Element elem1, Element elem2, CompareOptions opts) {
        ComparisonTask task = new ComparisonTask(elem1, elem2, opts, "");
        return pool.invoke(task);
    }
}

class ComparisonTask extends RecursiveTask<List<Difference>> {
    private final Element elem1, elem2;
    private final CompareOptions opts;
    private final String path;

    protected List<Difference> compute() {
        // Get children
        NodeList children1 = elem1.getChildNodes();
        NodeList children2 = elem2.getChildNodes();

        int childCount = Math.max(children1.getLength(), children2.getLength());

        if (childCount > THRESHOLD) {
            // Split into tasks
            List<ComparisonTask> subtasks = new ArrayList<>();

            for (int i = 0; i < childCount; i += THRESHOLD) {
                Node child1 = i < children1.getLength() ? children1.item(i) : null;
                Node child2 = i < children2.getLength() ? children2.item(i) : null;

                if (child1 instanceof Element && child2 instanceof Element) {
                    ComparisonTask task = new ComparisonTask(
                        (Element) child1, (Element) child2, opts, path + "/" + i
                    );
                    task.fork();
                    subtasks.add(task);
                }
            }

            // Collect results
            List<Difference> allDiffs = new ArrayList<>();
            for (ComparisonTask task : subtasks) {
                allDiffs.addAll(task.join());
            }
            return allDiffs;
        } else {
            // Compare serially
            return compareSerial();
        }
    }

    private List<Difference> compareSerial() {
        // Actual comparison logic
        return XmlCompare.compareElements(elem1, elem2, opts, path);
    }
}
```

#### Implementation Checklist
- [ ] Implement work-stealing with multiprocessing (Python)
- [ ] Implement ForkJoinPool pattern (Java)
- [ ] Add benchmarks showing speedup
- [ ] Test on 4, 8, 16 core systems
- [ ] Create documentation on when parallelization helps
- [ ] Add `--threads` option to control parallelism
- [ ] Add tests for consistency (serial vs parallel)

---

### Feature #3: Troubleshooting & FAQ Documentation

#### Document: `/docs/TROUBLESHOOTING.md`

**Content Structure:**

```markdown
# Troubleshooting & FAQ

## Common Errors

### Error: "Out of Memory: Java heap space"

**Cause:** File too large for DOM parser (>1GB)

**Solution 1 - Use streaming:**
```bash
java -jar xmlcompare.jar --files huge1.xml huge2.xml --stream
# Memory: ~50MB instead of file-size dependent
```

**Solution 2 - Increase heap:**
```bash
java -Xmx8G -jar xmlcompare.jar --files file1.xml file2.xml
```

**Solution 3 - Use Python (faster streaming):**
```bash
python xmlcompare.py --files file1.xml file2.xml --stream
```

---

### Error: "Comparison is taking too long (>30 seconds)"

**Investigation Steps:**

1. Check file sizes:
```bash
ls -lh file1.xml file2.xml
```

2. Check if parallelization could help:
```bash
# If file > 50MB, use parallel (must be 4+ cores)
java -jar xmlcompare.jar --files file1.xml file2.xml --parallel
```

3. Check if redundant options are set:
```bash
# BAD - ignores order twice
java -jar xmlcompare.jar --files a.xml b.xml --unordered --ignore-attributes
# GOOD - only necessary options
java -jar xmlcompare.jar --files a.xml b.xml --unordered
```

---

### Error: "Invalid XML at line 523"

**Cause:** Malformed XML - non-well-formed

**Debug:**
```bash
# Validate XML structure
xmllint --noout file.xml
# Read around line 523
sed -n '520,530p' file.xml
```

---

## FAQ

### Q: What's the maximum file size?

**A:**
- Without `--stream`: Limited by available RAM (~1GB practical limit)
- With `--stream`: Unlimited (tested to 5GB+)

Recommendation: Use `--stream` for files >500MB

---

### Q: Why is my comparison showing no differences when I expect some?

**Possible Causes:**
1. Using `--ignore-case` or `--ignore-namespaces` unintentionally
2. Using `--structure-only` (only compares structure, not content)
3. Using `--ignore-attributes` when attributes differ
4. Files actually are identical

**Debug:**
```bash
# Check what options are in effect
java -jar xmlcompare.jar --files a.xml b.xml --summary
# Shows count of differences
```

---

### Q: How do I compare only specific elements?

**A:** Use XPath filtering:
```bash
java -jar xmlcompare.jar --files a.xml b.xml \
  --filter "//order[@status='active']"
```

---

### Q: Should I use JSON or HTML output?

**A:**
- **JSON:** Parsing/scripting, CI/CD integration
- **HTML:** Human review, reporting, audit trails
- **Text:** Quick checks, terminal viewing
- **Diff:** Patch generation, version control

---

## Performance Optimization

### For Small Files (<10MB)
No optimization needed - pure comparison time < 100ms

### For Medium Files (10-500MB)
Consider:
- `--fail-fast` to exit on first difference
- `--summary` if you only need count

### For Large Files (>500MB)
1. Use `--stream` for constant memory
2. Use `--parallel --threads $(nproc)` on multi-core
3. Consider `--structure-only` if you don't need content

### For Very Large Files (>2GB)
1. MUST use `--stream` (DOM parsing will fail)
2. Use `--parallel` on high-core systems (16+)
3. Consider splitting file into chunks

---

## Platform-Specific tips

### Windows
- Use backslashes in paths or quotes: `--files "c:\path\file.xml"`
- Use `build.bat` instead of `build.sh`

### macOS
- Ensure write permissions to output files
- Use `brew install openjdk` for Java 21+

### Linux
- Use `./build.sh` for builds
- Ensure 755 permissions on scripts

---
```

#### Implementation Checklist
- [ ] Create `/docs/TROUBLESHOOTING.md`
- [ ] Add 10-15 common error scenarios
- [ ] Include debugging steps for each
- [ ] Add performance tuning section
- [ ] Platform-specific tips
- [ ] Link from main README
- [ ] Request feedback from early users

---

### Feature #4: Advanced XPath Support

#### Problem Statement
Current XPath support only handles simple patterns like `//tag`. Users need:
- Attribute matching: `//order[@status='active']`
- Position predicates: `//item[position() > 5]`
- Text content: `//text()[contains(., 'error')]`

#### Proposed Solution - Python

**Enhancement to:** `python/xmlcompare.py`

**Current Code:**
```python
def apply_xpath_filter(root, xpath_str):
    """Currently just string matching"""
    if xpath_str.startswith('//'):
        tag = xpath_str[2:]
        return root.findall('.//' + tag)
    return [root]
```

**Proposed Code:**
```python
def apply_xpath_filter(root, xpath_str):
    """Use lxml for full XPath 1.0 support."""
    try:
        from lxml import etree
        # Convert ElementTree to lxml for XPath evaluation
        lxml_root = etree.fromstring(ET.tostring(root))
        return lxml_root.xpath(xpath_str)
    except ImportError:
        # Fallback to basic matching if lxml not available
        return apply_xpath_filter_basic(root, xpath_str)

def apply_xpath_filter_basic(root, xpath_str):
    """Fallback for environments without lxml."""
    # Only supports //tag format
    if xpath_str.startswith('//'):
        tag = xpath_str[2:]
        return root.findall('.//' + tag)
    elif xpath_str.startswith('/'):
        return root.findall(xpath_str)
    return [root]
```

**Supported Patterns After Enhancement:**
```bash
# Attribute matching
--filter "//order[@status='active']"

# Position-based
--filter "//item[position() > 5]"

# Text content
--filter "//error[contains(.,'timeout')]"

# Complex predicates
--filter "//transaction[@amount > 1000][@type='debit']"

# Namespaces (with ignore-namespaces flag)
--filter "//ns:order" --ignore-namespaces
```

#### Proposed Solution - Java

**Enhancement to:** `java/src/main/java/com/xmlcompare/XmlCompare.java`

```java
public List<Element> applyXPathFilter(Element root, String xpathStr)
        throws XPathExpressionException {

    // Use javax.xml.xpath for XPath 1.0 support
    XPathFactory factory = XPathFactory.newInstance();
    XPath xpath = factory.newXPath();

    XPathExpression expr = xpath.compile(xpathStr);
    NodeList nodes = (NodeList) expr.evaluate(root, XPathConstants.NODESET);

    List<Element> results = new ArrayList<>();
    for (int i = 0; i < nodes.getLength(); i++) {
        if (nodes.item(i) instanceof Element) {
            results.add((Element) nodes.item(i));
        }
    }
    return results;
}
```

#### Implementation Checklist
- [ ] Add lxml dependency (Python, optional)
- [ ] Implement XPath evaluation
- [ ] Add tests for common XPath patterns
- [ ] Document supported XPath syntax
- [ ] Handle namespace resolution
- [ ] Add error messages for invalid XPath
- [ ] Graceful fallback if lxml not available

---

### Feature #5: Java Interactive Mode

#### Problem Statement
Python has interactive CLI (`interactive_cli.py`), Java doesn't. This creates feature parity gap and reduces usability.

#### Specification

**Required Features:**
1. File selection menu
2. Difference filtering and navigation
3. Result visualization
4. Export filtered results

**UI Framework Options:**
- **Lanterna:** Full TUI support, tables, colors
- **Picocli Tables:** Built into picocli, simpler
- **Text menu:** Basic but functional

**Recommended:** Lanterna (better UX)

#### Implementation Checklist
- [ ] Add Lanterna dependency to `pom.xml` and `build.gradle`
- [ ] Create `com.xmlcompare.interactive.InteractiveMode` class
- [ ] Implement file selection menu
- [ ] Implement result navigation
- [ ] Implement filtering UI
- [ ] Add colors and formatting
- [ ] Create tests for interactive mode
- [ ] Document interactive features

---

## Implementation Priority & Timeline

| Feature | Priority | Start | Duration | Status |
|---------|----------|-------|----------|--------|
| Streaming Parser | 1 (Critical) | Week 1 | 3 days dev + 1 test | Not started |
| Parallel Processing | 2 (Critical) | Week 2 | 3 days dev + 1 test | Not started |
| Troubleshooting Guide | 3 (Important) | Week 3 | 1 day | Not started |
| Advanced XPath | 4 (Important) | Week 4 | 3 days | Not started |
| Java Interactive | 5 (Nice-to-have) | Week 5 | 3 days | Not started |

**Total Estimate for v1.1:** 4-5 weeks of development work

---

## Success Metrics

### Feature Success Definitions

**Streaming Parser:**
- ✅ Processes 5GB file in under 5 minutes
- ✅ Memory usage never exceeds 100MB
- ✅ Results identical to DOM parsing
- ✅ 100% backward compatible

**Parallel Processing:**
- ✅ 2.5x+ speedup on 4-core system
- ✅ Results identical to serial processing
- ✅ No memory overhead
- ✅ 100% backward compatible

**Troubleshooting Guide:**
- ✅ Covers 10+ common errors
- ✅ Each error has solution steps
- ✅ Reduces support issues by 30%+

...
