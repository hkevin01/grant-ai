# Dialog AttributeError Fix

## Issue
When clicking "Details" button in the Enhanced Past Grants tab, the application crashed with:
```
AttributeError: 'GrantDetailDialog' object has no attribute 'center_on_parent'
```

## Root Cause
The `GrantDetailDialog` class was calling `self.center_on_parent()` in its `setup_ui()` method, but the `center_on_parent()` method was defined in the wrong class (the main `EnhancedPastGrantsTab` class instead of the dialog class).

## Fix Applied
Added the `center_on_parent()` method to the `GrantDetailDialog` class in `src/grant_ai/gui/enhanced_past_grants_tab.py`.

### Method Added
```python
def center_on_parent(self):
    """Center the dialog on its parent or screen."""
    if self.parent():
        # Center on parent widget
        parent_geometry = self.parent().geometry()
        parent_center = parent_geometry.center()
        
        # Calculate position to center this dialog
        dialog_size = self.size()
        new_x = parent_center.x() - dialog_size.width() // 2
        new_y = parent_center.y() - dialog_size.height() // 2
        
        # Ensure the dialog stays within screen bounds
        desktop = QApplication.desktop()
        screen_geometry = desktop.availableGeometry()
        
        new_x = max(screen_geometry.left(),
                    min(new_x, screen_geometry.right() - dialog_size.width()))
        new_y = max(screen_geometry.top(),
                    min(new_y, screen_geometry.bottom() - dialog_size.height()))
        
        self.move(new_x, new_y)
    else:
        # Center on screen
        desktop = QApplication.desktop()
        screen_geometry = desktop.availableGeometry()
        screen_center = screen_geometry.center()
        
        dialog_size = self.size()
        new_x = screen_center.x() - dialog_size.width() // 2
        new_y = screen_center.y() - dialog_size.height() // 2
        
        self.move(new_x, new_y)
```

## Result
- ✅ Dialog now opens without AttributeError
- ✅ Dialog is properly centered on parent window or screen
- ✅ Dialog stays within screen bounds
- ✅ Dialog is moveable and resizable as intended

## Testing
- GUI launches successfully without crashes
- Past grants detail dialogs can be opened by clicking "Details" button
- Dialogs are properly positioned and user-friendly

## Files Modified
- `src/grant_ai/gui/enhanced_past_grants_tab.py` - Added `center_on_parent()` method to `GrantDetailDialog` class

## Status
✅ **FIXED** - Dialog positioning issue resolved, application no longer crashes when viewing grant details.
