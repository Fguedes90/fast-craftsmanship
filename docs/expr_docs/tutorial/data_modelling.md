---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
(tutorial_data_modelling)=

# Data Modeling with Expression Library

## Core Concepts

Expression library enables type-safe data modeling in Python using data classes and tagged unions.

## Basic Data Modeling

### Simple Types with Dataclasses

```python
from dataclasses import dataclass
from typing import Literal
from expression import tagged_union, case, tag

# DO ✅
@dataclass(frozen=True)  # Make immutable
class User:
    id: str
    name: str
    age: int

# DON'T ❌
class UserMutable:
    def __init__(self, id: str, name: str, age: int):
        self.id = id
        self.name = name
        self.age = age
        
# WHY: Frozen dataclasses ensure immutability and provide automatic __eq__, __hash__, etc.
```

### Tagged Unions (Sum Types)

```python
# DO ✅
@tagged_union
class PaymentMethod:
    tag: Literal["card", "bank_transfer"] = tag()
    
    card: tuple[str, str] = case()  # (card_number, expiry)
    bank_transfer: str = case()     # account_number
    
    @staticmethod
    def Card(number: str, expiry: str) -> 'PaymentMethod':
        return PaymentMethod(card=(number, expiry))
    
    @staticmethod
    def BankTransfer(account: str) -> 'PaymentMethod':
        return PaymentMethod(bank_transfer=account)

# DON'T ❌
class LegacyPayment:
    def __init__(self, type: str, data: dict):
        self.type = type
        self.data = data
        
# WHY: Tagged unions provide type safety and exhaustive pattern matching
```

## Pattern Matching with Tagged Unions

```python
# DO ✅
def process_payment(method: PaymentMethod) -> str:
    match method:
        case PaymentMethod(tag="card", card=(number, _)):
            return f"Processing card: {number[-4:]}"
        case PaymentMethod(tag="bank_transfer", bank_transfer=account):
            return f"Processing transfer to: {account}"
            
# DON'T ❌
def process_legacy_payment(payment: LegacyPayment) -> str:
    if payment.type == "card":
        return f"Processing card: {payment.data['number']}"
    elif payment.type == "transfer":
        return f"Processing transfer: {payment.data['account']}"
    else:
        raise ValueError("Unknown payment type")

# WHY: Pattern matching ensures all cases are handled and provides better type inference
```

## Advanced Patterns

### Single Case Tagged Unions

```python
# DO ✅
@tagged_union(frozen=True, repr=False)
class Email:
    value: str = case()
    
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email")
            
    def __str__(self) -> str:
        return self.value

# DON'T ❌
class EmailString(str):
    def __new__(cls, value: str):
        if "@" not in value:
            raise ValueError("Invalid email")
        return super().__new__(cls, value)

# WHY: Tagged unions provide better type safety and validation
```

### Complex Data Models

```python
from typing import Generic, TypeVar

T = TypeVar("T")

# DO ✅
@tagged_union
class Result(Generic[T]):
    tag: Literal["success", "error"] = tag()
    
    success: T = case()
    error: str = case()
    
    @staticmethod
    def Success(value: T) -> 'Result[T]':
        return Result(success=value)
        
    @staticmethod
    def Error(msg: str) -> 'Result[T]':
        return Result(error=msg)

def process_data(data: dict) -> Result[User]:
    build_user = lambda data: User(**data)
    
    if "id" not in data:
        return Result.Error("Missing id")
    return Result.Success(build_user(data))

# DON'T ❌
def process_data_unsafe(data: dict) -> tuple[bool, User | str]:
    if "id" not in data:
        return False, "Missing id"
    return True, User(**data)

# WHY: Generic tagged unions provide type-safe error handling
```

## Best Practices

### DO ✅
- Use frozen dataclasses for immutable value types
- Use tagged unions for sum types
- Implement static factory methods for union cases
- Use pattern matching for type-safe branching
- Make your types self-validating

### DON'T ❌
- Use mutable classes for data models
- Mix different validation approaches
- Use strings or dictionaries for type discrimination
- Return mixed type tuples for results

## Testing Example

```python
def test_payment_processing():
    # Given
    card = PaymentMethod.Card("1234-5678-9012-3456", "12/25")
    transfer = PaymentMethod.BankTransfer("GB123456789")
    
    # When
    extract_last_four = lambda result: "3456" in result
    contains_account = lambda result: "GB123456789" in result
    
    card_result = process_payment(card)
    transfer_result = process_payment(transfer)
    
    # Then
    assert extract_last_four(card_result)
    assert contains_account(transfer_result)

def test_email_validation():
    # Valid case
    email = Email(value="test@example.com")
    assert str(email) == "test@example.com"
    
    # Invalid case
    try:
        Email(value="invalid-email")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected

