# test-project

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
