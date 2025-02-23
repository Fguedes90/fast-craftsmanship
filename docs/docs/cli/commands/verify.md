# CLI Commands

## Verify Command

The verify command provides functionality to run various code quality checks on your codebase. It uses functional programming principles with railway-oriented programming to handle failures gracefully and provide clear error messages.

### Usage

```bash
fcship verify [check_type]
```

### Arguments

- `check_type` (optional): Type of verification to run. Defaults to "all".
  - Valid values: "all", "type", "lint", "test", "format"

### Verification Types

The following verifications are available:

- **Type Check**: Verifies type annotations using `mypy`
- **Lint**: Runs code linting using `flake8`
- **Test**: Executes test suite using `pytest`
- **Format**: Checks code formatting using `black`

### Implementation Details

The verify command is implemented using functional programming principles:

- **Railway-oriented programming** with `Result` types for error handling
- **Pure functions** with explicit error types
- **Immutable data structures** using `Block` and `Map`
- **Tagged unions** for type-safe error handling

### Key Types

```python
class CommandOutput:
    stdout: str      # Standard output
    stderr: str      # Standard error
    returncode: int  # Return code

class VerificationOutcome:
    tag: Literal["success", "failure", "validation_error", "execution_error"]
    success: str | None
    failure: tuple[str, str] | None
    validation_error: str | None
    execution_error: tuple[str, str] | None
```

### Workflow

1. Validates the check type
2. Determines which verifications to run
3. Executes each verification independently
4. Collects and processes results
5. Displays summary table and detailed failures
6. Returns overall success/failure

### Example Output

```
┌─────────────────────────────────┐
│     Verification Results        │
├───────────────┬────────────────┤
│ Type Check    │ ✨ Passed      │
│ Lint          │ ✨ Passed      │
│ Test          │ ✨ Passed      │
│ Format        │ ✨ Passed      │
└───────────────┴────────────────┘

✨ All verifications passed successfully!
```

Or with failures:

```
┌─────────────────────────────────┐
│     Verification Results        │
├───────────────┬────────────────┤
│ Type Check    │ ❌ Failed      │
│ Lint          │ ✨ Passed      │
│ Test          │ ✨ Passed      │
│ Format        │ ✨ Passed      │
└───────────────┴────────────────┘

Type Check Failed
mypy found type errors:
main.py:10: error: Incompatible return value type
```

### Error Handling

The command uses a sophisticated error handling system with distinct error types:

- **ValidationError**: Input validation failures
- **ExecutionError**: Command execution failures
- **Failure**: Verification check failures
- **DisplayError**: UI rendering failures

Each error type is handled appropriately with clear error messages and proper error propagation.

### Customization

The verifications are configured using a `Map` of commands:

```python
VERIFICATIONS = Map.of_seq([
    ("type", Block.of_seq(["mypy", "."])),
    ("lint", Block.of_seq(["flake8"])),
    ("test", Block.of_seq(["pytest"])),
    ("format", Block.of_seq(["black", "--check", "."]))
])
```

To add or modify verifications, update this configuration map with the desired commands.