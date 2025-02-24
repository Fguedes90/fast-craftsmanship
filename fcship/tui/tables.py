from dataclasses import dataclass, field
from typing import List, Tuple, Optional, TypeVar, Generic, Callable
from expression import Ok, Error, Result, pipe, effect, MailboxProcessor, AsyncReplyChannel
from expression.collections import seq
from rich.table import Table
from fcship.tui.helpers import validate_table_row, validate_table_data, validate_input
from fcship.tui.errors import DisplayError
from fcship.tui.display import console
import asyncio

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

@effect.result[list[str], DisplayError]()
def create_table_row(row: TableRow) -> Result[list[str], DisplayError]:
    """Create a table row from a TableRow instance"""
    if not row.name.strip():
        yield Error(DisplayError.Validation("Row name cannot be empty"))
    else:
        yield Ok([row.name, row.status])

@effect.result[Table, DisplayError]()
def add_row_to_table(table: Table, row: TableRow) -> Result[Table, DisplayError]:
    """Add a row to a table"""
    if not isinstance(table, Table):
        yield Error(DisplayError.Validation("Invalid table object"))
    else:
        try:
            table.add_row(row.name, row.status)
            yield Ok(table)
        except Exception as e:
            yield Error(DisplayError.Rendering("Failed to add row to table", e))

@effect.result[Table, DisplayError]()
def create_summary_table(title: str, rows: List[TableRow]) -> Result[Table, DisplayError]:
    """Create a summary table from a list of rows"""
    try:
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="bold")
        
        for row in rows:
            result = yield add_row_to_table(table, row)
            if result.is_error():
                yield result
        
        yield Ok(table)
    except Exception as e:
        yield Error(DisplayError.Rendering("Failed to create summary table", e))

def format_message(message: str) -> str:
    """Format a message based on its content"""
    match message.lower():
        case "success":
            return "[green]Success[/green]"
        case "failure":
            return "[red]Failure[/red]"
        case _:
            return message

@effect.result[Table, DisplayError]()
def create_multi_column_table(title: str, headers: List[str], rows: List[List[str]]) -> Result[Table, DisplayError]:
    """Create a multi-column table"""
    if not headers:
        yield Error(DisplayError.Validation("Headers list cannot be empty"))
        return
    
    if not all(isinstance(h, str) for h in headers):
        yield Error(DisplayError.Validation("Headers must be strings"))
        return
    
    if not all(len(row) == len(headers) for row in rows):
        yield Error(DisplayError.Validation("Row length must match number of columns"))
        return
    
    try:
        table = Table(title=title)
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*row)
        yield Ok(table)
    except Exception as e:
        yield Error(DisplayError.Rendering("Failed to create table", e))

@dataclass
class ResultContainer:
    """Mutable container for storing the result"""
    result: Result[None, DisplayError] = field(default_factory=lambda: Error(DisplayError.Rendering("No result", None)))

@dataclass(frozen=True)
class DisplayMessage:
    """Message for display operations"""
    table: Table | None
    callback: Callable[[Result[None, DisplayError]], None]

class DisplayMailbox:
    """Mailbox for handling display operations"""
    def __init__(self):
        self.mailbox = None
        self.started = False
        self._worker_task = None
    
    async def worker(self, inbox: MailboxProcessor) -> None:
        """Worker that handles display operations"""
        try:
            while True:
                msg = await inbox.receive()
                if not isinstance(msg, DisplayMessage):
                    continue
                    
                if msg.table is None or not isinstance(msg.table, Table):
                    msg.callback(Error(DisplayError.Validation("Invalid table object")))
                    continue

                try:
                    console.print(msg.table)
                    msg.callback(Ok(None))
                except Exception as e:
                    msg.callback(Error(DisplayError.Rendering("Failed to display table", e)))
        except asyncio.CancelledError:
            # Handle task cancellation gracefully
            pass
        except Exception as e:
            # Handle any unexpected errors in the worker
            if 'msg' in locals() and hasattr(msg, 'callback'):
                msg.callback(Error(DisplayError.Rendering("Worker error", e)))
    
    def start(self):
        """Start the mailbox if not already started"""
        if not self.started:
            if self._worker_task is not None:
                self._worker_task.cancel()
            # Create mailbox with no cancellation token
            self.mailbox = MailboxProcessor(None)
            # Start the mailbox with the worker function
            self._worker_task = asyncio.create_task(self.worker(self.mailbox))
            self.started = True
    
    def stop(self):
        """Stop the mailbox"""
        if self._worker_task is not None:
            self._worker_task.cancel()
            self._worker_task = None
        self.mailbox = None
        self.started = False

# Create the display mailbox
display_mailbox = DisplayMailbox()

@effect.result[None, DisplayError]()
def display_table(table: Table) -> Result[None, DisplayError]:
    """Display a table using the console via mailbox"""
    if table is None or not isinstance(table, Table):
        yield Error(DisplayError.Validation("Invalid table object"))
        return
        
    try:
        # Ensure mailbox is started
        if not display_mailbox.started:
            display_mailbox.start()
            
        # Verify mailbox is ready
        if not display_mailbox.started or display_mailbox.mailbox is None:
            yield Error(DisplayError.Rendering("Mailbox not initialized", None))
            return
            
        # Create message builder
        def build_message(reply_channel: AsyncReplyChannel[Result[None, DisplayError]]) -> DisplayMessage:
            return DisplayMessage(table=table, callback=reply_channel)
            
        try:
            # Post message and wait for reply
            result = display_mailbox.mailbox.post_and_async_reply(build_message)
            yield Ok(result)
        except Exception as e:
            yield Error(DisplayError.Rendering("Failed to display table", e))
    except Exception as e:
        yield Error(DisplayError.Rendering("Failed to initialize display", e))
