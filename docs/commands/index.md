# Commands Reference

Fast Craftsmanship provides a set of commands to help you implement software projects quickly while following best practices.

## Command Structure

All commands follow a consistent structure:

```bash
fcship <command> <subcommand> [options] [arguments]
```

For example:

```bash
fcship github create my-repository
```

## Main Command Groups

Fast Craftsmanship organizes functionality into these main command groups:

| Command | Description |
| ------- | ----------- |
| `github` | GitHub repository and workflow management |
| `project` | Project creation and setup |
| `domain` | Domain model generation |
| `service` | Service layer generation |
| `repo` | Repository layer generation |
| `api` | API endpoint generation |
| `verify` | Code verification and analysis |
| `test` | Test utility commands |
| `commit` | Git commit assistance with conventional commits |

## Getting Help

You can get detailed help on any command by adding the `--help` flag:

```bash
fcship github --help
fcship github create --help
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
- [Verify Commands](verify.md) - Code verification and analysis  
- [Project Commands](project.md) - Project creation and setup