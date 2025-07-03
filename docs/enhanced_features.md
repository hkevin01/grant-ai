# Grant AI Enhanced Features - Fix for VS Code Force Quit Issues

## Overview

The Grant AI project has been enhanced with robust error handling, AI-powered features, and threading improvements to fix issues that were causing VS Code to force quit during searches. This document outlines the improvements and how to use them.

## Issues Fixed

### 1. VS Code Force Quit During Searches
**Problem**: Long-running synchronous search operations were blocking the main thread, causing VS Code to become unresponsive and force quit.

**Solution**: 
- Implemented threaded search operations using PyQt5 QThread
- Added progress indicators and status updates
- Enabled search cancellation
- Added comprehensive error handling

### 2. Web Scraping Failures
**Problem**: The scraping operations were encountering 403 Forbidden, 404 Not Found, and DNS resolution errors without proper recovery.

**Solution**:
- Created `RobustWebScraper` with retry logic and fallback URLs
- Added user agent rotation to avoid detection
- Implemented domain cooldown and failure tracking
- Added comprehensive error handling for different HTTP status codes

### 3. Limited Grant Matching Intelligence
**Problem**: Basic keyword matching was not providing relevant results.

**Solution**:
- Integrated AI-powered semantic similarity using sentence transformers
- Added intelligent search term suggestions
- Implemented form auto-fill capabilities
- Created AI-enhanced grant ranking and filtering

## New Features

### 1. AI Assistant Service (`ai_assistant.py`)
- **Semantic Grant Matching**: Uses sentence transformers for intelligent grant-organization matching
- **Auto-fill Suggestions**: Automatically suggests form field values based on organization profile
- **Search Term Generation**: Generates relevant search terms from organization descriptions
- **Grant Requirement Extraction**: Uses NLP to extract and structure grant requirements

### 2. Robust Web Scraper (`robust_scraper.py`)
- **Error Recovery**: Handles 403, 404, DNS, and timeout errors gracefully
- **Fallback URLs**: Tries alternative URLs when primary sources fail
- **Rate Limiting Protection**: Implements delays and backoff strategies
- **Domain Health Tracking**: Tracks failed domains and implements cooldown periods

### 3. Enhanced Threading (`enhanced_threading.py`)
- **Background Search**: Runs all search operations in background threads
- **Progress Tracking**: Real-time progress updates and status messages
- **Search Cancellation**: Ability to stop long-running searches
- **Error Isolation**: Prevents errors in one operation from crashing the GUI

## Installation and Setup

### 1. Install AI Dependencies
```bash
# Using the run script (recommended)
./run.sh setup-ai

# Or manually
pip install -r requirements-ai.txt
python -m spacy download en_core_web_sm
```

### 2. Test AI Features
```bash
# Test AI functionality
./run.sh test-ai

# Run enhanced search demo
./run.sh demo-search
```

### 3. Launch Enhanced GUI
```bash
# Launch GUI with AI features and threading
./run.sh gui-enhanced

# Or launch basic GUI
./run.sh gui
```

## Usage

### Enhanced Grant Search
1. **Load Organization Profile**: Go to Organization Profile tab and load a profile
2. **Start Intelligent Search**: Click "🔍 Intelligent Grant Search" button
3. **Monitor Progress**: Watch real-time status updates in the status text area
4. **View Results**: Results are automatically ranked by AI relevance

### AI-Powered Features
- **Automatic Form Filling**: AI suggests values for grant application forms
- **Smart Search Terms**: AI generates relevant search terms from your organization profile
- **Semantic Matching**: AI finds grants that are conceptually similar to your needs
- **Grant Analysis**: AI extracts key requirements and eligibility criteria from grants

### Robust Error Handling
- **Automatic Retries**: Failed requests are automatically retried with backoff
- **Fallback Sources**: Alternative URLs are tried when primary sources fail
- **Graceful Degradation**: System continues working even when some features fail
- **User Feedback**: Clear error messages and status updates

## Configuration

### AI Model Configuration
The AI assistant uses lightweight, CPU-compatible models by default:
- **Sentence Transformers**: `all-MiniLM-L6-v2` for semantic similarity
- **spaCy**: `en_core_web_sm` for NLP tasks
- **TextBlob**: For basic text processing

### Threading Configuration
- **Search Timeout**: 30 seconds per source (configurable)
- **Progress Updates**: Real-time status messages
- **Thread Safety**: All operations are thread-safe

### Web Scraping Configuration
- **Retry Strategy**: 3 retries with exponential backoff
- **Timeout**: 10 seconds connect, 30 seconds read
- **User Agent Rotation**: 5 different user agents
- **Domain Cooldown**: 5 minutes for failed domains

## Troubleshooting

### AI Features Not Working
```bash
# Check AI status
python -c "from grant_ai.services.ai_assistant import AIAssistant; print(AIAssistant().get_status())"

# Reinstall AI dependencies
./run.sh setup-ai
```

### GUI Still Crashing
```bash
# Use basic GUI without threading
./run.sh gui

# Check for Qt issues
export QT_LOGGING_RULES='*.debug=false;qt.qpa.*=false'
./run.sh gui-enhanced
```

### Search Taking Too Long
- Use the enhanced GUI which allows search cancellation
- Check network connectivity
- Review scraper health: `python -c "from grant_ai.services.robust_scraper import RobustWebScraper; print(RobustWebScraper().health_check())"`

## Performance Improvements

### Search Speed
- **Parallel Processing**: Multiple sources searched simultaneously
- **Intelligent Caching**: Results cached to avoid duplicate searches
- **Smart Filtering**: AI pre-filters results for relevance

### Memory Usage
- **Efficient Models**: Lightweight AI models that run on CPU
- **Background Processing**: Heavy operations moved to background threads
- **Resource Cleanup**: Automatic cleanup of threads and resources

### Network Efficiency
- **Smart Retries**: Only retry operations that are likely to succeed
- **Domain Tracking**: Avoid repeatedly hitting failed domains
- **Rate Limiting**: Respectful delays between requests

## Development Notes

### Adding New AI Features
1. Extend `AIAssistant` class with new methods
2. Update `enhanced_threading.py` to include new features in search workflow
3. Add tests in `test_ai_features.py`

### Adding New Scrapers
1. Inherit from `RobustWebScraper` 
2. Define selectors for grant extraction
3. Implement fallback URLs
4. Add to search workflow in `enhanced_threading.py`

### Debugging
- Enable detailed logging: `logging.basicConfig(level=logging.DEBUG)`
- Use AI status checks: `ai_assistant.get_status()`
- Check scraper health: `robust_scraper.health_check()`

## Future Enhancements

### Planned Features
1. **GPU Acceleration**: Optional GPU support for faster AI processing
2. **Advanced NLP**: Integration with larger language models
3. **Machine Learning**: Learning from user preferences and feedback
4. **API Integration**: Direct integration with foundation and government APIs

### Performance Optimizations
1. **Caching Layer**: Persistent caching of search results
2. **Database Optimization**: Improved database queries and indexing
3. **Distributed Processing**: Support for multiple worker processes

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the GUI status area
3. Run diagnostic commands: `./run.sh test-ai`
4. Check the GitHub issues page

The enhanced Grant AI system is designed to be robust, intelligent, and user-friendly while preventing the crashes and errors that were previously causing VS Code to force quit during searches.
