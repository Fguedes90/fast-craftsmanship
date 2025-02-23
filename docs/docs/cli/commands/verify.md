# CLI Commands

## Verify Command

The verify command provides functionality to run various code quality checks and tests on your codebase. It uses railway-oriented programming with functional effects to handle failures gracefully and provide clear error messages.

### Usage

```bash
fcship verify
```

### Verification Types

The following verifications are run:

- **Style**: Checks code formatting using black and linting with flake8
- **Types**: Verifies type annotations using mypy
- **Tests**: Runs pytest test suite

### Error Handling

The verify command uses railway-oriented programming to handle errors gracefully:

- Each verification is run independently
- Failures are captured and reported without stopping other checks
- Clear error messages show which check failed and why
- Command execution errors are handled separately from check failures

### Example Output

```
Running verifications...

Style Check
✨ Passed

Type Check
❌ Failed
mypy found type errors:
main.py:10: error: Incompatible return value type

Test Run
✨ Passed

Summary:
Check       Status
Style       [green]✨ Passed[/green]
Types       [red]❌ Failed[/red]
Tests       [green]✨ Passed[/green]
```

### Implementation Details

The verify command is implemented using:

- **Railway-oriented programming** for error handling
- **Pure functions** for predictable behavior 
- **Effect system** for handling side effects
- **Immutable data structures** for thread safety

Key types:

```python
# Command execution result
class CommandOutput:
    stdout: str  # Standard output
    stderr: str  # Standard error
    returncode: int  # Return code
    
# Verification result
class VerificationOutcome:
    name: str  # Name of check
    message: str  # Success/failure message
```

Example workflow:

```python
from expression import Ok, Error, pipe
from fcship.commands.verify import verify_all

# Run all verifications
result = verify_all()

match result:
    case Ok(verifications):
        # Process successful verifications
        for name, check_result in verifications:
            display_result(name, check_result)
            
    case Error(error):
        # Handle verification failure
        display_error(error)
```

### Adding New Verifications

New verifications can be added by updating the `VERIFICATIONS` registry:

```python
VERIFICATIONS = {
    "Style": ["black --check .", "flake8 ."],
    "Types": ["mypy ."],
    "Tests": ["pytest"],
    "Custom": ["your-command --check"]  # Add new verification
}
```

Each verification can run multiple commands in sequence. All commands must succeed for the verification to pass.