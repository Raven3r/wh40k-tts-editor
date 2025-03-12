"""
Parser for Warhammer 40k unit descriptions.
"""
import re
from typing import Dict, List


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
    
    # Skip the first line (section header)
    if len(weapon_lines) <= 1:
        return weapons
    
    # Process the lines in pairs (name line followed by stats line)
    i = 1  # Start after the header
    while i < len(weapon_lines) - 1:
        # Get the name line and stats line
        name_line = weapon_lines[i]
        stats_line = weapon_lines[i + 1]
        
        # Remove color codes for parsing
        clean_name_line = re.sub(r'\[[^\]]*\]', '', name_line)
        clean_stats_line = re.sub(r'\[[^\]]*\]', '', stats_line)
        
        # Extract weapon name
        if "(" in clean_name_line and ")" in clean_name_line:
            weapon_name = clean_name_line.split('(')[0].strip()
            
            # Create weapon dictionary
            weapon = {"name": weapon_name}
            
            if weapon_type == "ranged":
                weapon.update({
                    "range": "",
                    "A": "",
                    "BS": "",
                    "S": "",
                    "AP": "",
                    "D": "",
                    "abilities": ""
                })
                
                # Try to extract range
                range_match = re.match(r'(\d+\")', clean_stats_line)
                if range_match:
                    weapon["range"] = range_match.group(1)
                
                # Use regex to extract each stat precisely
                a_match = re.search(r'A:(\S+)', clean_stats_line)
                if a_match:
                    weapon["A"] = a_match.group(1)
                
                bs_match = re.search(r'BS:(\S+)', clean_stats_line)
                if bs_match:
                    weapon["BS"] = bs_match.group(1)
                
                s_match = re.search(r'(?<!\w)S:(\S+)', clean_stats_line)
                if s_match:
                    weapon["S"] = s_match.group(1)
                
                ap_match = re.search(r'AP:(\S+)', clean_stats_line)
                if ap_match:
                    weapon["AP"] = ap_match.group(1)
                
                d_match = re.search(r'D:(\S+)', clean_stats_line)
                if d_match:
                    weapon["D"] = d_match.group(1)
                
                # Extract abilities - look for anything in square brackets after the D: value
                # The original stats line might have color codes, so we need to check the original line
                original_stats_line = stats_line
                
                # First try to find abilities in the format [7bc596][abilities][-]
                abilities_match = re.search(r'\[7bc596\]\[([^\]]*)\]', original_stats_line)
                if abilities_match:
                    weapon["abilities"] = abilities_match.group(1).strip()
                # If that fails, try to find abilities after the D: value
                elif "D:" in original_stats_line:
                    # Split the line at D: and take everything after the value
                    parts = re.split(r'D:\s*\S+\s+', original_stats_line, 1)
                    if len(parts) > 1 and parts[1].strip():
                        # Extract text between [ and ]
                        ability_match = re.search(r'\[([^\]]*)\]', parts[1])
                        if ability_match:
                            weapon["abilities"] = ability_match.group(1).strip()
            
            elif weapon_type == "melee":
                weapon.update({
                    "A": "",
                    "WS": "",
                    "S": "",
                    "AP": "",
                    "D": "",
                    "abilities": ""
                })
                
                # Use regex to extract each stat precisely
                a_match = re.search(r'A:(\S+)', clean_stats_line)
                if a_match:
                    weapon["A"] = a_match.group(1)
                
                ws_match = re.search(r'WS:(\S+)', clean_stats_line)
                if ws_match:
                    weapon["WS"] = ws_match.group(1)
                
                s_match = re.search(r'(?<!\w)S:(\S+)', clean_stats_line)
                if s_match:
                    weapon["S"] = s_match.group(1)
                
                ap_match = re.search(r'AP:(\S+)', clean_stats_line)
                if ap_match:
                    weapon["AP"] = ap_match.group(1)
                
                d_match = re.search(r'D:(\S+)', clean_stats_line)
                if d_match:
                    weapon["D"] = d_match.group(1)
                
                # Extract abilities - look for anything in square brackets after the D: value
                # The original stats line might have color codes, so we need to check the original line
                original_stats_line = stats_line
                
                # First try to find abilities in the format [7bc596][abilities][-]
                abilities_match = re.search(r'\[7bc596\]\[([^\]]*)\]', original_stats_line)
                if abilities_match:
                    weapon["abilities"] = abilities_match.group(1).strip()
                # If that fails, try to find abilities after the D: value
                elif "D:" in original_stats_line:
                    # Split the line at D: and take everything after the value
                    parts = re.split(r'D:\s*\S+\s+', original_stats_line, 1)
                    if len(parts) > 1 and parts[1].strip():
                        # Extract text between [ and ]
                        ability_match = re.search(r'\[([^\]]*)\]', parts[1])
                        if ability_match:
                            weapon["abilities"] = ability_match.group(1).strip()
            
            weapons.append(weapon)
        
        i += 2  # Move to the next pair of lines
    
    return weapons


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


def generate_description(stats: Dict[str, str], 
                         ranged_weapons: List[Dict[str, str]], 
                         melee_weapons: List[Dict[str, str]], 
                         abilities: List[str]) -> str:
    """
    Generate a description from the provided data.
    
    Args:
        stats: Dictionary of stat values
        ranged_weapons: List of ranged weapon dictionaries
        melee_weapons: List of melee weapon dictionaries
        abilities: List of ability strings
        
    Returns:
        The generated description
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
