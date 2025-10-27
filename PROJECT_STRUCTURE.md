# 📁 **META MINDS - Project Structure Documentation**

This document provides a comprehensive overview of the Meta Minds project structure, file organization, and component responsibilities.

---

## 🏗️ **Overall Architecture** (v2.0 - 10/10 Rating)

```
1. META_MINDS/
├── 📂 src/                   # Complete source code
│   └── 📂 core/              # Core analysis engine (v2.0)
│       ├── main.py                    # Main orchestrator with CLI support
│       ├── config.py                  # Configuration management
│       ├── data_loader.py             # Multi-format data loading with safety limits
│       ├── data_analyzer.py           # 🆕 Intelligent column analysis
│       ├── output_handler.py          # Report generation + export integration
│       ├── emoji_utils.py             # 🆕 Professional emoji system
│       ├── export_utils.py            # 🆕 Excel/JSON/HTML export functions
│       ├── cli_handler.py             # 🆕 CLI automation support
│       ├── agents.py                  # CrewAI agent definitions
│       ├── tasks.py                   # Task orchestration + question trimming
│       ├── smart_question_generator.py # SMART engine with enhanced context
│       ├── smart_validator.py         # Quality control & validation
│       └── context_collector.py       # 17 templates + 6 enhanced questions
├── 📂 input/                 # Hybrid input system (3 template files)
│   ├── Business_Background.txt    # Project context template
│   ├── Dataset_Background.txt     # Dataset-specific context template
│   └── Message.txt               # Senior stakeholder instructions template
├── 📂 dataset/               # Sample datasets (for testing)
├── 📂 Output/                # Generated reports (git-ignored)
│   ├── Individual_*.txt          # Individual dataset reports
│   ├── Cross-Dataset_*.txt       # Cross-dataset comparison reports
│   ├── *.xlsx                    # 🆕 Excel exports
│   ├── *.json                    # 🆕 JSON exports
│   └── *.html                    # 🆕 HTML dashboards
├── 📂 docs/                  # Comprehensive documentation
├── 📂 examples/              # Examples and demos
├── 📂 workflows/             # Workflow definitions
├── 📄 .gitignore             # Git ignore rules
├── 📄 env.example            # Environment template
├── 📄 requirements.txt       # Python dependencies
├── 📄 README.md              # Project documentation (v2.0)
└── 📄 PROJECT_STRUCTURE.md   # This file
```

---

## 🆕 **What's New in v2.0 (10/10 Upgrade)**

### **Major Enhancements:**

#### **1. 🧠 Intelligent Column Analysis**
- **Before**: "Column 'YEAR' with sample values: 2013, 2013, 2013"
- **After**: "Temporal identifier representing calendar year. Range: 2013-2023. Used for time-series analysis."
- **Impact**: Meaningful insights instead of repetitive data
- **Auto-detects**: 15+ column types with statistical context

#### **2. 🖥️ Full CLI Automation**
```bash
# Quick mode - zero prompts
python main.py --quick --datasets data.csv --questions 20 --export-all

# Config mode - reusable settings  
python main.py --config my_analysis.json

# Batch mode - multiple analyses
python main.py --batch config_folder/
```
- **Impact**: Enables automation, scripting, CI/CD integration

#### **3. 📤 Multiple Export Formats**
- **TXT**: Professional reports (default)
- **Excel**: Multi-sheet workbooks with metadata
- **JSON**: Structured data for APIs
- **HTML**: Interactive dashboards with copy buttons
- **Impact**: Flexibility for different stakeholders

#### **4. 🎯 Exact Question Count Enforcement**
- **Before**: Request 13, get 15 (AI overgeneration)
- **After**: Request 13, get exactly 13 (forced trimming)
- **Impact**: Predictable output, no surprises

#### **5. 💎 Professional Emoji System**
- **Auto-detects** terminal encoding (UTF-8 vs cp1252)
- **UTF-8 terminals**: Beautiful emojis (🚀📊🔍)
- **Windows cmd**: Professional text symbols (>>[CHART][SEARCH])
- **Impact**: No more Unicode encoding errors

#### **6. 🏢 Enhanced Context Collection**
- **6 optional deep-dive questions** for 9.5/10 quality
- **Intelligent quality ranges** (7.5-8.0, 8.5-9.0, 9.0-9.5)
- **Skip/Must-Have/All/Custom** selection modes
- **Impact**: Flexible quality levels based on need

#### **7. 📁 Smart Output Management**
- Auto-detects correct Output folder location
- Multiple fallback directories if permission denied
- Shows exact file save location
- **Impact**: No more "file not found" issues

#### **8. 📊 Intelligent Recommendations**
- Auto-calculates recommended question count
- Based on data complexity (columns, rows)
- Shows dataset preview before asking for counts
- **Impact**: Better decisions, less guessing

---

## 📂 **Detailed Directory Structure**

### **📂 `src/core/` - Core Analysis Engine**

#### **🧠 Core Processing Files**

| File | Purpose | Key Features | Dependencies |
|------|---------|--------------|--------------|
| **`main.py`** | 🎯 **Main Orchestrator** | Entry point, CLI support, workflow coordination, offline mode, question count enforcement | All core modules |
| **`config.py`** | ⚙️ **Configuration Hub** | OpenAI client setup, logging configuration, environment management | `openai`, `logging` |
| **`data_loader.py`** | 📁 **Data Processing** | Multi-format file loading (CSV/Excel/JSON), safety limits, validation | `pandas`, `openpyxl` |
| **`data_analyzer.py`** | 🔍 **Dataset Analysis** | **Intelligent column analysis**, statistical insights, purpose detection | `pandas` |
| **`output_handler.py`** | 💾 **Report Generation** | Professional formatting, smart directory detection, export integration | `datetime`, `os` |
| **`emoji_utils.py`** | 🎨 **UI Enhancement** | Professional emoji system with automatic encoding detection & fallback | `sys`, `os` |
| **`export_utils.py`** | 📤 **Multi-Format Export** | Excel/JSON/HTML export functions, interactive dashboards | `pandas`, `json` |
| **`cli_handler.py`** | 🖥️ **CLI Interface** | Command-line arguments, config files, batch processing | `argparse`, `json` |

#### **🤖 AI & Agent Management**

| File | Purpose | Key Features | Dependencies |
|------|---------|--------------|--------------|
| **`agents.py`** | 🤖 **CrewAI Agents** | Schema Sleuth & Question Genius agent definitions, GPT-4 integration | `crewai`, `langchain_openai` |
| **`tasks.py`** | 📋 **Task Orchestration** | Dynamic task creation, **exact question count limiting**, validation workflows | `crewai` |
| **`smart_question_generator.py`** | 🧠 **SMART Engine** | Advanced question generation with diversity framework, enhanced context support | `openai`, `numpy`, `pandas` |
| **`smart_validator.py`** | ✅ **Quality Control** | Multi-layer validation, SMART compliance scoring, quality thresholds | `dataclasses`, `re` |
| **`context_collector.py`** | 📝 **Context Management** | 17 templates, 6 enhanced questions, intelligent quality ranges | `json`, `datetime` |

---

## 🔧 **Component Relationships**

### **📊 Data Flow Architecture**
```
User Input → Hybrid Context Collection → Data Loading → Analysis → AI Processing → Validation → Report Generation
     ↑              ↓                         ↓             ↓           ↓             ↓              ↓
   main.py → context_collector → data_loader → data_analyzer → agents → smart_validator → output_handler
     ↑              ↓                         ↓             ↓           ↓             ↓              ↓
  Offline Mode → input/ folder → fallback → offline → context-aware → quality → professional
```

### **🤖 AI Processing Pipeline**
```
Dataset Analysis → Question Generation → Quality Validation → Report Formatting
       ↓                    ↓                   ↓                    ↓
  data_analyzer → smart_question_generator → smart_validator → output_handler
       ↑                    ↑                   ↑                    ↑
   GPT-4 API         Diversity Framework    SMART Methodology    Professional Templates
       ↑                    ↑                   ↑                    ↑
  Offline Mode      Context-Aware Questions  Business Integration  Executive Focus
```

---

## 📋 **File-by-File Documentation**

### **🎯 `main.py` - Application Entry Point**
```python
# Main workflow orchestration
def main():
    # 1. Hybrid context collection & validation
    # 2. Dataset loading & processing  
    # 3. AI agent creation & configuration
    # 4. Task execution & monitoring
    # 5. Quality validation & scoring
    # 6. Report generation & output
    # 7. Offline fallback mode handling
```

**Key Functions:**
- `check_dependencies()` - Validates Python version, API keys, required packages
- `get_smart_analysis_context()` - Hybrid context collection from input files
- `_detect_rate_limiting()` - Automatic offline mode detection
- `_generate_offline_results()` - Offline fallback with context-aware questions
- `main()` - Primary workflow coordinator

### **⚙️ `config.py` - Configuration Management**
```python
# Core configuration settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

**Responsibilities:**
- Environment variable management
- OpenAI client initialization
- Logging configuration
- System-wide constants

### **📁 `data_loader.py` - Data Processing Engine**
```python
class DataLoader:
    def load_dataset(self, file_path: str) -> pd.DataFrame:
        # Multi-format support: CSV, Excel, JSON
        # Encoding detection and handling
        # Error recovery and validation
        # Memory optimization
```

**Key Features:**
- **Multi-format Support**: CSV, XLSX, JSON
- **Encoding Detection**: UTF-8, UTF-8-BOM, CP1252
- **Error Handling**: Graceful failure recovery
- **Validation**: Data integrity checks

### **🔍 `data_analyzer.py` - Intelligent Dataset Analysis**
```python
def _analyze_column_intelligently(column_name: str, series: pd.Series) -> str:
    # Intelligent column purpose detection
    # Statistical range analysis (min, max, avg, unique counts)
    # Type-specific insights generation
    # Context-aware descriptions
    
def generate_summary(df: pd.DataFrame) -> dict:
    # Intelligent column description generation (no GPT needed!)
    # Statistical summary creation
    # Data quality assessment
    # Business context integration
```

**Core Capabilities:**
- **Intelligent Column Analysis**: Auto-detects 15+ column types (Temporal, Financial, Identifiers, etc.)
- **Statistical Insights**: Min/Max/Avg/Unique counts with meaningful context
- **Purpose Detection**: Explains what each column is used for
- **No API Dependency**: Works 100% offline with intelligent analysis
- **Quality Assessment**: Completeness and validity checks

**Auto-Detected Column Types:**
- 📅 Temporal (Year, Quarter, Month, Date)
- 💰 Financial (Ratio, Revenue, Cost, Asset, Liability, Profit)
- 🔑 Identifiers (ID, Code, Carrier, Ticker)
- 📊 Categorical (Category, Type, Status, Location)
- ✓ Boolean (Flags, True/False fields)

### **🤖 `agents.py` - AI Agent Definitions**
```python
# Schema analysis agent
schema_sleuth = Agent(
    role='Data Structure Analyst',
    goal='Understand dataset structure and relationships',
    llm=gpt4_llm  # GPT-4 for premium quality
)

# Question generation agent  
question_genius = Agent(
    role='Analytical Question Generator',
    goal='Create insightful, SMART-compliant questions',
    llm=gpt4_llm
)
```

**Agent Responsibilities:**
- **Schema Sleuth**: Data structure analysis, relationship identification
- **Question Genius**: SMART question generation, context integration

### **📋 `tasks.py` - Task Management**
```python
def create_smart_tasks(datasets, schema_agent, question_agent, context, question_count):
    # Dynamic task creation based on datasets
    # SMART methodology integration
    # Quality validation workflows
    # Cross-dataset comparison tasks
```

**Task Types:**
- **Individual Analysis**: Dataset-specific question generation
- **Cross-Dataset**: Comparative analysis across multiple datasets
- **Validation**: Quality scoring and compliance checking

### **🧠 `smart_question_generator.py` - Question Generation Engine**
```python
class SmartQuestionGenerator:
    def generate_enhanced_questions(self, dataset_name, df, context, num_questions):
        # Diversity framework implementation
        # Business-specific templates
        # SMART methodology compliance
        # Quality optimization
```

**Core Features:**
- **Diversity Framework**: 5 analytical categories
- **Business Templates**: Industry-specific approaches
- **SMART Compliance**: Methodology enforcement
- **Quality Optimization**: 97%+ score targeting

**Question Categories:**
1. **📊 Descriptive Analysis** - Statistical summaries, outlier identification
2. **🔍 Comparative Analysis** - Benchmarking, segment comparison
3. **📈 Pattern Analysis** - Trends, forecasting, seasonality
4. **🎯 Business Impact** - Strategic insights, optimization
5. **🔗 Relationship Discovery** - Correlations, causality

### **✅ `smart_validator.py` - Quality Assurance**
```python
class SmartValidator:
    def validate_questions(self, questions, context):
        # Multi-layer quality scoring
        # SMART criteria validation  
        # Business relevance assessment
        # Diversity compliance checking
```

**Validation Layers:**
- **SMART Compliance**: 97% base score with component weighting
- **Clarity Assessment**: Readability and comprehension
- **Specificity Scoring**: Variable targeting and precision
- **Actionability Check**: Analytical verb usage
- **Relevance Validation**: Business context alignment

### **📝 `context_collector.py` - User Context Management**
```python
class DatasetContext:
    subject_area: str
    analysis_objectives: List[str]
    target_audience: str
    business_context: str
    time_sensitivity: str

def collect_context_hybrid():
    # 1. Read from input/ folder (Business_Background.txt, Dataset_Background.txt, message.txt)
    # 2. Fallback to interactive prompts if insufficient
    # 3. Combine for maximum context quality
```

**Hybrid Input System:**
- **Business_Background.txt** - Project context, objectives, audience
- **Dataset_Background.txt** - Dataset-specific context and details
- **message.txt** - Senior stakeholder instructions and strategic priorities
- **Interactive Fallback** - Traditional prompts if input files insufficient
- **Context Integration** - Combines file content with user preferences

**Context Templates:**
- **Financial Analysis** - Performance evaluation, risk assessment
- **Sales Analytics** - Pipeline analysis, performance tracking
- **Marketing Analytics** - Campaign effectiveness, segmentation
- **Operations** - Efficiency optimization, cost reduction
- **HR Analytics** - Performance analysis, retention
- **+ 12 additional industry templates**

### **💾 `output_handler.py` - Report Generation**
```python
def save_separate_reports(datasets, results, context):
    # Professional formatting
    # Timestamped file naming
    # Structured output organization
    # Quality metrics integration
```

**Output Features:**
- **Professional Formatting**: Executive-ready reports
- **Dynamic Naming**: Context-based file naming
- **Quality Integration**: Comprehensive scoring display
- **Structured Organization**: Categorized output folders

---

## 📊 **Configuration Files**

### **📄 `.env` - Environment Variables (Local Only)**
```bash
# Required (optional - offline mode available)
OPENAI_API_KEY=your_openai_api_key_here

# Optional
LOG_LEVEL=INFO
OUTPUT_DIRECTORY=Output
MAX_QUESTIONS_PER_DATASET=30
```

### **📄 `env.example` - Environment Template (GitHub)**
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional Configuration
LOG_LEVEL=INFO
OUTPUT_DIRECTORY=Output
MAX_QUESTIONS_PER_DATASET=30

# Instructions:
# 1. Copy this file to .env
# 2. Replace 'your_openai_api_key_here' with your actual OpenAI API key
# 3. The .env file will be ignored by git for security
```

### **📄 `user_context.json` - User Preferences (Local Only)**
```json
[
  {
    "subject_area": "financial analysis",
    "analysis_objectives": ["performance evaluation", "risk assessment"],
    "target_audience": "executives",
    "business_context": "quarterly reporting",
    "time_sensitivity": "medium",
    "timestamp": "2025-01-08T14:30:00"
  }
]
```

### **📄 `.gitignore` - Git Ignore Rules (GitHub)**
```gitignore
# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class

# Output files
Output/
*.txt
!requirements.txt

# User context (contains personal preferences)
user_context.json

# Input files (users should create their own)
input/Business_Background.txt
input/Dataset_Background.txt
input/message.txt
```

---

## 📈 **Output Structure**

### **📂 `Output/` - Generated Reports (Local Only)**
```
Output/ (excluded from GitHub)
├── Individual_Financialanalysis_Riskassessmentriskas_Executives_2025-09-10_21-05.txt
├── Cross-Dataset_Financialanalysis_Riskassessmentriskas_Executives_2025-09-10_21-05.txt
├── Individual_Salesperformance_Riskassessment_Managers_2025-01-08_16-45.txt
└── Cross-Dataset_Salesperformance_Riskassessment_Managers_2025-01-08_16-45.txt
```

**Features:**
- ✅ **Context-aware questions** with business background integration
- ✅ **Executive-focused language** and strategic orientation
- ✅ **Industry-specific terminology** and risk assessment focus
- ✅ **Offline mode capability** with 100% reliability

**Naming Convention:**
- **Format**: `[Type]_[Focus]_[Objective]_[Audience]_[DateTime].txt`
- **Type**: Individual | Cross-Dataset
- **Focus**: Business domain (e.g., Financialanalysis, Salesperformance)
- **Objective**: Analysis goal (e.g., Performanceevaluation, Riskassessment)
- **Audience**: Target users (e.g., Executives, Managers, Analysts)
- **DateTime**: YYYY-MM-DD_HH-MM format

---

## 🔄 **Dependencies & Requirements**

### **Core Dependencies**
```
pandas>=1.5.0          # Data manipulation and analysis
openai>=1.0.0          # GPT-4 API integration
crewai>=0.1.0          # Multi-agent orchestration
langchain-openai       # LangChain OpenAI integration
numpy>=1.21.0          # Numerical computing
openpyxl>=3.0.0        # Excel file support
python-dotenv>=0.19.0  # Environment variable management
```

### **Python Version**
- **Minimum**: Python 3.13+
- **Recommended**: Python 3.13.7
- **OS Support**: Windows, macOS, Linux

---

## 🛠️ **Development Guidelines**

### **Code Organization**
- **Modular Design**: Each file has single responsibility
- **Clear Interfaces**: Well-defined function signatures
- **Error Handling**: Comprehensive exception management
- **Documentation**: Inline comments and docstrings

### **Quality Standards**
- **Type Hints**: All functions use type annotations
- **Error Recovery**: Graceful failure handling
- **Logging**: Comprehensive activity tracking
- **Validation**: Input/output validation throughout

### **Extension Points**
- **New Business Templates**: Add to `context_collector.py`
- **Additional File Formats**: Extend `data_loader.py`
- **Custom Validation**: Enhance `smart_validator.py`
- **Output Formats**: Modify `output_handler.py`

---

## 📋 **Usage Patterns**

### **Standard Analysis Workflow**
1. **Hybrid Context Collection** → Input files + interactive prompts
2. **Dataset Loading** → Multi-file processing and validation
3. **AI Processing** → Context-aware question generation and quality scoring
4. **Offline Fallback** → Automatic fallback if API limits reached
5. **Report Generation** → Professional output formatting

### **Customization Options**
- **Question Counts**: Configurable per dataset and cross-dataset
- **Business Context**: 17+ predefined templates + hybrid input system
- **Quality Thresholds**: Adjustable scoring criteria
- **Output Format**: Customizable report structure
- **Input System**: File-based context + interactive prompts
- **Offline Mode**: 100% reliability with context-aware fallback

### **Integration Points**
- **API Integration**: Extensible for BI tool integration
- **Batch Processing**: Multiple analysis session support
- **Export Formats**: Ready for downstream processing

---

**This structure enables Meta Minds to deliver professional-grade AI-powered data analysis with hybrid input system, offline fallback mode, context-aware question generation, and enterprise scalability.** 🧠✨