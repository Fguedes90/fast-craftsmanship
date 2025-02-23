# CLI Commands

Fast Craftsmanship CLI provides a set of commands designed to help you maintain high-quality code and follow best practices in your development workflow.

## Available Commands

### Verification Commands

- [verify](verify.md): Run code quality checks including type checking, linting, testing, and formatting
  - Type checking with mypy
  - Linting with flake8
  - Testing with pytest
  - Format checking with black

### Architecture Commands

- **api**: Generate and manage API endpoints
- **domain**: Work with domain models and business logic
- **service**: Manage service layer components
- **repo**: Handle data access and repository patterns

### Project Commands

- **project**: Initialize and manage project structure
- **docs**: Generate and maintain documentation
- **test**: Create and run tests

## Command Design Principles

All commands in Fast Craftsmanship follow these core principles:

1. **Functional Programming**
   - Pure functions with explicit error types
   - Railway-oriented programming using Result types
   - Immutable data structures

2. **Type Safety**
   - Static type checking with mypy
   - Tagged unions for error handling
   - Generic types for flexible, type-safe operations

3. **User Experience**
   - Clear, consistent error messages
   - Rich terminal output
   - Progress indicators for long-running operations

4. **Error Handling**
   - Structured error types
   - Graceful error recovery
   - Detailed error reporting

## Common Features

Every command shares these common features:

- **Result-based error handling**: All operations return `Result[T, Error]`
- **Rich UI**: Consistent terminal output using the UI utilities
- **Validation**: Input validation and error checking
- **Documentation**: Detailed help and usage information

## Usage Examples

### Running Verifications

```bash
# Run all verifications
fcship verify

# Run specific verification
fcship verify type
```

### Working with Projects

```bash
# Initialize a new project
fcship project init

# Generate documentation
fcship docs generate
```

## See Also

- [UI Utilities](../utils/ui.md): Documentation for the UI components used by commands
- [Error Handling](../utils/error_handling.md): Guide to error handling patterns
- [Type System](../utils/type_utils.md): Information about type safety and validation