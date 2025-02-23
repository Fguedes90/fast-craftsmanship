from expression import Ok, Error, Result, pipe, seq
from rich.table import Table
from fcship.tui.helpers import validate_table_row, validate_table_data, validate_input
from fcship.tui.errors import DisplayError

def create_table_row(name_result: tuple[str, Result[str, any]]) -> Result[tuple[str, str], DisplayError]:
    name, result = name_result
    return pipe(
        validate_input(name, "Row name"),
        lambda n: Ok((n.title(), "[green]✨ Passed[/green]")) if result.is_ok() else Ok((n, "[red]❌ Failed[/red]"))
    )

def add_row_to_table(table: Table, row: tuple[str, str]) -> Result[Table, DisplayError]:
    if not isinstance(table, Table):
        return Error(DisplayError.Validation("Invalid table object"))
    try:
        table.add_row(*row)
        return Ok(table)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to add row to table", e))

def create_summary_table(results: list[tuple[str, Result[str, any]]]) -> Result[Table, DisplayError]:
    table = Table()
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    
    def add_row(acc: Result[Table, DisplayError], row: tuple[str, Result[str, any]]) -> Result[Table, DisplayError]:
        return acc.bind(lambda t: create_table_row(row).bind(lambda r: add_row_to_table(t, r)))
    
    return pipe(
        results,
        lambda r: seq.fold(add_row, Ok(table), r)
    )

def format_message(parts: list[str], separator: str = "\n\n") -> Result[str, DisplayError]:
    if not isinstance(parts, list):
        return Error(DisplayError.Validation("Message parts must be a list"))
    filtered = list(filter(None, parts))
    if filtered:
        return Ok(separator.join(filtered))
    else:
        return Error(DisplayError.Validation("At least one non-empty message part is required"))

def create_multi_column_table(columns: list[tuple[str, str | None]], rows: list[list[str]]) -> Result[Table, DisplayError]:
    try:
        if not columns:
            return Error(DisplayError.Validation("Headers list cannot be empty"))
        if not all(isinstance(col[0], str) for col in columns):
            return Error(DisplayError.Validation("Headers must be strings"))
        if any(len(row) != len(columns) for row in rows):
            return Error(DisplayError.Rendering("Row length must match number of columns"))
        table = Table()
        for header, style in columns:
            table.add_column(header, style=style)
        for row in rows:
            table.add_row(*row)
        return Ok(table)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to create table", e))

async def display_table(table: Table) -> Result[None, DisplayError]:
    from fcship.tui.display import console
    try:
        console.print(table)
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display table", e))
