# Configuration File Guide

Complete guide to using configuration files with xmlcompare.

## Overview

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
  "ignoreCase": false,
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
ignoreCase: false
unordered: true
skipKeys:
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
  "ignoreCase": false,
  "unordered": true,
  "ignoreNamespaces": true,
  "skipKeys": [
    "//timestamp",
    "//uuid"
  ],
  "outputFormat": "json"
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
| `ignoreCase`      | boolean | false   | Case-insensitive comparison         |
| `unordered`       | boolean | false   | Ignore element order                |
| `ignoreNamespaces`| boolean | false   | Ignore namespace URIs               |
| `ignoreAttributes`| boolean | false   | Ignore all attributes               |
| `structureOnly`   | boolean | false   | Compare only structure              |
| `maxDepth`        | integer | null    | Limit depth (null = unlimited)      |
| `skipKeys`        | array   | []      | Elements to skip                    |
| `skipPattern`     | string  | null    | Regex pattern for skipping          |
| `filterXpath`     | string  | null    | XPath filter                        |
| `outputFormat`    | string  | "text"  | Output format                       |
| `outputFile`      | string  | null    | Output file path                    |
| `summary`         | boolean | false   | Print summary only                  |
| `verbose`         | boolean | false   | Verbose output                      |
| `quiet`           | boolean | false   | Suppress output                     |
| `failFast`        | boolean | false   | Stop on first difference            |
| `schema`          | string  | null    | XSD schema file path                |
| `typeAware`       | boolean | false   | Type-aware comparison               |
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
  "ignoreCase": true,
  "unordered": true,
  "ignoreNamespaces": true,
  "verbose": true
}
```

### production.json

```json
{
  "tolerance": 0.0,
  "ignoreCase": false,
  "unordered": false,
  "ignoreNamespaces": false,
  "failFast": false,
  "outputFormat": "json"
}
```

### performance.json (Java)

```json
{
  "parallel": true,
  "threads": 8,
  "stream": true,
  "failFast": true,
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
  "ignoreCase": false
}
```

**Command:**

```bash
# This overrides tolerance to 0.05
python xmlcompare.py --files file1.xml file2.xml --config config.json --tolerance 0.05
```

**Result:**

- tolerance: 0.05 (overridden)
- ignoreCase: false (from config)

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
  "ignoreNamespaces": true,
  "ignorCase": false
}
```

**strict.json (extends base):**

```json
{
  "ignoreNamespaces": true,
  "ignoreCase": false,
  "tolerance": 0.0,
  "failFast": true
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
     "ignoreCase": false
   }
   ```

3. **Version Control Configs**

   ```bash"
   git add config*.json
   git commit -m "Add production config
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
     "outputFormat": "$OUTPUT_FORMAT"
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
