import pytest
from expression import Ok, Error, Result, effect
from rich.table import Table
from fcship.tui.tables import (
    TableRow,
    create_table_row,
    add_row_to_table,
    create_summary_table,
    format_message,
    create_multi_column_table,
    display_table,
)
from fcship.tui.errors import DisplayError

@pytest.fixture
def sample_table():
    table = Table()
    table.add_column("Name")
    table.add_column("Status")
    return table

@pytest.fixture
def sample_row():
    return TableRow(name="Test Item", status="Success")

def test_table_row_creation():
    """Test creating a TableRow instance"""
    row = TableRow(name="Test", status="Done")
    assert row.name == "Test"
    assert row.status == "Done"

@effect.result[list[str], DisplayError]()
def test_create_table_row_success():
    """Test successful table row creation"""
    row = TableRow(name="Test Item", status="Success")
    result = yield from create_table_row(row)
    assert result.is_ok()
    assert result.ok == ["Test Item", "Success"]

@effect.result[list[str], DisplayError]()
def test_create_table_row_validation():
    """Test table row validation"""
    row = TableRow(name="", status="Success")
    result = yield from create_table_row(row)
    assert result.is_error()
    assert result.error.tag == "validation"

@effect.result[Table, DisplayError]()
def test_add_row_to_table_success(sample_table, sample_row):
    """Test adding a row to a table"""
    result = yield from add_row_to_table(sample_table, sample_row)
    assert result.is_ok()
    table = result.ok
    assert isinstance(table, Table)
    # Rich tables don't expose their data directly, so we can only verify the type

@effect.result[Table, DisplayError]()
def test_create_summary_table():
    """Test creating a summary table"""
    rows = [
        TableRow(name="Item 1", status="Success"),
        TableRow(name="Item 2", status="Failure")
    ]
    result = yield from create_summary_table("Test Summary", rows)
    assert result.is_ok()
    assert isinstance(result.ok, Table)
    assert result.ok.title == "Test Summary"

def test_format_message_success():
    """Test message formatting for success status"""
    result = format_message("Success")
    assert result == "[green]Success[/green]"

def test_format_message_failure():
    """Test message formatting for failure status"""
    result = format_message("Failure")
    assert result == "[red]Failure[/red]"

def test_format_message_other():
    """Test message formatting for other status"""
    result = format_message("In Progress")
    assert result == "In Progress"

@effect.result[Table, DisplayError]()
def test_create_multi_column_table():
    """Test creating a multi-column table"""
    headers = ["Name", "Status", "Description"]
    rows = [["Item 1", "Success", "Test description"]]
    result = yield from create_multi_column_table("Test Table", headers, rows)
    assert result.is_ok()
    assert isinstance(result.ok, Table)
    assert result.ok.title == "Test Table"

@effect.result[Table, DisplayError]()
def test_create_multi_column_table_validation():
    """Test validation in multi-column table creation"""
    headers = ["Name", "Status"]
    rows = [["Item 1", "Success", "Extra"]]  # Row longer than headers
    result = yield from create_multi_column_table("Test Table", headers, rows)
    assert result.is_error()
    assert result.error.tag == "validation"

@effect.result[None, DisplayError]()
async def test_display_table(sample_table):
    """Test table display"""
    result = await display_table(sample_table)
    assert result.is_ok()

@effect.result[None, DisplayError]()
async def test_display_table_error():
    """Test table display error handling"""
    result = await display_table(None)  # Should cause an error
    assert result.is_error()
    assert result.error.tag == "rendering" 