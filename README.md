# Fast-Craftsmanship CLI Tool

Fast-Craftsmanship is a CLI tool designed to streamline the management and scaffolding of FastAPI projects. It follows best practices to help you create a clean, consistent, and scalable project structure, whether you are starting a new project or adding features to an existing one.

## Features

- **Project Initialization**: Quickly scaffold a new FastAPI project with a pre-defined structure.
- **DDD Structure Generation**: Generate files for domain, service, API, repository, and tests following Domain-Driven Design principles.
- **Database Migrations**: Easily create, apply, and rollback database migrations.
- **Code Verification**: Run type checking, linting, tests, and formatting checks using a single command.
- **Extensibility**: Easily extend the CLI with custom templates and commands.

## Installation

### From PyPI

If the package is available on PyPI:

```bash
pip install fast-craftsmanship
```

### From Source

Clone the repository and install in editable mode:

```bash
git clone <repository-URL>
cd fcship
pip install -e ".[dev]"
```

## Usage

After installation, use the CLI by invoking `craftsmanship` followed by the desired command.

### Basic Commands

- **Project Initialization**
  ```bash
  craftsmanship project init <project_name>
  ```

- **Domain Generation**
  ```bash
  craftsmanship domain create <domain_name>
  ```

- **Service Layer Generation**
  ```bash
  craftsmanship service create <service_name>
  ```

- **API Endpoint Generation**
  ```bash
  craftsmanship api create <api_name>
  ```

- **Repository Implementation**
  ```bash
  craftsmanship repo create <repository_name>
  ```

- **Test File Generation**
  ```bash
  craftsmanship test create <unit|integration> <test_name>
  ```

- **Database Migrations**
  ```bash
  craftsmanship db migration <migration_name>
  craftsmanship db migrate
  craftsmanship db rollback
  ```

- **Code Verification**
  ```bash
  craftsmanship verify <all|type|lint|test|format>
  ```

### Additional

- **Version Information**
  ```bash
  craftsmanship --version
  ```

## Project Structure

When a new project is initialized, the following structure is created:

```
├── api/              # API endpoints and schemas
├── domain/           # Domain entities and interfaces
├── service/          # Service layer implementation
├── infrastructure/   # Database and external services
└── tests/            # Test suites (unit and integration)
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-feature`
3. Commit your changes.
4. Push your branch: `git push origin feature/my-feature`
5. Open a pull request describing your feature.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues or have suggestions, please open an issue in the repository.

---

Happy coding with Fast-Craftsmanship! 🚀
