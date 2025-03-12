#!/usr/bin/env python
"""
Main entry point for the Warhammer 40k TTS Unit Editor.
"""
import sys
import os
import argparse

from .app import Application


def main():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="Warhammer 40k TTS Unit Editor")
    parser.add_argument("file", nargs="?", help="TTS JSON file to open")
    args = parser.parse_args()
    
    # Set the default file environment variable if specified
    if args.file:
        os.environ["TTS_EDITOR_DEFAULT_FILE"] = args.file
    
    # Create and run the application
    app = Application()
    app.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
