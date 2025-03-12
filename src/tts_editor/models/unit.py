"""
Unit data model for the Warhammer 40k TTS Unit Editor.
"""
import re
from typing import Dict, List, Optional, Any


class UnitProfile:
    """Represents a single unit profile (variant) in the TTS JSON."""
    
    def __init__(self, index: int, name: str, nickname: str, description: str):
        """
        Initialize a unit profile.
        
        Args:
            index: The index of this profile in the original JSON ObjectStates array
            name: The profile name (e.g., "Standard", "Exarch", etc.)
            nickname: The original nickname from the JSON
            description: The description text containing stats, weapons, and abilities
        """
        self.index = index
        self.name = name
        self.nickname = nickname
        self.description = description
        self.count = 1
        self.identical_indices = [index]  # List of indices for identical profiles


class Unit:
    """Represents a unit with potentially multiple profiles/variants."""
    
    def __init__(self, name: str):
        """
        Initialize a unit.
        
        Args:
            name: The unit name
        """
        self.name = name
        self.profiles: List[UnitProfile] = []
    
    def add_profile(self, profile: UnitProfile) -> None:
        """
        Add a profile to this unit.
        
        Args:
            profile: The profile to add
        """
        self.profiles.append(profile)


class UnitManager:
    """Manages units and their profiles from the TTS JSON data."""
    
    def __init__(self):
        """Initialize the unit manager."""
        self.units: List[Unit] = []
        self.json_data: Optional[Dict[str, Any]] = None
    
    def load_json(self, json_data: Dict[str, Any]) -> None:
        """
        Load unit data from JSON.
        
        Args:
            json_data: The TTS JSON data
        """
        self.json_data = json_data
        self.units = []
        self._group_units()
    
    def _group_units(self) -> None:
        """Group models that belong to the same unit."""
        if not self.json_data or "ObjectStates" not in self.json_data:
            return
            
        unit_map: Dict[str, Unit] = {}
        
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
                unit_map[base_name] = Unit(base_name)
            
            # Check if this profile matches an existing one
            unit = unit_map[base_name]
            description = obj.get("Description", "")
            profile_name = variant if variant else "Standard"
            
            # Try to find a matching profile
            matching_profile = None
            for profile in unit.profiles:
                if (profile.name == profile_name and 
                    profile.description == description):
                    matching_profile = profile
                    break
            
            if matching_profile:
                # Update existing profile
                matching_profile.count += 1
                matching_profile.identical_indices.append(i)
            else:
                # Add new profile
                profile = UnitProfile(
                    index=i,
                    name=profile_name,
                    nickname=nickname,
                    description=description
                )
                unit.add_profile(profile)
        
        # Convert map to list and sort alphabetically
        self.units = sorted(list(unit_map.values()), key=lambda x: x.name.lower())
    
    def save_profile_changes(self, unit_index: int, profile_index: int, new_description: str) -> None:
        """
        Save changes to a profile's description.
        
        Args:
            unit_index: The index of the unit in the units list
            profile_index: The index of the profile in the unit's profiles list
            new_description: The new description text
        """
        if not self.json_data or not self.units:
            return
        
        if unit_index < 0 or unit_index >= len(self.units):
            return
            
        unit = self.units[unit_index]
        if profile_index < 0 or profile_index >= len(unit.profiles):
            return
            
        profile = unit.profiles[profile_index]
        
        # Update the profile's description and all identical profiles
        profile = unit.profiles[profile_index]
        profile.description = new_description
        
        # Update all identical profiles in the JSON data
        for obj_index in profile.identical_indices:
            self.json_data["ObjectStates"][obj_index]["Description"] = new_description
