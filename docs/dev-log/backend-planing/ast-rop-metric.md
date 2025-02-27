# ROP Conformity Metric Tool Planning

## Overview
A Flake8 extension to analyze Python code and provide a deterministic metric for Railway-Oriented Programming (ROP) conformity. The tool will leverage Flake8's AST processing capabilities to identify patterns and anti-patterns, assigning penalty points for violations.

## Technical Approach

### 1. Analysis Engine Selection
We'll implement this as a Flake8 extension because:
- Integrates with existing Python tooling ecosystem
- Provides robust AST handling infrastructure
- Can be used with existing IDE integrations
- Supports parallel file processing out of the box
- Can be combined with other Flake8 plugins

### 2. Detailed ROP Rules and Scoring

#### Critical Violations (ROP1XX - 5 points each)

1. **Control Flow Violations**
   - ROP101: Try/Except blocks detected (use Result instead)
   - ROP102: For/While loops detected (use map/filter/functional operations)
   - ROP103: If/Else statements outside pattern matching
   - ROP104: Direct exception raising (use Error return)
   - ROP105: Return None or Optional usage (use Option type)

2. **State Management Violations**
   - ROP110: Mutable class attributes (missing @dataclass(frozen=True))
   - ROP111: Global variable usage
   - ROP112: Class or instance variable modification
   - ROP113: List/Dict/Set mutation methods (append, update, etc.)
   - ROP114: Assignment to function parameters

3. **Railway Pattern Violations**
   - ROP120: Missing Result type for functions that can fail
   - ROP121: Direct access to Result.value/error (use pattern matching)
   - ROP122: Missing error handling in pipeline
   - ROP123: Mixing Result with exception handling
   - ROP124: Using async/await instead of @effect.result

4. **Pydantic Model Violations**
   - ROP130: Non-immutable Pydantic model (missing ConfigDict(frozen=True))
   - ROP131: Direct model instantiation without Result (not using create factory)
   - ROP132: Exception raising in model validators
   - ROP133: Mutable model defaults (lists, dicts)
   - ROP134: Direct model attribute modification

#### Major Violations (ROP2XX - 3 points each)

1. **Type System Violations**
   - ROP201: Missing type hints
   - ROP202: Using Any type
   - ROP203: Missing Result/Option type annotations
   - ROP204: Incorrect Result/Option generic types
   - ROP205: Using Union instead of tagged_union

2. **Functional Pattern Violations**
   - ROP210: Using .bind() method (use pipeline or @effect.result)
   - ROP211: Direct attribute access without pattern matching
   - ROP212: Missing pipeline for sequential Result operations
   - ROP213: Non-pure functions (side effects)
   - ROP214: Missing static factory methods for tagged_union

3. **Data Model Violations**
   - ROP220: Non-frozen dataclasses
   - ROP221: Missing immutable collections (using list instead of tuple)
   - ROP222: Mutable default arguments
   - ROP223: Missing validation in data models
   - ROP224: Direct attribute modification

4. **Pydantic Pattern Violations**
   - ROP230: Missing model_validator decorators
   - ROP231: Missing ImmutableModel base class
   - ROP232: Incorrect validator mode (not using 'after')
   - ROP233: Missing create factory method
   - ROP234: Incorrect error handling in validators

#### Minor Violations (ROP3XX - 1 point each)

1. **Documentation Violations**
   - ROP301: Missing docstrings in functions
   - ROP302: Non-descriptive error messages
   - ROP303: Missing type documentation
   - ROP304: Missing error case documentation
   - ROP305: Missing pipeline step documentation
   - ROP306: Multi-line docstring detected (must be single line)
   - ROP307: Empty docstring
   - ROP308: Docstring with redundant type information

2. **Import Violations**
   - ROP310: Missing required expression imports
   - ROP311: Unused expression imports
   - ROP312: Star imports
   - ROP313: Relative imports
   - ROP314: Missing __future__ annotations import

3. **Style Violations**
   - ROP320: Non-descriptive Result error messages
   - ROP321: Inconsistent pattern matching style
   - ROP322: Complex pattern matching (too many cases)
   - ROP323: Missing line breaks in long pipelines
   - ROP324: Inconsistent Result/Option naming

### 3. Pattern Detection Rules

#### Required Imports Detection
```python
REQUIRED_IMPORTS = {
    'expression': [
        'Result', 'Ok', 'Error',
        'Option', 'Some', 'Nothing',
        'effect', 'pipeline', 'pipe',
        'tagged_union', 'case', 'tag'
    ],
    'typing': ['TypeVar', 'TypeAlias', 'Self'],
    'collections.abc': ['Callable', 'Awaitable', 'Generator'],
    'pydantic': ['BaseModel', 'ConfigDict', 'model_validator', 'TypeAdapter']
}
```

#### Pattern Matching Detection
```python
VALID_PATTERN_MATCH = '''
match result:
    case Ok(value) if isinstance(value, dict):
        # handle dict success
    case Ok(value):
        # handle other success
    case Error(msg) if "database" in str(msg):
        # handle database errors
    case Error():
        # handle other errors
'''

INVALID_PATTERN_MATCH = '''
if isinstance(result, Ok):
    value = result.value
    if isinstance(value, dict):
        # handle dict
else:
    error = result.error
'''
```

#### Type Annotation Examples
```python
type Point = tuple[float, float]
type JsonDict = dict[str, "JsonValue"]
type JsonValue = str | int | float | bool | None | JsonDict | list[JsonValue]

def process_data(data: JsonDict) -> Result[JsonValue, str]:
    match data:
        case {"type": "point", "coords": [x, y]}:
            return Ok((float(x), float(y)))
        case _:
            return Error("Invalid data format")
```

#### Pipeline Pattern Detection
```python
VALID_PIPELINE = '''
result = pipeline(
    validate_data,
    transform_data,
    save_data
)(data)
'''

INVALID_PIPELINE = '''
result1 = validate_data(data)
if is_ok(result1):
    result2 = transform_data(result1.value)
    if is_ok(result2):
        result3 = save_data(result2.value)
'''
```

#### Pydantic Model Pattern Detection
```python
VALID_PYDANTIC_MODEL = '''
from typing import Self

class ImmutableModel(BaseModel):
    """Base model for all Pydantic models in ROP style"""
    model_config = ConfigDict(frozen=True, strict=True)
    
    @classmethod
    def create(cls: type[Self], **data) -> Result[Self, str]:
        try:
            adapter = TypeAdapter(cls)
            instance = adapter.validate_python(data)
            return Ok(instance)
        except Exception as e:
            return Error(str(e))

class User(ImmutableModel):
    name: str
    email: str
    
    @model_validator(mode='after')
    def validate_user(self) -> Self:
        # validation logic
        return self
'''

INVALID_PYDANTIC_MODEL = '''
class User(BaseModel):
    name: str
    email: str
    
    def validate(self) -> "User":
        if not self.email:
            raise ValueError("Email required")
        return self
'''
```

#### Effect Pattern Detection
```python
VALID_EFFECT = '''
@effect.result[str, str]()
def process_user(user_id: str) -> Result[str, str]:
    user = yield from fetch_user(user_id)
    match user:
        case {"status": "active", **data}:
            return Ok(f"User {data['name']} is active")
        case _:
            return Error("Invalid user data")
'''

INVALID_EFFECT = '''
async def process_user(user_id: str):
    try:
        user = await fetch_user(user_id)
        if user["status"] == "active":
            return user["name"]
    except Exception as e:
        return None
'''
```

#### Pydantic Validation Pattern Detection
```python
VALID_VALIDATION = '''
@model_validator(mode='after')
def validate_order(self) -> 'Order':
    if len(self.items) == 0 and self.total > 0:
        raise ValueError("Cannot have total > 0 with no items")
    return self
'''

INVALID_VALIDATION = '''
def validate(self):
    if len(self.items) == 0 and self.total > 0:
        return False
'''
```

#### Docstring Pattern Detection
```python
VALID_DOCSTRING = '''
def process_user(name: str) -> Result[User, str]:
    """Creates a new user with validation and returns Result."""
    # function implementation
'''

INVALID_DOCSTRING_MULTILINE = '''
def process_user(name: str) -> Result[User, str]:
    """Creates a new user with validation and returns Result.
    
    Args:
        name: The user's name
    Returns:
        Result containing the user or error
    """
    # function implementation
'''

INVALID_DOCSTRING_TYPE_INFO = '''
def process_user(name: str) -> Result[User, str]:
    """Takes a string name and returns Result[User, str]."""
    # function implementation
'''

INVALID_DOCSTRING_EMPTY = '''
def process_user(name: str) -> Result[User, str]:
    """"""
    # function implementation
'''
```

### 4. Auto-fix Suggestions

1. **Control Flow Fixes**
   ```python
   # Before
   try:
       result = risky_operation()
   except Exception as e:
       handle_error(e)
   
   # After
   def risky_operation() -> Result[str, str]:
       match condition:
           case True: return Ok("success")
           case False: return Error("operation failed")
   ```

2. **Loop Fixes**
   ```python
   # Before
   results = []
   for x in items:
       results.append(process(x))
   
   # After
   results = list(map(process, items))
   ```

3. **Pattern Matching Fixes**
   ```python
   # Before
   if is_ok(result):
       value = result.value
   else:
       error = result.error
   
   # After
   match result:
       case Ok(value):
           handle_success(value)
       case Error(error):
           handle_error(error)
   ```

4. **Pydantic Model Fixes**
   ```python
   # Before (Old style)
   class User(BaseModel):
       name: str
       email: str
       
       class Config:
           validate_assignment = True
       
       def __init__(self, **data):
           try:
               super().__init__(**data)
           except Exception as e:
               raise ValueError(str(e))
   
   # After (Python 3.12 + Pydantic 2.0)
   from typing import Self
   
   class User(ImmutableModel):
       name: str
       email: str
       
       model_config = ConfigDict(
           frozen=True,
           strict=True,
           validate_assignment=True
       )
       
       @classmethod
       def create(cls: type[Self], **data) -> Result[Self, str]:
           try:
               adapter = TypeAdapter(cls)
               instance = adapter.validate_python(data)
               return Ok(instance)
           except Exception as e:
               return Error(str(e))
   ```

5. **Pydantic Validation Fixes**
   ```python
   # Before
   def validate_total(self):
       if self.total < 0:
           raise ValueError("Total cannot be negative")
   
   # After
   @model_validator(mode='after')
   def validate_total(self) -> 'Order':
       if self.total < 0:
           raise ValueError("Total cannot be negative")
       return self
   ```

6. **Docstring Fixes**
   ```python
   # Before (Multi-line with type info)
   def validate_user(user: User) -> Result[User, str]:
       """Validates user data and returns Result.
       
       Args:
           user: User instance to validate
       Returns:
           Result[User, str]: Validated user or error
       """
       # implementation
   
   # After (Single line, no type info)
   def validate_user(user: User) -> Result[User, str]:
       """Validates user data and returns success or validation errors."""
       # implementation
   
   # Before (Empty or meaningless)
   def process_data(data: dict) -> Result[dict, str]:
       """Process data"""  # Too vague
       # implementation
   
   # After (Descriptive single line)
   def process_data(data: dict) -> Result[dict, str]:
       """Transforms raw data into normalized format with validation."""
       # implementation
   ```

### 5. Flake8 Extension Structure

```python
from flake8.options.manager import OptionManager
from flake8_rop.visitor import ROPVisitor

class ROPChecker:
    name = 'flake8-rop'
    version = '0.1.0'
    
    # Error codes prefix with ROP
    # ROP1XX: Critical violations
    # ROP2XX: Major violations
    # ROP3XX: Minor violations
    
    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        
    @classmethod
    def add_options(cls, parser: OptionManager):
        parser.add_option(
            '--rop-score-threshold',
            type=int,
            default=10,
            help='Maximum allowed ROP violation score'
        )
    
    def run(self):
        visitor = ROPVisitor(self.filename)
        visitor.visit(self.tree)
        for violation in visitor.violations:
            yield (
                violation['line'],
                violation['col'],
                f"ROP{violation['code']}: {violation['message']}",
                type(self)
            )
```

### 6. Configuration Options

```ini
# setup.cfg or .flake8
[flake8]
rop-score-threshold = 10
rop-ignore = ROP301,ROP302
rop-select = ROP1XX,ROP2XX
max-complexity = 10
```

## Implementation Strategy

### Phase 1: Core Extension (MVP)
1. Basic Flake8 plugin setup
2. Critical violation detection
3. Error code system
4. Basic configuration

### Phase 2: Enhanced Analysis
1. Type hint verification
2. Pattern matching detection
3. Custom options handling
4. Detailed error messages

### Phase 3: Advanced Features
1. Auto-fix suggestions via `flake8-fix`
2. Score calculation and reporting
3. Integration with popular IDEs
4. Performance optimization

## Code Structure

```
flake8_rop/
├── __init__.py
├── checker.py        # Main Flake8 plugin class
├── core/
│   ├── visitor.py    # AST visitor implementation
│   ├── rules.py      # Violation rules
│   └── scoring.py    # Scoring logic
├── fixes/           # Auto-fix suggestions
│   ├── loops.py
│   ├── exceptions.py
│   └── patterns.py
└── utils/
    ├── ast_helpers.py
    └── type_analysis.py
```

## Installation and Usage

```bash
# Installation
pip install flake8-rop

# Usage
flake8 path/to/code/

# With specific options
flake8 --rop-score-threshold=15 path/to/code/

# Generate detailed report
flake8 --format=rop-report path/to/code/
```

## Integration Examples

### VS Code settings.json
```json
{
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": [
        "--rop-score-threshold=10",
        "--rop-select=ROP1XX,ROP2XX"
    ]
}
```

### Pre-commit Configuration
```yaml
repos:
-   repo: https://github.com/pycqa/flake8
    rev: '6.1.0'
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-rop]
        args: [--rop-score-threshold=10]
```

## Testing Strategy

1. Unit Tests:
   ```python
   def test_try_except_violation():
       code = '''
       try:
           do_something()
       except Exception:
           handle_error()
       '''
       tree = ast.parse(code)
       checker = ROPChecker(tree, 'test.py')
       errors = list(checker.run())
       assert len(errors) == 1
       assert errors[0][2].startswith('ROP101')
   ```

2. Integration Tests:
   - Full Flake8 pipeline testing
   - Configuration handling
   - Multiple file analysis
   - Plugin interactions

3. Performance Tests:
   - Large codebase analysis
   - Memory usage monitoring
   - Processing time benchmarks

## Benefits of Flake8 Integration

1. Ecosystem Benefits:
   - Works with existing CI/CD pipelines
   - IDE integration out of the box
   - Compatible with other Flake8 extensions
   - Familiar configuration format

2. Technical Benefits:
   - Robust AST handling
   - Parallel file processing
   - Standardized error reporting
   - Plugin system for extensions

3. User Experience:
   - Familiar interface
   - Standard installation process
   - Configurable severity levels
   - IDE integration

## Development Roadmap

1. Week 1: Basic Extension
   - Flake8 plugin structure
   - Basic AST visitor
   - Error code system

2. Week 2-3: Core Rules
   - Critical violation detection
   - Configuration handling
   - Basic reporting

3. Week 4: Enhanced Features
   - Advanced pattern detection
   - Scoring system
   - Documentation

4. Week 5-6: Polish & Release
   - Testing
   - Performance optimization
   - PyPI release
   - Documentation

### Docstring Guidelines

1. **Single Line Rule**
   - Must be exactly one line
   - No line breaks
   - No empty lines
   - Maximum length of 100 characters

2. **Content Rules**
   - Focus on WHAT the function does, not HOW
   - No type information (types go in annotations)
   - No parameter descriptions (clear parameter names instead)
   - No return value descriptions (clear return type instead)

3. **Style Rules**
   - Start with a capital letter
   - End with a period
   - Use active voice
   - Be descriptive but concise

4. **Examples of Good Docstrings**
   ```python
   def validate_email(email: str) -> Result[str, str]:
       """Ensures email format is valid and domain exists."""
   
   def process_order(order: Order) -> Result[Order, str]:
       """Validates and processes order with inventory and payment checks."""
   
   def transform_data(data: JsonDict) -> Result[NormalizedData, str]:
       """Normalizes raw JSON data into standard internal format."""
   
   @effect.result[User, str]()
   def create_user(data: dict) -> Result[User, str]:
       """Creates new user with validation and permission checks."""
   ```

5. **Examples of Bad Docstrings**
   ```python
   def validate_email(email: str) -> Result[str, str]:
       """This function takes an email string and returns a Result[str, str]."""  # No type info
   
   def process_order(order: Order) -> Result[Order, str]:
       """Processes the order.
       Returns success or error."""  # No multi-line
   
   def transform_data(data: JsonDict) -> Result[NormalizedData, str]:
       """Takes data and transforms it."""  # Too vague
   
   @effect.result[User, str]()
   def create_user(data: dict) -> Result[User, str]:
       """Creates user by taking the data dict and validating each field
       then saving to database if valid."""  # Too detailed/multi-line
   ```
