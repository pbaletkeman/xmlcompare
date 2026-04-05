# Configuration File Guide

Complete guide to using configuration files with xmlcompare.

## Overview

- [Configuration File Guide](#configuration-file-guide)
  - [Overview](#overview)
  - [Supported Formats](#supported-formats)
    - [JSON](#json)
    - [YAML](#yaml)
  - [Creating a Configuration File](#creating-a-configuration-file)
    - [Step 1: Choose Your Settings](#step-1-choose-your-settings)
    - [Step 2: Create Configuration File](#step-2-create-configuration-file)
    - [Step 3: Use the Configuration](#step-3-use-the-configuration)
  - [Configuration Options](#configuration-options)
  - [Configuration Profiles](#configuration-profiles)
    - [development.json](#developmentjson)
    - [production.json](#productionjson)
    - [performance.json (Java)](#performancejson-java)
  - [Override Config with Command Line](#override-config-with-command-line)
  - [Advanced Patterns](#advanced-patterns)
    - [Batch Processing](#batch-processing)
    - [Chained Configurations](#chained-configurations)
    - [Environment-Specific Configs](#environment-specific-configs)
  - [JSON Syntax Reference](#json-syntax-reference)
    - [Valid JSON](#valid-json)
    - [Common Mistakes](#common-mistakes)
  - [Validation](#validation)
    - [Python: Validate JSON](#python-validate-json)
    - [Java: Validate JSON](#java-validate-json)
    - [YAML Validation](#yaml-validation)
  - [Best Practices](#best-practices)
  - [Troubleshooting](#troubleshooting)
    - ["Config file not found"](#config-file-not-found)
    - ["Invalid JSON"](#invalid-json)
    - ["Config seems to be ignored"](#config-seems-to-be-ignored)
  - [Examples](#examples)
  - [See Also](#see-also)

Configuration files allow you to:

- Save and reuse comparison settings
- Eliminate repetitive command-line arguments
- Manage different profiles for different use cases
- Version control your comparison settings

## Supported Formats

### JSON

**Extension:** `.json`

Best for:

- Automated tool integration
- CI/CD pipelines
- Most programming languages have JSON support
- Human-editable while maintaining structure

**Example:**

```json
{
  "tolerance": 0.001,
  "ignore_case": false,
  "unordered": true
}
```

### YAML

**Extension:** `.yaml` or `.yml`

Best for:

- Human readability
- Complex nested structures
- Configuration management systems
- Easier manual editing

**Requires:** Python version needs PyYAML installed

**Example:**

```yaml
tolerance: 0.001
ignore_case: false
unordered: true
skip_keys:
  - "//timestamp"
  - "//uuid"
```

## Creating a Configuration File

### Step 1: Choose Your Settings

Decide which options you need:

```bash
# I want to ignore namespaces, case, and order
# Skip timestamp fields
# Output as JSON
```

### Step 2: Create Configuration File

**production.json:**

```json
{
  "tolerance": 0.001,
  "ignore_case": false,
  "unordered": true,
  "ignore_namespaces": true,
  "skip_keys": [
    "//timestamp",
    "//uuid"
  ],
  "output_format": "json"
}
```

### Step 3: Use the Configuration

**Python:**

```bash
python xmlcompare.py --files file1.xml file2.xml --config production.json
```

**Java:**

```bash
java -jar xmlcompare.jar --files file1.xml file2.xml --config production.json
```

## Configuration Options

All available options (see also [config.json.example](../config.json.example)):

| Option            | Type    | Default | Description                         |
|-------------------|---------|---------|-------------------------------------|
| `tolerance`       | number  | 0.0     | Numeric tolerance for comparisons   |
| `ignore_case`      | boolean | false   | Case-insensitive comparison         |
| `unordered`       | boolean | false   | Ignore element order                |
| `ignore_namespaces`| boolean | false   | Ignore namespace URIs               |
| `ignore_attributes`| boolean | false   | Ignore all attributes               |
| `structure_only`   | boolean | false   | Compare only structure              |
| `max_depth`        | integer | null    | Limit depth (null = unlimited)      |
| `skip_keys`        | array   | []      | Elements to skip                    |
| `skip_pattern`     | string  | null    | Regex pattern for skipping          |
| `filter_xpath`     | string  | null    | XPath filter                        |
| `output_format`    | string  | "text"  | Output format                       |
| `output_file`      | string  | null    | Output file path                    |
| `summary`         | boolean | false   | Print summary only                  |
| `verbose`         | boolean | false   | Verbose output                      |
| `quiet`           | boolean | false   | Suppress output                     |
| `fail_fast`        | boolean | false   | Stop on first difference            |
| `schema`          | string  | null    | XSD schema file path                |
| `type_aware`       | boolean | false   | Type-aware comparison               |
| `plugins`         | array   | []      | Plugin classes to load              |

**Java-specific options:**

| Option      | Type    | Default | Description            |
|-------------|---------|---------|------------------------|
| `stream`    | boolean | false   | Use streaming parser   |
| `parallel`  | boolean | false   | Use parallel processing|
| `threads`   | integer | 4       | Number of threads      |

## Configuration Profiles

Create different profiles for different scenarios:

### development.json

```json
{
  "tolerance": 0.01,
  "ignore_case": true,
  "unordered": true,
  "ignore_namespaces": true,
  "verbose": true
}
```

### production.json

```json
{
  "tolerance": 0.0,
  "ignore_case": false,
  "unordered": false,
  "ignore_namespaces": false,
  "fail_fast": false,
  "output_format": "json"
}
```

### performance.json (Java)

```json
{
  "parallel": true,
  "threads": 8,
  "stream": true,
  "fail_fast": true,
  "summary": true
}
```

Usage:

```bash
# Use development profile
python xmlcompare.py --files test1.xml test2.xml --config development.json

# Use production profile
python xmlcompare.py --files test1.xml test2.xml --config production.json
```

## Override Config with Command Line

Command-line options always override config file values:

**config.json:**

```json
{
  "tolerance": 0.001,
  "ignore_case": false
}
```

**Command:**

```bash
# This overrides tolerance to 0.05
python xmlcompare.py --files file1.xml file2.xml --config config.json --tolerance 0.05
```

**Result:**

- tolerance: 0.05 (overridden)
- ignore_case: false (from config)

## Advanced Patterns

### Batch Processing

Create a script that uses config:

**batch-compare.sh:**

```bash
#!/bin/bash

CONFIG=$1
DIR1=$2
DIR2=$3

for file1 in "$DIR1"/*.xml; do
  file2="$DIR2/$(basename "$file1")"
  if [ -f "$file2" ]; then
    python xmlcompare.py --files "$file1" "$file2" --config "$CONFIG"
  fi
done
```

Usage:

```bash
./batch-compare.sh production.json baseline/ current/
```

### Chained Configurations

Use multiple config files progressively:

**base.json:**

```json
{
  "ignore_namespaces": true,
  "ignore_case": false
}
```

**strict.json (extends base):**

```json
{
  "ignore_namespaces": true,
  "ignore_case": false,
  "tolerance": 0.0,
  "fail_fast": true
}
```

### Environment-Specific Configs

**config.dev.json:** For development
**config.staging.json:** For staging
**config.prod.json:** For production

```bash
# Select based on environment
ENV=${ENVIRONMENT:-dev}
python xmlcompare.py --files file1.xml file2.xml --config "config.$ENV.json"
```

## JSON Syntax Reference

### Valid JSON

```json
{
  "stringValue": "text",
  "numberValue": 42,
  "decimalValue": 0.001,
  "booleanValue": true,
  "nullValue": null,
  "arrayValue": ["item1", "item2"],
  "nestedObject": {
    "key": "value"
  }
}
```

### Common Mistakes

❌ Wrong: Single quotes

```json
{ 'key': 'value' }  // JSON requires double quotes
```

**✓ Right:**

```json
{ "key": "value" }
```

❌ Wrong: Trailing comma

```json
{ "key": "value", }  // No trailing commas in JSON
```

**✓ Right:**

```json
{ "key": "value" }
```

❌ Wrong: Comments in JSON

```json
{
  "key": "value"  // This comment will break JSON
}
```

**✓ Right:**

```json
{
  "description": "Store comments in description field",
  "key": "value"
}
```

## Validation

### Python: Validate JSON

```bash
# Using Python
python -m json.tool config.json

# Using online validator
# https://jsonlint.com/
```

### Java: Validate JSON

```bash
# Quick validation
java -jar /path/to/jackson-cli.jar validate config.json
```

### YAML Validation

```bash
# Using Python
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

## Best Practices

1. **Use Semantic Naming**
   - ✓ `config-production.json`
   - ✗ `cfg1.json`

2. **Document Your Configs**

   ```json
   {
     "description": "Production validation - strict matching",
     "tolerance": 0.0,
     "ignore_case": false
   }
   ```

3. **Version Control Configs**

   ```bash
   git add config*.json
   git commit -m "Add production config"
   ```

4. **Use Profiles**

   - Separate configs for dev/staging/production
   - Separate configs for different XML types

5. **Environment Variables**

   ```bash
   # Create config from environment
   cat > config.json <<EOF
   {
     "tolerance": $TOLERANCE,
     "output_format": "$OUTPUT_FORMAT"
   }
   EOF
   ```

## Troubleshooting

### "Config file not found"

```bash
# Use absolute path
python xmlcompare.py --files file1.xml file2.xml --config /absolute/path/config.json

# Or relative from execution directory
python xmlcompare.py --files file1.xml file2.xml --config ./configs/production.json
```

### "Invalid JSON"

```bash
# Validate structure
python -m json.tool config.json

# Check for common issues
# - Missing quotes around keys
# - Trailing commas
# - Incorrect value types
```

### "Config seems to be ignored"

```bash
# Command-line options override config
# This ignores config tolerance:
python xmlcompare.py --files file1.xml file2.xml --config config.json --tolerance 0.1

# Use --verbose to see what's loaded
java -jar xmlcompare.jar --files file1.xml file2.xml --config config.json --verbose
```

## Examples

See [config.json.example](../config.json.example) for comprehensive examples including:

- Basic comparison
- Strict testing
- Flexible development
- Performance optimization
- Different output formats
- Advanced filtering

## See Also

- [Python CLI Reference](../python/docs/CLI_REFERENCE.md)
- [Java CLI Reference](../java/docs/CLI_REFERENCE.md)
- [Python FEATURES](../python/docs/FEATURES.md)
- [Java FEATURES](../java/docs/FEATURES.md)
