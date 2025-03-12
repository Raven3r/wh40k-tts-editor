"""
Application module for the Warhammer 40k TTS Unit Editor.
"""
import tkinter as tk
import os
import json
from typing import Optional

from .ui.main_window import MainWindow


class Application:
    """Main application class for the Warhammer 40k TTS Unit Editor."""
    
    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root)
        
        # Try to load the default file if specified
        self.default_file = os.environ.get("TTS_EDITOR_DEFAULT_FILE")
        if self.default_file and os.path.exists(self.default_file):
            self.load_file(self.default_file)
    
    def load_file(self, file_path: str) -> bool:
        """
        Load a TTS JSON file.
        
        Args:
            file_path: The path to the file to load
            
        Returns:
            True if the file was loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = file.read()
                
            # Parse JSON
            json_data = json.loads(json_data)
            
            # Load the data into the unit manager
            self.main_window.unit_manager.load_json(json_data)
            
            # Update the UI
            self.main_window.load_units()
            self.main_window.root.title(f"Warhammer 40k TTS Unit Editor - {os.path.basename(file_path)}")
            
            return True
            
        except Exception as e:
            print(f"Failed to load file: {str(e)}")
            return False
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def run_app():
    """Run the application."""
    app = Application()
    app.run()


if __name__ == "__main__":
    run_app()
