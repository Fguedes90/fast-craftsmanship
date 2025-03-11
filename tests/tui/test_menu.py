"""Tests for the menu module."""
from unittest.mock import patch, MagicMock, call
import os
import pytest
import subprocess
from typing import Dict, List

from expression import Error, Ok, effect

from fcship.tui.menu import (
    clear_screen,
    display_title,
    display_categories,
    display_commands,
    display_command_options,
    run_command,
    run_tui
)


class TestMenuFunctions:
    @patch('os.system')
    def test_clear_screen(self, mock_system):
        # Test for both Windows and Unix-like systems
        with patch('os.name', 'nt'):
            clear_screen()
            mock_system.assert_called_with('cls')
        
        with patch('os.name', 'posix'):
            clear_screen()
            mock_system.assert_called_with('clear')

    @patch('fcship.tui.menu.console')
    def test_display_title(self, mock_console):
        display_title()
        # Check that console.print was called twice
        assert mock_console.print.call_count == 2
        # The first call should have a Panel argument
        assert 'Panel' in str(mock_console.print.call_args_list[0])

    @patch('fcship.tui.menu.console')
    @patch('fcship.tui.menu.clear_screen')
    @patch('fcship.tui.menu.display_title')
    @patch('fcship.tui.menu.COMMAND_CATEGORIES', {'category1': 'Category 1', 'category2': 'Category 2'})
    @patch('fcship.tui.menu.COMMANDS_BY_CATEGORY', {
        'category1': {'cmd1': (None, 'Command 1')},
        'category2': {'cmd2': (None, 'Command 2')}
    })
    def test_display_categories(self, mock_display_title, mock_clear_screen, mock_console):
        result = display_categories()
        
        # Verify function calls
        mock_clear_screen.assert_called_once()
        mock_display_title.assert_called_once()
        assert mock_console.print.call_count >= 4
        
        # Verify the result
        assert result == ['category1', 'category2']

    @patch('fcship.tui.menu.console')
    @patch('fcship.tui.menu.clear_screen')
    @patch('fcship.tui.menu.display_title')
    @patch('fcship.tui.menu.COMMAND_CATEGORIES', {'category1': 'Category 1'})
    @patch('fcship.tui.menu.COMMANDS_BY_CATEGORY', {
        'category1': {'cmd1': (None, 'Command 1'), 'cmd2': (None, 'Command 2')}
    })
    def test_display_commands(self, mock_display_title, mock_clear_screen, mock_console):
        result = display_commands('category1')
        
        # Verify function calls
        mock_clear_screen.assert_called_once()
        mock_display_title.assert_called_once()
        assert mock_console.print.call_count >= 4
        
        # Verify the result
        assert 'cmd1' in result
        assert 'cmd2' in result

    @patch('fcship.tui.menu.console')
    @patch('fcship.tui.menu.clear_screen')
    @patch('fcship.tui.menu.display_title')
    @patch('fcship.tui.menu.COMMANDS_BY_CATEGORY', {})
    def test_display_commands_no_commands(self, mock_display_title, mock_clear_screen, mock_console):
        result = display_commands('unknown_category')
        
        # Verify function calls
        mock_clear_screen.assert_called_once()
        mock_display_title.assert_called_once()
        
        # Verify the result
        assert result is None

    @patch('fcship.tui.menu.console')
    @patch('fcship.tui.menu.clear_screen')
    @patch('fcship.tui.menu.display_title')
    @patch('fcship.tui.menu.COMMANDS_BY_CATEGORY', {
        'category1': {'cmd1': (None, 'Command 1')}
    })
    def test_display_command_options(self, mock_display_title, mock_clear_screen, mock_console):
        display_command_options('category1', 'cmd1')
        
        # Verify function calls
        mock_clear_screen.assert_called_once()
        mock_display_title.assert_called_once()
        assert mock_console.print.call_count >= 4

    @patch('subprocess.Popen')
    @patch('fcship.tui.menu.console')
    @patch('fcship.tui.menu.clear_screen')
    @patch('builtins.input')
    def test_run_command_success(self, mock_input, mock_clear_screen, mock_console, mock_popen):
        # Configure mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Run function
        run_command('test_command')
        
        # Verify function calls
        mock_clear_screen.assert_called_once()
        mock_popen.assert_called_with(['python', '-m', 'fcship.cli', 'test_command'])
        mock_process.wait.assert_called_once()
        mock_input.assert_called_once()
        
        # Verify success message was printed
        success_call = False
        for call_args in mock_console.print.call_args_list:
            if 'green' in str(call_args) and 'success' in str(call_args).lower():
                success_call = True
                break
        assert success_call

    @patch('subprocess.Popen')
    @patch('fcship.tui.menu.console')
    @patch('fcship.tui.menu.clear_screen')
    @patch('builtins.input')
    def test_run_command_failure(self, mock_input, mock_clear_screen, mock_console, mock_popen):
        # Configure mock
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        # Run function
        run_command('test_command')
        
        # Verify error message was printed
        error_call = False
        for call_args in mock_console.print.call_args_list:
            if 'red' in str(call_args) and 'failed' in str(call_args).lower():
                error_call = True
                break
        assert error_call

    @patch('subprocess.Popen')
    @patch('fcship.tui.menu.console')
    @patch('fcship.tui.menu.clear_screen')
    @patch('builtins.input')
    def test_run_command_exception(self, mock_input, mock_clear_screen, mock_console, mock_popen):
        # Configure mock to raise an exception
        mock_popen.side_effect = Exception("Command error")
        
        # Run function
        run_command('test_command')
        
        # Verify error message was printed
        error_call = False
        for call_args in mock_console.print.call_args_list:
            if 'red' in str(call_args) and 'error' in str(call_args).lower():
                error_call = True
                break
        assert error_call

    @patch('fcship.tui.menu.display_categories')
    @patch('fcship.tui.menu.Prompt.ask')
    def test_run_tui_quit_from_main_menu(self, mock_ask, mock_display_categories):
        # Configure mocks
        mock_display_categories.return_value = ['category1', 'category2']
        mock_ask.return_value = 'q'
        
        # Run function
        run_tui()
        
        # Verify function calls
        mock_display_categories.assert_called_once()
        mock_ask.assert_called_once()

    @patch('fcship.tui.menu.display_categories')
    @patch('fcship.tui.menu.display_commands')
    @patch('fcship.tui.menu.Prompt.ask')
    @patch('builtins.input')
    def test_run_tui_category_no_commands(self, mock_input, mock_ask, mock_display_commands, mock_display_categories):
        # Configure mocks
        mock_display_categories.return_value = ['category1']
        mock_ask.side_effect = ['1', 'q']  # Select category 1, then quit
        mock_display_commands.return_value = None  # No commands in the category
        mock_input.return_value = "" # Mock pressing Enter
        
        # Run function
        run_tui()
        
        # Verify function calls
        assert mock_display_categories.call_count >= 1
        mock_display_commands.assert_called_once_with('category1')

    @patch('fcship.tui.menu.display_categories')
    @patch('fcship.tui.menu.display_commands')
    @patch('fcship.tui.menu.display_command_options')
    @patch('fcship.tui.menu.run_command')
    @patch('fcship.tui.menu.Prompt.ask')
    @patch('builtins.input')
    def test_run_tui_run_command(self, mock_input, mock_ask, mock_run_command, 
                                mock_display_command_options, mock_display_commands, 
                                mock_display_categories):
        # Configure mocks
        mock_display_categories.return_value = ['category1']
        mock_display_commands.return_value = {'cmd1': (None, 'Command 1')}
        
        # Simulate: select category 1, select command 1, select option 1 (run), then back to main menu, then quit
        mock_ask.side_effect = ['1', '1', '1', 'b', 'q']
        
        # Run function
        run_tui()
        
        # Verify function calls
        mock_display_categories.assert_called()
        mock_display_commands.assert_called_with('category1')
        mock_display_command_options.assert_called_with('category1', 'cmd1')
        mock_run_command.assert_called_with('cmd1', show_help=False)

    @patch('fcship.tui.menu.display_categories')
    @patch('fcship.tui.menu.display_commands')
    @patch('fcship.tui.menu.display_command_options')
    @patch('fcship.tui.menu.run_command')
    @patch('fcship.tui.menu.Prompt.ask')
    def test_run_tui_show_help(self, mock_ask, mock_run_command, 
                              mock_display_command_options, mock_display_commands, 
                              mock_display_categories):
        # Configure mocks
        mock_display_categories.return_value = ['category1']
        mock_display_commands.return_value = {'cmd1': (None, 'Command 1')}
        
        # Simulate: select category 1, select command 1, select option 2 (help), then back to categories, then quit
        mock_ask.side_effect = ['1', '1', '2', 'b', 'q']
        
        # Run function
        run_tui()
        
        # Verify function calls
        mock_run_command.assert_called_with('cmd1', show_help=True)

    @patch('fcship.tui.menu.display_categories')
    @patch('fcship.tui.menu.console')
    def test_run_tui_keyboard_interrupt(self, mock_console, mock_display_categories):
        # Configure mock to raise KeyboardInterrupt
        mock_display_categories.side_effect = KeyboardInterrupt()
        
        # Run function
        run_tui()
        
        # Verify the exit message was printed
        interrupted_msg_printed = False
        for call_args in mock_console.print.call_args_list:
            if 'interrupted' in str(call_args).lower():
                interrupted_msg_printed = True
                break
        assert interrupted_msg_printed

    @patch('fcship.tui.menu.display_categories')
    @patch('fcship.tui.menu.Prompt.ask')
    @patch('fcship.tui.menu.console')
    def test_run_tui_invalid_category(self, mock_console, mock_ask, mock_display_categories):
        # Configure mocks
        mock_display_categories.return_value = ['category1']
        # First invalid choice, then quit
        mock_ask.side_effect = ['99', 'q']
        
        # Run function
        run_tui()
        
        # Verify error message was printed
        error_call = False
        for call_args in mock_console.print.call_args_list:
            if 'invalid' in str(call_args).lower():
                error_call = True
                break
        assert error_call