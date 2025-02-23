# CLI Utilities

The Fast Craftsmanship CLI utilities provide a foundation for building robust, type-safe, and functional command-line applications. These utilities are designed with functional programming principles and focus on error handling, user experience, and maintainability.

## Available Utilities

### User Interface
- [UI Utilities](ui.md): Rich terminal output, interactive prompts, and display components
  - Display functions (messages, panels, tables)
  - Error handling and recovery
  - Progress tracking
  - Input validation
  - Context management

### Error Handling
- **Error Handling**: Functional approach to error management
  - Railway-oriented programming
  - Tagged union error types
  - Error recovery strategies
  - Command error decorators

### Type System
- **Type Utils**: Type safety and validation utilities
  - Generic type constraints
  - Runtime type checking
  - Type validation functions
  - Type-safe conversions

### File Operations
- **File Utils**: File system operations
  - Path validation
  - Safe file operations
  - File type checking
  - Directory management

### Validation
- **Validation**: Input validation utilities
  - Data validators
  - Schema validation
  - Format checking
  - Custom validation rules

## Design Philosophy

The utilities follow these core principles:

1. **Functional Programming**
   - Pure functions
   - Immutable data structures
   - Explicit error handling
   - Composition over inheritance

2. **Type Safety**
   - Static type checking
   - Runtime type validation
   - Generic type constraints
   - Type-safe error handling

3. **User Experience**
   - Consistent UI patterns
   - Clear error messages
   - Interactive feedback
   - Progressive disclosure

4. **Maintainability**
   - Modular design
   - Clear documentation
   - Comprehensive testing
   - Consistent patterns

## Getting Started

### Basic Usage

```python
from fcship.utils.ui import display_message, success_message
from fcship.utils.error_handling import handle_command_errors
from expression import Result, Ok, Error

@handle_command_errors
def my_command() -> None:
    result = display_message("Starting operation...", "cyan")
    if result.is_ok():
        success_message("Operation completed!")
```

### Error Handling

```python
from fcship.utils.ui import DisplayError, handle_ui_error
from expression import Result

def safe_operation() -> Result[None, DisplayError]:
    # Your operation here
    return Ok(None)

result = safe_operation()
if result.is_error():
    handle_ui_error(result.error)
```

## Integration Examples

### Combining Multiple Utilities

```python
from fcship.utils import ui, error_handling, validation
from expression import Result, pipe

def validated_command(input_data: str) -> Result[None, DisplayError]:
    return (
        validation.validate_input(input_data)
        .bind(process_data)
        .bind(ui.display_result)
    )
```

## Best Practices

1. **Error Handling**
   - Always use Result types for operations that can fail
   - Handle all error cases explicitly
   - Provide meaningful error messages
   - Use appropriate error types

2. **Type Safety**
   - Use type hints consistently
   - Validate input types at runtime
   - Use generic types for flexible components
   - Maintain type safety across boundaries

3. **User Interface**
   - Follow consistent display patterns
   - Provide clear feedback
   - Handle long operations with progress indicators
   - Use appropriate UI components

4. **Testing**
   - Write unit tests for all utilities
   - Test error cases explicitly
   - Mock external dependencies
   - Test type constraints

## Contributing

When adding new utilities:

1. Follow functional programming principles
2. Maintain type safety
3. Add comprehensive documentation
4. Include unit tests
5. Follow existing patterns

## See Also

- [Command Documentation](../commands/index.md)
- [Functional Programming Guide](../../functional_programming/index.md)
- [Architecture Guidelines](../../backend/index.md)