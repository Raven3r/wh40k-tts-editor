#!/usr/bin/env python
"""
Launcher script for the Warhammer 40k TTS Unit Editor.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from tts_editor.main import main

if __name__ == "__main__":
    sys.exit(main())
