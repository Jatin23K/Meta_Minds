# Meta Minds - AI-Powered Data Analysis Tool

![Meta Minds Logo](https://via.placeholder.com/150)  <!-- Replace with your actual logo -->

## 📝 Overview
Meta Minds is an intelligent data analysis tool that leverages AI to automatically generate insightful questions and analyses from your datasets. Features hybrid input system, offline fallback mode, and context-aware question generation. It's designed to help data analysts and researchers quickly understand their data and generate meaningful analytical questions with executive-ready insights.

## ✨ Features

- **Multi-format Support**: Works with CSV, Excel, and JSON files
- **AI-Powered Analysis**: Uses advanced AI to understand your data
- **Automated Question Generation**: Generates relevant analytical questions
- **Comparative Analysis**: Compares multiple datasets to find insights
- **Detailed Summaries**: Provides comprehensive data summaries and statistics
- **Hybrid Input System**: File-based context + interactive prompts
- **Offline Fallback Mode**: Robust operation without API access
- **Context-Aware Questions**: Business background integration
- **Rate Limiting Handling**: Automatic fallback and graceful degradation

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- Git
- OpenAI API key (optional - offline mode available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/meta-minds.git
   cd meta-minds
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. **Set up input system (optional but recommended)**
   Create an `input/` folder with context files:
   ```
   input/
   ├── Business_Background.txt    # Project context, objectives, audience
   ├── Dataset_Background.txt     # Dataset-specific context and details
   └── message.txt               # Senior stakeholder instructions
   ```

## 🛠️ Usage

1. **Run the application**
   ```bash
   py src\core\main.py
   ```

2. **Follow the prompts**
   - System reads context from `input/` folder (if available)
   - Enter the number of datasets you want to analyze
   - Provide the full paths to your dataset files
   - View the generated analysis in the console and in `Output/` folder
   - Offline mode activates automatically if API limits reached

## 📂 Project Structure

```
1. META_MINDS/
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
├── README.md               # Main documentation
├── requirements.txt        # Python dependencies
├── input/                  # Input system folder
│   ├── Business_Background.txt    # Project context
│   ├── Dataset_Background.txt     # Dataset-specific context
│   └── message.txt               # Senior instructions
├── src/
│   └── core/
│       ├── main.py         # Main application entry point
│       ├── context_collector.py  # Hybrid context collection
│       ├── data_analyzer.py      # Data analysis functions
│       ├── agents.py             # AI agent definitions
│       ├── tasks.py              # Task definitions
│       ├── output_handler.py     # Output management
│       └── smart_question_generator.py  # SMART methodology
├── Output/                 # Generated reports
├── examples/               # Sample outputs and demos
└── docs/                   # Documentation
```

## 🤖 AI Agents

### Schema Sleuth
- Analyzes data structure and schema
- Identifies data types and patterns
- Provides high-level dataset overview

### Curious Catalyst
- Generates insightful analytical questions
- Identifies trends and anomalies
- Suggests potential areas for deeper analysis
- Context-aware question generation
- Offline fallback capabilities

## 📊 Example Output

```
--- Dataset: sales_data.csv ---
• Rows: 10,000
• Columns: 15
• Analysis complete

--- Questions for sales_data.csv ---
1. What is the correlation between marketing spend and sales revenue?
2. Which product category has the highest profit margin?
3. How do sales vary by region and season?
...
```
