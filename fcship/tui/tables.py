from dataclasses import dataclass
from typing import List, Tuple, Optional, TypeVar, Generic
from expression import Ok, Error, Result, pipe, effect
from expression.collections import seq
from rich.table import Table
from fcship.tui.helpers import validate_table_row, validate_table_data, validate_input
from fcship.tui.errors import DisplayError
from fcship.tui.display import console

T = TypeVar('T')

@dataclass(frozen=True)
class TableRow:
    """Represents a row in a table"""
    name: str
    status: str

@dataclass(frozen=True)
class TableColumn:
    """Represents a column in a table"""
    header: str
    style: Optional[str]

def create_table_row(name_result: Tuple[str, Result[str, T]]) -> Result[TableRow, DisplayError]:
    """Create a table row from a name and result"""
    name, result = name_result
    return pipe(
        validate_input(name, "Row name"),
        lambda n: Ok(TableRow(
            n.title(),
            "[green]✨ Passed[/green]" if result.is_ok() else "[red]❌ Failed[/red]"
        ))
    )

def add_row_to_table(table: Table, row: TableRow) -> Result[Table, DisplayError]:
    """Add a row to a table"""
    match isinstance(table, Table):
        case False:
            return Error(DisplayError.Validation("Invalid table object"))
        case True:
            return pipe(
                Ok(table),
                lambda t: Ok(t.add_row(row.name, row.status)),
                lambda _: Ok(table)
            ).map_error(lambda e: DisplayError.Rendering("Failed to add row to table", e))

def create_summary_table(results: List[Tuple[str, Result[str, T]]]) -> Result[Table, DisplayError]:
    """Create a summary table from a list of results"""
    def init_table() -> Table:
        table = Table()
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="bold")
        return table
    
    def add_row(acc: Result[Table, DisplayError], row: Tuple[str, Result[str, T]]) -> Result[Table, DisplayError]:
        return pipe(
            acc,
            lambda table: create_table_row(row),
            lambda row_result: row_result.bind(lambda r: add_row_to_table(table.unwrap(), r))
        )
    
    return pipe(
        results,
        lambda r: seq.fold(add_row, Ok(init_table()), r)
    )

def format_message(parts: List[str], separator: str = "\n\n") -> Result[str, DisplayError]:
    """Format a list of message parts into a single string"""
    match (isinstance(parts, list), list(filter(None, parts))):
        case (False, _):
            return Error(DisplayError.Validation("Message parts must be a list"))
        case (True, []):
            return Error(DisplayError.Validation("At least one non-empty message part is required"))
        case (True, filtered):
            return Ok(separator.join(filtered))

def create_multi_column_table(columns: List[TableColumn], rows: List[List[str]]) -> Result[Table, DisplayError]:
    """Create a multi-column table"""
    def validate_input() -> Result[None, DisplayError]:
        match (bool(columns), all(isinstance(col.header, str) for col in columns)):
            case (False, _):
                return Error(DisplayError.Validation("Headers list cannot be empty"))
            case (_, False):
                return Error(DisplayError.Validation("Headers must be strings"))
            case _:
                return Ok(None)
    
    def validate_rows() -> Result[None, DisplayError]:
        return (
            Ok(None)
            if all(len(row) == len(columns) for row in rows)
            else Error(DisplayError.Rendering("Row length must match number of columns"))
        )
    
    def create_table() -> Result[Table, DisplayError]:
        return pipe(
            Ok(Table()),
            lambda t: Ok([t.add_column(col.header, style=col.style) for col in columns] and t),
            lambda t: Ok([t.add_row(*row) for row in rows] and t)
        ).map_error(lambda e: DisplayError.Rendering("Failed to create table", e))
    
    return pipe(
        validate_input(),
        lambda _: validate_rows(),
        lambda _: create_table()
    )

async def display_table(table: Table) -> Result[None, DisplayError]:
    """Display a table using the console"""
    return pipe(
        Ok(console.print(table)),
        lambda _: Ok(None)
    ).map_error(lambda e: DisplayError.Rendering("Failed to display table", e))
