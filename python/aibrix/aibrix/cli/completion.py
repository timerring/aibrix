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

"""Auto-completion support for AIBrix CLI."""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional


def generate_bash_completion() -> str:
    """Generate bash completion script for AIBrix CLI.
    
    Returns:
        Bash completion script as string
    """
    return '''
# AIBrix CLI bash completion

_aibrix_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    if [[ ${COMP_CWORD} == 1 ]]; then
        opts="install uninstall status deploy list delete update scale validate logs port-forward templates"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    # Command-specific completions
    case "${COMP_WORDS[1]}" in
        install)
            case "${prev}" in
                --component)
                    opts="controller gateway metadata monitoring"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    return 0
                    ;;
                --env)
                    opts="default dev prod"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    return 0
                    ;;
            esac
            opts="--version --env --component"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        deploy)
            case "${prev}" in
                --template)
                    opts="quickstart autoscaling kvcache"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                    return 0
                    ;;
                --file|-f)
                    COMPREPLY=( $(compgen -f -X '!*.yaml' -X '!*.yml' -- ${cur}) )
                    return 0
                    ;;
            esac
            opts="--file --template --params"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        list)
            if [[ ${COMP_CWORD} == 2 ]]; then
                opts="deployments services custom all"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                return 0
            fi
            opts="--selector"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        scale)
            opts="--workload --replicas"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        logs)
            opts="--workload --container --tail --follow --previous"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        port-forward)
            opts="--service --port"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        templates)
            if [[ ${COMP_CWORD} == 2 ]]; then
                opts="list info generate"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                return 0
            fi
            case "${COMP_WORDS[2]}" in
                info|generate)
                    if [[ ${COMP_CWORD} == 3 ]]; then
                        opts="quickstart autoscaling kvcache"
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                        return 0
                    fi
                    ;;
            esac
            ;;
        validate)
            case "${prev}" in
                --file|-f)
                    COMPREPLY=( $(compgen -f -X '!*.yaml' -X '!*.yml' -- ${cur}) )
                    return 0
                    ;;
            esac
            opts="--file"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
    esac

    # Global options
    global_opts="--kubeconfig --namespace --verbose --help"
    COMPREPLY=( $(compgen -W "${global_opts}" -- ${cur}) )
}

complete -F _aibrix_completion aibrix
'''


def generate_zsh_completion() -> str:
    """Generate zsh completion script for AIBrix CLI.
    
    Returns:
        Zsh completion script as string
    """
    return '''
#compdef aibrix

# AIBrix CLI zsh completion

_aibrix() {
    local context curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -C \
        '(-h --help)'{-h,--help}'[show help message]' \
        '(-v --verbose)'{-v,--verbose}'[enable verbose output]' \
        '(-n --namespace)'{-n,--namespace}'[kubernetes namespace]:namespace:' \
        '--kubeconfig[path to kubeconfig file]:file:_files' \
        '1: :_aibrix_commands' \
        '*:: :->args'

    case $state in
        args)
            case $words[1] in
                install)
                    _arguments \
                        '--version[aibrix version]:version:' \
                        '--env[target environment]:env:(default dev prod)' \
                        '--component[specific component]:component:(controller gateway metadata monitoring)'
                    ;;
                deploy)
                    _arguments \
                        '(-f --file)'{-f,--file}'[yaml manifest file]:file:_files -g "*.yaml *.yml"' \
                        '--template[template name]:template:(quickstart autoscaling kvcache)' \
                        '--params[template parameters]:params:'
                    ;;
                list)
                    _arguments \
                        '1:type:(deployments services custom all)' \
                        '(-l --selector)'{-l,--selector}'[label selector]:selector:'
                    ;;
                scale)
                    _arguments \
                        '--workload[workload name]:workload:' \
                        '--replicas[number of replicas]:replicas:'
                    ;;
                logs)
                    _arguments \
                        '--workload[workload name]:workload:' \
                        '(-c --container)'{-c,--container}'[container name]:container:' \
                        '--tail[number of lines]:lines:' \
                        '(-f --follow)'{-f,--follow}'[follow logs]' \
                        '(-p --previous)'{-p,--previous}'[previous container]'
                    ;;
                port-forward)
                    _arguments \
                        '--service[service name]:service:' \
                        '--port[port specification]:port:'
                    ;;
                templates)
                    _arguments \
                        '1:subcommand:(list info generate)' \
                        '*:: :->template_args'
                    case $state in
                        template_args)
                            case $words[1] in
                                info|generate)
                                    _arguments \
                                        '1:template:(quickstart autoscaling kvcache)'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
                validate)
                    _arguments \
                        '(-f --file)'{-f,--file}'[yaml manifest file]:file:_files -g "*.yaml *.yml"'
                    ;;
            esac
            ;;
    esac
}

_aibrix_commands() {
    local commands; commands=(
        'install:Install AIBrix components'
        'uninstall:Uninstall AIBrix components'
        'status:Show installation status'
        'deploy:Deploy workloads'
        'list:List workloads'
        'delete:Delete workloads'
        'update:Update workloads'
        'scale:Scale workloads'
        'validate:Validate manifests'
        'logs:Show workload logs'
        'port-forward:Forward local port to service'
        'templates:Manage templates'
    )
    _describe 'commands' commands
}

_aibrix "$@"
'''


def install_completion(shell: str = "bash") -> bool:
    """Install completion script for the specified shell.
    
    Args:
        shell: Shell type (bash or zsh)
        
    Returns:
        True if installation succeeded
    """
    try:
        if shell == "bash":
            script = generate_bash_completion()
            completion_dir = Path.home() / ".bash_completion.d"
            completion_file = completion_dir / "aibrix"
        elif shell == "zsh":
            script = generate_zsh_completion()
            completion_dir = Path.home() / ".zsh" / "completions"
            completion_file = completion_dir / "_aibrix"
        else:
            print(f"Unsupported shell: {shell}")
            return False
        
        # Create completion directory if it doesn't exist
        completion_dir.mkdir(parents=True, exist_ok=True)
        
        # Write completion script
        with open(completion_file, 'w') as f:
            f.write(script)
        
        print(f"Completion script installed: {completion_file}")
        
        if shell == "bash":
            print("To enable completion, add this to your ~/.bashrc:")
            print(f"source {completion_file}")
        elif shell == "zsh":
            print("To enable completion, add this to your ~/.zshrc:")
            print(f"fpath=(~/.zsh/completions $fpath)")
            print("autoload -U compinit && compinit")
        
        return True
        
    except Exception as e:
        print(f"Failed to install completion: {e}")
        return False


def handle_completion_command(args: argparse.Namespace) -> int:
    """Handle completion command."""
    if args.install:
        success = install_completion(args.shell)
        return 0 if success else 1
    elif args.generate:
        if args.shell == "bash":
            print(generate_bash_completion())
        elif args.shell == "zsh":
            print(generate_zsh_completion())
        else:
            print(f"Unsupported shell: {args.shell}", file=sys.stderr)
            return 1
        return 0
    else:
        print("Use --install or --generate", file=sys.stderr)
        return 1


def add_completion_parser(subparsers) -> None:
    """Add completion command to parser."""
    completion_parser = subparsers.add_parser(
        "completion",
        help="Generate shell completion scripts",
        description="Generate and install shell completion scripts for AIBrix CLI"
    )
    
    completion_parser.add_argument(
        "--shell",
        choices=["bash", "zsh"],
        default="bash",
        help="Shell type (default: bash)"
    )
    
    action_group = completion_parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--install",
        action="store_true",
        help="Install completion script"
    )
    action_group.add_argument(
        "--generate",
        action="store_true",
        help="Generate completion script to stdout"
    )
    
    completion_parser.set_defaults(func=handle_completion_command)
