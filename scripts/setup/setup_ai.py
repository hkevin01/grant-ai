#!/usr/bin/env python3
"""
Setup script for AI models and dependencies for Grant Research AI Project.
"""
import logging
import subprocess
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def install_requirements():
    """Install AI requirements."""
    try:
        requirements_file = Path(__file__).parent / "requirements-ai.txt"
        
        if not requirements_file.exists():
            logger.error("requirements-ai.txt not found!")
            return False
        
        logger.info("Installing AI dependencies...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ AI dependencies installed successfully")
            return True
        else:
            logger.error(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error installing requirements: {e}")
        return False


def download_spacy_model():
    """Download spaCy English language model."""
    try:
        logger.info("Downloading spaCy English model...")
        result = subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ spaCy model downloaded successfully")
            return True
        else:
            logger.warning(f"⚠️ spaCy model download failed: {result.stderr}")
            logger.info("You can manually install it later with: python -m spacy download en_core_web_sm")
            return False
            
    except Exception as e:
        logger.error(f"Error downloading spaCy model: {e}")
        return False


def test_ai_features():
    """Test if AI features are working correctly."""
    try:
        logger.info("Testing AI features...")
        
        # Test sentence transformers
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            test_text = "This is a test sentence"
            embedding = model.encode(test_text)
            logger.info("✅ Sentence transformers working")
        except Exception as e:
            logger.error(f"❌ Sentence transformers test failed: {e}")
            return False
        
        # Test spaCy
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp("This is a test sentence")
            logger.info("✅ spaCy model working")
        except Exception as e:
            logger.warning(f"⚠️ spaCy test failed: {e}")
            logger.info("spaCy features will be limited")
        
        # Test basic NLP
        try:
            from textblob import TextBlob
            blob = TextBlob("This is a test sentence")
            words = blob.words
            logger.info("✅ TextBlob working")
        except Exception as e:
            logger.warning(f"⚠️ TextBlob test failed: {e}")
        
        logger.info("🎉 AI setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing AI features: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("🚀 Setting up AI features for Grant Research AI...")
    
    # Step 1: Install requirements
    if not install_requirements():
        logger.error("Failed to install requirements. Exiting.")
        return 1
    
    # Step 2: Download spaCy model
    download_spacy_model()
    
    # Step 3: Test features
    if test_ai_features():
        logger.info("✅ AI setup completed successfully!")
        logger.info("You can now use the enhanced GUI with: python launch_enhanced_gui.py")
        return 0
    else:
        logger.warning("⚠️ AI setup completed with some issues.")
        logger.info("Basic functionality should still work.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
