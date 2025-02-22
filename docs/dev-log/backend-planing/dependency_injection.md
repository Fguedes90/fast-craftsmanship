# Dependency Injection and Service Configuration

## Core Principles

### 1. Dependency Injection Container

```python
from dataclasses import dataclass
from typing import Dict, Type, Callable, Any

class Container:
    def __init__(self):
        self._services: Dict[Type, Callable[[], Any]] = {}
        
    def register(self, interface: Type, factory: Callable[[], Any]) -> None:
        self._services[interface] = factory
        
    def resolve(self, interface: Type) -> Any:
        factory = self._services.get(interface)
        if not factory:
            raise ValueError(f"No registration found for {interface}")
        return factory()
```

### 2. Service Registration

```python
@dataclass
class Settings:
    database_url: str
    redis_url: str
    aws_access_key: str
    aws_secret_key: str

def configure_services(settings: Settings) -> Container:
    container = Container()
    
    # Database
    container.register(
        Session,
        lambda: create_session(settings.database_url)
    )
    
    # Repositories
    container.register(
        UserRepository,
        lambda: PostgresUserRepository(container.resolve(Session))
    )
    
    # Services
    container.register(
        TokenService,
        lambda: JWTTokenService(settings.jwt_secret)
    )
    
    return container
```

## FastAPI Integration

### 1. Dependency Provider

```python
from fastapi import Depends
from typing import Annotated

class ServiceProvider:
    def __init__(self, container: Container):
        self._container = container
    
    def get_user_repository(self) -> UserRepository:
        return self._container.resolve(UserRepository)
    
    def get_user_service(
        self,
        repo: UserRepository = Depends(get_user_repository)
    ) -> UserService:
        return UserService(repo)

# Usage in FastAPI
UserRepo = Annotated[UserRepository, Depends(provider.get_user_repository)]
UserSvc = Annotated[UserService, Depends(provider.get_user_service)]

@router.post("/users")
def create_user(
    data: UserCreate,
    service: UserSvc
):
    return service.create_user(data)
```

### 2. Middleware Configuration

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

def configure_middlewares(app: FastAPI, container: Container) -> None:
    # Authentication
    app.add_middleware(
        AuthenticationMiddleware,
        token_service=container.resolve(TokenService)
    )
    
    # Tenant
    app.add_middleware(
        TenantMiddleware,
        tenant_service=container.resolve(TenantService)
    )
    
    # Logging
    app.add_middleware(
        LoggingMiddleware,
        logger=container.resolve(Logger)
    )
```

## Service Lifetime Management

### 1. Service Scopes

```python
from enum import Enum, auto

class ServiceLifetime(Enum):
    SINGLETON = auto()
    SCOPED = auto()
    TRANSIENT = auto()

class ScopedContainer:
    def __init__(self, parent: Container):
        self._parent = parent
        self._scoped_services: Dict[Type, Any] = {}
    
    def resolve(self, interface: Type) -> Any:
        if interface in self._scoped_services:
            return self._scoped_services[interface]
        
        service = self._parent.resolve(interface)
        self._scoped_services[interface] = service
        return service
```

### 2. Request Scope Management

```python
class RequestScopeMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        container: Container
    ):
        super().__init__(app)
        self._container = container
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.container = ScopedContainer(self._container)
        response = await call_next(request)
        return response
```

## Testing Support

### 1. Mock Service Registration

```python
def configure_test_services() -> Container:
    container = Container()
    
    # Register mock services
    container.register(
        UserRepository,
        lambda: MockUserRepository()
    )
    
    container.register(
        TokenService,
        lambda: MockTokenService()
    )
    
    return container
```

### 2. Test Fixtures

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def app():
    container = configure_test_services()
    app = create_app(container)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)
```

## Configuration Management

### 1. Settings Management

```python
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # AWS
    aws_access_key: str
    aws_secret_key: str
    s3_bucket: str
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"

def get_settings() -> AppSettings:
    return AppSettings()
```

### 2. Environment-Specific Configuration

```python
def configure_environment() -> Container:
    settings = get_settings()
    
    if settings.environment == "development":
        return configure_development(settings)
    elif settings.environment == "testing":
        return configure_testing(settings)
    else:
        return configure_production(settings)
```

## Best Practices

1. **Single Responsibility**
   - Each service should have a single, well-defined responsibility
   - Avoid service classes that do too much
   - Keep service interfaces focused

2. **Interface Segregation**
   - Define clear interfaces for services
   - Avoid large, monolithic service interfaces
   - Split services based on client needs

3. **Dependency Inversion**
   - Depend on abstractions, not implementations
   - Use interface protocols for service definitions
   - Configure concrete implementations at startup

4. **Lifecycle Management**
   - Properly manage service lifetimes
   - Clean up resources when services are disposed
   - Use appropriate scope for each service

5. **Testing Support**
   - Easy service mocking
   - Configurable test containers
   - Isolated test environments

These patterns ensure:
- Loose coupling between components
- Easy testing and mocking
- Clear service boundaries
- Maintainable codebase
- Flexible configuration
- Proper resource management