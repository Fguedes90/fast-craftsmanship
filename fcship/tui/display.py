from ast import TypeAlias
from collections.abc import Generator
from expression import Ok, Error, Result, pipe, tagged_union, effect
from rich.console import Console
from rich.rule import Rule
from dataclasses import dataclass
from typing import Optional, Tuple, List, Literal, TypeVar, Generic, Protocol, Any, ForwardRef
from enum import Enum
from functools import reduce

T = TypeVar('T')

# Create console instance
console = Console()

# Protocol for console abstraction
class ConsoleProtocol(Protocol):
    def print(self, *args, **kwargs) -> None: ...

@tagged_union
class DisplayError:
    """Display-related errors"""
    tag: Literal["validation", "rendering"]
    validation: str = None
    rendering: Tuple[str, Exception] = None

    @staticmethod
    def Validation(msg: str) -> "DisplayError":
        return DisplayError(tag="validation", validation=msg)

    @staticmethod
    def Rendering(msg: str, exc: Exception) -> "DisplayError":
        return DisplayError(tag="rendering", rendering=(msg, exc))

# Immutable data structures
@dataclass(frozen=True)
class DisplayMessage:
    content: str
    style: Optional[str] = None
    indent_level: int = 0

@dataclass(frozen=True)
class BatchMessages:
    messages: List[Tuple[str, str]]

@dataclass(frozen=True)
class DisplayContext:
    console: ConsoleProtocol

class DisplayStyle(Enum):
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    ERROR_DETAIL = "red dim"

# Type aliases for improved readability
MessagePair = Tuple[str, str]
MessageList = List[MessagePair]
DisplayResult = Result[None, DisplayError]
MessageResult = Result[DisplayMessage, DisplayError]
BatchResult = Result[BatchMessages, DisplayError]

def validate_message_pair(msg_pair: MessagePair) -> Result[MessagePair, DisplayError]:
    msg, style = msg_pair
    return (
        Ok((msg, style))
        if msg and style
        else Error(DisplayError.Validation("Message and style cannot be empty"))
    )

# Pure validation functions
def validate_message(message: DisplayMessage) -> MessageResult:
    return (
        Ok(message)
        if message.content.strip()
        else Error(DisplayError.Validation("Message content cannot be empty"))
    )

@effect.result[BatchMessages, DisplayError]()
def validate_batch_messages(batch: BatchMessages) -> Generator[Any, None, Result[BatchMessages, DisplayError]]:
    """Validate a batch of messages using effect system"""
    if not batch.messages:
        return Error(DisplayError.Validation("Batch messages cannot be empty"))
    
    validated_messages: MessageList = []
    for msg_pair in batch.messages:
        result = yield from validate_message_pair(msg_pair)
        validated_messages.append(result)
    
    return Ok(BatchMessages(messages=validated_messages))

# Pure console I/O functions
def print_styled(ctx: DisplayContext, message: DisplayMessage) -> DisplayResult:
    """Pure function to print styled message to console"""
    def format_message() -> str:
        indent = "  " * message.indent_level
        return (
            f"{indent}[{message.style}]{message.content}[/{message.style}]"
            if message.style
            else f"{indent}{message.content}"
        )
    
    return pipe(
        Ok(format_message()),
        lambda msg: Ok(ctx.console.print(msg)),
        lambda _: Ok(None)
    ).map_error(lambda e: DisplayError.Rendering("Failed to print styled message", e))

def print_rule(ctx: DisplayContext, message: str, style: Optional[str] = None) -> DisplayResult:
    """Pure function to print a rule to console"""
    return pipe(
        Ok(Rule(message, style=style)),
        lambda rule: Ok(ctx.console.print(rule)),
        lambda _: Ok(None)
    ).map_error(lambda e: DisplayError.Rendering("Failed to print rule", e))

# Create display context
display_ctx = DisplayContext(console=Console())

@effect.result[None, DisplayError]()
def handle_display(ctx: DisplayContext, message: DisplayMessage) -> Generator[Any, None, Result[None, DisplayError]]:
    """Handle display with effect system"""
    validated = yield from validate_message(message)
    return print_styled(ctx, validated)

@effect.result[None, DisplayError]()
def display_message(ctx: DisplayContext, message: DisplayMessage) -> Generator[Any, None, Result[None, DisplayError]]:
    return (yield from handle_display(ctx, message))

def success_message(ctx: DisplayContext, content: str) -> DisplayResult:
    return pipe(
        content,
        lambda c: DisplayMessage(content=c, style=DisplayStyle.SUCCESS.value),
        lambda m: display_message(ctx, m)
    )

@effect.result[None, DisplayError]()
def error_message(ctx: DisplayContext, content: str, details: Optional[str] = None) -> Generator[Any, None, Result[None, DisplayError]]:
    """Display error message with optional details using effect system"""
    yield from display_message(ctx, DisplayMessage(
        content=content,
        style=DisplayStyle.ERROR.value
    ))
    
    if details:
        yield from display_message(ctx, DisplayMessage(
            content=f"Details: {details}",
            style=DisplayStyle.ERROR_DETAIL.value
        ))
    
    return Ok(None)

def warning_message(ctx: DisplayContext, content: str) -> DisplayResult:
    return pipe(
        content,
        lambda c: DisplayMessage(content=c, style=DisplayStyle.WARNING.value),
        lambda m: display_message(ctx, m)
    )

def display_rule(ctx: DisplayContext, content: str, style: Optional[str] = None) -> DisplayResult:
    return print_rule(ctx, content, style)

def create_display_message(msg_pair: MessagePair) -> DisplayMessage:
    msg, style = msg_pair
    return DisplayMessage(content=msg, style=style)

@effect.result[None, DisplayError]()
def process_messages(ctx: DisplayContext, batch: BatchMessages) -> Generator[Any, None, Result[None, DisplayError]]:
    """Process messages with effect system"""
    validated_batch = yield from validate_batch_messages(batch)
    
    for msg_pair in validated_batch.messages:
        yield from display_message(ctx, create_display_message(msg_pair))
    
    return Ok(None)

@effect.result[None, DisplayError]()
def batch_display_messages(ctx: DisplayContext, batch: BatchMessages) -> Generator[Any, None, Result[None, DisplayError]]:
    return (yield from process_messages(ctx, batch))

def display_indented_text(ctx: DisplayContext, content: str, level: int = 1) -> DisplayResult:
    return pipe(
        content,
        lambda c: DisplayMessage(content=c, indent_level=level),
        lambda m: display_message(ctx, m)
    )
