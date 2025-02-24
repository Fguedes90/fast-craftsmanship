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
    display_mailbox,
)
from fcship.tui.errors import DisplayError
import asyncio
import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def setup_mailbox():
    """Initialize the mailbox before each test"""
    # Reset mailbox state
    display_mailbox.stop()
    await asyncio.sleep(0.1)  # Give time for cleanup

    # Start mailbox and wait for it to be ready
    display_mailbox.start()
    await asyncio.sleep(0.1)  # Give the worker time to start

    # Verify mailbox is ready
    assert display_mailbox.started
    assert display_mailbox.mailbox is not None
    assert display_mailbox._worker_task is not None
    assert not display_mailbox._worker_task.done()

    yield display_mailbox

    # Cleanup
    display_mailbox.stop()
    await asyncio.sleep(0.1)  # Give time for cleanup

@pytest.fixture
def sample_table():
    """Create a sample table for testing"""
    table = Table()
    table.add_column("Name")
    table.add_column("Status")
    table.add_row("Test Item", "Success")
    return table

@pytest.fixture
def sample_row():
    return TableRow(name="Test Item", status="Success")

def test_table_row_creation():
    """Test creating a TableRow instance"""
    row = TableRow(name="Test", status="Done")
    assert row.name == "Test"
    assert row.status == "Done"

@effect.result[None, DisplayError]()
def test_create_table_row_success():
    """Test creating a table row successfully"""
    row = TableRow(name="Test Item", status="Success")
    result = yield from create_table_row(row)
    assert result.is_ok()
    assert result.ok == ["Test Item", "Success"]
    yield Ok(None)

@effect.result[None, DisplayError]()
def test_create_table_row_validation():
    """Test table row validation"""
    row = TableRow(name="", status="Success")
    result = yield from create_table_row(row)
    assert result.is_error()
    assert result.error.tag == "validation"
    assert "cannot be empty" in str(result.error)
    yield Ok(None)

@effect.result[None, DisplayError]()
def test_add_row_to_table_success(sample_table, sample_row):
    """Test adding a row to a table"""
    result = yield from add_row_to_table(sample_table, sample_row)
    assert result.is_ok()
    table = result.ok
    assert isinstance(table, Table)
    # Rich tables don't expose their data directly, so we can only verify the type
    yield Ok(None)

@effect.result[None, DisplayError]()
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
    yield Ok(None)

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

@effect.result[None, DisplayError]()
def test_create_multi_column_table():
    """Test creating a multi-column table"""
    headers = ["Name", "Status", "Description"]
    rows = [["Item 1", "Success", "Test description"]]
    result = yield from create_multi_column_table("Test Table", headers, rows)
    assert result.is_ok()
    assert isinstance(result.ok, Table)
    assert result.ok.title == "Test Table"
    yield Ok(None)

@effect.result[None, DisplayError]()
def test_create_multi_column_table_validation():
    """Test validation in multi-column table creation"""
    headers = ["Name", "Status"]
    rows = [["Item 1", "Success", "Extra"]]  # Row longer than headers
    result = yield from create_multi_column_table("Test Table", headers, rows)
    assert result.is_error()
    assert result.error.tag == "validation"
    yield Ok(None)

@effect.result[None, DisplayError]()
def test_display_table(setup_mailbox, sample_table):
    """Test table display"""
    try:
        result = yield from display_table(sample_table)
        assert result.is_ok()
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")
    yield Ok(None)

@effect.result[None, DisplayError]()
def test_display_table_error(setup_mailbox):
    """Test table display error handling"""
    try:
        result = yield from display_table(None)  # Should cause an error
        assert result.is_error()
        assert result.error.tag == "validation"
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")
    yield Ok(None)
