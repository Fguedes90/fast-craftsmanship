# Fast-Craftsmanship CLI

Fast-craftsmanship is a comprehensive CLI tool that helps you maintain a clean and consistent project structure following domain-driven design principles and FastAPI best practices.

## Command Categories

The CLI is organized into the following categories:

### Project Scaffolding & Structure

Commands for creating and managing your project structure and components:

- `project` - Initialize and manage project structure
- `domain` - Create and manage domain components
- `service` - Create and manage service layer components
- `api` - Generate API endpoints and schemas
- `repo` - Create and manage repository implementations

� [Learn more about Scaffolding commands](./commands/scaffold.md)

### Version Control & Collaboration

Commands for managing version control:

- `commit` - Tool to create conventional commit messages

� [Learn more about VCS commands](./commands/vcs.md)

### GitHub Integration

Commands for interacting with GitHub:

- GitHub repository setup and management
- GitHub Actions workflows
- Pull requests and issues

� [Learn more about GitHub commands](./commands/github.md)

### Quality Assurance & Testing

Commands for ensuring code quality:

- `test` - Create test files and run tests
- `verify` - Run code quality checks

� [Learn more about Quality commands](./commands/quality.md)

### Database Management

Commands for managing databases:

- `db` - Manage database migrations

� [Learn more about Database commands](./commands/db.md)

### Documentation Management

Commands for generating and managing documentation:

- Documentation tools

� [Learn more about Documentation commands](./commands/docs.md)

### Web Scraping

Commands for web scraping:

- Markdown scraping tools

� [Learn more about Scraping commands](./commands/scraper.md)

## Getting Started

To get started with the Fast-craftsmanship CLI, run:

```bash
# Show available commands
craftsmanship --help

# View command categories
craftsmanship --categories

# View specific category commands
craftsmanship scaffold --help

# Launch interactive Terminal UI
craftsmanship menu
# or
craftsmanship --tui
```

### Interactive Terminal UI

Fast-craftsmanship includes an interactive Terminal UI that makes it easy to browse and run commands without remembering all the options. You can launch it with:

```bash
craftsmanship menu
```

The TUI provides:

- Category-based navigation
- Command descriptions
- Help text for each command
- One-click execution of commands

## Common Usage Patterns

```bash
# Initialize a new project
craftsmanship project init

# Create domain components
craftsmanship domain entity user

# Generate API routes
craftsmanship api create users

# Run code quality checks
craftsmanship verify
```

For detailed documentation on each command, refer to the specific category pages.