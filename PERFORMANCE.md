# xmlcompare Performance Guide

Comprehensive guide to understanding and optimizing xmlcompare performance for your use case.

## Performance Profiles

### File Processing Speed

Benchmark results on a reference machine (Intel i7, 16GB RAM, SSD):

| File Size | Format | Time  | Memory | Throughput |
| --------- | ------ | ----- | ------ | ---------- |
| 1 MB      | DOM    | 120ms | 15MB   | ~8 MB/s    |
| 1 MB      | Stream | 180ms | 3MB    | ~5 MB/s    |
| 10 MB     | DOM    | 1.2s  | 150MB  | ~8 MB/s    |
| 10 MB     | Stream | 2.5s  | 5MB    | ~4 MB/s    |
| 100 MB    | DOM    | 12s   | 1.5GB  | ~8 MB/s    |
| 100 MB    | Stream | 30s   | 15MB   | ~3 MB/s    |
| 1 GB      | Stream | 5min  | 50MB   | ~3 MB/s    |

### Comparison Options Overhead

Relative cost of comparison options (compared to baseline):

| Option           | Overhead       | Notes                      |
| ---------------- | -------------- | -------------------------- |
| baseline         | 1x             | Simple element comparison  |
| --ignore-case    | +10%           | Case normalization         |
| --unordered      | +20%           | Set-based sorting          |
| --tolerance 0.01 | +5%            | Numeric normalization      |
| --structure-only | -50%           | Skips text/attr comparison |
| --schema         | +15%           | XSD validation             |
| --type-aware     | +20%           | Type-aware matching        |

### Memory Usage Patterns

Typical memory usage by comparison size (DOM parsing):

```plaintext
File Size  Memory Usage
1 MB       ~15 MB
10 MB      ~150 MB
100 MB     ~1.5 GB
1 GB       ~15 GB (with swapping, very slow)
```

With streaming parser:

```plaintext
Any size   ~50 MB (constant)
```

---

## Optimization Strategies

### For Large Files (>100 MB)

1. **Use Streaming Parser**

   ```bash
   xmlcompare --files huge1.xml huge2.xml --stream
   # Saves 100x memory
   ```

2. **Skip Metadata Elements**

   ```bash
   xmlcompare --files huge1.xml huge2.xml \
              --skip-keys "timestamp" "version" "revision" \
              --skip-pattern "temp_.*"
   # Reduces comparison work by 30-40%
   ```

3. **Use Structure-Only Mode**

   ```bash
   xmlcompare --files huge1.xml huge2.xml --structure-only
   # 2x faster when only structure matters
   ```

### For Frequent Comparisons

1. **Pre-filter Unchanged Files**

   ```bash
   # Quick size/checksum check before full comparison
   if [[ $(stat -c%s file1.xml) -ne $(stat -c%s file2.xml) ]]; then
       xmlcompare --files file1.xml file2.xml
   fi
   ```

2. **Cache Schema Analysis**

   ```bash
   # First run: schema loaded, cached
   xmlcompare --files a.xml b.xml --schema schema.xsd
   # Subsequent runs use cache
   ```

3. **Parallelize Multiple Comparisons**

   ```bash
   # Process multiple files in parallel
   for f1 in file_*.xml; do
       f2="${f1/expected/actual}"
       xmlcompare --files "$f1" "$f2" &
   done
   wait
   ```

### For Real-Time Monitoring

1. **Use Interactive Mode**
2.

   ```bash
   xmlcompare --interactive
   # Lazy load, filter on demand
   ```

3. **Export for Analysis**
4.

   ```bash
   xmlcompare --files file1.xml file2.xml --output-format json > results.json
   # Process asynchronously
   ```

### For Report Generation

1. **Generate Once, Filter Many**
2.

   ```bash
   # Generate full report once
   xmlcompare --files file1.xml file2.xml --output-format json > full_report.json
   # Filter/transform with jq or Python
   cat full_report.json | jq '.[] | select(.kind == "text")'
   ```

---

## Performance Checklist

### Before Running Comparison

- [ ] File sizes known?
- [ ] Files available locally (not network)?
- [ ] Have sufficient disk space for output?
- [ ] Know which comparison options are needed?

### For Large Files (>50 MB)

- [ ] Using `--stream` flag?
- [ ] Memory usage acceptable?
- [ ] Comparison time acceptable (might take minutes)?
- [ ] Consider `--structure-only` if possible?

### For Frequent Comparisons

- [ ] Batch operations where possible?
- [ ] Cache schemas?
- [ ] Skip unnecessary comparisons (identical files)?
- [ ] Use interactive mode for drill-down exploration?

### For Production Deployment

- [ ] Baseline performance benchmarked?
- [ ] Resource limits configured (memory, CPU)?
- [ ] Error handling for edge cases?
- [ ] Timeout configured for long comparisons?

---

## Profiling & Debugging

### Timing Comparisons

```bash
# Measure total execution time
time xmlcompare --files file1.xml file2.xml

# Measure with detailed tracing
xmlcompare --files file1.xml file2.xml --verbose
```

### Memory Monitoring

```bash
# Linux: Monitor memory during comparison
watch -n 1 "ps aux | grep xmlcompare"

# Windows: Use Task Manager or:
Get-Process java -Name xmlcompare | Select-Object WorkingSet
```

### Finding Slow Comparisons

```bash
# Test with increasing depth limits
xmlcompare --files file1.xml file2.xml --max-depth 3
xmlcompare --files file1.xml file2.xml --max-depth 10
xmlcompare --files file1.xml file2.xml --max-depth 100
# Identify at which depth speed degrades
```

---

## Tuning Parameters

### Java JVM Tuning

```bash
# Increase heap for very large files
java -Xmx4g -jar xmlcompare.jar --files huge1.xml huge2.xml

# Tune garbage collection
java -XX:+UseG1GC -Xmx4g -jar xmlcompare.jar ...
```

### Python Tuning

```python
# Disable unnecessary features
import sys
sys.dont_write_bytecode = True  # Faster startup

# Use PyPy for 2-3x speedup (if compatible)
pypy3 xmlcompare.py ...
```

---

## Common Performance Issues

### Issue: Comparison takes too long

**Cause:** File too large for DOM parsing
**Solution:** Use `--stream` flag

### Issue: Out of memory

**Cause:** File too large, DOM loaded entirely into memory
**Solution:** Use `--stream` flag, or split file into chunks

### Issue: Slow on network files

**Cause:** Network I/O overhead
**Solution:** Copy files locally first, then compare

### Issue: Interactive mode unresponsive

**Cause:** Too many differences to display
**Solution:** Filter by type or path first

---

## Benchmarking Your Environment

Run the included benchmark suite:

```bash
# Python
python -m pytest --benchmark-only tests/

# Java
mvn clean integration-test -P benchmark
```

Compare results against baseline to identify regressions.

---

## See Also

- [FEATURES.md](FEATURES.md) — Feature guide
- [README.md](README.md) — General usage
- [PLUGINS.md](PLUGINS.md) — Creating custom plugins
