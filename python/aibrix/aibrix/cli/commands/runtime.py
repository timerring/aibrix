"""
Runtime command for AIBrix CLI.

Integrates with the existing aibrix_runtime entry point.
"""

import argparse
import sys
import os
from aibrix.app import main as runtime_main


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the runtime command parser."""
    parser.add_argument(
        "--host",
        type=str,
        help="Host name to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port number (default: 8080)"
    )
    parser.add_argument(
        "--enable-fastapi-docs",
        action="store_true",
        default=False,
        help="Enable FastAPI's OpenAPI schema, Swagger UI, and ReDoc endpoint"
    )


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the runtime command."""
    try:
        # Set up sys.argv to match what the original runtime expects
        original_argv = sys.argv.copy()
        
        # Build new argv for the runtime
        new_argv = ["aibrix_runtime"]
        
        if args.host:
            new_argv.extend(["--host", args.host])
        
        new_argv.extend(["--port", str(args.port)])
        
        if args.enable_fastapi_docs:
            new_argv.append("--enable-fastapi-docs")
        
        # Replace sys.argv temporarily
        sys.argv = new_argv
        
        try:
            # Call the original runtime main function
            return runtime_main()
        finally:
            # Restore original argv
            sys.argv = original_argv
            
    except Exception as e:
        print(f"Error starting runtime server: {e}")
        return 1 