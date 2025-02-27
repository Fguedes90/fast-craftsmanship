# Verify Commands

The `verify` command group provides tools for validating your project code, checking for issues, and ensuring adherence to best practices.

## Overview

The `verify` command helps you:

- Run code quality checks
- Validate project structure
- Ensure dependencies are correctly installed
- Check for common issues and anti-patterns

## Commands

### Verify Project

```bash
fcship verify
```

Runs a complete verification of the current project, checking:

- Project structure
- Required files
- Code quality
- Dependency integrity

The command will output a detailed report of any issues found, with suggestions for remediation.

### Verify Structure

```bash
fcship verify structure
```

Checks only the project structure, including:

- Directory organization
- Required configuration files
- Package naming conventions

### Verify Dependencies

```bash
fcship verify dependencies
```

Validates that all required dependencies are correctly installed and compatible.

## Options

| Option | Description |
| ------ | ----------- |
| `--fix` | Automatically fix common issues where possible |
| `--output=FORMAT` | Output format (text, json, html) |
| `--verbose` | Show detailed information during verification |
| `--report-file=FILE` | Save verification report to a file |

## Examples

### Basic Verification

```bash
fcship verify
```

This performs a standard verification of the current project.

### Fixing Issues Automatically

```bash
fcship verify --fix
```

This attempts to automatically fix common issues found during verification.

### Getting Detailed Output

```bash
fcship verify --verbose
```

Shows detailed information about each check performed during verification.

### Generating a Report

```bash
fcship verify --output=html --report-file=verification-report.html
```

Generates an HTML report of the verification results.

## Customizing Verification

You can create a `.fcshiprc.yaml` file in your project root to customize verification:

```yaml
verify:
  exclude:
    - "build/"
    - "dist/"
    - "*.pyc"
  rules:
    code_quality: true
    structure: true
    dependencies: true
  custom_checks:
    - path: "scripts/custom_verify.py"
      function: "run_my_check"
```

## Integration with CI/CD

The verify command can be integrated into CI/CD pipelines to ensure code quality:

```yaml
# In your GitHub workflow
- name: Verify project
  run: |
    pip install fast-craftsmanship
    fcship verify --output=json --report-file=verification.json
```