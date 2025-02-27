"""Project templates"""


def get_project_templates(name: str) -> dict[str, str]:
    """Get templates for project scaffolding."""
    return {
        "pyproject.toml": f"""[project]
name = "{name}"
version = "0.1.0"
description = "A FastAPI project using fast-craftsmanship"
requires-python = ">=3.12"

[project.dependencies]
fastapi = ">=0.109.0"
sqlalchemy = ">=2.0.25"
alembic = ">=1.13.1"
pydantic = ">=2.5.3"
pydantic-settings = ">=2.1.0"
python-jose = {{"extras": ["cryptography"], "version": ">=3.3.0"}}
passlib = {{"extras": ["bcrypt"], "version": ">=1.7.4"}}

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.5",
    "black>=24.1.1",
    "flake8>=7.0.0",
    "mypy>=1.8.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
""",
        "README.md": f"""# {name}

A FastAPI project using fast-craftsmanship.

## Development

1. Create and activate virtual environment
2. Install dependencies: `pip install -e ".[dev]"`
3. Run development server: `uvicorn app.main:app --reload`

## Project Structure

```
├── api/          # API endpoints and schemas
├── domain/       # Domain entities and interfaces
├── service/      # Service layer implementation
├── infrastructure/ # Database and external services
└── tests/        # Test suites
```
""",
    }
