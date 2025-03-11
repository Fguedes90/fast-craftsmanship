# Commands Reference

Fast Craftsmanship provides a set of commands to help you implement software projects quickly while following best practices.

## Command Structure

All commands follow a consistent structure:

```bash
fcship <command> <subcommand> [options] [arguments]
```

For example:

```bash
fcship github setup init-repo my-repository
```

## Main Command Groups

Fast Craftsmanship organizes functionality into these main command groups:

| Command | Description |
| ------- | ----------- |
| `github` | GitHub repository and workflow management |
| `project` | Project creation and setup |
| `docs` | Documentation generation and management |
| `verify` | Code verification and analysis |
| `compact` | Compact code representation generation |
| `domain` | Domain model generation |
| `service` | Service layer generation |
| `repo` | Repository layer generation |
| `api` | API endpoint generation |
| `test` | Test utility commands |
| `commit` | Git commit assistance with conventional commits |

## Getting Help

You can get detailed help on any command by adding the `--help` flag:

```bash
fcship github --help
fcship github setup init-repo --help
```

## Common Options

These options are available across most commands:

| Option | Description |
| ------ | ----------- |
| `--help` | Display help for a command |
| `--version` | Display version information |
| `--verbose` | Enable detailed output |
| `--quiet` | Suppress all output except errors |
| `--no-color` | Disable colorized output |

## Command Details

Click on a specific command below to see detailed documentation:

- [GitHub Commands](github.md) - Repository and workflow management
- [Project Commands](project.md) - Project creation and setup
- [Documentation Commands](docs.md) - Documentation generation and management
- [Verify Commands](verify.md) - Code verification and analysis
- [Compact Commands](compact.md) - Compact code representation generation

## Command Examples

Here are some common command examples to get you started:

### Setting up a new project

```bash
# Create a new project
fcship project create my-awesome-project --template api

# Set up documentation
fcship docs setup --site-name "My Awesome Project" --repo-url "https://github.com/username/my-awesome-project"

# Initialize GitHub repository
fcship github setup init-repo my-awesome-project --description "My awesome project"
```

### Working with existing projects

```bash
# Verify code quality
fcship verify --fix

# Generate compact code representation
fcship compact -o docs/code_overview.txt

# Serve documentation locally
fcship docs serve --dev-addr 127.0.0.1:8080
```

### Preparing for deployment

```bash
# Build documentation
fcship docs build --clean

# Create a GitHub release
fcship github release my-awesome-project --tag-name v1.0.0 --name "Version 1.0.0"
```