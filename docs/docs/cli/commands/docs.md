# Documentation Management Commands

The documentation commands help you generate, manage, and publish project documentation.

## Available Commands

### Documentation Generation

```bash
# Generate documentation from code
craftsmanship docs generate

# Generate API documentation
craftsmanship docs api

# Generate documentation site
craftsmanship docs site build
```

## Documentation Types

The `docs` command supports various documentation types:

| Type       | Description                                      |
|------------|--------------------------------------------------|
| `api`      | API documentation from OpenAPI specs             |
| `code`     | Code documentation from docstrings               |
| `guides`   | User guides and tutorials                        |
| `concepts` | Domain concepts and architecture                 |
| `site`     | Complete documentation site                      |

## Documentation Formats

Documentation can be generated in multiple formats:

```bash
# Generate HTML documentation
craftsmanship docs generate --format html

# Generate Markdown documentation
craftsmanship docs generate --format markdown

# Generate PDF documentation
craftsmanship docs generate --format pdf
```

## Documentation Publishing

Publishing documentation:

```bash
# Publish documentation to GitHub Pages
craftsmanship docs publish --target github-pages

# Publish documentation to ReadTheDocs
craftsmanship docs publish --target readthedocs
```

## Template Management

Working with documentation templates:

```bash
# List available templates
craftsmanship docs templates list

# Create a custom template
craftsmanship docs templates create my-template

# Use a specific template
craftsmanship docs generate --template my-template
```

## Usage Examples

```bash
# Complete documentation workflow
craftsmanship docs generate
craftsmanship docs site build
craftsmanship docs publish

# Generate specific documentation
craftsmanship docs api --title "Project API" --version "1.0.0"
```