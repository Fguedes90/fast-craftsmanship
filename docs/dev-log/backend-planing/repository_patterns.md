# Repository Pattern Implementation Guidelines

## Design Principles

### 1. Domain-Specific Repositories

Each domain should have its own repositories that handle data access specific to that domain's context. For example:

```python
# Domain: Users
class UserRepository(Protocol):
    def get_by_email(self, email: str) -> Optional[User]:
        ...
    def save(self, user: User) -> User:
        ...

# Domain: Auth
class TokenRepository(Protocol):
    def save_refresh_token(self, token: RefreshToken) -> None:
        ...
    def validate_token(self, token_value: str) -> bool:
        ...
```

### 2. Repository Interface Location

Repository interfaces should be defined in the domain layer, while implementations reside in the infrastructure layer:

```
domains/
├── users/
│   ├── domain/
│   │   └── repositories.py  # Interfaces
│   └── infrastructure/
│       └── postgres_repository.py  # Implementations
```

## Implementation Patterns

### 1. Base Repository Pattern

```python
from typing import TypeVar, Generic, Protocol

T = TypeVar('T')

class Repository(Protocol, Generic[T]):
    def get(self, id: Any) -> Optional[T]:
        ...
    def save(self, entity: T) -> T:
        ...
    def delete(self, id: Any) -> None:
        ...
```

### 2. Domain-Specific Repository Methods

```python
class UserRepository(Repository[User]):
    def get_by_email(self, email: str) -> Optional[User]:
        ...
    def get_by_username(self, username: str) -> Optional[User]:
        ...
```

## Tenant-Aware Repositories

### 1. Base Tenant-Aware Repository

```python
class TenantAwareRepository(Repository[T]):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def get_for_tenant(self, id: Any) -> Optional[T]:
        ...
    def save_for_tenant(self, entity: T) -> T:
        ...
```

### 2. Implementation Example

```python
class PostgresUserRepository(TenantAwareRepository[User]):
    def __init__(self, session: Session, tenant_id: str):
        super().__init__(tenant_id)
        self._session = session

    def get_for_tenant(self, id: Any) -> Optional[User]:
        return self._session.query(UserModel)\
            .filter(UserModel.tenant_id == self.tenant_id)\
            .filter(UserModel.id == id)\
            .first()
```

## Query Specifications

### 1. Specification Pattern

```python
class Specification(Protocol[T]):
    def is_satisfied_by(self, entity: T) -> bool:
        ...

class QuerySpecification(Protocol[T]):
    def to_query(self) -> Any:
        ...
```

### 2. Implementation Example

```python
class ActiveUsersSpecification(QuerySpecification[User]):
    def to_query(self):
        return User.is_active == True

class UserRepository(Repository[User]):
    def find_by_specification(self, spec: QuerySpecification[User]) -> List[User]:
        return self._session.query(User).filter(spec.to_query()).all()
```

## Repository Factory Pattern

### 1. Factory Interface

```python
class RepositoryFactory(Protocol):
    def create_user_repository(self) -> UserRepository:
        ...
    def create_token_repository(self) -> TokenRepository:
        ...
```

### 2. Implementation

```python
class PostgresRepositoryFactory(RepositoryFactory):
    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    def create_user_repository(self) -> UserRepository:
        return PostgresUserRepository(self._session_factory())
```

## Transaction Management

### 1. Unit of Work Pattern

```python
class UnitOfWork(Protocol):
    def begin(self) -> None:
        ...
    def commit(self) -> None:
        ...
    def rollback(self) -> None:
        ...
    def __enter__(self) -> 'UnitOfWork':
        ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...
```

### 2. Implementation

```python
class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory
        
    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
```

## Integration Guidelines

### 1. Service Layer Usage

```python
class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        unit_of_work: UnitOfWork
    ):
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work

    def create_user(self, user_data: UserCreate) -> User:
        with self._unit_of_work:
            user = User.create(user_data)
            return self._user_repository.save(user)
```

### 2. API Layer Integration

```python
@router.post("/users")
def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return user_service.create_user(user_data)
```

## Best Practices

1. **Repository Independence**
   - Repositories should be independent of each other
   - Avoid repository-to-repository calls
   - Use service layer for cross-repository operations

2. **Query Optimization**
   - Implement lazy loading where appropriate
   - Use query specifications for complex queries
   - Consider implementing query objects for complex scenarios

3. **Error Handling**
   - Define repository-specific exceptions
   - Translate database errors to domain exceptions
   - Handle connection errors gracefully

4. **Testing**
   - Create mock repositories for testing
   - Test repository implementations in isolation
   - Use in-memory databases for integration tests

These patterns ensure:
- Clean separation of concerns
- Testable data access layer
- Flexible and maintainable code
- Support for multi-tenant architecture
- Consistent data access patterns across the application