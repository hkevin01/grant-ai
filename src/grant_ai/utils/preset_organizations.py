"""
Preset Organization Manager for Grant AI GUI
Handles loading and managing preset organization profiles efficiently.
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from grant_ai.config import PROFILES_DIR


@dataclass
class PresetOrganization:
    """Data class for preset organization information."""
    name: str
    display_name: str
    file_path: Path
    description: str
    focus_area: str
    location: str


class PresetOrganizationManager:
    """Manages preset organization profiles for quick loading in the GUI."""
    
    def __init__(self):
        self.profiles_dir = PROFILES_DIR
        self._presets_cache: Optional[List[PresetOrganization]] = None
        self._profile_data_cache: Dict[str, Dict[str, Any]] = {}
        
    def get_available_presets(self) -> List[PresetOrganization]:
        """Get all available preset organizations."""
        if self._presets_cache is not None:
            return self._presets_cache
            
        presets = []
        
        # Add custom organization option
        presets.append(PresetOrganization(
            name="custom",
            display_name="Custom Organization",
            file_path=Path(""),
            description="Start with a blank form to create your own organization profile",
            focus_area="Custom",
            location="Custom"
        ))
        
        # Scan profiles directory for available organizations
        if self.profiles_dir.exists():
            for profile_file in self.profiles_dir.glob("*.json"):
                try:
                    # Load basic info without full profile data
                    with open(profile_file, "r") as f:
                        data = json.load(f)
                    
                    # Handle both single objects and lists
                    organizations = []
                    if isinstance(data, list):
                        # File contains a list of organizations
                        organizations = data
                        # Use filename as prefix for organization names
                        file_prefix = profile_file.stem.replace("_", " ").title()
                    else:
                        # File contains a single organization
                        organizations = [data]
                        file_prefix = ""
                    
                    for i, org_data in enumerate(organizations):
                        if not isinstance(org_data, dict):
                            continue
                            
                        # Extract focus area for display
                        focus_areas = org_data.get("focus_areas", [])
                        focus_area = "Other"
                        if focus_areas:
                            # Map focus areas to display names
                            focus_mapping = {
                                "education": "Education",
                                "art_education": "Arts & Education", 
                                "robotics": "STEM & Robotics",
                                "housing": "Housing",
                                "community": "Community Development",
                                "healthcare": "Healthcare",
                                "music": "Music & Arts",
                                "senior_services": "Senior Services",
                                "youth_development": "Youth Development",
                                "social_services": "Social Services",
                                "affordable_housing": "Affordable Housing",
                                "music_education": "Music Education"
                            }
                            for fa in focus_areas:
                                if fa in focus_mapping:
                                    focus_area = focus_mapping[fa]
                                    break
                            else:
                                focus_area = focus_areas[0].replace("_", " ").title()
                        
                        # Truncate description if too long
                        description = org_data.get("description", "")
                        if len(description) > 100:
                            description = description[:100] + "..."
                        
                        # Create display name
                        display_name = org_data.get("name", "")
                        if not display_name and file_prefix:
                            display_name = f"{file_prefix} Organization {i+1}"
                        
                        # Create unique name for caching
                        if len(organizations) > 1:
                            # Multiple organizations in file - use index
                            unique_name = f"{profile_file.stem}_{i}"
                        else:
                            # Single organization - use filename
                            unique_name = profile_file.stem
                        
                        presets.append(PresetOrganization(
                            name=unique_name,
                            display_name=display_name,
                            file_path=profile_file,
                            description=description,
                            focus_area=focus_area,
                            location=org_data.get("location", "Not specified")
                        ))
                    
                except Exception as e:
                    print(f"Error loading preset info from {profile_file}: {e}")
                    continue
        
        # Sort presets alphabetically by display name, but keep custom first
        custom_preset = presets[0] if presets else None
        other_presets = sorted(presets[1:], key=lambda x: x.display_name.lower())
        
        if custom_preset:
            presets = [custom_preset] + other_presets
        
        self._presets_cache = presets
        return presets
    
    def load_preset_profile(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific preset profile by name."""
        if preset_name == "custom":
            return self._get_empty_profile()
        
        # Check cache first
        if preset_name in self._profile_data_cache:
            return self._profile_data_cache[preset_name]
        
        # Find the preset
        presets = self.get_available_presets()
        preset = next((p for p in presets if p.name == preset_name), None)
        
        if not preset or not preset.file_path.exists():
            return None
        
        try:
            with open(preset.file_path, "r") as f:
                data = json.load(f)
            
            # Handle both single objects and lists
            if isinstance(data, list):
                # Extract the specific organization from the list
                if "_" in preset_name:
                    # Format: filename_index
                    parts = preset_name.split("_")
                    if len(parts) >= 2:
                        try:
                            index = int(parts[-1])
                            if 0 <= index < len(data):
                                org_data = data[index]
                            else:
                                return None
                        except ValueError:
                            return None
                    else:
                        return None
                else:
                    # Single organization from list file
                    org_data = data[0] if data else None
            else:
                # Single organization object
                org_data = data
            
            if not org_data:
                return None
            
            # Cache the data
            self._profile_data_cache[preset_name] = org_data
            return org_data
            
        except Exception as e:
            print(f"Error loading preset profile {preset_name}: {e}")
            return None
    
    def _get_empty_profile(self) -> Dict[str, Any]:
        """Get an empty profile template."""
        return {
            "name": "",
            "description": "",
            "focus_areas": [],
            "program_types": [],
            "target_demographics": [],
            "annual_budget": None,
            "location": "",
            "website": "",
            "ein": "",
            "founded_year": None,
            "preferred_grant_size": [10000, 100000],
            "grant_history": [],
            "contact_name": "",
            "contact_email": "",
            "contact_phone": ""
        }
    
    def clear_cache(self):
        """Clear the profile data cache."""
        self._profile_data_cache.clear()
        self._presets_cache = None
    
    def get_preset_by_display_name(self, display_name: str) -> Optional[PresetOrganization]:
        """Get a preset by its display name."""
        presets = self.get_available_presets()
        return next((p for p in presets 
                    if p.display_name == display_name), None)


# Global instance for easy access
preset_manager = PresetOrganizationManager() 