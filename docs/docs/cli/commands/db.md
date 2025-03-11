# Database Management Commands

The database commands help you manage database migrations, schemas, and data.

## Available Commands

### `db`

Manage database migrations and schemas.

```bash
# Create a new migration
craftsmanship db migration create add_users_table

# Run migrations
craftsmanship db migrate

# Rollback migration
craftsmanship db rollback

# Generate database schema
craftsmanship db schema generate
```

## Database Operations

The `db` command supports various database operations:

| Operation   | Description                                    |
|-------------|------------------------------------------------|
| `migration` | Create and manage database migrations          |
| `migrate`   | Apply pending migrations                       |
| `rollback`  | Rollback previously applied migrations         |
| `schema`    | Generate and validate database schemas         |
| `seed`      | Seed the database with test or initial data    |
| `reset`     | Reset the database (drop and recreate)         |

## Migration Management

Managing database migrations:

```bash
# Create a new migration
craftsmanship db migration create add_user_fields

# List all migrations
craftsmanship db migration list

# Check migration status
craftsmanship db migration status
```

## Database Schemas

Working with database schemas:

```bash
# Generate schema from models
craftsmanship db schema generate

# Export schema to SQL
craftsmanship db schema export --format sql

# Visualize schema as diagram
craftsmanship db schema visualize
```

## Database Seeding

Seeding the database with data:

```bash
# Seed database with default data
craftsmanship db seed

# Seed with specific data set
craftsmanship db seed --dataset test_users
```

## Usage Examples

```bash
# Complete database setup
craftsmanship db migration create initial_schema
craftsmanship db migrate
craftsmanship db seed

# Check database status
craftsmanship db migration status
```