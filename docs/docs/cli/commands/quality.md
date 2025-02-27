# Quality Assurance & Testing Commands

The quality commands help you ensure code quality through testing, linting, type checking, and other verification steps.

## Available Commands

### `test`

Create and run tests.

```bash
# Run all tests
craftsmanship test run

# Create a test file
craftsmanship test create users_service

# Run specific tests
craftsmanship test run --pattern "*user*"
```

### `verify`

Run code quality checks.

```bash
# Run all verifications
craftsmanship verify

# Run only linting
craftsmanship verify --lint

# Run only type checking
craftsmanship verify --types
```

## Code Quality Checks

The `verify` command includes the following checks:

| Check         | Description                                |
|---------------|--------------------------------------------|
| Lint          | Code style and best practices using Ruff   |
| Type checking | Static type checking with mypy             |
| Tests         | Run tests and check code coverage          |
| Security      | Check for security vulnerabilities         |
| Formatting    | Verify code formatting                     |

## Test Patterns

The `test` command supports various patterns for creating tests:

```bash
# Create a unit test
craftsmanship test create --type unit user_service

# Create an integration test
craftsmanship test create --type integration auth_flow

# Create a test with specific assertions
craftsmanship test create user_service --assertions equality validation
```

## Continuous Integration

These commands are designed to work well in CI environments:

```bash
# Run in CI mode (with appropriate output format)
craftsmanship verify --ci

# Run tests with JUnit report
craftsmanship test run --report junit
```

## Usage Examples

```bash
# Complete quality check before commit
craftsmanship verify

# Create and run a specific test
craftsmanship test create user_service
craftsmanship test run --pattern "*user_service*"
```