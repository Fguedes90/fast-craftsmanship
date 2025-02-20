# Domain-Driven Design Implementation Guidelines

## Domain Structure

### 1. Domain Organization
```
app/
├── domains/
│   ├── auth/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── aggregates/
│   │   │   ├── events/
│   │   │   └── repositories.py
│   │   ├── application/
│   │   │   ├── services/
│   │   │   └── use_cases/
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   └── api/
│   │       └── routes/
│   └── [other domains]/
├── core/
└── shared/
```

## Domain Components

### 1. Entities

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    created_at: datetime
    
    @classmethod
    def create(cls, email: str, password: str) -> "User":
        return cls(
            id=uuid4(),
            email=email,
            password_hash=hash_password(password),
            created_at=datetime.utcnow()
        )
    
    def update_password(self, new_password: str) -> None:
        self.password_hash = hash_password(new_password)
```

### 2. Value Objects

```python
@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError("Invalid email format")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        return '@' in email and '.' in email.split('@')[1]
```

### 3. Aggregates

```python
class UserAccount:
    def __init__(self, user: User, profile: Profile):
        self._user = user
        self._profile = profile
        self._preferences = UserPreferences()
    
    @property
    def user(self) -> User:
        return self._user
    
    def update_profile(self, profile_data: ProfileUpdate) -> None:
        self._profile.update(profile_data)
        self._raise_domain_event(ProfileUpdated(self._user.id))
```

### 4. Domain Events

```python
@dataclass(frozen=True)
class DomainEvent:
    occurred_on: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class UserCreated(DomainEvent):
    user_id: UUID
    email: str

class DomainEventPublisher:
    def publish(self, event: DomainEvent) -> None:
        ...
```

### 5. Domain Services

```python
class PasswordResetService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
        email_service: EmailService
    ):
        self._user_repository = user_repository
        self._token_service = token_service
        self._email_service = email_service
    
    def initiate_reset(self, email: str) -> None:
        user = self._user_repository.get_by_email(email)
        if user:
            token = self._token_service.create_reset_token(user.id)
            self._email_service.send_reset_email(email, token)
```

## Use Cases

### 1. Use Case Structure

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class CreateUserInput:
    email: str
    password: str
    name: str

@dataclass
class CreateUserOutput:
    user_id: UUID
    email: str

class CreateUser(Protocol):
    def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        ...

class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: DomainEventPublisher
    ):
        self._user_repository = user_repository
        self._event_publisher = event_publisher
    
    def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        user = User.create(
            email=input_data.email,
            password=input_data.password
        )
        
        saved_user = self._user_repository.save(user)
        
        self._event_publisher.publish(
            UserCreated(user_id=saved_user.id, email=saved_user.email)
        )
        
        return CreateUserOutput(
            user_id=saved_user.id,
            email=saved_user.email
        )
```

## Domain Rules and Invariants

### 1. Business Rules

```python
class BusinessRule(Protocol):
    def is_satisfied(self) -> bool:
        ...
    
    def message(self) -> str:
        ...

class UserEmailMustBeUnique(BusinessRule):
    def __init__(self, email: str, user_repository: UserRepository):
        self._email = email
        self._user_repository = user_repository
    
    def is_satisfied(self) -> bool:
        return not self._user_repository.exists_by_email(self._email)
    
    def message(self) -> str:
        return f"Email {self._email} is already in use"
```

### 2. Domain Exceptions

```python
class DomainException(Exception):
    pass

class BusinessRuleValidationException(DomainException):
    def __init__(self, rule: BusinessRule):
        super().__init__(rule.message())
        self.rule = rule
```

## Domain Service Implementation

### 1. Application Services

```python
class ApplicationService:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

class UserApplicationService(ApplicationService):
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        user_repository: UserRepository,
        event_publisher: DomainEventPublisher
    ):
        super().__init__(unit_of_work)
        self._user_repository = user_repository
        self._event_publisher = event_publisher
    
    def create_user(self, command: CreateUserCommand) -> UUID:
        with self._unit_of_work:
            user = User.create(
                email=command.email,
                password=command.password
            )
            
            # Check business rules
            self._check_rule(
                UserEmailMustBeUnique(
                    command.email,
                    self._user_repository
                )
            )
            
            saved_user = self._user_repository.save(user)
            self._event_publisher.publish(
                UserCreated(user_id=saved_user.id, email=saved_user.email)
            )
            
            return saved_user.id
```

## Best Practices

### 1. Domain Isolation
- Keep domain logic pure and framework-independent
- Use value objects for validated attributes
- Encapsulate business rules within entities and aggregates

### 2. Rich Domain Model
- Place business logic in domain objects
- Avoid anemic domain models
- Use domain services for operations spanning multiple aggregates

### 3. Bounded Contexts
- Clear boundaries between different domains
- Explicit context mapping
- Use shared kernel for common concepts

### 4. Event-Driven Design
- Domain events for cross-aggregate communication
- Event sourcing for critical state changes
- Event-driven integration between bounded contexts

### 5. Business Rules
- Explicit business rule objects
- Centralized rule validation
- Clear error messages

These guidelines ensure:
- Clear business logic representation
- Domain model integrity
- Maintainable and testable code
- Scalable architecture
- Proper separation of concerns