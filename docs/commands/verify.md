# Verify Commands

The `verify` command group provides tools for validating your project code, checking for issues, and ensuring adherence to best practices.

## Overview

The `verify` command helps you:

- Run code quality checks
- Validate project structure
- Ensure dependencies are correctly installed
- Check for common issues and anti-patterns

## Basic Usage

```bash
fcship verify [CHECK_TYPE] [OPTIONS]
```

Where `CHECK_TYPE` can be:
- `all` (default): Run all verification checks
- `type`: Run type checking with mypy
- `lint`: Run linting with flake8
- `test`: Run tests with pytest
- `format`: Check code formatting with black
- `structure`: Verify project structure
- `dependencies`: Verify dependencies

## Options

| Option | Description |
| ------ | ----------- |
| `--fix / --no-fix` | Automatically fix common issues where possible (default: no fix) |
| `--output FORMAT` | Output format: text, json, html (default: text) |
| `--verbose / --no-verbose` | Show detailed information during verification (default: not verbose) |
| `--report-file FILE` | Save verification report to a file |
| `--strict / --no-strict` | Use strict mode for all checks (default: not strict) |
| `--exclude PATTERN` | Exclude files/directories matching pattern (can be used multiple times) |

## Examples

### Basic Verification

Run all verification checks on the current project:

```bash
fcship verify
```

This performs a standard verification of the current project, running type checking, linting, tests, and format checking.

### Running Specific Checks

Run only type checking:

```bash
fcship verify type
```

Run only linting:

```bash
fcship verify lint
```

Run only tests:

```bash
fcship verify test
```

Check only code formatting:

```bash
fcship verify format
```

### Fixing Issues Automatically

Run verification and attempt to fix common issues:

```bash
fcship verify --fix
```

This will:
- Format code with black
- Apply automatic fixes for linting issues
- Update import sorting
- Fix simple type issues where possible

### Generating Reports

Generate a detailed HTML report:

```bash
fcship verify --output html --report-file verification-report.html
```

Generate a JSON report for CI/CD integration:

```bash
fcship verify --output json --report-file verification.json
```

### Advanced Usage

Run verification with strict mode and verbose output:

```bash
fcship verify --strict --verbose
```

Run verification excluding specific directories:

```bash
fcship verify --exclude "tests/*" --exclude "examples/*"
```

Run type checking with custom mypy configuration:

```bash
fcship verify type --config-file mypy.ini
```

## Verification Checks

### Type Checking

The `type` check runs mypy to verify type annotations and catch type-related issues:

```bash
fcship verify type
```

Common issues detected:
- Missing type annotations
- Incompatible types
- Undefined names
- Incorrect function signatures

### Linting

The `lint` check runs flake8 to enforce coding standards:

```bash
fcship verify lint
```

Common issues detected:
- Code style violations
- Potential bugs
- Complexity issues
- Unused imports
- Undefined variables

### Testing

The `test` check runs pytest to execute your test suite:

```bash
fcship verify test
```

Options:
- `--test-path PATH`: Specify test directory or file
- `--test-markers MARKERS`: Run tests with specific markers
- `--test-coverage`: Generate coverage report

Example with test options:
```bash
fcship verify test --test-path tests/unit --test-markers "not slow" --test-coverage
```

### Format Checking

The `format` check verifies code formatting using black:

```bash
fcship verify format
```

When used with `--fix`, it will reformat code to match the black style:
```bash
fcship verify format --fix
```

### Structure Verification

The `structure` check validates your project structure:

```bash
fcship verify structure
```

This checks:
- Directory organization
- Required configuration files
- Package naming conventions
- Documentation structure

### Dependency Verification

The `dependencies` check validates your project dependencies:

```bash
fcship verify dependencies
```

This checks:
- Package installation status
- Version compatibility
- Security vulnerabilities
- Outdated packages

## Customizing Verification

You can create a `.fcshiprc.yaml` file in your project root to customize verification:

```yaml
verify:
  exclude:
    - "build/"
    - "dist/"
    - "*.pyc"
  rules:
    type_checking:
      enabled: true
      strict: true
      config_file: "mypy.ini"
    linting:
      enabled: true
      config_file: ".flake8"
    testing:
      enabled: true
      path: "tests/"
      markers: "not slow"
    formatting:
      enabled: true
      line_length: 88
    structure:
      enabled: true
      template: "default"
    dependencies:
      enabled: true
      check_vulnerabilities: true
  custom_checks:
    - path: "scripts/custom_verify.py"
      function: "run_my_check"
```

## Integration with CI/CD

The verify command can be integrated into CI/CD pipelines to ensure code quality:

### GitHub Actions Example

```yaml
name: Verify Code Quality

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install fast-craftsmanship
          pip install -e .
      - name: Verify project
        run: |
          fcship verify --output json --report-file verification.json
      - name: Upload verification report
        uses: actions/upload-artifact@v3
        with:
          name: verification-report
          path: verification.json
```

### GitLab CI Example

```yaml
verify:
  stage: test
  script:
    - pip install fast-craftsmanship
    - pip install -e .
    - fcship verify --output json --report-file verification.json
  artifacts:
    paths:
      - verification.json
```

## Best Practices

- Run verification locally before committing code
- Include verification in your CI/CD pipeline
- Fix issues as they are detected rather than accumulating technical debt
- Use `--fix` for formatting issues, but review changes before committing
- Create a custom configuration file for project-specific rules
- Set up pre-commit hooks to run verification automatically