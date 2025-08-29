# Copyright 2024 The Aibrix Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for AIBrix CLI main module."""

import pytest
from unittest.mock import Mock, patch
from aibrix.cli.main import create_parser, main


class TestCLIParser:
    """Test CLI argument parser."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser.prog == "aibrix"
        
    def test_help_output(self):
        """Test help output."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])
    
    def test_version_output(self):
        """Test version output."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])
    
    def test_global_arguments(self):
        """Test global arguments parsing."""
        parser = create_parser()
        args = parser.parse_args([
            "--kubeconfig", "/path/to/config",
            "--namespace", "test-ns",
            "--verbose",
            "status"
        ])
        
        assert args.kubeconfig == "/path/to/config"
        assert args.namespace == "test-ns"
        assert args.verbose is True
        assert args.command == "status"
    
    def test_install_command(self):
        """Test install command parsing."""
        parser = create_parser()
        args = parser.parse_args([
            "install",
            "--version", "v0.3.0",
            "--env", "dev",
            "--component", "controller"
        ])
        
        assert args.command == "install"
        assert args.version == "v0.3.0"
        assert args.env == "dev"
        assert args.component == "controller"
    
    def test_deploy_command_with_file(self):
        """Test deploy command with file."""
        parser = create_parser()
        args = parser.parse_args([
            "deploy",
            "--file", "deployment.yaml"
        ])
        
        assert args.command == "deploy"
        assert args.file == "deployment.yaml"
        assert args.template is None
    
    def test_deploy_command_with_template(self):
        """Test deploy command with template."""
        parser = create_parser()
        args = parser.parse_args([
            "deploy",
            "--template", "quickstart",
            "--params", "model_name=test", "replicas=2"
        ])
        
        assert args.command == "deploy"
        assert args.template == "quickstart"
        assert args.params == ["model_name=test", "replicas=2"]
    
    def test_scale_command(self):
        """Test scale command parsing."""
        parser = create_parser()
        args = parser.parse_args([
            "scale",
            "--workload", "my-model",
            "--replicas", "5"
        ])
        
        assert args.command == "scale"
        assert args.workload == "my-model"
        assert args.replicas == 5
    
    def test_logs_command(self):
        """Test logs command parsing."""
        parser = create_parser()
        args = parser.parse_args([
            "logs",
            "--workload", "my-model",
            "--tail", "100",
            "--follow"
        ])
        
        assert args.command == "logs"
        assert args.workload == "my-model"
        assert args.tail == 100
        assert args.follow is True


class TestCLIMain:
    """Test CLI main function."""
    
    def test_main_no_command(self):
        """Test main with no command shows help."""
        with patch('aibrix.cli.main.create_parser') as mock_parser:
            mock_parser_instance = Mock()
            mock_parser.return_value = mock_parser_instance
            mock_parser_instance.parse_args.return_value = Mock(command=None)
            
            result = main([])
            
            assert result == 1
            mock_parser_instance.print_help.assert_called_once()
    
    def test_main_with_command_handler(self):
        """Test main with command that has handler."""
        mock_handler = Mock(return_value=0)
        
        with patch('aibrix.cli.main.create_parser') as mock_parser:
            mock_parser_instance = Mock()
            mock_parser.return_value = mock_parser_instance
            mock_args = Mock(command="test", func=mock_handler, verbose=False)
            mock_parser_instance.parse_args.return_value = mock_args
            
            result = main(["test"])
            
            assert result == 0
            mock_handler.assert_called_once_with(mock_args)
    
    def test_main_keyboard_interrupt(self):
        """Test main handles keyboard interrupt."""
        mock_handler = Mock(side_effect=KeyboardInterrupt())
        
        with patch('aibrix.cli.main.create_parser') as mock_parser:
            mock_parser_instance = Mock()
            mock_parser.return_value = mock_parser_instance
            mock_args = Mock(command="test", func=mock_handler, verbose=False)
            mock_parser_instance.parse_args.return_value = mock_args
            
            result = main(["test"])
            
            assert result == 130
    
    def test_main_exception_handling(self):
        """Test main handles exceptions."""
        mock_handler = Mock(side_effect=Exception("Test error"))
        
        with patch('aibrix.cli.main.create_parser') as mock_parser:
            mock_parser_instance = Mock()
            mock_parser.return_value = mock_parser_instance
            mock_args = Mock(command="test", func=mock_handler, verbose=False)
            mock_parser_instance.parse_args.return_value = mock_args
            
            result = main(["test"])
            
            assert result == 1
    
    def test_main_verbose_mode(self):
        """Test main with verbose mode."""
        mock_handler = Mock(side_effect=Exception("Test error"))
        
        with patch('aibrix.cli.main.create_parser') as mock_parser, \
             patch('logging.getLogger') as mock_logger, \
             patch('traceback.print_exc') as mock_traceback:
            
            mock_parser_instance = Mock()
            mock_parser.return_value = mock_parser_instance
            mock_args = Mock(command="test", func=mock_handler, verbose=True)
            mock_parser_instance.parse_args.return_value = mock_args
            
            result = main(["test"])
            
            assert result == 1
            mock_traceback.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
