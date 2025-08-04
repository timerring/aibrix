"""
Tests for AIBrix CLI.

Basic tests to ensure CLI functionality works correctly.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from aibrix.cli.main import main, create_parser


def test_create_parser():
    """Test that the parser can be created without errors."""
    parser = create_parser()
    assert parser is not None
    assert hasattr(parser, 'parse_args')


def test_parser_help():
    """Test that help can be displayed."""
    parser = create_parser()
    
    # Test main help
    with patch('sys.argv', ['aibrix', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args()
        assert exc_info.value.code == 0


def test_deploy_command_help():
    """Test deploy command help."""
    parser = create_parser()
    
    with patch('sys.argv', ['aibrix', 'deploy', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args()
        assert exc_info.value.code == 0


def test_list_command_help():
    """Test list command help."""
    parser = create_parser()
    
    with patch('sys.argv', ['aibrix', 'list', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args()
        assert exc_info.value.code == 0


def test_main_no_command():
    """Test main function with no command (should show help)."""
    with patch('sys.argv', ['aibrix']):
        with patch('argparse.ArgumentParser.print_help') as mock_help:
            result = main()
            assert result == 1
            mock_help.assert_called_once()


def test_main_unknown_command():
    """Test main function with unknown command."""
    with patch('sys.argv', ['aibrix', 'unknown-command']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2


@patch('aibrix.cli.commands.deploy.handle')
def test_main_deploy_command(mock_deploy_handle):
    """Test main function with deploy command."""
    mock_deploy_handle.return_value = 0
    
    with patch('sys.argv', ['aibrix', 'deploy', '--template', 'deepseek-7b']):
        result = main()
        assert result == 0
        mock_deploy_handle.assert_called_once()


@patch('aibrix.cli.commands.list_workloads.handle')
def test_main_list_command(mock_list_handle):
    """Test main function with list command."""
    mock_list_handle.return_value = 0
    
    with patch('sys.argv', ['aibrix', 'list']):
        result = main()
        assert result == 0
        mock_list_handle.assert_called_once()


@patch('aibrix.cli.commands.runtime.handle')
def test_main_runtime_command(mock_runtime_handle):
    """Test main function with runtime command."""
    mock_runtime_handle.return_value = 0
    
    with patch('sys.argv', ['aibrix', 'runtime', '--port', '8080']):
        result = main()
        assert result == 0
        mock_runtime_handle.assert_called_once()


@patch('aibrix.cli.commands.download.handle')
def test_main_download_command(mock_download_handle):
    """Test main function with download command."""
    mock_download_handle.return_value = 0
    
    with patch('sys.argv', ['aibrix', 'download', '--model-uri', 'test-model']):
        result = main()
        assert result == 0
        mock_download_handle.assert_called_once()


@patch('aibrix.cli.commands.benchmark.handle')
def test_main_benchmark_command(mock_benchmark_handle):
    """Test main function with benchmark command."""
    mock_benchmark_handle.return_value = 0
    
    with patch('sys.argv', ['aibrix', 'benchmark', '-m', 'test-model', '-o', './results']):
        result = main()
        assert result == 0
        mock_benchmark_handle.assert_called_once()


@patch('aibrix.cli.commands.gen_profile.handle')
def test_main_gen_profile_command(mock_gen_profile_handle):
    """Test main function with gen-profile command."""
    mock_gen_profile_handle.return_value = 0
    
    with patch('sys.argv', ['aibrix', 'gen-profile', 'test-deployment', '--cost', '1.0']):
        result = main()
        assert result == 0
        mock_gen_profile_handle.assert_called_once()


def test_main_keyboard_interrupt():
    """Test main function handles keyboard interrupt gracefully."""
    with patch('sys.argv', ['aibrix', 'list']):
        with patch('aibrix.cli.commands.list_workloads.handle', side_effect=KeyboardInterrupt()):
            with patch('builtins.print') as mock_print:
                result = main()
                assert result == 130
                mock_print.assert_called_with("\nOperation cancelled by user")


def test_main_exception_handling():
    """Test main function handles exceptions gracefully."""
    with patch('sys.argv', ['aibrix', 'list']):
        with patch('aibrix.cli.commands.list_workloads.handle', side_effect=Exception("Test error")):
            with patch('builtins.print') as mock_print:
                result = main()
                assert result == 1
                mock_print.assert_called_with("Error: Test error")


if __name__ == "__main__":
    pytest.main([__file__]) 