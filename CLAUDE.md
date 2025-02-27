# Fast-craftsmanship Development Guide

## Commands
- Run all tests: `pytest tests`
- Run specific test: `pytest tests/path/to/test_file.py::test_function -v`
- Run tests with coverage: `pytest --cov=fcship tests/`
- Lint: `ruff check fcship/`

## Code Style Guidelines
- Follow ROP (Railway Oriented Programming) with Expression library
- Avoid try/except, if/else, for/while loops - Use Result/Option types
- Use pattern matching and functional operations (pipe, pipeline)
- Ensure all functions have proper type hints
- Use @effect.result for sequential operations
- Always make Pydantic models immutable (inherit from ImmutableModel)

## Working with @effect.result
- Use `@effect.result` with `yield` when replacing async functions or chaining sequential operations
- For simple synchronous functions, directly returning `Ok` or `Error` is sufficient without `@effect.result`
- When using `@effect.result`, use `yield` instead of `return` when returning `Ok` or `Error` values
- When you need early returns in `@effect.result` functions, use `yield Error(...)` followed by `return` statement
- Function signatures should include types like `@effect.result[SuccessType, ErrorType]()`
- Chain effect functions with `result = yield from other_effect_function()`

## Naming Conventions
- snake_case for functions and variables
- PascalCase for classes and type aliases
- ALL_CAPS for constants
- Descriptive error messages in Result.Error returns

## Testing
- Test both success and failure cases for Result objects
- Use `.is_ok()` and `.ok` for success cases
- Use `.is_error()` and `.error` for failure cases
- Mock external calls and side effects
- When testing @effect.result functions, test functions must also use @effect.result
- When directly testing generator-based effect functions, collect the final result by iterating through the generator:
  ```python
  final_result = None
  for step in effect_function():
      final_result = step
  assert final_result.is_ok()
  ```