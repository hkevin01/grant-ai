#!/bin/bash

# Screenshot capture script for Grant AI application
# This script captures screenshots of the Grant AI GUI for documentation

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if screenshot tools are available
check_screenshot_tools() {
    if command -v gnome-screenshot &> /dev/null; then
        SCREENSHOT_TOOL="gnome-screenshot"
    elif command -v scrot &> /dev/null; then
        SCREENSHOT_TOOL="scrot"
    elif command -v import &> /dev/null; then
        SCREENSHOT_TOOL="import"  # ImageMagick
    else
        print_error "No screenshot tool found. Please install gnome-screenshot, scrot, or ImageMagick"
        print_status "Install with: sudo apt-get install gnome-screenshot"
        exit 1
    fi
    
    print_status "Using screenshot tool: $SCREENSHOT_TOOL"
}

# Capture screenshot function
capture_screenshot() {
    local filename="$1"
    local delay="$2"
    
    print_status "Capturing screenshot: $filename (waiting ${delay}s)"
    
    case $SCREENSHOT_TOOL in
        "gnome-screenshot")
            gnome-screenshot --delay=$delay --file="docs/images/$filename"
            ;;
        "scrot")
            sleep $delay
            scrot "docs/images/$filename"
            ;;
        "import")
            sleep $delay
            import -window root "docs/images/$filename"
            ;;
    esac
    
    if [ -f "docs/images/$filename" ]; then
        print_status "✅ Screenshot saved: docs/images/$filename"
    else
        print_error "❌ Failed to capture screenshot: $filename"
    fi
}

# Main screenshot capture workflow
main() {
    print_status "📸 Grant AI Screenshot Capture"
    echo ""
    
    # Check for screenshot tools
    check_screenshot_tools
    
    # Create images directory if it doesn't exist
    mkdir -p docs/images
    
    print_status "🚀 Starting Grant AI GUI..."
    
    # Start the GUI application in background
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Launch GUI
    python -m grant_ai.gui.qt_app &
    GUI_PID=$!
    
    print_warning "Please wait for the GUI to fully load..."
    sleep 3
    
    echo ""
    print_status "📷 Ready to capture screenshots!"
    echo ""
    echo "Screenshots to capture:"
    echo "1. Main application window"
    echo "2. Grant Search tab"
    echo "3. Organization Profile tab"
    echo "4. Application Tracking tab"
    echo ""
    
    # Capture main window
    print_status "Position the main Grant AI window and press Enter..."
    read -p "Press Enter when ready to capture main window..."
    capture_screenshot "main-window.png" 2
    
    # Capture grant search tab
    print_status "Switch to Grant Search tab and press Enter..."
    read -p "Press Enter when ready to capture Grant Search tab..."
    capture_screenshot "grant-search-tab.png" 2
    
    # Capture organization profile tab
    print_status "Switch to Organization Profile tab and press Enter..."
    read -p "Press Enter when ready to capture Organization Profile tab..."
    capture_screenshot "organization-profile-tab.png" 2
    
    # Capture application tracking tab
    print_status "Switch to Applications tab and press Enter..."
    read -p "Press Enter when ready to capture Applications tab..."
    capture_screenshot "application-tracking-tab.png" 2
    
    # Optional: Enhanced past grants tab
    print_status "Switch to Enhanced Past Grants tab (optional) and press Enter..."
    read -p "Press Enter when ready to capture Enhanced Past Grants tab (or Ctrl+C to skip)..."
    capture_screenshot "enhanced-past-grants-tab.png" 2
    
    # Clean up
    print_status "🛑 Stopping GUI application..."
    kill $GUI_PID 2>/dev/null || true
    
    # Show results
    echo ""
    print_status "📸 Screenshot capture complete!"
    echo ""
    print_status "Captured screenshots:"
    ls -la docs/images/*.png 2>/dev/null || print_warning "No screenshots found"
    
    echo ""
    print_status "🔧 Next steps:"
    echo "1. Review screenshots in docs/images/"
    echo "2. Edit any screenshots if needed"
    echo "3. Run: ./scripts/update_readme_screenshots.sh"
    echo "4. Commit screenshots to git: git add docs/images/ && git commit -m 'Add application screenshots'"
}

# Run main function
main "$@"
