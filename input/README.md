# 📝 Input Folder - Context Templates

This folder contains **pre-filled template files** that provide context for META_MINDS analysis.

---

## 📋 **Required Files**

### **1. Business_Background.txt**
Provides the business context and project overview.

**What to include:**
- Business problem statement
- Key stakeholders (who will use the analysis)
- Business objectives (what you want to achieve)
- Project timeline
- Target audience
- Expected deliverables

---

### **2. Dataset_Background.txt**
Provides specific details about your datasets.

**What to include:**
- Dataset names and descriptions
- Data size (rows, columns)
- Data quality notes
- Time period covered
- Analysis objectives for each dataset
- Specific column descriptions (if needed)

---

### **3. Message.txt**
Simulates a message from a senior stakeholder (CEO, CIO, etc.).

**What to include:**
- High-priority strategic objectives
- Focus areas for analysis
- Analysis approach preferences
- Risk factors to consider
- Quality requirements
- Presentation format expectations

---

## 🎯 **How to Use**

1. **For New Analysis:**
   - Copy the templates from `examples/input_templates/`
   - Paste them here in the `input/` folder
   - Fill them with your project-specific information

2. **For Sample Analysis:**
   - Current files contain a complete example (US Airline Financial Analysis 2013-2023)
   - Run META_MINDS to see how it works with real data

3. **For Quick Testing:**
   - Use the pre-filled templates as-is
   - Add your datasets to the `dataset/` folder
   - Run `python main.py`

---

## 📊 **Current Example**

The current templates demonstrate analysis of the US Airline Industry's financial health from 2013-2023, including:
- **Assets.csv** - Asset composition and trends
- **Liabilities.csv** - Liability structure and risk indicators  
- **Top_10_Ratio.csv** - Key financial performance ratios

---

## 💡 **Tips for Best Results**

1. **Be Specific:** The more context you provide, the better the questions
2. **Include Numbers:** Mention data size, time periods, key metrics
3. **Define Objectives:** Clear goals = relevant questions
4. **Mention Stakeholders:** Knowing the audience shapes question complexity
5. **Add Domain Knowledge:** Industry-specific details improve question quality

---

## 🔗 **Related Folders**

- **`dataset/`** - Place your CSV/Excel files here
- **`Output/`** - Generated reports will be saved here
- **`examples/`** - Additional templates and samples

---

**Need help?** Check `QUICK_START.md` for a complete walkthrough!

