# 📁 GitHub Folder Visibility Guide

This document explains what folders and files will be **visible** vs **hidden** on GitHub.

---

## ✅ **VISIBLE ON GITHUB** (What Users Will See)

### **📂 Folders:**
```
Meta_Minds_-Question_Generator-/
├── src/                          ✅ All source code
│   ├── core/                    ✅ Main application modules
│   ├── agents/                  ✅ AI agent definitions
│   ├── ml/                      ✅ ML and optimization
│   ├── ui/                      ✅ User interface
│   └── workflows/               ✅ Automation workflows
├── input/                        ✅ Context template folder (with README.md)
│   ├── README.md                ✅ Explains how to use templates
│   ├── Business_Background.txt  ✅ Example filled template
│   ├── Dataset_Background.txt   ✅ Example filled template
│   └── Message.txt              ✅ Example filled template
├── Output/                       ✅ Output folder (with README.md only)
│   └── README.md                ✅ Explains output format and structure
├── examples/                     ✅ Sample workflows and templates
├── dataset/                      ✅ Sample datasets (CSV files)
├── docs/                         ✅ Additional documentation
├── config/                       ✅ Configuration files
└── workflows/                    ✅ YAML workflow definitions
```

### **📄 Key Files:**
```
✅ README.md                     Main documentation
✅ PROJECT_STRUCTURE.md          Project architecture
✅ QUICK_START.md                Getting started guide
✅ requirements.txt              Python dependencies
✅ .gitignore                    Git exclusion rules
✅ main.py                       Main entry point
✅ launch.py                     Launcher script
✅ env.example                   Example environment variables
✅ All batch/shell scripts       Helper scripts for users
```

---

## ❌ **HIDDEN FROM GITHUB** (Excluded by .gitignore)

### **📂 Folders:**
```
❌ venv/                         Virtual environment (users create their own)
❌ __pycache__/                  Python bytecode cache
❌ logs/                         Log files (user-generated)
❌ .vscode/                      IDE settings
❌ .idea/                        IDE settings
❌ .cursor/                      Editor settings
```

### **📄 Files:**
```
❌ Output/*.txt                  Generated reports (user-specific)
❌ .env                          API keys and secrets (SECURITY)
❌ user_context.json             Personal user preferences
❌ *.log                         Log files
❌ *.pyc, *.pyo                  Python compiled files
❌ *.tmp, *.bak                  Temporary files
❌ test_*.py, debug_*.py         Test and debug scripts
```

---

## 🎯 **Why This Visibility Strategy?**

### **✅ What Users NEED to See:**
1. **Source Code** - To understand how META_MINDS works
2. **Documentation** - To learn how to use it
3. **Templates** - To see examples of proper input format
4. **Sample Data** - To test the system immediately
5. **Output README** - To understand what reports look like

### **❌ What Users DON'T NEED:**
1. **venv/** - Every user creates their own virtual environment
2. **Output TXT files** - User-generated, specific to each analysis
3. **.env** - Contains API keys (security risk)
4. **Cache files** - Regenerated automatically
5. **Personal settings** - User-specific preferences

---

## 📊 **Folder Purpose on GitHub**

| Folder | Visible? | Purpose | What's Included |
|--------|----------|---------|-----------------|
| `input/` | ✅ YES | Show template format | README.md + example filled templates |
| `Output/` | ✅ YES | Explain output structure | README.md only (no .txt files) |
| `venv/` | ❌ NO | User creates own | Nothing (excluded) |
| `src/` | ✅ YES | Source code | All Python modules |
| `examples/` | ✅ YES | Usage examples | Sample workflows, templates |
| `dataset/` | ✅ YES | Sample data | Example CSV files |
| `docs/` | ✅ YES | Documentation | Guides and references |
| `logs/` | ❌ NO | Runtime logs | Nothing (excluded) |

---

## 🔍 **How Users Will Explore Your Repo**

### **1. First Impression (GitHub Landing Page):**
```
Meta_Minds_-Question_Generator-
├── README.md                    ← They read this first
├── QUICK_START.md               ← Then jump to quick start
├── src/                         ← Browse the code
├── input/                       ← See template examples
│   └── README.md                ← Learn how to use templates
├── Output/                      ← Understand output format
│   └── README.md                ← Learn what reports contain
└── requirements.txt             ← Check dependencies
```

### **2. Setting Up Locally:**
```bash
git clone https://github.com/Jatin23K/Meta_Minds_-Question_Generator-.git
cd Meta_Minds_-Question_Generator-
python -m venv venv              ← They create venv (not in repo)
venv\Scripts\activate
pip install -r requirements.txt
python main.py                   ← Start using it!
```

### **3. Running Analysis:**
- They see `input/` folder with examples
- They understand format from `input/README.md`
- They add their own datasets to `dataset/`
- They run the analysis
- Their reports save to `Output/` (which already exists with README)

---

## 💡 **Benefits of This Approach**

### **For New Users:**
✅ **Clear Structure** - Folders exist, so they know where to put files  
✅ **Examples Included** - Pre-filled templates show proper format  
✅ **No Clutter** - No venv or cache files confusing them  
✅ **Professional** - Clean, organized repository  

### **For Repository Health:**
✅ **Small Size** - No huge venv folder (thousands of files)  
✅ **Security** - No API keys or secrets exposed  
✅ **Privacy** - No user-generated data included  
✅ **Standards** - Follows GitHub best practices  

### **For Collaboration:**
✅ **Easy to Fork** - Others can copy and customize  
✅ **Clear Examples** - Templates show expected format  
✅ **Self-Documenting** - README files explain each folder  
✅ **Production-Ready** - Professional setup from the start  

---

## 🎉 **Result: Professional, Production-Ready Repository!**

Users will see:
- ✅ Clean, organized folder structure
- ✅ Comprehensive documentation
- ✅ Working examples and templates
- ✅ Clear instructions
- ✅ Professional presentation

Users won't see:
- ❌ Clutter from development
- ❌ Personal files
- ❌ Security risks
- ❌ Unnecessary bloat

**This is exactly what a 10/10 repository looks like!** 🌟

