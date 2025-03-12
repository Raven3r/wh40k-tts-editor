import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import os
import re

class TTSUnitEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Warhammer 40k TTS Unit Editor")
        self.root.geometry("900x700")
        
        self.json_data = None
        self.current_file = None
        self.current_unit_index = None
        self.current_profile_index = None
        self.units = []  # Will store grouped units
        
        self.create_menu()
        self.create_ui()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)
        
    def create_ui(self):
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
        
        # Tab 1: Text Editor
        text_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(text_tab, text="Text Editor")
        
        # Description text area with scrollbar
        text_frame = ttk.Frame(text_tab)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.description_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.description_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.description_text.yview)
        
        # Tab 2: Structured Editor
        structured_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(structured_tab, text="Structured Editor")
        
        # Create frames for different sections
        self.create_structured_editor(structured_tab)
        
        # Preview area
        preview_frame = ttk.LabelFrame(right_frame, text="Preview", padding="5")
        preview_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.X)
        
        # Color code tools
        color_frame = ttk.LabelFrame(right_frame, text="Color Tools", padding="5")
        color_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Color buttons frame
        color_buttons_frame = ttk.Frame(color_frame)
        color_buttons_frame.pack(fill=tk.X)
        
        # Define colors with their hex codes and display names
        colors = [
            {"code": "00ff16", "name": "Green", "display": "#00ff16"},
            {"code": "e85545", "name": "Red", "display": "#e85545"},
            {"code": "c6c930", "name": "Yellow", "display": "#c6c930"},
            {"code": "7bc596", "name": "Light Green", "display": "#7bc596"},
            {"code": "dc61ed", "name": "Purple", "display": "#dc61ed"},
            {"code": "56f442", "name": "Bright Green", "display": "#56f442"}
        ]
        
        # Create color buttons
        for color in colors:
            btn = ttk.Button(
                color_buttons_frame, 
                text=color["name"],
                command=lambda c=color["code"]: self.insert_color_code(c)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # End color button
        ttk.Button(
            color_buttons_frame,
            text="End Color [-]",
            command=lambda: self.description_text.insert(tk.INSERT, "[-]")
        ).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Preview button
        ttk.Button(
            color_frame,
            text="Update Preview",
            command=self.update_preview
        ).pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Common sections buttons
        sections_frame = ttk.LabelFrame(right_frame, text="Insert Sections", padding="5")
        sections_frame.pack(fill=tk.X, pady=(5, 0))
        
        sections = [
            ("Stats", self.insert_stats_template),
            ("Ranged Weapons", self.insert_ranged_weapons_template),
            ("Melee Weapons", self.insert_melee_weapons_template),
            ("Abilities", self.insert_abilities_template)
        ]
        
        for name, command in sections:
            ttk.Button(sections_frame, text=name, command=command).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Save button
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.RIGHT)
        
    def create_structured_editor(self, parent):
        """Create a structured editor with fields for each stat"""
        # Main container with scrollbar
        container = ttk.Frame(parent)
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
            command=self.generate_description_from_fields
        ).pack(pady=10)
        
    def add_weapon_row(self, parent, weapon_type):
        """Add a new weapon row to the specified weapon frame"""
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
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open TTS JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.json_data = json.load(file)
                
            self.current_file = file_path
            self.group_units()
            self.load_units()
            self.root.title(f"Warhammer 40k TTS Unit Editor - {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def group_units(self):
        """Group models that belong to the same unit"""
        if not self.json_data or "ObjectStates" not in self.json_data:
            return
            
        self.units = []
        unit_map = {}
        
        # First pass: identify unique units by nickname (ignoring color codes and counts)
        for i, obj in enumerate(self.json_data["ObjectStates"]):
            nickname = obj.get("Nickname", f"Unit {i+1}")
            
            # Extract the base unit name (remove color codes and counts)
            clean_nickname = re.sub(r'\[[^\]]*\]', '', nickname)  # Remove color codes
            base_name = re.sub(r'^\d+/\d+\s+', '', clean_nickname).strip()  # Remove counts like "1/1"
            
            # Check if this is a variant (like "- Exarch" or "- Fusion Pistol")
            variant = ""
            if " - " in base_name:
                parts = base_name.split(" - ", 1)
                base_name = parts[0].strip()
                variant = parts[1].strip()
            
            # Create or update unit entry
            if base_name not in unit_map:
                unit_map[base_name] = {
                    "name": base_name,
                    "profiles": []
                }
            
            # Add this profile
            profile_name = variant if variant else "Standard"
            unit_map[base_name]["profiles"].append({
                "index": i,
                "name": profile_name,
                "nickname": nickname,
                "description": obj.get("Description", "")
            })
        
        # Convert map to list
        self.units = list(unit_map.values())
    
    def load_units(self):
        """Load the grouped units into the unit listbox"""
        self.unit_listbox.delete(0, tk.END)
        self.profile_listbox.delete(0, tk.END)
        
        for unit in self.units:
            self.unit_listbox.insert(tk.END, unit["name"])
    
    def on_unit_select(self, event):
        """Handle unit selection"""
        if not self.units:
            return
            
        selection = self.unit_listbox.curselection()
        if not selection:
            return
            
        self.current_unit_index = selection[0]
        self.load_profiles(self.current_unit_index)
    
    def load_profiles(self, unit_index):
        """Load profiles for the selected unit"""
        self.profile_listbox.delete(0, tk.END)
        
        unit = self.units[unit_index]
        for profile in unit["profiles"]:
            self.profile_listbox.insert(tk.END, profile["name"])
    
    def on_profile_select(self, event):
        """Handle profile selection"""
        if not self.units or self.current_unit_index is None:
            return
            
        selection = self.profile_listbox.curselection()
        if not selection:
            return
            
        self.current_profile_index = selection[0]
        profile = self.units[self.current_unit_index]["profiles"][self.current_profile_index]
        
        # Get the actual object index in the JSON data
        obj_index = profile["index"]
        
        # Clear and update description text
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, profile["description"])
        
        # Update the structured editor
        self.populate_structured_editor(profile["description"])
        
        # Update preview
        self.update_preview()
    
    def populate_structured_editor(self, description):
        """Parse the description and populate the structured editor fields"""
        # Clear existing weapon rows
        for child in self.ranged_weapons_frame.winfo_children():
            child.destroy()
        for child in self.melee_weapons_frame.winfo_children():
            child.destroy()
        
        # Clear abilities text
        self.abilities_text.delete(1.0, tk.END)
        
        # Clear stat entries
        for entry in self.stat_entries.values():
            entry.delete(0, tk.END)
        
        # Parse the description
        lines = description.split('\n')
        section = None
        
        for line in lines:
            # Remove color codes for parsing
            clean_line = re.sub(r'\[[^\]]*\]', '', line)
            
            # Check for section headers
            if "M" in clean_line and "T" in clean_line and "Sv" in clean_line and "W" in clean_line:
                section = "stats"
                continue
            elif "Ranged weapons" in clean_line:
                section = "ranged"
                continue
            elif "Melee weapons" in clean_line:
                section = "melee"
                continue
            elif "Abilities" in clean_line:
                section = "abilities"
                continue
            
            # Process based on current section
            if section == "stats":
                # Try to extract stats
                if len(clean_line.strip()) > 0 and not clean_line.strip().startswith('['):
                    parts = re.split(r'\s+', clean_line.strip())
                    if len(parts) >= 6:
                        stats = ["M", "T", "Sv", "W", "Ld", "OC"]
                        for i, stat in enumerate(stats):
                            if i < len(parts):
                                self.stat_entries[stat].insert(0, parts[i])
            elif section == "ranged" and "(" in clean_line and ")" in clean_line:
                # This is a weapon name line
                weapon_name = clean_line.split('(')[0].strip()
                self.add_weapon_row(self.ranged_weapons_frame, "ranged")
                row_frame = self.ranged_weapons_frame.winfo_children()[-1]
                row_frame.data["name"].insert(0, weapon_name)
            elif section == "ranged" and "A:" in clean_line and "BS:" in clean_line:
                # This is a weapon stats line
                if self.ranged_weapons_frame.winfo_children():
                    row_frame = self.ranged_weapons_frame.winfo_children()[-1]
                    entries = row_frame.data["entries"]
                    
                    # Try to extract range
                    range_match = re.match(r'(\d+\")', clean_line)
                    if range_match and len(entries) > 0:
                        entries[0].insert(0, range_match.group(1))
                    
                    # Extract other stats
                    stats = ["A:", "BS:", "S:", "AP:", "D:"]
                    for i, stat in enumerate(stats):
                        if stat in clean_line and i+1 < len(entries):
                            stat_value = clean_line.split(stat)[1].split()[0]
                            entries[i+1].insert(0, stat_value)
                    
                    # Extract abilities
                    abilities_match = re.search(r'\[7bc596\]\[(.*?)\]', line)
                    if abilities_match and len(entries) > 6:
                        entries[6].insert(0, abilities_match.group(1))
            elif section == "melee" and "(" in clean_line and ")" in clean_line:
                # This is a weapon name line
                weapon_name = clean_line.split('(')[0].strip()
                self.add_weapon_row(self.melee_weapons_frame, "melee")
                row_frame = self.melee_weapons_frame.winfo_children()[-1]
                row_frame.data["name"].insert(0, weapon_name)
            elif section == "melee" and "A:" in clean_line and "WS:" in clean_line:
                # This is a weapon stats line
                if self.melee_weapons_frame.winfo_children():
                    row_frame = self.melee_weapons_frame.winfo_children()[-1]
                    entries = row_frame.data["entries"]
                    
                    # Extract stats
                    stats = ["A:", "WS:", "S:", "AP:", "D:"]
                    for i, stat in enumerate(stats):
                        if stat in clean_line and i < len(entries):
                            stat_value = clean_line.split(stat)[1].split()[0]
                            entries[i].insert(0, stat_value)
                    
                    # Extract abilities
                    abilities_match = re.search(r'\[7bc596\]\[(.*?)\]', line)
                    if abilities_match and len(entries) > 5:
                        entries[5].insert(0, abilities_match.group(1))
            elif section == "abilities" and len(clean_line.strip()) > 0:
                # Add to abilities text
                self.abilities_text.insert(tk.END, clean_line + "\n")
    
    def generate_description_from_fields(self):
        """Generate a formatted description from the structured editor fields"""
        description = ""
        
        # Stats section
        description += "[56f442] M    T   Sv    W    Ld   OC  [-]\n"
        stats_line = ""
        for stat in ["M", "T", "Sv", "W", "Ld", "OC"]:
            value = self.stat_entries[stat].get()
            # Pad with spaces for alignment
            if stat == "M":
                stats_line += f"{value}   "
            else:
                stats_line += f"{value}   "
        description += stats_line + "[-][-]\n\n"
        
        # Ranged weapons section
        if self.ranged_weapons_frame.winfo_children():
            description += "[e85545]Ranged weapons[-]\n"
            for child in self.ranged_weapons_frame.winfo_children():
                if hasattr(child, 'data'):
                    data = child.data
                    weapon_name = data["name"].get()
                    description += f"[c6c930]{weapon_name} (Ranged Weapons)[-]\n"
                    
                    # Build stats line
                    entries = data["entries"]
                    if len(entries) >= 7:
                        range_val = entries[0].get()
                        a_val = entries[1].get()
                        bs_val = entries[2].get()
                        s_val = entries[3].get()
                        ap_val = entries[4].get()
                        d_val = entries[5].get()
                        abilities = entries[6].get()
                        
                        stats_line = f"{range_val} A:{a_val} BS:{bs_val} S:{s_val} AP:{ap_val} D:{d_val} "
                        if abilities:
                            stats_line += f"[7bc596][{abilities}][-] "
                        description += stats_line + "\n"
            description += "\n"
        
        # Melee weapons section
        if self.melee_weapons_frame.winfo_children():
            description += "[e85545]Melee weapons[-]\n"
            for child in self.melee_weapons_frame.winfo_children():
                if hasattr(child, 'data'):
                    data = child.data
                    weapon_name = data["name"].get()
                    description += f"[c6c930]{weapon_name} (Melee Weapons)[-]\n"
                    
                    # Build stats line
                    entries = data["entries"]
                    if len(entries) >= 6:
                        a_val = entries[0].get()
                        ws_val = entries[1].get()
                        s_val = entries[2].get()
                        ap_val = entries[3].get()
                        d_val = entries[4].get()
                        abilities = entries[5].get()
                        
                        stats_line = f"A:{a_val} WS:{ws_val} S:{s_val} AP:{ap_val} D:{d_val} "
                        if abilities:
                            stats_line += f"[7bc596][{abilities}][-] "
                        description += stats_line + "\n"
            description += "\n"
        
        # Abilities section
        abilities_text = self.abilities_text.get(1.0, tk.END).strip()
        if abilities_text:
            description += "[dc61ed]Abilities[-]\n"
            description += abilities_text
        
        # Update the text editor
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, description)
        
        # Update preview
        self.update_preview()
    
    def insert_color_code(self, color_code):
        """Insert a color code at the current cursor position"""
        self.description_text.insert(tk.INSERT, f"[{color_code}]")
    
    def update_preview(self):
        """Update the preview area with formatted text"""
        # Get the current description text
        description = self.description_text.get(1.0, tk.END)
        
        # Enable editing of preview text temporarily
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        # Process the text and add it to preview
        current_color = None
        
        lines = description.split('\n')
        for line in lines:
            line_pos = 0
            while line_pos < len(line):
                # Find the next color code or end marker
                color_start = line.find('[', line_pos)
                if color_start == -1:
                    # No more color codes, add the rest of the line
                    self.preview_text.insert(tk.END, line[line_pos:])
                    line_pos = len(line)
                else:
                    # Add text before the color code
                    if color_start > line_pos:
                        self.preview_text.insert(tk.END, line[line_pos:color_start])
                    
                    # Find the end of the color code
                    color_end = line.find(']', color_start)
                    if color_end == -1:
                        # Malformed color code, just add it as text
                        self.preview_text.insert(tk.END, line[color_start:])
                        line_pos = len(line)
                    else:
                        color_code = line[color_start:color_end+1]
                        if color_code == "[-]":
                            # End of color
                            current_color = None
                            line_pos = color_end + 1
                        else:
                            # New color
                            hex_color = color_code[1:-1]
                            if len(hex_color) == 6:
                                try:
                                    # Create a tag for this color if it doesn't exist
                                    tag_name = f"color_{hex_color}"
                                    if tag_name not in self.preview_text.tag_names():
                                        self.preview_text.tag_configure(tag_name, foreground=f"#{hex_color}")
                                    current_color = tag_name
                                    
                                    # Apply the color to the next text
                                    next_text_start = color_end + 1
                                    next_color_start = line.find('[', next_text_start)
                                    
                                    if next_color_start == -1:
                                        # No more color codes, apply to the rest of the line
                                        text_to_color = line[next_text_start:]
                                        self.preview_text.insert(tk.END, text_to_color, current_color)
                                        line_pos = len(line)
                                    else:
                                        # Apply color until the next color code
                                        text_to_color = line[next_text_start:next_color_start]
                                        self.preview_text.insert(tk.END, text_to_color, current_color)
                                        line_pos = next_color_start
                                except:
                                    # Invalid color code
                                    line_pos = color_end + 1
                            else:
                                line_pos = color_end + 1
            
            # Add a newline at the end of each line
            self.preview_text.insert(tk.END, '\n')
        
        # Disable editing of preview text
        self.preview_text.config(state=tk.DISABLED)
    
    def insert_stats_template(self):
        """Insert a template for unit stats"""
        template = "[56f442] M    T   Sv    W    Ld   OC  [-]\n"
        template += "X\"   X   X+   X    X+   X   [-][-]\n\n"
        self.description_text.insert(tk.INSERT, template)
    
    def insert_ranged_weapons_template(self):
        """Insert a template for ranged weapons"""
        template = "[e85545]Ranged weapons[-]\n"
        template += "[c6c930]Weapon Name (Ranged Weapons)[-]\n"
        template += "X\" A:X BS:X+ S:X AP:-X D:X [7bc596][Abilities][-] \n\n"
        self.description_text.insert(tk.INSERT, template)
