"""Tests for the CLI module."""

from unittest.mock import patch, MagicMock, call
import os
import pytest
import typer
from typer.testing import CliRunner
import click

from expression import Error, Ok, effect
from fcship.cli import (
    app,
    version_callback,
    show_categories_callback,
    tui_callback,
    COMMANDS_BY_CATEGORY
)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


class TestCallbacks:
    @patch('fcship.cli.console')
    def test_version_callback(self, mock_console):
        # Test that version callback prints version and exits
        with pytest.raises(typer.Exit):
            version_callback(True)
        
        # Verify console.print was called with version info
        assert mock_console.print.call_count == 1
        assert 'version' in str(mock_console.print.call_args[0][0])
    
    def test_version_callback_no_action(self):
        # Test that nothing happens when value is False
        result = version_callback(False)
        assert result is None

    @patch('fcship.cli.console')
    def test_show_categories_callback(self, mock_console):
        # Test that show_categories_callback prints categories and exits
        with pytest.raises(typer.Exit):
            show_categories_callback(True)
        
        # Verify console.print was called with a table
        assert mock_console.print.call_count >= 1
        
    def test_show_categories_callback_no_action(self):
        # Test that nothing happens when value is False
        result = show_categories_callback(False)
        assert result is None

    @patch('fcship.tui.menu.run_tui')
    def test_tui_callback(self, mock_run_tui):
        # Test that tui_callback calls run_tui and exits
        with pytest.raises(typer.Exit):
            tui_callback(True)
        
        # Verify run_tui was called
        mock_run_tui.assert_called_once()
        
    def test_tui_callback_no_action(self):
        # Test that nothing happens when value is False
        result = tui_callback(False)
        assert result is None


class TestCLIUtils:
    @patch('fcship.cli.console')
    def test_handle_result_success_string(self, mock_console):
        from fcship.cli import handle_result
        result = Ok("Success message")
        handle_result(result)
        mock_console.print.assert_called_once()
        assert "Success message" in str(mock_console.print.call_args[0][0])
    
    @patch('fcship.cli.console')
    def test_handle_result_error(self, mock_console):
        from fcship.cli import handle_result
        result = Error("Error message")
        with pytest.raises(typer.Exit):
            handle_result(result)
        mock_console.print.assert_called_once()
        assert "Error message" in str(mock_console.print.call_args[0][0])
    
    def test_wrap_command_success(self):
        from fcship.cli import wrap_command
        
        def test_func():
            return Ok("Success")
        
        wrapped = wrap_command(test_func)
        result = wrapped()
        assert result.is_ok()
        assert result.ok == "Success"

    @patch('fcship.cli.console')
    def test_wrap_command_exception(self, mock_console):
        from fcship.cli import wrap_command
        
        def test_func():
            raise ValueError("Test error")
        
        wrapped = wrap_command(test_func)
        with pytest.raises(typer.Exit):
            wrapped()
        mock_console.print.assert_called_once()
        assert "Test error" in str(mock_console.print.call_args[0][0])


class TestCommandHelp:
    """Test that command help text and arguments are properly displayed."""
    
    def test_main_help_contains_categories(self):
        """Test that main help text contains all command categories."""
        for category, desc in COMMAND_CATEGORIES.items():
            cmd = app.registered_commands[0]  # Main command group
            help_text = cmd.help
            assert category in help_text or desc in help_text
            
    def test_command_help_texts(self):
        """Test that command help texts are properly registered."""
        for category, commands in COMMANDS_BY_CATEGORY.items():
            for cmd_name, (_, help_text) in commands.items():
                # Find the command in the app's command tree
                cmd_group = next((c for c in app.registered_commands if c.name == category), None)
                if cmd_group:
                    cmd = next((c for c in cmd_group.commands.values() if c.name == cmd_name), None)
                    if cmd and help_text:
                        assert help_text in cmd.help

    def test_common_options(self):
        """Test that common options are available on the main command."""
        cmd = app.registered_commands[0]  # Main command group
        option_names = {p.name for p in cmd.params}
        assert "version" in option_names
        assert "categories" in option_names
        assert "tui" in option_names

    def test_option_defaults(self):
        """Test that options have correct default values."""
        cmd = app.registered_commands[0]  # Main command group
        version_opt = next(p for p in cmd.params if p.name == "version")
        assert version_opt.default is None
        assert version_opt.is_flag
        assert version_opt.help