# 🧠 META MINDS - Quick Start Guide

## One-Command Launch

Simply run this single command to start Meta Minds:

```bash
py src\core\main.py
```

That's it! The system will automatically:
- ✅ Check Python version compatibility
- ✅ Set up your OpenAI API key (optional - offline mode available)
- ✅ Install missing dependencies
- ✅ Launch the application with hybrid input system
- ✅ Handle rate limiting with offline fallback mode

## What You Need

1. **Python 3.13+** (the system will check this)
2. **OpenAI API key** (optional - offline mode available)
3. **Input system setup** (optional but recommended for better quality)

## First Time Setup

When you run `py src\core\main.py` for the first time:

1. The system will check if you have an API key
2. If not found, it will prompt you to enter it (optional)
3. Your API key will be automatically saved to a `.env` file
4. Dependencies will be installed if missing
5. Meta Minds will launch with hybrid input system
6. Offline fallback mode will be available if API issues occur

## Alternative Ways to Run

```bash
# Main launcher (recommended)
py src\core\main.py

# With virtual environment
.\venv\Scripts\Activate.ps1
py src\core\main.py

# With input system setup
# 1. Create input/ folder
# 2. Add Business_Background.txt, Dataset_Background.txt, and message.txt
# 3. Run: py src\core\main.py

# Direct CLI
python src\core\main.py
```

## Supported Data Formats

- CSV files
- Excel files (.xlsx) 
- JSON files

## Analysis Modes

1. **SMART Enhanced Analysis** (Recommended)
   - Context-aware question generation
   - Hybrid input system integration
   - Quality validation and scoring
   - Business context integration
   - Offline fallback mode

2. **Offline Mode** (Automatic)
   - Context-aware fallback questions
   - 100% reliability
   - No API dependencies

## Get Your OpenAI API Key (Optional)

1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key
3. Run `py src\core\main.py` and enter the key when prompted

**Note**: API key is optional - the system includes offline fallback mode for 100% reliability!

The system makes everything easy with hybrid input system and offline fallback mode! 🚀
