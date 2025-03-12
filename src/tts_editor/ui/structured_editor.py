"""
Structured editor component for the Warhammer 40k TTS Unit Editor.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional, Any

from tts_editor.utils import description_parser


class StructuredEditor(ttk.Frame):
    """Structured editor component for editing unit descriptions."""
    
    def __init__(self, parent, on_generate: Optional[Callable] = None):
        """
        Initialize the structured editor.
        
        Args:
            parent: The parent widget
            on_generate: Optional callback for when description is generated
        """
        super().__init__(parent)
        self.on_generate = on_generate
        self.stat_entries = {}
        self.ranged_weapons_frame = None
        self.melee_weapons_frame = None
        self.abilities_text = None
        self.create_widgets()
    
    def create_widgets(self):
        """Create the structured editor widgets."""
        # Main container with scrollbar
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        self.structured_frame = ttk.Frame(canvas)
        self.structured_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.structured_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Stats section
        stats_frame = ttk.LabelFrame(self.structured_frame, text="Stats", padding="5")
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Create a grid for stats
        stat_labels = ["M", "T", "Sv", "W", "Ld", "OC"]
        self.stat_entries = {}
        
        for i, label in enumerate(stat_labels):
            ttk.Label(stats_frame, text=label).grid(row=0, column=i, padx=5, pady=2)
            entry = ttk.Entry(stats_frame, width=5)
            entry.grid(row=1, column=i, padx=5, pady=2)
            self.stat_entries[label] = entry
        
        # Ranged Weapons section
        ranged_frame = ttk.LabelFrame(self.structured_frame, text="Ranged Weapons", padding="5")
        ranged_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.ranged_weapons_frame = ttk.Frame(ranged_frame)
        self.ranged_weapons_frame.pack(fill=tk.X)
        
        ttk.Button(
            ranged_frame, 
            text="Add Ranged Weapon", 
            command=lambda: self.add_weapon_row(self.ranged_weapons_frame, "ranged")
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Melee Weapons section
        melee_frame = ttk.LabelFrame(self.structured_frame, text="Melee Weapons", padding="5")
        melee_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.melee_weapons_frame = ttk.Frame(melee_frame)
        self.melee_weapons_frame.pack(fill=tk.X)
        
        ttk.Button(
            melee_frame, 
            text="Add Melee Weapon", 
            command=lambda: self.add_weapon_row(self.melee_weapons_frame, "melee")
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Abilities section
        abilities_frame = ttk.LabelFrame(self.structured_frame, text="Abilities", padding="5")
        abilities_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.abilities_text = tk.Text(abilities_frame, wrap=tk.WORD, height=6)
        self.abilities_text.pack(fill=tk.X)
        
        # Button to update text editor from structured editor
        ttk.Button(
            self.structured_frame,
            text="Generate Description from Fields",
            command=self.generate_description
        ).pack(pady=10)
    
    def add_weapon_row(self, parent, weapon_type):
        """
        Add a new weapon row to the specified weapon frame.
        
        Args:
            parent: The parent frame to add the row to
            weapon_type: The type of weapon ("ranged" or "melee")
        """
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=(2, 0))
        
        # Weapon name
        ttk.Label(row_frame, text="Name:").pack(side=tk.LEFT, padx=(0, 2))
        name_entry = ttk.Entry(row_frame, width=20)
        name_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Common weapon stats
        stats = []
        
        if weapon_type == "ranged":
            stats = [
                {"label": "Range:", "width": 5},
                {"label": "A:", "width": 3},
                {"label": "BS:", "width": 4},
                {"label": "S:", "width": 3},
                {"label": "AP:", "width": 4},
                {"label": "D:", "width": 4},
                {"label": "Abilities:", "width": 15}
            ]
        else:  # melee
            stats = [
                {"label": "A:", "width": 3},
                {"label": "WS:", "width": 4},
                {"label": "S:", "width": 3},
                {"label": "AP:", "width": 4},
                {"label": "D:", "width": 4},
                {"label": "Abilities:", "width": 15}
            ]
        
        entries = []
        for stat in stats:
            ttk.Label(row_frame, text=stat["label"]).pack(side=tk.LEFT, padx=(0, 2))
            entry = ttk.Entry(row_frame, width=stat["width"])
            entry.pack(side=tk.LEFT, padx=(0, 5))
            entries.append(entry)
        
        # Delete button
        ttk.Button(
            row_frame, 
            text="X", 
            width=2,
            command=lambda: row_frame.destroy()
        ).pack(side=tk.LEFT)
        
        # Store the row data
        row_data = {
            "name": name_entry,
            "entries": entries,
            "type": weapon_type
        }
        
        # Attach the data to the frame for later retrieval
        row_frame.data = row_data
    
    def clear(self):
        """Clear all fields."""
        # Clear stat entries
        for entry in self.stat_entries.values():
            entry.delete(0, tk.END)
        
        # Clear weapon rows
        for child in self.ranged_weapons_frame.winfo_children():
            child.destroy()
        for child in self.melee_weapons_frame.winfo_children():
            child.destroy()
        
        # Clear abilities text
        self.abilities_text.delete(1.0, tk.END)
    
    
    def populate_from_description(self, description: str):
        """
        Populate the structured editor from a description.
        
        Args:
            description: The description text to parse
        """
        # Clear existing data
        self.clear()
        
        # Parse the description
        sections = description_parser.parse_description(description)
        
        # Extract and populate stats
        stats = description_parser.extract_stats(sections["stats"])
        for key, value in stats.items():
            if key in self.stat_entries:
                self.stat_entries[key].insert(0, value)
        
        # Extract and populate ranged weapons
        ranged_weapons = description_parser.extract_weapons(sections["ranged"], "ranged")
        for weapon in ranged_weapons:
            self.add_weapon_row(self.ranged_weapons_frame, "ranged")
            row_frame = self.ranged_weapons_frame.winfo_children()[-1]
            row_frame.data["name"].insert(0, weapon["name"])
            
            entries = row_frame.data["entries"]
            if len(entries) >= 7:
                entries[0].insert(0, weapon.get("range", ""))
                entries[1].insert(0, weapon.get("A", ""))
                entries[2].insert(0, weapon.get("BS", ""))
                entries[3].insert(0, weapon.get("S", ""))
                entries[4].insert(0, weapon.get("AP", ""))
                entries[5].insert(0, weapon.get("D", ""))
                entries[6].insert(0, weapon.get("abilities", ""))
        
        # Extract and populate melee weapons
        melee_weapons = description_parser.extract_weapons(sections["melee"], "melee")
        for weapon in melee_weapons:
            self.add_weapon_row(self.melee_weapons_frame, "melee")
            row_frame = self.melee_weapons_frame.winfo_children()[-1]
            row_frame.data["name"].insert(0, weapon["name"])
            
            entries = row_frame.data["entries"]
            if len(entries) >= 6:
                entries[0].insert(0, weapon.get("A", ""))
                entries[1].insert(0, weapon.get("WS", ""))
                entries[2].insert(0, weapon.get("S", ""))
                entries[3].insert(0, weapon.get("AP", ""))
                entries[4].insert(0, weapon.get("D", ""))
                entries[5].insert(0, weapon.get("abilities", ""))
        
        # Extract and populate abilities
        abilities = description_parser.extract_abilities(sections["abilities"])
        for ability in abilities:
            self.abilities_text.insert(tk.END, ability + "\n")
    
    def get_stats(self) -> Dict[str, str]:
        """
        Get the stats from the editor.
        
        Returns:
            A dictionary of stat values
        """
        stats = {}
        for key, entry in self.stat_entries.items():
            stats[key] = entry.get()
        return stats
    
    def get_ranged_weapons(self) -> List[Dict[str, str]]:
        """
        Get the ranged weapons from the editor.
        
        Returns:
            A list of ranged weapon dictionaries
        """
        weapons = []
        for child in self.ranged_weapons_frame.winfo_children():
            if hasattr(child, 'data'):
                data = child.data
                weapon = {"name": data["name"].get()}
                
                entries = data["entries"]
                if len(entries) >= 7:
                    weapon["range"] = entries[0].get()
                    weapon["A"] = entries[1].get()
                    weapon["BS"] = entries[2].get()
                    weapon["S"] = entries[3].get()
                    weapon["AP"] = entries[4].get()
                    weapon["D"] = entries[5].get()
                    weapon["abilities"] = entries[6].get()
                
                weapons.append(weapon)
        
        return weapons
    
    def get_melee_weapons(self) -> List[Dict[str, str]]:
        """
        Get the melee weapons from the editor.
        
        Returns:
            A list of melee weapon dictionaries
        """
        weapons = []
        for child in self.melee_weapons_frame.winfo_children():
            if hasattr(child, 'data'):
                data = child.data
                weapon = {"name": data["name"].get()}
                
                entries = data["entries"]
                if len(entries) >= 6:
                    weapon["A"] = entries[0].get()
                    weapon["WS"] = entries[1].get()
                    weapon["S"] = entries[2].get()
                    weapon["AP"] = entries[3].get()
                    weapon["D"] = entries[4].get()
                    weapon["abilities"] = entries[5].get()
                
                weapons.append(weapon)
        
        return weapons
    
    def get_abilities(self) -> List[str]:
        """
        Get the abilities from the editor.
        
        Returns:
            A list of ability strings
        """
        abilities_text = self.abilities_text.get(1.0, tk.END).strip()
        if not abilities_text:
            return []
        
        return [line.strip() for line in abilities_text.split('\n') if line.strip()]
    
    def generate_description(self) -> str:
        """
        Generate a description from the editor fields.
        
        Returns:
            The generated description
        """
        stats = self.get_stats()
        ranged_weapons = self.get_ranged_weapons()
        melee_weapons = self.get_melee_weapons()
        abilities = self.get_abilities()
        
        description = description_parser.generate_description(
            stats, ranged_weapons, melee_weapons, abilities
        )
        
        if self.on_generate:
            self.on_generate(description)
        
        return description
