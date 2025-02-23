from expression import Ok, Error, Result, pipe
from rich.console import Console
from rich.rule import Rule
from dataclasses import dataclass
from typing import Optional, Tuple, List
from enum import Enum
from functools import reduce

# Immutable data structures
@dataclass(frozen=True)
class DisplayMessage:
    content: str
    style: Optional[str] = None
    indent_level: int = 0

@dataclass(frozen=True)
class BatchMessages:
    messages: list[tuple[str, str]]

class DisplayStyle(Enum):
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    ERROR_DETAIL = "red dim"

def validate_message_pair(msg_pair: Tuple[str, str]) -> Result[Tuple[str, str], str]:
    msg, style = msg_pair
    if not msg or not style:
        return Error("Message and style cannot be empty")
    return Ok((msg, style))

# Pure validation functions
def validate_message(message: DisplayMessage) -> Result[DisplayMessage, str]:
    if not message.content.strip():
        return Error("Message content cannot be empty")
    return Ok(message)

def validate_batch_messages(batch: BatchMessages) -> Result[BatchMessages, str]:
    if not batch.messages:
        return Error("Batch messages cannot be empty")
    
    def combine_results(acc: Result[List[Tuple[str, str]], str], curr: Result[Tuple[str, str], str]) -> Result[List[Tuple[str, str]], str]:
        if acc.is_error():
            return acc
        if curr.is_error():
            return curr
        return Ok([*acc.ok, curr.ok])
    
    validation_results = map(validate_message_pair, batch.messages)
    combined_result = reduce(combine_results, validation_results, Ok([]))
    
    return combined_result.map(lambda msgs: BatchMessages(messages=msgs))

# Pure console I/O functions
def print_styled(console: Console, message: DisplayMessage) -> Result[None, str]:
    """Pure function to print styled message to console."""
    try:
        indent = "  " * message.indent_level
        if message.style:
            console.print(f"{indent}[{message.style}]{message.content}[/{message.style}]")
        else:
            console.print(f"{indent}{message.content}")
        return Ok(None)
    except Exception as e:
        return Error(str(e))

def print_rule(console: Console, message: str, style: Optional[str] = None) -> Result[None, str]:
    """Pure function to print a rule to console."""
    try:
        rule = Rule(message, style=style)
        console.print(rule)
        return Ok(None)
    except Exception as e:
        return Error(str(e))

# Initialize console singleton
console = Console()

def handle_display(validated: DisplayMessage) -> Result[None, str]:
    result = print_styled(console, validated)
    if result.is_error():
        return Error(f"Failed to display message: {result.error}")
    return Ok(None)

def display_message(message: DisplayMessage) -> Result[None, str]:
    return pipe(
        message,
        validate_message,
        handle_display
    )

def success_message(content: str) -> Result[None, str]:
    return pipe(
        content,
        lambda c: DisplayMessage(content=c, style=DisplayStyle.SUCCESS.value),
        display_message
    )

def error_message(content: str, details: Optional[str] = None) -> Result[None, str]:
    def display_details(result: Result[None, str]) -> Result[None, str]:
        if details and result.is_ok():
            details_msg = DisplayMessage(
                content=f"Details: {details}",
                style=DisplayStyle.ERROR_DETAIL.value
            )
            return display_message(details_msg)
        return result

    return pipe(
        content,
        lambda c: DisplayMessage(content=c, style=DisplayStyle.ERROR.value),
        display_message,
        display_details
    )

def warning_message(content: str) -> Result[None, str]:
    return pipe(
        content,
        lambda c: DisplayMessage(content=c, style=DisplayStyle.WARNING.value),
        display_message
    )

def display_rule(content: str, style: Optional[str] = None) -> Result[None, str]:
    result = print_rule(console, content, style)
    if result.is_error():
        return Error(f"Failed to display rule: {result.error}")
    return Ok(None)

def create_display_message(msg_pair: Tuple[str, str]) -> DisplayMessage:
    msg, style = msg_pair
    return DisplayMessage(content=msg, style=style)

def process_messages(validated_batch: Result[BatchMessages, str]) -> Result[None, str]:
    def combine_display_results(acc: Result[None, str], msg: DisplayMessage) -> Result[None, str]:
        if acc.is_error():
            return acc
        return display_message(msg)
    
    if validated_batch.is_error():
        return validated_batch
        
    batch = validated_batch.ok
    messages = map(create_display_message, batch.messages)
    return reduce(combine_display_results, messages, Ok(None))

def batch_display_messages(batch: BatchMessages) -> Result[None, str]:
    return pipe(
        batch,
        validate_batch_messages,
        process_messages
    )

def display_indented_text(content: str, level: int = 1) -> Result[None, str]:
    return pipe(
        content,
        lambda c: DisplayMessage(content=c, indent_level=level),
        display_message
    )
