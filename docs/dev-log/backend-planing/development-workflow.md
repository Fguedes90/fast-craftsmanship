# Development Workflow

## Overview

This document describes how to effectively use the provided tools and follow the project's architectural patterns in your daily development workflow.

## Getting Started

### 1. Environment Setup
```bash
# Install CLI tool
pip install craftsmanship

# Install VSCode snippets
cp .vscode/craftsmanship.code-snippets ~/.vscode/snippets/
```

### 2. Configure VSCode
- Install recommended extensions
- Enable format on save
- Use project-specific settings

## Feature Development Workflow

### 1. Creating New Features

#### a. Domain-First Approach
```bash
# Create domain structure
craftsmanship domain create customer

# Implement domain components using snippets
- Use `entity` snippet for domain entity
- Use `repo-interface` snippet for repository interface
```

#### b. Infrastructure Layer
```bash
# Generate repository implementation
craftsmanship repo create customer

# Implement using snippets
- Use `repo-impl` snippet for repository implementation
```

#### c. Service Layer
```bash
# Generate service structure
craftsmanship service create customer

# Implement using snippets
- Use `service` snippet for service class
- Use `dto` snippet for DTOs
```

#### d. API Layer
```bash
# Generate API endpoints
craftsmanship api create customer

# Implement using snippets
- Use `router` snippet for FastAPI router
- Use `schema` snippet for request/response models
```

### 2. Testing

#### a. Unit Tests
```bash
# Generate test structure
craftsmanship test create unit customer

# Implement using snippets
- Use `test-unit` snippet for test cases
```

#### b. Integration Tests
```bash
# Generate test structure
craftsmanship test create integration customer

# Implement using snippets
- Use `test-integration` snippet for API tests
```

### 3. Code Quality Checks
```bash
# Run all verifications
craftsmanship verify

# Individual checks
craftsmanship verify lint
craftsmanship verify type
craftsmanship verify test
```

## Common Development Tasks

### 1. Database Changes

```bash
# Create new migration
craftsmanship db migration create add_customer_table

# Apply migrations
craftsmanship db migrate

# Rollback if needed
craftsmanship db rollback
```

### 2. Adding New API Endpoints

```bash
# Generate route and schema files
craftsmanship api create endpoint-name

# Implement endpoint
1. Define request/response schemas using `schema` snippet
2. Implement route handler using `router` snippet
3. Add service method if needed
4. Create integration test using `test-integration` snippet
```

### 3. Adding New Domain Features

```bash
# Complete domain implementation
1. Create domain using CLI
2. Implement entity using snippets
3. Define repository interface
4. Create repository implementation
5. Add service layer
6. Create API endpoints
7. Add tests
```

## Best Practices

### 1. Code Organization

- One domain concept per directory
- Clear separation of layers
- Consistent file naming
- Follow interface segregation

### 2. Implementation Guidelines

- Use type hints everywhere
- Document public APIs
- Keep functions focused
- Follow SOLID principles

### 3. Testing Strategy

- Write tests first
- Cover edge cases
- Use meaningful test names
- Keep tests independent

### 4. Version Control

- Small, focused commits
- Clear commit messages
- Feature branches
- PR reviews

## Troubleshooting

### 1. Common Issues

- CLI tool errors
- Migration conflicts
- Test failures
- Type checking issues

### 2. Solutions

- Check logs
- Verify migrations
- Run specific tests
- Use debug mode

## Quick Reference

### Snippets

```
entity         - Create domain entity
repo-interface - Create repository interface
repo-impl     - Create repository implementation
service        - Create service class
dto           - Create DTO class
router        - Create API router
schema        - Create Pydantic schema
test-unit     - Create unit test
test-integration - Create integration test
```

### CLI Commands

```
craftsmanship domain create   - Create domain
craftsmanship service create  - Create service
craftsmanship api create      - Create API endpoint
craftsmanship repo create     - Create repository
craftsmanship test create    - Create test file
craftsmanship verify         - Run verifications
craftsmanship db migration   - Manage migrations
```

## Support

- Check documentation in `/docs`
- Use issue tracker
- Contact team lead
- Review architecture docs

Remember: The CLI tools and snippets are designed to help maintain consistency and reduce boilerplate. They should be used as part of your regular development workflow to ensure the codebase remains clean and maintainable.