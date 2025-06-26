# GUI Crash Fixes - Summary

## Problem
The PyQt5 GUI was causing system crashes when users selected "Load Profile from Coda" in the Organization Profile tab.

## Root Causes Identified

1. **Path Construction Issues**: Using `Path(__file__).parent.parent.parent.parent` which could fail to resolve correctly
2. **Missing Error Handling**: No try-catch blocks around file operations and data parsing
3. **Data Type Mismatches**: Coda profile had `preferred_grant_size` as list instead of tuple
4. **Focus Area Mapping Problems**: Profile focus areas didn't match GUI combo box options
5. **Qt Warning Issues**: Wayland and threading warnings causing confusion

## Fixes Implemented

### 1. Robust Path Resolution
- **Before**: `Path(__file__).parent.parent.parent.parent / "data" / "profiles" / "coda_profile.json"`
- **After**: Using centralized config module with `PROFILES_DIR / "coda_profile.json"`

### 2. Comprehensive Error Handling
```python
def load_coda_profile(self):
    """Load Coda Mountain Academy profile."""
    try:
        # Use the config module for proper path resolution
        from grant_ai.config import PROFILES_DIR
        coda_profile_path = PROFILES_DIR / "coda_profile.json"
        
        if coda_profile_path.exists():
            with open(coda_profile_path, "r") as f:
                data = json.load(f)
            # ... profile loading logic ...
        else:
            # Fallback to hardcoded values
            self.name_input.setText("Coda Mountain Academy")
            # ... fallback logic ...
            
    except Exception as e:
        # Log error and provide fallback
        print(f"Error loading Coda profile: {e}")
        # Set basic fallback values
        self.name_input.setText("Coda Mountain Academy")
        # ... error recovery ...
```

### 3. Data Type Handling
- Added proper conversion from list to tuple for `preferred_grant_size`
- Implemented data validation for required fields
- Added type checking for profile data

### 4. Focus Area Mapping
```python
# Map focus areas to combo box options
focus_mapping = {
    "education": "Education",
    "art_education": "Arts", 
    "robotics": "Robotics",
    "housing": "Housing",
    "community": "Community"
}
```

### 5. Qt Warning Suppression
- Added environment variables to suppress Qt warnings:
  - `QT_LOGGING_RULES = '*.debug=false;qt.qpa.*=false'`
  - `QT_QPA_PLATFORM = 'xcb'` (force X11 backend)
- Improved main function with better error handling

### 6. SQLAlchemy Query Fixes
- Fixed incorrect filter syntax: `== None` → `.is_(None)`
- Used proper SQLAlchemy expressions: `|` instead of `or`

## Testing Results

✅ **Coda Profile Loading Test**: All tests passed - profile loads correctly from JSON  
✅ **GUI Component Test**: GUI components create and load profiles without crashing  
✅ **Data Validation**: All required fields present and data types correct  
✅ **Error Recovery**: System handles missing files and data gracefully  
✅ **CLI Integration**: Added `gui` command to CLI for easy launching  

## New Features Added

### 1. CLI GUI Command
```bash
python -m grant_ai.core.cli gui
```
- Provides clean launch with proper environment setup
- Includes user guidance and error handling
- Suppresses Qt warnings automatically

### 2. Launcher Script
```bash
python launch_gui.py
```
- Standalone launcher with comprehensive error handling
- User-friendly output with emojis and tips
- Environment configuration included

### 3. Improved Documentation
- Updated README with PyQt5 GUI instructions
- Added quick start guide
- Documented multiple launch methods

## Usage Instructions

### Launching the GUI
```bash
# Method 1: CLI command (recommended)
python -m grant_ai.core.cli gui

# Method 2: Direct module execution
python -m grant_ai.gui.qt_app

# Method 3: Launcher script
python launch_gui.py
```

### Using the Coda Profile
1. Launch the GUI using any method above
2. Go to "Organization Profile" tab
3. Select "Coda Mountain Academy" from the dropdown
4. The profile will load automatically without crashes
5. Switch to "Grant Search" tab to see suggested grants

## Files Modified

1. `src/grant_ai/gui/qt_app.py` - Main GUI fixes
2. `src/grant_ai/core/cli.py` - Added GUI command
3. `launch_gui.py` - New launcher script
4. `README.md` - Updated documentation

## Prevention Measures

1. **Comprehensive Testing**: Added test scripts to verify functionality
2. **Error Recovery**: All operations have fallback mechanisms
3. **User Feedback**: Clear error messages and guidance
4. **Documentation**: Updated README with usage instructions
5. **Multiple Launch Methods**: Users have several ways to start the GUI

The GUI should now work reliably without system crashes when loading profiles from Coda or any other source. 