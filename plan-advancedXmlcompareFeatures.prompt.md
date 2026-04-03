# Implementation Plan: Advanced xmlcompare Features

**TL;DR**: Implement 5 major features across 4 phased releases with dependencies resolved upfront. Start with foundational infrastructure (plugin system + schema integration), then build output formats, performance, and interactive mode. Estimate 12-16 weeks for full implementation.

---

## Requirements Summary

| Feature | Format | Scale | Extensibility | Interactions | Schema Role |
|---------|--------|-------|---|---|---|
| Diff Output | Unified (CLI) + HTML | Large (10MB-1GB) | Full plugins | N/A | N/A |
| Performance | Streaming + parallel | 10MB-1GB | Via config | N/A | N/A |
| Plugins | Rules + formatters + diff handling | All | Full extensibility | N/A | Full |
| Interactive | File browser + filtering + drill-down | All | Via plugins | All | Full |
| Schema-Aware | Pre-validation + matching + type-aware | All | Via config | N/A | Full |

---

## Phase Overview

### Phase 1: Foundation (Weeks 1-3) — Plugin Architecture & Schema Integration
**Goal**: Build extensibility framework and schema-aware comparison engine as foundation for other features.
**Deliverable**: Runnable comparison with basic plugin system and schema hints during comparison.

### Phase 2: Output Formats (Weeks 4-6) — Diff Output + HTML Side-by-Side
**Goal**: Implement unified diff (CLI) and side-by-side HTML diff output using plugin system.
**Deliverable**: CLI supports `--format unified-diff`, new HTML output with side-by-side view.

### Phase 3: Performance (Weeks 7-10) — Large File Optimization & Streaming
**Goal**: Optimize for 10MB-1GB files using streaming parsing and optional parallelization.
**Deliverable**: Benchmark suite, SAX/iterparse implementations, `--stream` flag, memory profiling.

### Phase 4: Interactive Mode (Weeks 11-14) — CLI Explorer + Web UI
**Goal**: Build interactive file browser, live filtering, hierarchical exploration.
**Deliverable**: `interactive` command with TUI, optional lightweight web UI.

### Phase 5: Polish & Testing (Weeks 15-16) — Integration, docs, performance validation
**Goal**: Cross-feature validation, documentation, performance benchmarking.
**Deliverable**: End-to-end tests, performance reports, user guides.

---

## Implementation Steps

### **Phase 1: Plugin Architecture & Schema Integration**

#### 1.1 Design Plugin System Architecture
**Files to Create:**
- `java/src/main/java/com/xmlcompare/plugin/ComparisonPluginSPI.java` — Service Provider Interface
- `java/src/main/java/com/xmlcompare/plugin/FormatterPlugin.java` — Formatter plugin base/interface
- `java/src/main/java/com/xmlcompare/plugin/DifferenceFilter.java` — Custom difference rules
- `python/xmlcompare/plugin_interface.py` — Python plugin interface
- `java/src/main/java/com/xmlcompare/plugin/PluginRegistry.java` — Plugin discovery & loading
- `java/src/main/resources/META-INF/services/com.xmlcompare.plugin.FormatterPlugin` — SPI manifest

**Tasks:**
1. Define Java SPI-based plugin interfaces for formatters and difference rules
2. Create Python plugin discovery mechanism (importlib entry points)
3. Implement `PluginRegistry.load()` for both Java and Python
4. Create example stub plugins (reference implementation)
5. Update `CompareOptions` to accept plugin configurations
6. Add plugin loading to CLI in both `Main.java` and `xmlcompare.py`

**Verification:**
- Plugin can be registered and discovered by name
- Custom formatter plugin can be loaded and executed
- All existing tests pass
- New `--plugins` CLI option is recognized

#### 1.2 Integrate Schema Awareness into Comparison
**Files to Modify:**
- `java/src/main/java/com/xmlcompare/XmlCompare.java` — Add schema-aware comparison logic
- `java/src/main/java/com/xmlcompare/CompareOptions.java` — Add schema path option
- `java/src/main/java/com/xmlcompare/schema/SchemaAnalyzer.java` — NEW, analyze schema metadata
- `python/xmlcompare.py` — Add schema-aware comparison wrapper
- `python/validate_xsd.py` — Extend to return schema metadata API

**Tasks:**
1. Create `SchemaAnalyzer` class that parses XSD and returns:
   - Element cardinality (minOccurs, maxOccurs)
   - Ordering constraints
   - Data types and patterns
   - Optional vs required fields
2. Pre-flight schema validation (both files against XSD if provided)
3. Pass schema hints to `compareElements()` for smarter matching (unordered vs ordered elements)
4. Type-aware comparison: if schema says `xs:date`, apply date tolerance rules
5. Add `--schema` CLI option to specify schema path
6. Add `--type-aware` flag to enable type-based normalization

**Verification:**
- Schema metadata correctly extracted for sample XSD
- Comparison uses schema hints for element matching
- Date/number fields compared with type awareness
- Pre-validation catches invalid XML early
- New `--schema` and `--type-aware` flags work

---

### **Phase 2: Output Formats (Diff Output + HTML Side-by-Side)**

#### 2.1 Implement Unified Diff Formatter
**Files to Create/Modify:**
- `java/src/main/java/com/xmlcompare/format/UnifiedDiffFormatter.java` — NEW
- `python/xmlcompare/format_unified_diff.py` — NEW
- Both implement formatter plugin interface from Phase 1

**Tasks:**
1. Create unified diff output format (similar to `git diff --unified=3`)
2. Display:
   - File headers: `--- expected.xml` / `+++ actual.xml`
   - Hunk headers: `@@ -start,count +start,count @@`
   - Context lines (3 lines before/after difference)
   - Removed lines prefixed with `-`, added with `+`, context with space
3. Implement as plugin (extends `FormatterPlugin`)
4. Add `--format unified-diff` CLI option
5. Color support for terminal (optional ANSI colors)

**Verification:**
- Unified diff output matches industry standard format
- Context lines display correctly
- ANSI colors work in terminal
- Plugin loads successfully

#### 2.2 Implement Side-by-Side HTML Diff Formatter
**Files to Create/Modify:**
- `java/src/main/java/com/xmlcompare/format/HtmlSideBySideFormatter.java` — NEW
- `python/xmlcompare/format_html_sidebyside.py` — NEW
- Include inline CSS styling (no external dependencies)

**Tasks:**
1. Generate HTML with two-column layout:
   - Left column: expected XML with line numbers
   - Right column: actual XML with line numbers
   - Differences highlighted in color
2. Include metadata (file paths, timestamps, summary statistics)
3. Use inline CSS for standalone viewing (no external files)
4. Optional: Interactive features (collapsible sections, hover tooltips)
5. Implement as plugin, register with `--format html-diff`
6. Generate self-contained HTML file (no browser dependencies)

**Verification:**
- HTML renders properly in browser (Chrome, Firefox, Safari)
- Side-by-side display is readable (reasonable column width)
- Differences are visually distinct
- File is self-contained (no external CSS/JS)
- Plugin loads successfully

---

### **Phase 3: Performance Optimization**

#### 3.1 Implement Streaming XML Parsing
**Files to Create/Modify:**
- `java/src/main/java/com/xmlcompare/parse/StreamingXmlParser.java` — NEW (SAX-based)
- `python/xmlcompare/parse_streaming.py` — NEW (iterparse-based)
- `java/src/main/java/com/xmlcompare/CompareOptions.java` — Add `--stream` mode flag
- `python/xmlcompare.py` — Add `--stream` mode option

**Tasks:**
1. **Java (SAX)**: Implement event-based parsing that:
   - Reads file incrementally without loading full DOM
   - Reports elements one at a time
   - Reduces memory footprint for large files (e.g., multi-GB logs)
2. **Python (iterparse)**: Use `xml.etree.ElementTree.iterparse()` for event-based streaming
3. Implement lazy comparison: compare as elements arrive, not after full parse
4. Add memory profiling to track heap usage
5. Implement `--stream` flag to enable streaming mode
6. Benchmark memory usage: streaming vs DOM for 10MB, 100MB, 1GB files

**Verification:**
- Memory usage < 50MB for 1GB file (vs typical 5GB for full DOM)
- Streaming output matches non-streaming output
- Comparison results identical
- `--stream` flag recognized

#### 3.2 Implement Parallel Diff Computation (Optional)
**Files to Create/Modify:**
- `java/src/main/java/com/xmlcompare/parallel/ParallelComparison.java` — NEW
- `python/xmlcompare/parallel.py` — NEW (multiprocessing)
- `java/src/main/java/com/xmlcompare/CompareOptions.java` — Add `--parallel` flag
- `python/xmlcompare.py` — Add `--parallel` flag

**Tasks:**
1. For large files, split into chunks and compare in parallel
2. Java: Use `ExecutorService` (thread pool)
3. Python: Use `multiprocessing.Pool` for CPU-bound comparison
4. Merge results maintaining order
5. Benchmark speedup on multi-core systems (target 2-4x on quad-core)
6. Add `--parallel` flag with optional thread count

**Verification:**
- Parallel comparison output matches serial output
- Speedup measured (e.g., 2x faster on 2+ cores)
- Memory usage is reasonable (not linear with thread count)

#### 3.3 Performance Profiling & Tuning
**Files to Create:**
- `.github/workflows/perf.yml` — NEW performance benchmark CI job
- `perf/benchmark.py` / `perf/benchmark.java` — performance test suite
- `perf/generate_large_xml.py` — generate test files (10MB, 100MB, 1GB)

**Tasks:**
1. Create benchmark suite that compares files of various sizes
2. Measure: parse time, comparison time, memory usage
3. Generate test files programmatically
4. CI job runs benchmarks on each commit, tracks trends
5. Document optimization opportunities in PERFORMANCE.md

**Verification:**
- Benchmark suite runs without errors
- Performance metrics collected and documented
- Streaming provides 5-10x memory improvement
- Parallel provides measurable speedup

---

### **Phase 4: Interactive Mode**

#### 4.1 Build Interactive CLI Explorer (TUI)
**Files to Create/Modify:**
- `java/src/main/java/com/xmlcompare/interactive/InteractiveMode.java` — NEW
- `python/xmlcompare/interactive_cli.py` — NEW
- `Main.java` / `xmlcompare.py` — Add `interactive` command
- `pom.xml` / `pyproject.toml` — Add TUI library dependencies:
  - Java: `Lanterna` (text GUI) or `Picocli` interactive features
  - Python: `prompt-toolkit` or `curses`

**Tasks:**
1. **File Browser**:
   - Navigate filesystem to select two XML files
   - Autocomplete file paths
   - Show file size/modification date
2. **Comparison Result Navigator**:
   - Display summary (# of differences, types)
   - List all differences with line numbers
   - Filter by difference type (tag, text, attr, missing, extra)
   - Filter by element path (e.g., `/root/*/child`)
3. **Live Filtering**:
   - Filter results by namespace, tag name, depth
   - Show filtered diff count in real-time
4. **Drill-Down Navigation**:
   - Expand/collapse difference context
   - Jump to specific difference
   - Show parent path and siblings
5. **Export**: Save current filtered results to file (JSON, HTML, unified diff)

**Verification:**
- TUI renders without corruption
- File browser can select files
- Filtering works correctly
- Export formats match non-interactive versions
- Navigation is smooth and responsive

#### 4.2 Build Lightweight Web UI (Optional)
**Files to Create:**
- `web/index.html` / `web/ui.js` — NEW simple web interface
- `java/src/main/java/com/xmlcompare/web/WebServer.java` — NEW (optional)
- `python/xmlcompare/web_api.py` — NEW REST API endpoints

**Tasks (Option A: Standalone)**:
1. Simple HTML UI for file upload + comparison
2. Display results with filtering and drill-down
3. Export to JSON/HTML/diff
4. No complex build system (vanilla JS + HTML5)

**Tasks (Option B: Optional Web Server)**:
1. REST API endpoints:
   - `POST /compare` — upload two files and compare
   - `GET /results/:id` — fetch comparison results
   - `GET /results/:id/differences?filter=tag` — filtered results
2. WebSocket support for live filtering (real-time response)
3. Lightweight server (Spark for Java, Flask for Python)

**Verification:**
- Web UI loads and renders correctly
- File upload works
- Comparison results display
- Filters work in real-time
- Export functions correctly

---

### **Phase 5: Integration & Polish**

#### 5.1 Cross-Feature Integration Tests
**Files to Create/Modify:**
- `tests/integration/test_diff_formats.py` / `XmlCompareDiffIntegrationTest.java` — NEW
- `tests/integration/test_schema_plugin_interaction.py` — NEW
- `tests/integration/test_performance_formats.py` — NEW

**Tasks:**
1. Test diff formats with schema-aware comparison
2. Test interactive mode with streaming parser
3. Test plugin loading with schema hints
4. Test performance benchmarks with parallel mode
5. End-to-end scenarios (CLI → interactive → export)

**Verification:**
- All integration tests pass
- No regressions in existing tests (119 Python + 57 Java)
- Feature combinations work as expected

#### 5.2 Documentation & User Guides
**Files to Create/Modify:**
- `FEATURES.md` — NEW, comprehensive feature list with examples
- `PLUGINS.md` — NEW plugin development guide
- `PERFORMANCE.md` — NEW performance tuning guide
- `INTERACTIVE.md` — NEW interactive mode guide
- `README.md` — Update with new features
- `.github/workflows/ci.yml` — Update to run new tests

**Tasks:**
1. Document each feature with examples
2. Plugin development guide (how to write plugins)
3. Performance tuning best practices
4. Interactive mode keyboard shortcuts / navigation
5. Update README with quick-start examples
6. Add CI jobs for new test suites

**Verification:**
- Documentation is clear and complete
- Examples can be copy-pasted and run
- Plugin guide enables third-party development

#### 5.3 Performance Validation & Benchmarking
**Files to Create:**
- `PERFORMANCE_REPORT.md` — benchmark results and analysis

**Tasks:**
1. Run full benchmark suite on reference machine
2. Document performance across file sizes (10MB, 100MB, 1GB)
3. Compare: streaming vs DOM, parallel vs serial
4. Identify remaining bottlenecks
5. Create performance regression tests in CI

**Verification:**
- Streaming provides expected memory savings
- Parallel provides measurable speedup
- Large file tests complete in reasonable time
- CI monitors performance trends

---

## Relevant Files Reference

### To Modify
- **Java CLI**: `java/src/main/java/com/xmlcompare/Main.java` (options)
- **Java Core**: `java/src/main/java/com/xmlcompare/XmlCompare.java` (comparison logic)
- **Python CLI**: `python/xmlcompare.py` (argparse, comparison wrapper)
- **Config**: `java/pom.xml`, `python/pyproject.toml` (add dependencies)

### To Create (Phase 1)
- Plugin system files (6 files: Java interfaces + Python module)
- Schema analyzer (2 files: Java + Python)

### To Create (Phases 2-5)
- Formatters (2 × 2 files: unified diff, HTML side-by-side)
- Streaming parsers (2 files: Java SAX, Python iterparse)
- Interactive mode (2 files: TUI + optional web)
- Tests & benchmarks (6+ files)
- Documentation (5+ files)

---

## Verification Strategy

### Per-Phase Verification
1. **Phase 1**: Plugin loads, schema metadata extracted correctly, existing tests pass
2. **Phase 2**: Diff output matches expected format, new `--format` options work
3. **Phase 3**: Memory usage < 50MB for 1GB file, parallel shows 2x speedup, all tests pass
4. **Phase 4**: TUI navigates without errors, interactive commands work, export matches formats
5. **Phase 5**: All integration tests pass, documentation is complete, performance benchmarks are established

### Regression Testing
- Run all 119 Python + 57 Java tests after each phase
- No output differences for existing comparison scenarios
- Performance must not degrade for small files

### Performance Checkpoints
- Phase 3: 10MB file comparison < 1s, 100MB file < 10s, 1GB file < 60s (with streaming)
- Parallel: 2-4x speedup vs serial on shared pool

---

## Dependencies & Ordering

**Critical Path**:
1. Phase 1 → Phase 2 (plugins required for diff formatters)
2. Phase 1 → Phase 3 (schema needed for type-aware optimization)
3. Phase 2 + Phase 3 → Phase 4 (interactive needs formatters + performance)
4. All phases → Phase 5 (integration testing)

**Parallel Implementation** (no blocker):
- Phase 2 and Phase 3 can run in parallel after Phase 1

---

## Scope & Exclusions

### Included
- ✅ Unified diff + HTML side-by-side formatters
- ✅ Streaming parser optimization
- ✅ Plugin system for formatters and custom rules
- ✅ Schema-aware comparison with type awareness
- ✅ Interactive CLI (TUI) with filtering and drill-down
- ✅ Benchmarking and performance validation

### Excluded (Out of Scope)
- ❌ Web server deployment / Docker containerization
- ❌ GUI application (Qt/Swing based)
- ❌ XSLT transformation during comparison
- ❌ Distributed comparison across network
- ❌ Real-time file watching / live comparison

---

## Success Criteria

| Criterion | Measurement |
|-----------|------------|
| Plugin system usable | Third-party plugin can be written in < 2 hours |
| Diff formats | Output matches industry standard (unified diff = git format, HTML = readable in all browsers) |
| Performance | 1GB file compares in < 60s, memory < 100MB |
| Interactive mode | All keyboard shortcuts documented, user can filter results in < 5 seconds |
| Schema-aware | Type-aware comparison reduces false positives by 50%+ vs standard comparison |
| Backward compatible | All existing tests (119 Python + 57 Java) pass without modification |

---

## Time Estimates

| Phase | Components | Estimate | Risk |
|-------|-----------|----------|------|
| **1** | Plugin system (2) + Schema (2) | 3 weeks | Medium (SPI design complexity) |
| **2** | Unified diff (2) + HTML diff (2) | 3 weeks | Low (straightforward implementations) |
| **3** | Streaming (2) + Parallel (2) + Benchmarks | 4 weeks | Medium (requires profiling, optimization) |
| **4** | TUI (2) + Web UI (2, optional) | 4 weeks | Medium (TUI complexity, responsive design) |
| **5** | Integration + Docs + Validation | 2 weeks | Low (assembly work) |
| **Total** | 16 components, 2 languages | **16 weeks** | — |

---

## Next Steps

1. **Review & Approval**: User confirms plan scope, priorities, and success criteria
2. **Phase 1 Kickoff**: Start plugin system + schema integration design
3. **Dependency Resolution**: Finalize library choices (Lanterna vs Picocli, prompt-toolkit vs curses)
4. **Create Tracking**: Set up GitHub issues for each phase/task
5. **CI/CD Setup**: Configure GitHub Actions for new test suites and benchmarks
