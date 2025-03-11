# Version Control & Collaboration Commands

The VCS commands help you manage version control with consistent commit messages following conventional commits format.

## Available Commands

### `commit`

Generate and create conventional commit messages.

```bash
# Create a conventional commit
craftsmanship commit

# Create a commit with a specific type
craftsmanship commit --type feat

# Create a commit with a scope
craftsmanship commit --type fix --scope auth
```

## Conventional Commit Types

Supported commit types:

| Type       | Description                                           |
|------------|-------------------------------------------------------|
| `feat`     | A new feature                                         |
| `fix`      | A bug fix                                             |
| `docs`     | Documentation only changes                            |
| `style`    | Changes that do not affect meaning (formatting)       |
| `refactor` | Code change that neither fixes a bug nor adds feature |
| `perf`     | Code change that improves performance                 |
| `test`     | Adding missing tests or correcting existing tests     |
| `build`    | Changes to build system or external dependencies      |
| `ci`       | Changes to CI configuration files and scripts         |
| `chore`    | Other changes that don't modify src or test files     |

## Integration with Git

The `commit` command integrates seamlessly with Git:

1. Automatically stages modified files
2. Creates a well-formatted commit message
3. Executes the commit

## Usage Examples

```bash
# Interactive commit generation
craftsmanship commit

# Quick commit with type and message
craftsmanship commit --type feat --message "Add user authentication"

# Commit with breaking change
craftsmanship commit --type feat --breaking --message "Complete API redesign"
```