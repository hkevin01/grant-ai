#!/usr/bin/env python3
"""Simple test to check if ML dependencies are available."""

def check_dependencies():
    """Check if required dependencies are available."""
    missing = []

    try:
        import sklearn
        print("✅ scikit-learn available")
    except ImportError:
        missing.append("scikit-learn")
        print("❌ scikit-learn missing")

    try:
        import textblob
        print("✅ textblob available")
    except ImportError:
        missing.append("textblob")
        print("❌ textblob missing")

    try:
        import numpy
        print("✅ numpy available")
    except ImportError:
        missing.append("numpy")
        print("❌ numpy missing")

    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install", " ".join(missing))
        return False
    else:
        print("\n🎉 All ML dependencies are available!")
        return True

if __name__ == "__main__":
    check_dependencies()
