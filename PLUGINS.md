# Plugin Development Guide

Complete guide for creating and integrating custom FormatterPlugins and DifferenceFilters with xmlcompare.

- [Plugin Development Guide](#plugin-development-guide)
  - [Plugin Architecture](#plugin-architecture)
    - [Core Concepts](#core-concepts)
    - [Plugin Lifecycle](#plugin-lifecycle)
    - [Plugin Interfaces](#plugin-interfaces)
      - [FormatterPlugin](#formatterplugin)
      - [DifferenceFilter](#differencefilter)
  - [Creating a Formatter Plugin](#creating-a-formatter-plugin)
    - [Python Example: CSV Formatter](#python-example-csv-formatter)
    - [Python Example: Markdown Formatter](#python-example-markdown-formatter)
    - [Java Example: Markdown Formatter](#java-example-markdown-formatter)
  - [Creating a Difference Filter](#creating-a-difference-filter)
    - [Python Example: Type Filter](#python-example-type-filter)
    - [Java Example: Severity Filter](#java-example-severity-filter)
  - [Python Implementation](#python-implementation)
    - [Setting Up Plugin Module](#setting-up-plugin-module)
    - [Registering Plugin in Python](#registering-plugin-in-python)
      - [Method 1: Programmatic Registration](#method-1-programmatic-registration)
      - [Method 2: Entry Points (setuptools)](#method-2-entry-points-setuptools)
  - [Java Implementation](#java-implementation)
    - [Setting Up Plugin Module Structure](#setting-up-plugin-module-structure)
    - [service manifest](#service-manifest)
    - [Registering Plugin in Java](#registering-plugin-in-java)
      - [Method One: Programmatic Registration](#method-one-programmatic-registration)
      - [Method Two: Service Loader (Automatic)](#method-two-service-loader-automatic)
  - [Testing Plugins](#testing-plugins)
    - [Python Test Example](#python-test-example)
    - [Java Test Example](#java-test-example)
  - [Registering Plugins](#registering-plugins)
    - [Python Auto-Registration](#python-auto-registration)
    - [Java Service Loader](#java-service-loader)
  - [Distributing Plugins](#distributing-plugins)
    - [Python Package](#python-package)
    - [Java Package](#java-package)
  - [Plugin Best Practices](#plugin-best-practices)
    - [Do](#do)
    - [Don't](#dont)
  - [Troubleshooting](#troubleshooting)
    - [Plugin Not Found](#plugin-not-found)
    - [ClassNotFoundException (Java)](#classnotfoundexception-java)
    - [ImportError (Python)](#importerror-python)
  - [Example: Complete Plugin Package](#example-complete-plugin-package)
  - [See Also](#see-also)

---

## Plugin Architecture

### Core Concepts

**FormatterPlugin**: Converts comparison results into formatted output

- Input: Comparison results (list of Difference objects)
- Output: Formatted string (any text-based format)
- Responsibility: Present differences in human-readable format

**DifferenceFilter**: Selects/excludes differences based on criteria

- Input: List of Difference objects
- Output: Filtered list
- Responsibility: Pre-process results before formatting

### Plugin Lifecycle

```plaintext
1. Plugin Loaded → 2. Plugin Registered → 3. Plugin Selected → 4. Plugin Executed → 5. Result Returned
```

### Plugin Interfaces

#### FormatterPlugin

**Python:**

```python
class FormatterPlugin:
    @property
    def name(self) -> str:
        """Unique plugin identifier (used with --output-format)"""
        return "my-format"

    def format(self, differences, label1=None, label2=None) -> str:
        """Format comparison results. Returns formatted string."""
        pass
```

**Java:**

```java
public interface FormatterPlugin {
    String getName();
    String format(List<Difference> differences,
                  String label1, String label2);
}
```

#### DifferenceFilter

**Python:**

```python
class DifferenceFilter:
    @property
    def name(self) -> str:
        """Unique filter identifier"""
        return "my-filter"

    def filter(self, differences) -> List[Difference]:
        """Filter differences. Return filtered list."""
        pass
```

**Java:**

```java
public interface DifferenceFilter {
    String getName();
    List<Difference> filter(List<Difference> differences);
}
```

---

## Creating a Formatter Plugin

### Python Example: CSV Formatter

```python
# my_plugins/csv_formatter.py

from plugin_interface import FormatterPlugin
import csv
import io

class CsvFormatter(FormatterPlugin):
    @property
    def name(self):
        return "csv"

    def format(self, differences, label1=None, label2=None):
        """Format differences as CSV."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'kind', 'path', 'element', 'value1', 'value2', 'message'
        ])

        writer.writeheader()
        for diff in differences:
            writer.writerow({
                'kind': diff.kind,
                'path': diff.path,
                'element': diff.element,
                'value1': getattr(diff, 'value1', ''),
                'value2': getattr(diff, 'value2', ''),
                'message': diff.message,
            })

        return output.getvalue()
```

**Usage:**

```bash
xmlcompare --files file1.xml file2.xml --output-format csv > results.csv
```

### Python Example: Markdown Formatter

```python
# my_plugins/markdown_formatter.py

from plugin_interface import FormatterPlugin

class MarkdownFormatter(FormatterPlugin):
    @property
    def name(self):
        return "markdown"

    def format(self, differences, label1=None, label2=None):
        """Format differences as Markdown."""
        lines = []
        lines.append(f"# XML Comparison Report")
        lines.append(f"\n**File 1:** {label1 or 'N/A'}")
        lines.append(f"**File 2:** {label2 or 'N/A'}")
        lines.append(f"\n## Summary\n")
        lines.append(f"- Total differences: {len(differences)}")
        lines.append(f"- Text changes: {sum(1 for d in differences if d.kind == 'text')}")
        lines.append(f"- Attribute changes: {sum(1 for d in differences if d.kind == 'attribute')}")
        lines.append(f"- Structure changes: {sum(1 for d in differences if d.kind in ['tag', 'missing', 'extra'])}")

        lines.append(f"\n## Differences\n")
        for i, diff in enumerate(differences, 1):
            lines.append(f"\n### {i}. {diff.kind.upper()}")
            lines.append(f"- **Path:** `{diff.path}`")
            lines.append(f"- **Message:** {diff.message}")
            if hasattr(diff, 'value1') and diff.value1:
                lines.append(f"- **Before:** `{diff.value1}`")
            if hasattr(diff, 'value2') and diff.value2:
                lines.append(f"- **After:** `{diff.value2}`")

        return "\n".join(lines)
```

### Java Example: Markdown Formatter

```java
// src/main/java/com/xmlcompare/format/MarkdownFormatter.java

package com.xmlcompare.format;

import com.xmlcompare.core.Difference;
import com.xmlcompare.plugin.FormatterPlugin;
import java.util.List;
import java.util.stream.Collectors;

public class MarkdownFormatter implements FormatterPlugin {

    @Override
    public String getName() {
        return "markdown";
    }

    @Override
    public String format(List<Difference> differences, String label1, String label2) {
        StringBuilder sb = new StringBuilder();
        sb.append("# XML Comparison Report\n\n");
        sb.append("**File 1:** ").append(label1 != null ? label1 : "N/A").append("\n");
        sb.append("**File 2:** ").append(label2 != null ? label2 : "N/A").append("\n\n");

        // Summary
        sb.append("## Summary\n\n");
        sb.append("- Total differences: ").append(differences.size()).append("\n");
        sb.append("- Text changes: ")
            .append(differences.stream().filter(d -> "text".equals(d.getKind())).count())
            .append("\n");
        sb.append("- Attribute changes: ")
            .append(differences.stream().filter(d -> "attribute".equals(d.getKind())).count())
            .append("\n");

        // Differences
        sb.append("\n## Differences\n\n");
        for (int i = 0; i < differences.size(); i++) {
            Difference diff = differences.get(i);
            sb.append("\n### ").append(i + 1).append(". ")
                .append(diff.getKind().toUpperCase()).append("\n");
            sb.append("- **Path:** `").append(diff.getPath()).append("`\n");
            sb.append("- **Message:** ").append(diff.getMessage()).append("\n");
        }

        return sb.toString();
    }
}
```

---

## Creating a Difference Filter

### Python Example: Type Filter

```python
# my_plugins/type_filter.py

from plugin_interface import DifferenceFilter

class TypeOnlyFilter(DifferenceFilter):
    """Filter to show only type-related differences."""

    @property
    def name(self):
        return "type-only"

    def filter(self, differences):
        """Keep only differences involving type mismatches."""
        return [d for d in differences
                if d.kind == "attribute" and "type" in d.path.lower()]
```

### Java Example: Severity Filter

```java
// src/main/java/com/xmlcompare/filter/SeverityFilter.java

package com.xmlcompare.filter;

import com.xmlcompare.core.Difference;
import com.xmlcompare.plugin.DifferenceFilter;
import java.util.List;
import java.util.stream.Collectors;

public class SeverityFilter implements DifferenceFilter {

    private String minSeverity; // "low", "medium", "high"

    public SeverityFilter(String minSeverity) {
        this.minSeverity = minSeverity;
    }

    @Override
    public String getName() {
        return "severity-" + minSeverity;
    }

    @Override
    public List<Difference> filter(List<Difference> differences) {
        int threshold = getSeverityLevel(minSeverity);
        return differences.stream()
            .filter(d -> getSeverityLevel(d.getKind()) >= threshold)
            .collect(Collectors.toList());
    }

    private int getSeverityLevel(String kind) {
        // Structural changes are high severity
        if (kind.equals("tag") || kind.equals("missing") || kind.equals("extra")) return 3;
        // Attribute changes are medium
        if (kind.equals("attribute")) return 2;
        // Text changes are low
        return 1;
    }
}
```

---

## Python Implementation

### Setting Up Plugin Module

```shell
my_plugins/
├── __init__.py
├── formatters/
│   ├── __init__.py
│   ├── csv_formatter.py
│   └── markdown_formatter.py
└── filters/
    ├── __init__.py
    └── type_filter.py
```

### Registering Plugin in Python

#### Method 1: Programmatic Registration

```python
from plugin_interface import get_registry
from my_plugins.formatters.csv_formatter import CsvFormatter

# Register plugin
registry = get_registry()
registry.register_formatter(CsvFormatter())

# Use in comparison
results = compare_xml_files("file1.xml", "file2.xml")
formatted = registry.get_formatter("csv").format(results)
```

#### Method 2: Entry Points (setuptools)

Add to `setup.py`:

```python
setup(
    name="xmlcompare-csv-plugin",
    entry_points={
        "xmlcompare.formatters": [
            "csv = my_plugins.formatters.csv_formatter:CsvFormatter",
            "markdown = my_plugins.formatters.markdown_formatter:MarkdownFormatter",
        ],
        "xmlcompare.filters": [
            "type-only = my_plugins.filters.type_filter:TypeOnlyFilter",
        ],
    },
)
```

Then install: `pip install -e .`

The entry points are automatically discovered on import:

```python
from plugin_interface import get_registry
registry = get_registry()
# All registered plugins available
```

---

## Java Implementation

### Setting Up Plugin Module Structure

```shell
my-plugins/
├── pom.xml
└── src/main/java/com/example/xmlcompare/plugin/
    ├── MarkdownFormatter.java
    └── SeverityFilter.java
```

### service manifest

Create: `src/main/resources/META-INF/services/com.xmlcompare.plugin.FormatterPlugin`

```java
com.example.xmlcompare.plugin.MarkdownFormatter
com.example.xmlcompare.plugin.CsvFormatter
```

Create: `src/main/resources/META-INF/services/com.xmlcompare.plugin.DifferenceFilter`

```java
com.example.xmlcompare.plugin.SeverityFilter
```

### Registering Plugin in Java

#### Method One: Programmatic Registration

```java

PluginRegistry registry = new PluginRegistry();
registry.registerFormatter(new MarkdownFormatter());
registry.registerFormatter(new CsvFormatter());
```

#### Method Two: Service Loader (Automatic)

```java
PluginRegistry registry = new PluginRegistry();
registry.loadServiceLoader(); // Automatically discovers all registered plugins
```

---

## Testing Plugins

### Python Test Example

```python
# tests/test_my_csv_formatter.py

import pytest
from my_plugins.formatters.csv_formatter import CsvFormatter
from xmlcompare import Difference

@pytest.fixture
def sample_differences():
    return [
        Difference(kind="text", path="/root/item", element="value",
                   message="Text differs", value1="A", value2="B"),
        Difference(kind="attribute", path="/root/item@id", element="@id",
                   message="Attribute differs", value1="1", value2="2"),
    ]

def test_csv_formatter_header(sample_differences):
    formatter = CsvFormatter()
    output = formatter.format(sample_differences)
    assert "kind,path,element,value1,value2,message" in output

def test_csv_formatter_data(sample_differences):
    formatter = CsvFormatter()
    output = formatter.format(sample_differences)
    assert "text" in output
    assert "attribute" in output
    assert "/root/item" in output
```

### Java Test Example

```java
// src/test/java/com/example/xmlcompare/plugin/MarkdownFormatterTest.java

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import com.xmlcompare.core.Difference;
import com.example.xmlcompare.plugin.MarkdownFormatter;
import java.util.Arrays;
import java.util.List;

class MarkdownFormatterTest {

    @Test
    void testFormatHeader() {
        MarkdownFormatter formatter = new MarkdownFormatter();
        List<Difference> diffs = Arrays.asList(
            new Difference("text", "/root/item", "value", "Text differs", "A", "B")
        );

        String output = formatter.format(diffs, "file1.xml", "file2.xml");
        assertTrue(output.contains("# XML Comparison Report"));
        assertTrue(output.contains("file1.xml"));
        assertTrue(output.contains("file2.xml"));
    }

    @Test
    void testFormatDifferences() {
        MarkdownFormatter formatter = new MarkdownFormatter();
        List<Difference> diffs = Arrays.asList(
            new Difference("text", "/root/item", "value", "Text differs", "A", "B")
        );

        String output = formatter.format(diffs, "file1.xml", "file2.xml");
        assertTrue(output.contains("TEXT"));
        assertTrue(output.contains("/root/item"));
    }
}
```

---

## Registering Plugins

### Python Auto-Registration

Place plugin in `xmlcompare.plugins` package or use entry_points:

```toml
# pyproject.toml
[project.entry-points."xmlcompare.formatters"]
myformat = "my_plugins.formatters:MyFormatter"
```

### Java Service Loader

Create service manifest and jar file:

```shell
my-plugin.jar/
└── META-INF/services/
    └── com.xmlcompare.plugin.FormatterPlugin
        → com.example.MyFormatter
```

Add jar to classpath:

```bash
java -cp xmlcompare.jar:my-plugin.jar ... main-class
```

---

## Distributing Plugins

### Python Package

1. Create `setup.py` or `pyproject.toml`:

```python
[project]
name = "xmlcompare-csv-plugin"
entry-points."xmlcompare.formatters" = {
    csv = "xmlcompare_csv.formatter:CsvFormatter"
}
```

2. Publish to PyPI:

```bash
pip install build
python -m build
twine upload dist/*
```

3. Users install:

```bash
pip install xmlcompare xmlcompare-csv-plugin
```

### Java Package

1. Create Maven project:

```xml
<project>
    <artifactId>xmlcompare-csv-plugin</artifactId>
    <groupId>com.example</groupId>
</project>
```

2. Publish to Maven Central:

```bash
mvn clean deploy
```

3. Users add dependency:

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>xmlcompare-csv-plugin</artifactId>
    <version>1.0</version>
</dependency>
```

---

## Plugin Best Practices

### Do

✅ Keep formatting logic separate from comparison logic

✅ Handle null/empty results gracefully

✅ Use descriptive plugin names (lowercase, hyphenated)

✅ Document plugin parameters and output format

✅ Add comprehensive tests

✅ Handle escape/encoding properly

✅ Return consistent formatted output

### Don't

❌ Modify differences in-place (use copies)

❌ Make blocking/network calls in format()

❌ Use undocumented internal APIs

❌ Hardcode paths or configuration

❌ Assume input always valid (validate!)

❌ Return unstructured output

---

## Troubleshooting

### Plugin Not Found

**Error:** `Plugin 'myformat' not found`

**Cause:** Plugin not registered
**Solution:** Ensure entry_points configured correctly or manually register

### ClassNotFoundException (Java)

**Error:** `java.lang.ClassNotFoundException: com.example.MyFormatter`

**Cause:** Plugin jar not in classpath
**Solution:** Add `-cp plugin.jar` to java command

### ImportError (Python)

**Error:** `ModuleNotFoundError: No module named 'my_plugins'`

**Cause:** Plugin module not installed
**Solution:** Install plugin package: `pip install .`

---

## Example: Complete Plugin Package

Full example at [github.com/xmlcompare-samples/csv-plugin](https://github.com)

---

## See Also

- [FEATURES.md](FEATURES.md) — Using plugins
- [PERFORMANCE.md](PERFORMANCE.md) — Plugin performance
- [README.md](README.md) — General usage
