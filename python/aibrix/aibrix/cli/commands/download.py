"""
Download command for AIBrix CLI.

Integrates with the existing aibrix_download entry point.
"""

import argparse
import sys
import json
from aibrix.downloader import download_model


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the download command parser."""
    parser.add_argument(
        "--model-uri",
        type=str,
        default="deepseek-ai/deepseek-coder-6.7b-instruct",
        required=True,
        help="Model URI from different source, support HuggingFace, AWS S3, TOS"
    )
    parser.add_argument(
        "--local-dir",
        type=str,
        help="Base dir of the model file. If not set, it will used with env `DOWNLOADER_LOCAL_DIR`"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        help="Subdir of the base dir to save model files"
    )
    parser.add_argument(
        "--enable-progress-bar",
        action="store_true",
        default=False,
        help="Enable download progress bar during downloading from TOS or S3"
    )
    parser.add_argument(
        "--download-extra-config",
        type=str,
        help="Extra config for download, like auth config, parallel config, etc. (JSON string)"
    )


def str_to_dict(s: str):
    """Convert JSON string to dictionary."""
    if s is None:
        return None
    try:
        return json.loads(s)
    except Exception as e:
        raise ValueError(f"Invalid json string {s}") from e


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the download command."""
    try:
        # Parse extra config if provided
        extra_config = None
        if args.download_extra_config:
            extra_config = str_to_dict(args.download_extra_config)
        
        # Call the download function
        download_model(
            args.model_uri,
            args.local_dir,
            args.model_name,
            extra_config,
            args.enable_progress_bar,
        )
        
        return 0
        
    except Exception as e:
        print(f"Error downloading model: {e}")
        return 1 