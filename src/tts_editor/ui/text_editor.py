"""
Text editor component for the Warhammer 40k TTS Unit Editor.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class TextEditor(ttk.Frame):
    """Text editor component for editing unit descriptions."""
    
    def __init__(self, parent, on_text_change: Optional[Callable] = None):
        """
        Initialize the text editor.
        
        Args:
            parent: The parent widget
            on_text_change: Optional callback for text change events
        """
        super().__init__(parent)
        self.on_text_change = on_text_change
        self.create_widgets()
    
    def create_widgets(self):
        """Create the text editor widgets."""
        # Description text area with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.description_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.description_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.description_text.yview)
        
        # Bind text change event
        if self.on_text_change:
            self.description_text.bind("<<Modified>>", self._on_text_modified)
    
    def _on_text_modified(self, event):
        """Handle text modified event."""
        if self.description_text.edit_modified():
            if self.on_text_change:
                self.on_text_change()
            self.description_text.edit_modified(False)
    
    def get_text(self) -> str:
        """
        Get the current text content.
        
        Returns:
            The text content
        """
        return self.description_text.get(1.0, tk.END).strip()
    
    def set_text(self, text: str):
        """
        Set the text content.
        
        Args:
            text: The text to set
        """
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, text)
    
    def insert_at_cursor(self, text: str):
        """
        Insert text at the current cursor position.
        
        Args:
            text: The text to insert
        """
        self.description_text.insert(tk.INSERT, text)
    
    def insert_template(self, template_type: str):
        """
        Insert a template at the current cursor position.
        
        Args:
            template_type: The type of template to insert ("stats", "ranged", "melee", "abilities")
        """
        if template_type == "stats":
            template = "[56f442] M    T   Sv    W    Ld   OC  [-]\n"
            template += "X\"   X   X+   X    X+   X   [-][-]\n\n"
        elif template_type == "ranged":
            template = "[e85545]Ranged weapons[-]\n"
            template += "[c6c930]Weapon Name (Ranged Weapons)[-]\n"
            template += "X\" A:X BS:X+ S:X AP:-X D:X [7bc596][Abilities][-] \n\n"
        elif template_type == "melee":
            template = "[e85545]Melee weapons[-]\n"
            template += "[c6c930]Weapon Name (Melee Weapons)[-]\n"
            template += "A:X WS:X+ S:X AP:X D:X [7bc596][Abilities][-] \n\n"
        elif template_type == "abilities":
            template = "[dc61ed]Abilities[-]\n"
            template += "Ability Name 1\n"
            template += "Ability Name 2\n"
            template += "Ability Name 3\n"
        else:
            return
        
        self.insert_at_cursor(template)
