"""
Color formatting utilities for the Warhammer 40k TTS Unit Editor.
"""
import re
import tkinter as tk
from typing import Dict, List, Tuple, Optional


class ColorFormatter:
    """Handles color formatting for TTS description text."""
    
    # Common color codes used in TTS descriptions
    COMMON_COLORS = [
        {"code": "00ff16", "name": "Green", "display": "#00ff16"},
        {"code": "e85545", "name": "Red", "display": "#e85545"},
        {"code": "c6c930", "name": "Yellow", "display": "#c6c930"},
        {"code": "7bc596", "name": "Light Green", "display": "#7bc596"},
        {"code": "dc61ed", "name": "Purple", "display": "#dc61ed"},
        {"code": "56f442", "name": "Bright Green", "display": "#56f442"}
    ]
    
    @staticmethod
    def apply_formatting(text_widget: tk.Text, description: str) -> None:
        """
        Apply color formatting to a text widget based on the description text.
        
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
        
        # Process the text and add it to the widget with formatting
        current_color = None
        
        lines = description.split('\n')
        for line in lines:
            line_pos = 0
            while line_pos < len(line):
                # Find the next color code or end marker
                color_start = line.find('[', line_pos)
                if color_start == -1:
                    # No more color codes, add the rest of the line
                    text_widget.insert(tk.END, line[line_pos:])
                    line_pos = len(line)
                else:
                    # Add text before the color code
                    if color_start > line_pos:
                        text_widget.insert(tk.END, line[line_pos:color_start])
                    
                    # Find the end of the color code
                    color_end = line.find(']', color_start)
                    if color_end == -1:
                        # Malformed color code, just add it as text
                        text_widget.insert(tk.END, line[color_start:])
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
                                    if tag_name not in text_widget.tag_names():
                                        text_widget.tag_configure(tag_name, foreground=f"#{hex_color}")
                                    current_color = tag_name
                                    
                                    # Apply the color to the next text
                                    next_text_start = color_end + 1
                                    next_color_start = line.find('[', next_text_start)
                                    
                                    if next_color_start == -1:
                                        # No more color codes, apply to the rest of the line
                                        text_to_color = line[next_text_start:]
                                        text_widget.insert(tk.END, text_to_color, current_color)
                                        line_pos = len(line)
                                    else:
                                        # Apply color until the next color code
                                        text_to_color = line[next_text_start:next_color_start]
                                        text_widget.insert(tk.END, text_to_color, current_color)
                                        line_pos = next_color_start
                                except:
                                    # Invalid color code
                                    line_pos = color_end + 1
                            else:
                                line_pos = color_end + 1
            
            # Add a newline at the end of each line
            text_widget.insert(tk.END, '\n')
        
        # Restore the disabled state if needed
        if was_disabled:
            text_widget.config(state=tk.DISABLED)
    
    @staticmethod
    def parse_description(description: str) -> Dict[str, List[str]]:
        """
        Parse a description into sections (stats, ranged weapons, melee weapons, abilities).
        
        Args:
            description: The description text to parse
            
        Returns:
            A dictionary with sections as keys and lists of lines as values
        """
        sections = {
            "stats": [],
            "ranged": [],
            "melee": [],
            "abilities": []
        }
        
        current_section = None
        lines = description.split('\n')
        
        for line in lines:
            # Remove color codes for parsing
            clean_line = re.sub(r'\[[^\]]*\]', '', line)
            
            # Check for section headers
            if "M" in clean_line and "T" in clean_line and "Sv" in clean_line and "W" in clean_line:
                current_section = "stats"
                sections[current_section].append(line)
            elif "Ranged weapons" in clean_line:
                current_section = "ranged"
                sections[current_section].append(line)
            elif "Melee weapons" in clean_line:
                current_section = "melee"
                sections[current_section].append(line)
            elif "Abilities" in clean_line:
                current_section = "abilities"
                sections[current_section].append(line)
            elif current_section:
                sections[current_section].append(line)
        
        return sections
    
    @staticmethod
    def extract_stats(stats_lines: List[str]) -> Dict[str, str]:
        """
        Extract stats from the stats section lines.
        
        Args:
            stats_lines: The lines from the stats section
            
        Returns:
            A dictionary with stat names as keys and values as values
        """
        stats = {
            "M": "",
            "T": "",
            "Sv": "",
            "W": "",
            "Ld": "",
            "OC": ""
        }
        
        if len(stats_lines) < 2:
            return stats
        
        # Skip the header line and process the values line
        values_line = stats_lines[1]
        clean_line = re.sub(r'\[[^\]]*\]', '', values_line)
        parts = re.split(r'\s+', clean_line.strip())
        
        if len(parts) >= 6:
            stat_keys = list(stats.keys())
            for i, key in enumerate(stat_keys):
                if i < len(parts):
                    stats[key] = parts[i]
        
        return stats
    
    @staticmethod
    def extract_weapons(weapon_lines: List[str], weapon_type: str) -> List[Dict[str, str]]:
        """
        Extract weapons from the weapon section lines.
        
        Args:
            weapon_lines: The lines from the weapon section
            weapon_type: The type of weapon ("ranged" or "melee")
            
        Returns:
            A list of dictionaries with weapon properties
        """
        weapons = []
        current_weapon = None
        
        for line in weapon_lines:
            # Skip the section header
            if "weapons" in line.lower():
                continue
                
            # Remove color codes for parsing
            clean_line = re.sub(r'\[[^\]]*\]', '', line)
            
            # Check if this is a weapon name line
            if "(" in clean_line and ")" in clean_line and ("Ranged Weapons" in clean_line or "Melee Weapons" in clean_line):
                if current_weapon:
                    weapons.append(current_weapon)
                
                weapon_name = clean_line.split('(')[0].strip()
                current_weapon = {"name": weapon_name}
                
                if weapon_type == "ranged":
                    current_weapon.update({
                        "range": "",
                        "A": "",
                        "BS": "",
                        "S": "",
                        "AP": "",
                        "D": "",
                        "abilities": ""
                    })
                else:  # melee
                    current_weapon.update({
                        "A": "",
                        "WS": "",
                        "S": "",
                        "AP": "",
                        "D": "",
                        "abilities": ""
                    })
            
            # Check if this is a weapon stats line
            elif current_weapon:
                if weapon_type == "ranged":
                    # Try to extract range
                    range_match = re.match(r'(\d+\")', clean_line)
                    if range_match:
                        current_weapon["range"] = range_match.group(1)
                    
                    # Extract other stats
                    for stat in ["A:", "BS:", "S:", "AP:", "D:"]:
                        if stat in clean_line:
                            stat_key = stat.replace(":", "")
                            stat_value = clean_line.split(stat)[1].split()[0]
                            current_weapon[stat_key] = stat_value
                    
                    # Extract abilities - look for anything after the D: value
                    abilities_match = re.search(r'D:\s*\S+\s+(.*)', clean_line)
                    if abilities_match:
                        current_weapon["abilities"] = abilities_match.group(1).strip()
                
                elif weapon_type == "melee":
                    # Extract stats
                    for stat in ["A:", "WS:", "S:", "AP:", "D:"]:
                        if stat in clean_line:
                            stat_key = stat.replace(":", "")
                            stat_value = clean_line.split(stat)[1].split()[0]
                            current_weapon[stat_key] = stat_value
                    
                    # Extract abilities - look for anything after the D: value
                    abilities_match = re.search(r'D:\s*\S+\s+(.*)', clean_line)
                    if abilities_match:
                        current_weapon["abilities"] = abilities_match.group(1).strip()
        
        # Add the last weapon if there is one
        if current_weapon:
            weapons.append(current_weapon)
        
        return weapons
    
    @staticmethod
    def extract_abilities(ability_lines: List[str]) -> List[str]:
        """
        Extract abilities from the abilities section lines.
        
        Args:
            ability_lines: The lines from the abilities section
            
        Returns:
            A list of ability strings
        """
        abilities = []
        
        for line in ability_lines:
            # Skip the section header
            if "Abilities" in line:
                continue
                
            # Remove color codes for parsing
            clean_line = re.sub(r'\[[^\]]*\]', '', line)
            
            if clean_line.strip():
                abilities.append(clean_line.strip())
        
        return abilities
    
    @staticmethod
    def generate_description(
        stats: Dict[str, str],
        ranged_weapons: List[Dict[str, str]],
        melee_weapons: List[Dict[str, str]],
        abilities: List[str]
    ) -> str:
        """
        Generate a formatted description from the provided data.
        
        Args:
            stats: Dictionary of stat values
            ranged_weapons: List of ranged weapon dictionaries
            melee_weapons: List of melee weapon dictionaries
            abilities: List of ability strings
            
        Returns:
            A formatted description string
        """
        description = ""
        
        # Stats section
        description += "[56f442] M    T   Sv    W    Ld   OC  [-]\n"
        stats_line = ""
        for stat in ["M", "T", "Sv", "W", "Ld", "OC"]:
            value = stats.get(stat, "")
            # Pad with spaces for alignment
            if stat == "M":
                stats_line += f"{value}   "
            else:
                stats_line += f"{value}   "
        description += stats_line + "[-][-]\n\n"
        
        # Ranged weapons section
        if ranged_weapons:
            description += "[e85545]Ranged weapons[-]\n"
            for weapon in ranged_weapons:
                description += f"[c6c930]{weapon['name']} (Ranged Weapons)[-]\n"
                
                # Build stats line
                range_val = weapon.get("range", "")
                a_val = weapon.get("A", "")
                bs_val = weapon.get("BS", "")
                s_val = weapon.get("S", "")
                ap_val = weapon.get("AP", "")
                d_val = weapon.get("D", "")
                abilities = weapon.get("abilities", "")
                
                stats_line = f"{range_val} A:{a_val} BS:{bs_val} S:{s_val} AP:{ap_val} D:{d_val} "
                if abilities:
                    stats_line += f"[7bc596][{abilities}][-] "
                description += stats_line + "\n"
            description += "\n"
        
        # Melee weapons section
        if melee_weapons:
            description += "[e85545]Melee weapons[-]\n"
            for weapon in melee_weapons:
                description += f"[c6c930]{weapon['name']} (Melee Weapons)[-]\n"
                
                # Build stats line
                a_val = weapon.get("A", "")
                ws_val = weapon.get("WS", "")
                s_val = weapon.get("S", "")
                ap_val = weapon.get("AP", "")
                d_val = weapon.get("D", "")
                abilities = weapon.get("abilities", "")
                
                stats_line = f"A:{a_val} WS:{ws_val} S:{s_val} AP:{ap_val} D:{d_val} "
                if abilities:
                    stats_line += f"[7bc596][{abilities}][-] "
                description += stats_line + "\n"
            description += "\n"
        
        # Abilities section
        if abilities:
            description += "[dc61ed]Abilities[-]\n"
            for ability in abilities:
                description += ability + "\n"
        
        return description
