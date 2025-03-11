# Project Scaffolding & Structure Commands

The scaffolding commands help you create and manage your project structure and components following domain-driven design principles and FastAPI best practices.

## Available Commands

### `project`

Initialize and manage project structure.

```bash
# Initialize a new project
craftsmanship project init

# Add a new module to the project
craftsmanship project add-module users
```

### `domain`

Create and manage domain components like entities, value objects, and domain services.

```bash
# Create a domain entity
craftsmanship domain entity user

# Create a value object
craftsmanship domain value-object email
```

### `service`

Create and manage service layer components.

```bash
# Create a service
craftsmanship service create user-service

# Generate service methods
craftsmanship service add-method user-service create-user
```

### `api`

Generate API endpoints and schemas.

```bash
# Create API routes
craftsmanship api create users

# Generate API schemas
craftsmanship api schema user
```

### `repo`

Create and manage repository implementations.

```bash
# Create a repository
craftsmanship repo create user-repository

# Add repository methods
craftsmanship repo add-method user-repository find-by-email
```

## Usage Patterns

### Creating a Complete Feature

To create a complete feature with all necessary components:

```bash
# Create domain components
craftsmanship domain entity user
craftsmanship domain value-object email

# Create repository layer
craftsmanship repo create user-repository

# Create service layer
craftsmanship service create user-service

# Create API endpoints
craftsmanship api create users
```

### Command Options

Each command supports various options. Use the `--help` flag to see all available options:

```bash
craftsmanship project --help
craftsmanship domain entity --help
```