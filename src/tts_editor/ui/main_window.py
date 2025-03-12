"""
Main window component for the Warhammer 40k TTS Unit Editor.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re
from typing import Optional, Dict, Any

from ..models.unit import UnitManager
from .text_editor import TextEditor
from .structured_editor import StructuredEditor


class MainWindow:
    """Main window for the Warhammer 40k TTS Unit Editor."""
    
    # Common color codes used in TTS descriptions
    COMMON_COLORS = [
        {"code": "00ff16", "name": "Green", "display": "#00ff16"},
        {"code": "e85545", "name": "Red", "display": "#e85545"},
        {"code": "c6c930", "name": "Yellow", "display": "#c6c930"},
        {"code": "7bc596", "name": "Light Green", "display": "#7bc596"},
        {"code": "dc61ed", "name": "Purple", "display": "#dc61ed"},
        {"code": "56f442", "name": "Bright Green", "display": "#56f442"}
    ]
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("Warhammer 40k TTS Unit Editor")
        self.root.geometry("900x700")
        
        self.unit_manager = UnitManager()
        self.current_unit_index = None
        self.current_profile_index = None
        self.current_file_path = None
        
        self.create_menu()
        self.create_ui()
    
    def create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save as...", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)
    
    def create_ui(self):
        """Create the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Unit list and profiles
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Units list
        units_frame = ttk.LabelFrame(left_frame, text="Units", padding="5")
        units_frame.pack(fill=tk.BOTH, expand=True)
        
        self.unit_listbox = tk.Listbox(units_frame, width=30, height=10)
        self.unit_listbox.pack(fill=tk.BOTH, expand=True)
        self.unit_listbox.bind('<<ListboxSelect>>', self.on_unit_select)
        
        # Profiles list
        profiles_frame = ttk.LabelFrame(left_frame, text="Profiles", padding="5")
        profiles_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.profile_listbox = tk.Listbox(profiles_frame, width=30, height=10)
        self.profile_listbox.pack(fill=tk.BOTH, expand=True)
        self.profile_listbox.bind('<<ListboxSelect>>', self.on_profile_select)
        
        # Right panel - Description editor
        right_frame = ttk.LabelFrame(main_frame, text="Unit Description", padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Tabbed interface for different editing modes
        self.tab_control = ttk.Notebook(right_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Structured Editor
        structured_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(structured_tab, text="Structured Editor")
        
        self.structured_editor = StructuredEditor(
            structured_tab, 
            on_generate=self.on_description_generated
        )
        self.structured_editor.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Text Editor
        text_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(text_tab, text="Text Editor")
        
        self.text_editor = TextEditor(text_tab)
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Preview area
        preview_frame = ttk.LabelFrame(right_frame, text="Preview", padding="5")
        preview_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.X)
        
        # # Color code tools
        # color_frame = ttk.LabelFrame(right_frame, text="Color Tools", padding="5")
        # color_frame.pack(fill=tk.X, pady=(5, 0))
        
        # # Color buttons frame
        # color_buttons_frame = ttk.Frame(color_frame)
        # color_buttons_frame.pack(fill=tk.X)
        
        # # Create color buttons
        # for color in self.COMMON_COLORS:
        #     btn = ttk.Button(
        #         color_buttons_frame, 
        #         text=color["name"],
        #         command=lambda c=color["code"]: self.insert_color_code(c)
        #     )
        #     btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # # End color button
        # ttk.Button(
        #     color_buttons_frame,
        #     text="End Color [-]",
        #     command=lambda: self.text_editor.insert_at_cursor("[-]")
        # ).pack(side=tk.LEFT, padx=2, pady=2)
        
        # # Preview button
        # ttk.Button(
        #     color_frame,
        #     text="Update Preview",
        #     command=self.update_preview
        # ).pack(side=tk.RIGHT, padx=2, pady=2)
        
        # # Common sections buttons
        # sections_frame = ttk.LabelFrame(right_frame, text="Insert Sections", padding="5")
        # sections_frame.pack(fill=tk.X, pady=(5, 0))
        
        # sections = [
        #     ("Stats", "stats"),
        #     ("Ranged Weapons", "ranged"),
        #     ("Melee Weapons", "melee"),
        #     ("Abilities", "abilities")
        # ]
        
        # for name, template_type in sections:
        #     ttk.Button(
        #         sections_frame, 
        #         text=name, 
        #         command=lambda t=template_type: self.text_editor.insert_template(t)
        #     ).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Save button
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="Save Changes", 
            command=self.save_changes
        ).pack(side=tk.RIGHT)
    
    def open_file(self):
        """Open a TTS JSON file."""
        file_path = filedialog.askopenfilename(
            title="Open TTS JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = file.read()
                
            # Parse JSON
            import json
            json_data = json.loads(json_data)
            
            # Load the data into the unit manager
            self.unit_manager.load_json(json_data)
            
            # Update the UI
            self.load_units()
            self.current_file_path = file_path
            self.root.title(f"Warhammer 40k TTS Unit Editor - {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def load_units(self):
        """Load units into the unit listbox."""
        self.unit_listbox.delete(0, tk.END)
        self.profile_listbox.delete(0, tk.END)
        
        for unit in self.unit_manager.units:
            self.unit_listbox.insert(tk.END, unit.name)
    
    def on_unit_select(self, event):
        """Handle unit selection."""
        selection = self.unit_listbox.curselection()
        if not selection:
            return
            
        self.current_unit_index = selection[0]
        self.load_profiles(self.current_unit_index)
        
        # Auto-select first profile if available
        if self.profile_listbox.size() > 0:
            self.profile_listbox.selection_clear(0, tk.END)
            self.profile_listbox.selection_set(0)
            self.profile_listbox.event_generate('<<ListboxSelect>>')
    
    def load_profiles(self, unit_index):
        """
        Load profiles for the selected unit.
        
        Args:
            unit_index: The index of the unit in the unit manager
        """
        self.profile_listbox.delete(0, tk.END)
        
        if unit_index < 0 or unit_index >= len(self.unit_manager.units):
            return
            
        unit = self.unit_manager.units[unit_index]
        for profile in unit.profiles:
            display_name = profile.name
            if profile.count > 1:
                display_name = f"{profile.name} (×{profile.count})"
            self.profile_listbox.insert(tk.END, display_name)
    
    def on_profile_select(self, event):
        """Handle profile selection."""
        if self.current_unit_index is None:
            return
            
        selection = self.profile_listbox.curselection()
        if not selection:
            return
            
        self.current_profile_index = selection[0]
        
        if self.current_unit_index < 0 or self.current_unit_index >= len(self.unit_manager.units):
            return
            
        unit = self.unit_manager.units[self.current_unit_index]
        if self.current_profile_index < 0 or self.current_profile_index >= len(unit.profiles):
            return
            
        profile = unit.profiles[self.current_profile_index]
        
        # Update the text editor
        self.text_editor.set_text(profile.description)
        
        # Update the structured editor
        self.structured_editor.populate_from_description(profile.description)
        
        # Update the preview
        self.update_preview()
    
    def insert_color_code(self, color_code):
        """
        Insert a color code at the current cursor position.
        
        Args:
            color_code: The color code to insert
        """
        self.text_editor.insert_at_cursor(f"[{color_code}]")
    
    def update_preview(self):
        """Update the preview area with formatted text."""
        description = self.text_editor.get_text()
        self.apply_formatting(self.preview_text, description)
    
    def apply_formatting(self, text_widget: tk.Text, description: str) -> None:
        """
        Apply formatting to a text widget based on the description text.
        
        Args:
            text_widget: The tkinter Text widget to apply formatting to
            description: The description text with color codes
        """
        # Enable editing of text widget temporarily if it's disabled
        was_disabled = text_widget.cget("state") == tk.DISABLED
        if was_disabled:
            text_widget.config(state=tk.NORMAL)
        
        # Clear the text widget
        text_widget.delete(1.0, tk.END)
        
        # Just insert the text without formatting for now
        text_widget.insert(tk.END, description)
        
        # Restore the disabled state if needed
        if was_disabled:
            text_widget.config(state=tk.DISABLED)
    
    def on_description_generated(self, description):
        """
        Handle description generated from structured editor.
        
        Args:
            description: The generated description
        """
        self.text_editor.set_text(description)
        self.update_preview()
    
    def save_changes(self):
        """Save changes to the current profile and to the file."""
        if self.current_unit_index is None or self.current_profile_index is None:
            messagebox.showwarning("Warning", "No unit profile selected.")
            return
            
        # Get the updated description
        description = self.text_editor.get_text()
        
        # Save the changes to the profile
        self.unit_manager.save_profile_changes(
            self.current_unit_index,
            self.current_profile_index,
            description
        )
        
        # Save to file
        if self.current_file_path:
            self.save_to_file(self.current_file_path)
            messagebox.showinfo("Success", "Changes saved to file.")
        else:
            # No current file, prompt to save
            self.save_file()
    
    def save_to_file(self, file_path):
        """Save the JSON data to the specified file path."""
        if not self.unit_manager.json_data:
            messagebox.showwarning("Warning", "No data to save.")
            return False
            
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.unit_manager.json_data, file, indent=2)
            
            self.current_file_path = file_path
            self.root.title(f"Warhammer 40k TTS Unit Editor - {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            return False
    
    def save_file(self):
        """Save the JSON file with a file dialog (Save As)."""
        if not self.unit_manager.json_data:
            messagebox.showwarning("Warning", "No data to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save TTS JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        
        if not file_path:
            return
        
        if self.save_to_file(file_path):
            messagebox.showinfo("Success", "File saved successfully.")
