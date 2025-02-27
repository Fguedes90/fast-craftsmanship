"""Tests for the CLI module."""

from unittest.mock import patch, MagicMock, call
import os
import pytest
import typer
from typer.testing import CliRunner

from expression import Error, Ok, effect
from fcship.cli import (
    app,
    version_callback,
    show_categories_callback,
    tui_callback
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