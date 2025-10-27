# =========================================================
# app.py: Meta Minds Web Interface - Streamlit Application
# =========================================================
# Modern web interface for Meta Minds SMART analysis
# Provides intuitive GUI for context collection and analysis

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Import Meta Minds components
from data_loader import read_file
from data_analyzer import generate_summary
from agents import create_agents
from tasks import create_smart_tasks, create_smart_comparison_task
from context_collector import ContextCollector, DatasetContext
from smart_question_generator import SMARTQuestionGenerator
from smart_validator import SMARTValidator
from output_handler import save_output
from main import run_crew_standard, format_quality_report

# Configure page
st.set_page_config(
    page_title="Meta Minds - AI-Powered Data Analysis",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    
    .quality-excellent {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .quality-good {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .quality-needs-improvement {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .success-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fed7aa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class MetaMindsWebApp:
    """Modern web interface for Meta Minds SMART analysis."""
    
    def __init__(self):
        self.context_collector = ContextCollector()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'analysis_complete' not in st.session_state:
            st.session_state.analysis_complete = False
        if 'datasets' not in st.session_state:
            st.session_state.datasets = []
        if 'context' not in st.session_state:
            st.session_state.context = None
        if 'quality_reports' not in st.session_state:
            st.session_state.quality_reports = {}
        if 'generated_questions' not in st.session_state:
            st.session_state.generated_questions = []
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'smart'
        if 'analysis_config' not in st.session_state:
            st.session_state.analysis_config = {
                'num_datasets': 1,
                'questions_per_dataset': 20,
                'comparison_questions': 15,
                'client_name': '',
                'problem_statement': '',
                'analysis_urgency': 'Medium - Standard',
                # Advanced Quality Defaults
                'industry_sector': 'Technology & Software',
                'domain_expertise': 'Intermediate',
                'regulatory_requirements': 'None',
                'data_maturity': 'Processed Data',
                'statistical_sophistication': 'Intermediate Analysis',
                'analysis_depth': 'Detailed Investigation',
                'decision_impact': 'Strategic Direction',
                'stakeholder_level': 'Executive Leadership',
                'confidence_requirements': 'Standard (95%)'
            }
    
    def render_header(self):
        """Render the main application header."""
        st.markdown('<h1 class="main-header">🧠 Meta Minds</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI-Powered SMART Data Analysis Platform</p>', unsafe_allow_html=True)
        
        # Add feature highlights
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("✅ **SMART Methodology**")
        with col2:
            st.markdown("🎯 **Context-Aware**")
        with col3:
            st.markdown("📊 **Quality Validation**")
        with col4:
            st.markdown("🚀 **Enterprise-Ready**")
        
        st.markdown("---")
    
    def render_sidebar(self):
        """Render the sidebar with navigation and controls."""
        with st.sidebar:
            st.image("https://via.placeholder.com/200x100/1e3a8a/ffffff?text=Meta+Minds", width=200)
            
            st.markdown("## 🎛️ Analysis Control Panel")
            
            # Analysis mode selection
            analysis_mode = st.selectbox(
                "Analysis Mode",
                options=['smart', 'standard'],
                format_func=lambda x: '🚀 SMART Enhanced' if x == 'smart' else '📊 Standard',
                index=0,
                help="SMART mode provides context-aware, high-quality questions"
            )
            st.session_state.analysis_mode = analysis_mode
            
            # Quick stats
            if st.session_state.datasets:
                st.markdown("## 📈 Quick Stats")
                st.metric("Datasets Loaded", len(st.session_state.datasets))
                
                total_rows = sum(len(df) for _, df in st.session_state.datasets)
                st.metric("Total Records", f"{total_rows:,}")
                
                if st.session_state.quality_reports:
                    avg_quality = sum(
                        report.get('summary', {}).get('average_score', 0) 
                        for report in st.session_state.quality_reports.values()
                    ) / len(st.session_state.quality_reports)
                    st.metric("Average Quality Score", f"{avg_quality:.2f}")
            
            # Help section
            st.markdown("## ❓ Help")
            with st.expander("How to Use"):
                st.markdown("""
                1. **Upload Data**: Upload your CSV, Excel, or JSON files
                2. **Set Context**: Choose your analysis context (SMART mode)
                3. **Run Analysis**: Generate high-quality analytical questions
                4. **Review Results**: Examine questions and quality reports
                5. **Export**: Download results for your team
                """)
            
            with st.expander("SMART Criteria"):
                st.markdown("""
                - **S**pecific: Target distinct variables
                - **M**easurable: Quantifiable outcomes
                - **A**ction-oriented: Prompt analysis
                - **R**elevant: Business context aligned
                - **T**ime-bound: Temporal references
                """)
    
    def render_file_upload(self):
        """Render file upload interface."""
        st.markdown("## 📁 Data Upload & Configuration")
        
        # Enhanced Configuration Section
        with st.expander("⚙️ Analysis Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Dataset Configuration")
                num_datasets = st.number_input(
                    "Number of datasets to analyze",
                    min_value=1,
                    max_value=10,
                    value=1,
                    help="How many datasets do you want to analyze?"
                )
                
                questions_per_dataset = st.number_input(
                    "Questions per dataset",
                    min_value=5,
                    max_value=50,
                    value=20,
                    help="Number of questions to generate for each individual dataset"
                )
                
                comparison_questions = st.number_input(
                    "Cross-dataset comparison questions",
                    min_value=0,
                    max_value=30,
                    value=15,
                    help="Number of questions comparing all datasets together"
                )
            
            with col2:
                st.markdown("### 👥 Project Information")
                client_name = st.text_input(
                    "Client/Organization Name",
                    placeholder="e.g., Acme Corporation, Marketing Department",
                    help="Who is this analysis for?"
                )
                
                problem_statement = st.text_area(
                    "Problem to Solve (Optional)",
                    placeholder="e.g., Identify declining sales patterns, Optimize customer retention, Improve operational efficiency...",
                    help="Describe the specific business problem or challenge you're trying to address",
                    height=100
                )
                
                analysis_urgency = st.selectbox(
                    "Analysis Priority",
                    options=["High - Urgent", "Medium - Standard", "Low - Exploratory"],
                    index=1,
                    help="How critical is this analysis for business decisions?"
                )
        
        # Advanced Quality Enhancement Section
        with st.expander("🎯 Quality Enhancement (For 99.9% Perfect Questions)", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🏭 Domain Expertise")
                industry_sector = st.selectbox(
                    "Industry/Sector",
                    options=[
                        "Technology & Software", "Finance & Banking", "Healthcare & Pharmaceuticals",
                        "Retail & E-commerce", "Manufacturing & Industrial", "Energy & Utilities",
                        "Government & Public Sector", "Education", "Consulting", "Other"
                    ],
                    help="Your industry affects question relevance"
                )
                
                domain_expertise = st.selectbox(
                    "Your Domain Expertise",
                    options=["Beginner", "Intermediate", "Expert", "C-Level Executive"],
                    index=1,
                    help="Your expertise level affects question sophistication"
                )
                
                regulatory_requirements = st.selectbox(
                    "Regulatory Considerations",
                    options=["None", "GDPR", "HIPAA", "SOX", "PCI-DSS", "Multiple Requirements"],
                    help="Compliance requirements affect question focus"
                )
            
            with col2:
                st.markdown("#### 📊 Data Intelligence")
                data_maturity = st.selectbox(
                    "Data Maturity Level",
                    options=["Raw Data", "Processed Data", "Previously Analyzed", "Strategic Ready"],
                    index=1,
                    help="Data maturity affects analysis depth"
                )
                
                statistical_sophistication = st.selectbox(
                    "Statistical Sophistication",
                    options=["Basic Statistics", "Intermediate Analysis", "Advanced Analytics", "Expert Level"],
                    index=1,
                    help="Statistical needs affect question complexity"
                )
                
                analysis_depth = st.selectbox(
                    "Required Analysis Depth",
                    options=["Surface Overview", "Detailed Investigation", "Deep-dive Analysis", "Comprehensive Research"],
                    index=1,
                    help="Analysis depth affects question granularity"
                )
            
            with col3:
                st.markdown("#### 🎯 Decision Context")
                decision_impact = st.selectbox(
                    "Decision Impact",
                    options=["Tactical Operations", "Strategic Direction", "Transformational Change"],
                    index=1,
                    help="Decision impact affects question focus"
                )
                
                stakeholder_level = st.selectbox(
                    "Primary Audience",
                    options=["Operational Team", "Management", "Executive Leadership", "Board Level"],
                    index=2,
                    help="Audience level affects question sophistication"
                )
                
                confidence_requirements = st.selectbox(
                    "Confidence Requirements",
                    options=["Exploratory", "Standard (95%)", "High (99%)", "Publication Ready"],
                    index=1,
                    help="Confidence level affects question precision"
                )
        
        # Store configuration in session state
        st.session_state.analysis_config = {
            'num_datasets': num_datasets,
            'questions_per_dataset': questions_per_dataset,
            'comparison_questions': comparison_questions,
            'client_name': client_name,
            'problem_statement': problem_statement,
            'analysis_urgency': analysis_urgency,
            # Advanced Quality Parameters
            'industry_sector': industry_sector,
            'domain_expertise': domain_expertise,
            'regulatory_requirements': regulatory_requirements,
            'data_maturity': data_maturity,
            'statistical_sophistication': statistical_sophistication,
            'analysis_depth': analysis_depth,
            'decision_impact': decision_impact,
            'stakeholder_level': stakeholder_level,
            'confidence_requirements': confidence_requirements
        }
        
        st.markdown("---")
        st.markdown("## 📁 Upload Your Datasets")
        
        uploaded_files = st.file_uploader(
            f"Upload your {num_datasets} dataset(s) (CSV, Excel, JSON)",
            type=['csv', 'xlsx', 'json'],
            accept_multiple_files=True,
            help=f"Upload up to {num_datasets} data files for analysis"
        )
        
        if uploaded_files:
            # Validate number of files matches configuration
            expected_files = st.session_state.analysis_config['num_datasets']
            if len(uploaded_files) != expected_files:
                st.warning(f"⚠️ Expected {expected_files} file(s), but {len(uploaded_files)} uploaded. Please adjust your configuration or upload the correct number of files.")
                return
                
            st.success(f"✅ Perfect! {len(uploaded_files)} file(s) uploaded as configured.")
            
            datasets = []
            upload_progress = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Load the data
                    df = read_file(temp_path)
                    datasets.append((uploaded_file.name, df))
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    upload_progress.progress(progress)
                    
                except Exception as e:
                    st.error(f"Error loading {uploaded_file.name}: {str(e)}")
            
            st.session_state.datasets = datasets
            status_text.text("✅ All files processed successfully!")
            
            # Display dataset summary
            if datasets:
                st.markdown("### 📊 Dataset Summary")
                
                summary_data = []
                for name, df in datasets:
                    summary_data.append({
                        'Dataset': name,
                        'Rows': len(df),
                        'Columns': len(df.columns),
                        'Size (MB)': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
    
    def render_context_collection(self):
        """Render context collection interface for SMART mode."""
        if st.session_state.analysis_mode != 'smart':
            return
        
        st.markdown("## 🎯 Analysis Context (SMART Mode)")
        
        # Quick setup or custom
        setup_mode = st.radio(
            "Context Setup",
            options=['predefined', 'custom'],
            format_func=lambda x: '⚡ Quick Setup (Predefined Templates)' if x == 'predefined' else '🛠️ Custom Context',
            horizontal=True
        )
        
        if setup_mode == 'predefined':
            self.render_predefined_context()
        else:
            self.render_custom_context()
    
    def render_predefined_context(self):
        """Render predefined context selection."""
        predefined_contexts = self.context_collector.predefined_contexts
        
        # Create context cards
        st.markdown("### Choose Your Analysis Domain")
        
        cols = st.columns(2)
        context_options = list(predefined_contexts.keys())
        
        for i, context_key in enumerate(context_options):
            with cols[i % 2]:
                context = predefined_contexts[context_key]
                
                with st.container():
                    st.markdown(f"#### 📊 {context.subject_area.title()}")
                    st.markdown(f"**Focus:** {', '.join(context.analysis_objectives[:2])}")
                    st.markdown(f"**Audience:** {context.target_audience}")
                    
                    if st.button(f"Select {context.subject_area.title()}", key=f"select_{context_key}"):
                        st.session_state.context = context
                        st.success(f"✅ Selected: {context.subject_area.title()}")
                        st.rerun()
        
        # Show selected context
        if st.session_state.context:
            st.markdown("### ✅ Selected Context")
            context = st.session_state.context
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Subject Area:** {context.subject_area}")
                st.markdown(f"**Target Audience:** {context.target_audience}")
            with col2:
                st.markdown(f"**Objectives:** {', '.join(context.analysis_objectives)}")
                st.markdown(f"**Business Context:** {context.business_context}")
    
    def render_custom_context(self):
        """Render custom context creation interface."""
        st.markdown("### 🛠️ Custom Context Configuration")
        
        with st.form("custom_context_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                subject_area = st.text_input(
                    "Subject Area",
                    placeholder="e.g., financial analysis, marketing analytics",
                    help="What domain does your data relate to?"
                )
                
                target_audience = st.selectbox(
                    "Target Audience",
                    options=['executives', 'data analysts', 'managers', 'researchers', 'consultants'],
                    help="Who will be using these insights?"
                )
                
                time_sensitivity = st.selectbox(
                    "Time Sensitivity",
                    options=['high', 'medium', 'low'],
                    index=1,
                    help="How urgent is this analysis?"
                )
            
            with col2:
                objectives = st.text_area(
                    "Analysis Objectives",
                    placeholder="trend analysis, performance evaluation, risk assessment",
                    help="What are your main goals? (comma-separated)"
                )
                
                business_context = st.text_area(
                    "Business Context",
                    placeholder="Budget allocation, strategic planning, process optimization",
                    help="How will this analysis support business decisions?"
                )
                
                dataset_background = st.text_area(
                    "Dataset Background",
                    placeholder="Source, time period, collection method",
                    help="Background information about your data"
                )
            
            submitted = st.form_submit_button("💾 Save Context", use_container_width=True)
            
            if submitted and subject_area and objectives:
                objectives_list = [obj.strip() for obj in objectives.split(',') if obj.strip()]
                
                custom_context = DatasetContext(
                    subject_area=subject_area.lower(),
                    analysis_objectives=objectives_list,
                    target_audience=target_audience,
                    business_context=business_context or "General business analysis",
                    dataset_background=dataset_background or "No background provided",
                    time_sensitivity=time_sensitivity
                )
                
                st.session_state.context = custom_context
                st.success("✅ Custom context saved successfully!")
                st.rerun()
    
    def render_analysis_execution(self):
        """Render analysis execution interface."""
        if not st.session_state.datasets:
            st.warning("⚠️ Please upload datasets first.")
            return
        
        if st.session_state.analysis_mode == 'smart' and not st.session_state.context:
            st.warning("⚠️ Please configure analysis context first.")
            return
        
        st.markdown("## 🚀 Run Analysis")
        
        # Enhanced Analysis configuration display
        st.markdown("### 📋 Analysis Configuration Summary")
        
        config = st.session_state.analysis_config
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**Mode:**")
            if st.session_state.analysis_mode == 'smart':
                st.markdown("🚀 SMART Enhanced")
            else:
                st.markdown("📊 Standard")
            
            st.markdown("**Datasets:**")
            st.markdown(f"{len(st.session_state.datasets)} files")
        
        with col2:
            st.markdown("**Questions Config:**")
            st.markdown(f"• Per Dataset: {config['questions_per_dataset']}")
            st.markdown(f"• Comparison: {config['comparison_questions']}")
            st.markdown(f"• **Total: ~{len(st.session_state.datasets) * config['questions_per_dataset'] + config['comparison_questions']}**")
        
        with col3:
            if config['client_name']:
                st.markdown("**Client:**")
                st.markdown(f"📋 {config['client_name']}")
            
            if st.session_state.context:
                st.markdown("**Context:**")
                st.markdown(f"🎯 {st.session_state.context.subject_area.title()}")
        
        with col4:
            st.markdown("**Priority:**")
            priority_icon = "🔴" if "High" in config['analysis_urgency'] else "🟡" if "Medium" in config['analysis_urgency'] else "🟢"
            st.markdown(f"{priority_icon} {config['analysis_urgency'].split(' - ')[0]}")
            
            if config['problem_statement']:
                st.markdown("**Problem Focus:**")
                st.markdown(f"🎯 {config['problem_statement'][:50]}{'...' if len(config['problem_statement']) > 50 else ''}")
        
        # Show problem statement in full if provided
        if config['problem_statement']:
            with st.expander("📝 Full Problem Statement"):
                st.markdown(config['problem_statement'])
        
        # Run analysis button
        if st.button("🎯 Generate Analytical Questions", use_container_width=True, type="primary"):
            self.run_analysis()
    
    def run_analysis(self):
        """Execute the analysis workflow."""
        with st.spinner("🔄 Running SMART analysis..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Generate summaries
                status_text.text("📊 Generating dataset summaries...")
                progress_bar.progress(0.2)
                
                dataset_summaries = {}
                for name, df in st.session_state.datasets:
                    summary = generate_summary(df)
                    dataset_summaries[name] = summary
                
                # Step 2: Create agents
                status_text.text("🤖 Initializing AI agents...")
                progress_bar.progress(0.4)
                
                schema_sleuth, question_genius = create_agents()
                agents = [schema_sleuth, question_genius]
                
                # Step 3: Create tasks
                status_text.text("📝 Creating analysis tasks...")
                progress_bar.progress(0.6)
                
                if st.session_state.analysis_mode == 'smart':
                    individual_tasks, individual_headers, quality_reports = create_smart_tasks(
                        st.session_state.datasets, schema_sleuth, question_genius, st.session_state.context
                    )
                    comparison_task, comparison_quality = create_smart_comparison_task(
                        st.session_state.datasets, question_genius, st.session_state.context
                    )
                    if comparison_quality:
                        quality_reports['comparison'] = comparison_quality
                    
                    st.session_state.quality_reports = quality_reports
                else:
                    from tasks import create_tasks, create_comparison_task
                    individual_tasks, individual_headers = create_tasks(
                        st.session_state.datasets, schema_sleuth, question_genius
                    )
                    comparison_task = create_comparison_task(st.session_state.datasets, question_genius)
                
                # Step 4: Run tasks
                status_text.text("🧠 Generating questions with AI...")
                progress_bar.progress(0.8)
                
                all_tasks = individual_tasks[:]
                all_headers = individual_headers[:]
                
                if comparison_task:
                    all_tasks.append(comparison_task)
                    if st.session_state.analysis_mode == 'smart':
                        all_headers.append("--- Enhanced Comparison Questions ---")
                    else:
                        all_headers.append("--- Comparison Questions ---")
                
                task_results = run_crew_standard(all_tasks, agents)
                
                # Step 5: Format output
                status_text.text("📄 Formatting results...")
                progress_bar.progress(1.0)
                
                from main import format_output_final
                formatted_output = format_output_final(dataset_summaries, task_results, all_headers)
                
                if st.session_state.analysis_mode == 'smart' and st.session_state.quality_reports:
                    quality_report_lines = format_quality_report(st.session_state.quality_reports, st.session_state.context)
                    formatted_output.extend(quality_report_lines)
                
                # Store results
                st.session_state.generated_questions = formatted_output
                st.session_state.analysis_complete = True
                
                status_text.text("✅ Analysis complete!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logging.error(f"Analysis error: {e}", exc_info=True)
    
    def render_results(self):
        """Render analysis results."""
        if not st.session_state.analysis_complete:
            return
        
        st.markdown("## 📊 Analysis Results")
        
        # Results tabs
        if st.session_state.analysis_mode == 'smart':
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Questions", "📈 Quality Report", "📊 Analytics", "💾 Export"])
        else:
            tab1, tab4 = st.tabs(["📝 Questions", "💾 Export"])
            tab2 = tab3 = None
        
        with tab1:
            self.render_questions_tab()
        
        if tab2:
            with tab2:
                self.render_quality_tab()
        
        if tab3:
            with tab3:
                self.render_analytics_tab()
        
        with tab4:
            self.render_export_tab()
    
    def render_questions_tab(self):
        """Render generated questions tab."""
        st.markdown("### 🎯 Generated Analytical Questions")
        
        if st.session_state.generated_questions:
            # Display questions in expandable sections
            current_section = None
            current_questions = []
            
            for line in st.session_state.generated_questions:
                if line.startswith("---") and "Questions" in line:
                    # New section
                    if current_section and current_questions:
                        self.display_question_section(current_section, current_questions)
                    
                    current_section = line.replace("---", "").strip()
                    current_questions = []
                elif line.strip() and not line.startswith("====") and not line.startswith("📊"):
                    current_questions.append(line)
            
            # Display last section
            if current_section and current_questions:
                self.display_question_section(current_section, current_questions)
        else:
            st.info("No questions generated yet. Please run the analysis first.")
    
    def display_question_section(self, section_title: str, questions: List[str]):
        """Display a section of questions."""
        with st.expander(f"📋 {section_title}", expanded=True):
            for question in questions:
                if question.strip():
                    # Check if it's a numbered question
                    if any(char.isdigit() for char in question[:5]):
                        st.markdown(f"• {question}")
                    else:
                        st.markdown(question)
    
    def render_quality_tab(self):
        """Render quality analysis tab."""
        if not st.session_state.quality_reports:
            st.info("Quality reports available only in SMART mode.")
            return
        
        st.markdown("### 📈 Quality Analysis Dashboard")
        
        # Overall quality metrics
        all_scores = []
        for report in st.session_state.quality_reports.values():
            if 'summary' in report:
                all_scores.append(report['summary']['average_score'])
        
        if all_scores:
            overall_avg = sum(all_scores) / len(all_scores)
            
            # Quality score visualization
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = overall_avg,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Quality Score"},
                delta = {'reference': 0.8},
                gauge = {
                    'axis': {'range': [None, 1]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 0.6], 'color': "lightgray"},
                        {'range': [0.6, 0.8], 'color': "yellow"},
                        {'range': [0.8, 1], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.9
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Quality breakdown by dataset
            if len(st.session_state.quality_reports) > 1:
                dataset_scores = []
                dataset_names = []
                
                for name, report in st.session_state.quality_reports.items():
                    if 'summary' in report and name != 'comparison':
                        dataset_names.append(name)
                        dataset_scores.append(report['summary']['average_score'])
                
                if dataset_scores:
                    fig_bar = px.bar(
                        x=dataset_names,
                        y=dataset_scores,
                        title="Quality Scores by Dataset",
                        labels={'x': 'Dataset', 'y': 'Quality Score'},
                        color=dataset_scores,
                        color_continuous_scale='RdYlGn'
                    )
                    fig_bar.update_layout(height=400)
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        # Detailed quality metrics
        for dataset_name, report in st.session_state.quality_reports.items():
            if 'summary' not in report:
                continue
                
            st.markdown(f"#### 📊 {dataset_name}")
            
            summary = report['summary']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Score", f"{summary['average_score']:.2f}")
            with col2:
                st.metric("High Quality", f"{summary['high_quality_count']}/{summary['total_questions']}")
            with col3:
                st.metric("Need Improvement", summary['needs_improvement_count'])
            with col4:
                if 'diversity_analysis' in report:
                    diversity_score = report['diversity_analysis']['diversity_score']
                    st.metric("Diversity Score", f"{diversity_score:.2f}")
            
            # Best question
            if 'best_question' in report:
                best = report['best_question']
                st.success(f"🌟 **Best Question (Score: {best['score']:.2f}):** {best['question']}")
            
            # Recommendations
            if 'improvement_recommendations' in report:
                with st.expander("💡 Improvement Recommendations"):
                    for rec in report['improvement_recommendations']:
                        st.markdown(f"• {rec}")
    
    def render_analytics_tab(self):
        """Render advanced analytics tab."""
        st.markdown("### 📊 Advanced Analytics")
        
        if not st.session_state.quality_reports:
            st.info("Advanced analytics available only in SMART mode.")
            return
        
        # SMART criteria analysis
        st.markdown("#### 🎯 SMART Criteria Coverage")
        
        criteria_data = []
        criteria_names = ['Specific', 'Measurable', 'Action-Oriented', 'Relevant', 'Time-Bound']
        
        # Simulate SMART criteria scores (in real implementation, extract from actual reports)
        for criterion in criteria_names:
            # Calculate average coverage across datasets
            coverage = 75 + (hash(criterion) % 20)  # Simulated data
            criteria_data.append({'Criterion': criterion, 'Coverage': coverage})
        
        criteria_df = pd.DataFrame(criteria_data)
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=criteria_df['Coverage'],
            theta=criteria_df['Criterion'],
            fill='toself',
            name='SMART Coverage'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="SMART Criteria Coverage Analysis"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Question type distribution
        st.markdown("#### 📋 Question Type Distribution")
        
        question_types = ['Trend Analysis', 'Relationship Discovery', 'Performance Metrics', 
                         'Comparative Analysis', 'Anomaly Detection']
        question_counts = [8, 6, 4, 5, 3]  # Simulated data
        
        fig_pie = px.pie(
            values=question_counts,
            names=question_types,
            title="Question Types Generated"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    def render_export_tab(self):
        """Render export options tab."""
        st.markdown("### 💾 Export Results")
        
        if not st.session_state.generated_questions:
            st.info("No results to export yet.")
            return
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 Text Export")
            
            # Prepare text content
            export_content = "\n".join(st.session_state.generated_questions)
            
            st.download_button(
                label="📥 Download Questions (TXT)",
                data=export_content,
                file_name=f"meta_minds_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### 📊 JSON Export")
            
            # Prepare JSON content
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'analysis_mode': st.session_state.analysis_mode,
                'context': st.session_state.context.__dict__ if st.session_state.context else None,
                'analysis_config': st.session_state.analysis_config,
                'datasets': [name for name, _ in st.session_state.datasets],
                'questions': st.session_state.generated_questions,
                'quality_reports': st.session_state.quality_reports if st.session_state.analysis_mode == 'smart' else None
            }
            
            json_content = json.dumps(export_data, indent=2, default=str)
            
            st.download_button(
                label="📥 Download Full Report (JSON)",
                data=json_content,
                file_name=f"meta_minds_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Preview export content
        with st.expander("👀 Preview Export Content"):
            st.text_area(
                "Generated Questions",
                value="\n".join(st.session_state.generated_questions[:1000]) + "..." if len("\n".join(st.session_state.generated_questions)) > 1000 else "\n".join(st.session_state.generated_questions),
                height=200,
                disabled=True
            )
    
    def run(self):
        """Main application entry point."""
        self.render_header()
        self.render_sidebar()
        
        # Main content area
        if not st.session_state.datasets:
            self.render_file_upload()
        else:
            # Show uploaded datasets summary
            with st.expander("📁 Uploaded Datasets", expanded=False):
                for name, df in st.session_state.datasets:
                    st.markdown(f"**{name}:** {len(df):,} rows × {len(df.columns)} columns")
            
            # Context collection for SMART mode
            self.render_context_collection()
            
            # Analysis execution
            self.render_analysis_execution()
            
            # Results display
            self.render_results()

def main():
    """Main function to run the Streamlit app."""
    app = MetaMindsWebApp()
    app.run()

if __name__ == "__main__":
    main()
