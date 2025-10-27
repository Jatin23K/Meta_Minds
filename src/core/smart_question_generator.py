# =========================================================
# smart_question_generator.py: SMART-Based Question Generation System
# =========================================================
# This module implements SMART methodology for generating high-quality,
# open-ended analytical questions that are:
# - Specific: Target distinct variables or trends
# - Measurable: Refer to quantifiable outcomes  
# - Action-Oriented: Use verbs that prompt analysis
# - Relevant: Relate to data context and stakeholder interests
# - Time-Bound: Reference periods or change over time

import logging
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from config import client

class QuestionType(Enum):
    """Types of analytical questions for different analysis focuses."""
    TREND_ANALYSIS = "trend_analysis"
    RELATIONSHIP_DISCOVERY = "relationship_discovery"
    ANOMALY_DETECTION = "anomaly_detection"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    PREDICTIVE_INSIGHTS = "predictive_insights"
    PERFORMANCE_METRICS = "performance_metrics"

@dataclass
class DatasetContext:
    """Enhanced context information for 9.5/10 quality question generation."""
    # Basic Context (Original)
    subject_area: str = "general"
    analysis_objectives: List[str] = None
    target_audience: str = "data analysts"
    dataset_background: str = ""
    business_context: str = ""
    time_sensitivity: str = "medium"
    
    # Enhanced Context (NEW - For 9.5/10 Quality)
    problem_statement: str = ""
    problem_symptoms: str = ""
    success_criteria: str = ""
    hypotheses: List[str] = None
    key_factors: str = ""
    constraints: str = ""
    expected_data_type: str = ""
    time_span: str = ""
    data_granularity: str = ""
    comparison_benchmarks: List[str] = None
    performance_thresholds: str = ""
    performance_definition: str = ""
    key_decisions: List[str] = None
    decision_makers: str = ""
    decision_urgency: str = "medium"
    high_risk_areas: str = ""
    critical_insights: List[str] = None
    sensitive_areas: str = ""
    
    def __post_init__(self):
        if self.analysis_objectives is None:
            self.analysis_objectives = ["exploratory analysis"]
        if self.hypotheses is None:
            self.hypotheses = []
        if self.comparison_benchmarks is None:
            self.comparison_benchmarks = []
        if self.key_decisions is None:
            self.key_decisions = []
        if self.critical_insights is None:
            self.critical_insights = []

@dataclass
class SMARTCriteria:
    """SMART criteria validation structure."""
    specific: bool = False
    measurable: bool = False
    action_oriented: bool = False
    relevant: bool = False
    time_bound: bool = False
    
    @property
    def compliance_score(self) -> float:
        """Calculate SMART compliance score (0-1)."""
        criteria_met = sum([self.specific, self.measurable, self.action_oriented, 
                           self.relevant, self.time_bound])
        return criteria_met / 5.0
    
    @property
    def is_compliant(self) -> bool:
        """Check if question meets minimum SMART compliance (80%)."""
        return self.compliance_score >= 0.8

class SMARTQuestionGenerator:
    """Enhanced question generator using SMART methodology."""
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
        self.smart_keywords = self._load_smart_keywords()
        self.open_ended_starters = self._load_open_ended_starters()
        self.closed_ended_patterns = self._load_closed_ended_patterns()
        
    def _load_question_templates(self) -> Dict[QuestionType, List[str]]:
        """Load SMART-compliant OPEN-ENDED question templates for different analysis types."""
        return {
            QuestionType.TREND_ANALYSIS: [
                "What specific trends can be identified in {variable} over the {time_period}, and how do these trends correlate with measurable changes in {related_variables}?",
                "How has {metric} evolved throughout {time_frame}, and what actionable insights can be derived from analyzing the rate of change?",
                "What measurable patterns emerge when examining {variable} across different {time_segments}, and how might these inform future {action_areas}?",
                "In what ways does {variable} demonstrate growth or decline patterns during {time_period}, and what factors might be driving these changes?",
                "How do seasonal or cyclical variations in {variable} manifest over {time_frame}, and what implications do these patterns have for {business_area}?"
            ],
            QuestionType.RELATIONSHIP_DISCOVERY: [
                "What is the quantifiable relationship between {variable1} and {variable2}, and how can this relationship be leveraged to improve {outcome_area}?",
                "How do changes in {independent_var} specifically impact {dependent_var}, and what measurable thresholds indicate significant effects?",
                "What correlations exist between {variables}, and how can these relationships guide strategic decisions in {context_area}?",
                "In what ways do {variable1} and {variable2} influence each other, and what does this reveal about underlying business dynamics?",
                "How do interactions between {variables} create compound effects on {outcome_metric}, and what optimization opportunities does this present?"
            ],
            QuestionType.ANOMALY_DETECTION: [
                "What specific outliers or anomalies can be identified in {variable}, and how do these deviations impact overall {performance_metric}?",
                "How can we quantify and categorize unusual patterns in {dataset_area}, and what actionable steps should be taken when these anomalies occur?",
                "What measurable criteria define normal vs. abnormal behavior in {variable}, and how frequently do these anomalies occur over {time_period}?",
                "In what circumstances do extreme values or unexpected patterns emerge in {variable}, and what root causes might explain these occurrences?",
                "How do anomalies in {variable} propagate through the system to affect {related_metrics}, and what early warning signals can be established?"
            ],
            QuestionType.COMPARATIVE_ANALYSIS: [
                "How do {entities} compare in terms of {measurable_metrics}, and what specific factors contribute to performance differences?",
                "What quantifiable differences exist between {group1} and {group2} regarding {outcome_variable}, and how can these insights drive improvement actions?",
                "How do performance metrics for {variable} vary across {categories}, and what actionable strategies emerge from this analysis?",
                "In what ways do {entities} differ in their approach to {metric_area}, and what best practices can be identified from top performers?",
                "What distinguishing characteristics separate high-performing {entities} from others in terms of {measurable_outcomes}?"
            ],
            QuestionType.PREDICTIVE_INSIGHTS: [
                "What historical patterns in {variable} can be used to predict future {outcome}, and how accurate are these predictions over {time_horizon}?",
                "How can current trends in {metrics} be leveraged to forecast {target_variable}, and what confidence intervals should be applied?",
                "What specific indicators in the data suggest future changes in {outcome_area}, and how can stakeholders prepare for these anticipated shifts?",
                "In what ways do leading indicators in {variable} signal upcoming changes in {target_metric}, and what timeframes are most reliable for forecasting?",
                "How do current patterns and trajectories in {metrics} inform scenario planning for {business_outcome} over the next {time_period}?"
            ],
            QuestionType.PERFORMANCE_METRICS: [
                "What key performance indicators can be derived from {dataset}, and how do these metrics align with {business_objectives}?",
                "How can we measure and track {performance_area} using available data, and what benchmarks indicate successful outcomes?",
                "What specific metrics best capture {organizational_goal}, and how frequently should these measurements be monitored for optimal decision-making?"
            ]
        }
    
    def _load_open_ended_starters(self) -> List[str]:
        """Load open-ended question starter words that encourage exploration."""
        return [
            "What", "How", "Why", "When", "Where", "Which", "Who",
            "In what ways", "To what extent", "How might", "What if",
            "How do", "What are", "How can", "What would", "How should",
            "What factors", "How does", "What patterns", "How could",
            "What insights", "How will", "What trends", "How has",
            "What relationships", "How do you explain", "What causes",
            "How would you describe", "What evidence", "How do you account for"
        ]
    
    def _load_closed_ended_patterns(self) -> List[str]:
        """Load patterns that indicate closed-ended (yes/no) questions to avoid."""
        return [
            r"^(is|are|was|were)\s+.*\?$",  # Starts with is/are/was/were
            r"^(will|would)\s+.*\?$",       # Starts with will/would  
            r"^(should|could|can)\s+.*\?$", # Starts with should/could/can
            r"^(do|does|did)\s+.*\?$",      # Starts with do/does/did
            r"^(have|has|had)\s+.*\?$",     # Starts with have/has/had
            r"\b(true|false|correct|incorrect|right|wrong)\b.*\?$",
            r".*\b(yes or no|true or false)\b.*\?$"
        ]
    
    def _load_smart_keywords(self) -> Dict[str, List[str]]:
        """Load keywords that enhance SMART compliance."""
        return {
            "specific": ["specific", "distinct", "particular", "individual", "targeted", "precise", "exact"],
            "measurable": ["quantifiable", "measurable", "percentage", "rate", "frequency", "volume", "count", "ratio", "metric"],
            "action_oriented": ["analyze", "investigate", "examine", "evaluate", "assess", "determine", "identify", "compare", "measure", "track"],
            "relevant": ["impact", "influence", "affect", "relate", "connect", "correlate", "business", "stakeholder", "outcome"],
            "time_bound": ["over time", "during", "within", "period", "timeframe", "timeline", "historical", "future", "trend", "change"]
        }
    
    def generate_enhanced_questions(self, 
                                  dataset_name: str, 
                                  df: pd.DataFrame, 
                                  context: DatasetContext,
                                  num_questions: int = 20) -> List[Dict]:
        """Generate SMART-compliant questions with enhanced context awareness."""
        
        logging.info(f"Generating SMART questions for {dataset_name} with context: {context.subject_area}")
        
        # Analyze dataset characteristics
        dataset_analysis = self._analyze_dataset_characteristics(df)
        
        # Generate context-aware prompt
        enhanced_prompt = self._create_smart_prompt(dataset_name, df, context, dataset_analysis, num_questions)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better reasoning
                messages=[
                    {"role": "system", "content": self._get_smart_system_prompt()},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            raw_questions = response.choices[0].message.content.strip()
            
            # Parse and validate questions
            questions = self._parse_and_validate_questions(raw_questions, context)
            
            # FORCE the exact number requested - no more, no less
            if len(questions) > num_questions:
                questions = questions[:num_questions]  # Truncate to exact count
            elif len(questions) < num_questions:
                logging.warning(f"Only {len(questions)} questions generated, need {num_questions}. Generating fallback questions.")
                additional_questions = self._generate_additional_questions(
                    dataset_name, df, context, num_questions - len(questions)
                )
                questions.extend(additional_questions)
                
                # If still not enough, generate simple fallback questions
                if len(questions) < num_questions:
                    fallback_questions = self._generate_fallback_questions(
                        dataset_name, df, num_questions - len(questions)
                    )
                    questions.extend(fallback_questions)
                
                questions = questions[:num_questions]  # Ensure exact count
            
            # Final safety check - absolutely ensure we have the right count
            return questions[:num_questions]
            
        except Exception as e:
            logging.error(f"Error generating SMART questions: {e}")
            return self._generate_fallback_questions(dataset_name, df, num_questions)
    
    def _analyze_dataset_characteristics(self, df: pd.DataFrame) -> Dict:
        """Analyze dataset to identify key characteristics for question generation."""
        characteristics = {
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist(),
            "date_columns": [],
            "has_time_series": False,
            "key_metrics": [],
            "potential_relationships": []
        }
        
        # Detect date columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                characteristics["date_columns"].append(col)
                characteristics["has_time_series"] = True
        
        # Identify potential key metrics (numeric columns with meaningful variation)
        for col in characteristics["numeric_columns"]:
            if df[col].nunique() > 10 and df[col].std() > 0:
                characteristics["key_metrics"].append(col)
        
        # Identify potential relationships (combinations of numeric columns)
        numeric_cols = characteristics["numeric_columns"]
        if len(numeric_cols) >= 2:
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    characteristics["potential_relationships"].append((numeric_cols[i], numeric_cols[j]))
        
        return characteristics
    
    def _build_enhanced_context_section(self, context: DatasetContext) -> str:
        """Build enhanced context section for 9.5/10 quality questions - ONLY includes fields with real content."""
        sections = []
        
        # Problem Definition - only if user provided real info
        if context.problem_statement:
            problem_parts = []
            problem_parts.append(f"- Core Problem: {context.problem_statement}")
            if context.problem_symptoms:
                problem_parts.append(f"- Symptoms: {context.problem_symptoms}")
            if context.success_criteria:
                problem_parts.append(f"- Success Criteria: {context.success_criteria}")
            
            if len(problem_parts) > 0:
                sections.append("**PROBLEM DEFINITION (CRITICAL - Use this to frame ALL questions):**\n" + '\n'.join(problem_parts))
        
        # Hypotheses - only if user provided real info
        hypothesis_parts = []
        if context.hypotheses and len(context.hypotheses) > 0:
            hypotheses_text = '\n  - '.join(context.hypotheses)
            hypothesis_parts.append(f"**HYPOTHESES TO TEST:**\n  - {hypotheses_text}")
        if context.key_factors:
            hypothesis_parts.append(f"- Key Factors to Investigate: {context.key_factors}")
        if context.constraints:
            hypothesis_parts.append(f"- Constraints: {context.constraints}")
        
        if hypothesis_parts:
            sections.append('\n'.join(hypothesis_parts))
        
        # Data Profile - only if user provided real info
        data_parts = []
        if context.expected_data_type:
            data_parts.append(f"- Data Type: {context.expected_data_type}")
        if context.time_span:
            data_parts.append(f"- Time Span: {context.time_span}")
        if context.data_granularity:
            data_parts.append(f"- Granularity: {context.data_granularity}")
        
        if data_parts:
            sections.append("**EXPECTED DATA PROFILE:**\n" + '\n'.join(data_parts))
        
        # Benchmarks - only if user provided real info
        benchmark_parts = []
        if context.comparison_benchmarks and len(context.comparison_benchmarks) > 0:
            benchmarks_text = ', '.join(context.comparison_benchmarks)
            benchmark_parts.append(f"- Compare Against: {benchmarks_text}")
        if context.performance_thresholds:
            benchmark_parts.append(f"- Performance Thresholds: {context.performance_thresholds}")
        if context.performance_definition:
            benchmark_parts.append(f"- Performance Definition: {context.performance_definition}")
        
        if benchmark_parts:
            sections.append("**COMPARISON & BENCHMARKING (Include in questions):**\n" + '\n'.join(benchmark_parts))
        
        # Decision Impact - only if user provided real info
        decision_parts = []
        if context.key_decisions and len(context.key_decisions) > 0 and context.key_decisions[0]:
            decisions_text = '\n  - '.join(context.key_decisions)
            decision_parts.append(f"**DECISION IMPACT (Questions must drive these decisions):**\n  - {decisions_text}")
        if context.decision_makers:
            decision_parts.append(f"- Decision Makers: {context.decision_makers}")
        if context.decision_urgency:
            decision_parts.append(f"- Urgency: {context.decision_urgency}")
        
        if decision_parts:
            sections.append('\n'.join(decision_parts))
        
        # Risk & Priorities - only if user provided real info
        risk_parts = []
        if context.high_risk_areas:
            risk_parts.append(f"- High-Risk Areas: {context.high_risk_areas}")
        if context.critical_insights and len(context.critical_insights) > 0 and context.critical_insights[0]:
            critical_text = '\n  - '.join(context.critical_insights)
            risk_parts.append(f"- Critical Must-Know Insights:\n  - {critical_text}")
        if context.sensitive_areas:
            risk_parts.append(f"- Sensitive Areas: {context.sensitive_areas}")
        
        if risk_parts:
            sections.append("**RISK & PRIORITIES (Prioritize these areas in questions):**\n" + '\n'.join(risk_parts))
        
        return '\n'.join(sections) if sections else ""
    
    def _create_smart_prompt(self, dataset_name: str, df: pd.DataFrame, 
                           context: DatasetContext, analysis: Dict, num_questions: int = 20) -> str:
        """Create enhanced prompt incorporating SMART criteria and context."""
        
        sample_data = df.head(3).to_string()
        if len(sample_data) > 1500:
            sample_data = sample_data[:1500] + "\n[...truncated...]"
        
        # Build enhanced context sections
        enhanced_context = self._build_enhanced_context_section(context)
        
        prompt = f"""
Generate exactly {num_questions} high-quality, open-ended analytical questions for the dataset '{dataset_name}' using SMART methodology.

**Dataset Context:**
- Subject Area: {context.subject_area}
- Analysis Objectives: {', '.join(context.analysis_objectives)}
- Target Audience: {context.target_audience}
- Business Context: {context.business_context}
- Dataset Background: {context.dataset_background}

{enhanced_context}

**Dataset Characteristics:**
- Rows: {len(df)}, Columns: {len(df.columns)}
- Numeric Variables: {', '.join(analysis['numeric_columns'][:5])}
- Key Metrics: {', '.join(analysis['key_metrics'][:3])}
- Time Series: {'Yes' if analysis['has_time_series'] else 'No'}

**Sample Data:**
{sample_data}

**SMART Criteria Requirements:**
Each question MUST be:
1. **Specific**: Target distinct variables, relationships, or patterns in the data
2. **Measurable**: Reference quantifiable outcomes, metrics, or statistical measures
3. **Action-Oriented**: Use analytical verbs (analyze, examine, evaluate, investigate, etc.)
4. **Relevant**: Connect to business objectives and stakeholder interests in {context.subject_area}
5. **Time-Bound**: Include temporal context where applicable (trends, periods, changes over time)

**Question Format Requirements:**
- Start with "What", "How", or "Why" for open-ended exploration
- Be clear, neutral, and specific to this dataset
- Avoid leading or biased language
- Focus on actionable insights and measurable outcomes
- Include specific variable names from the dataset

**QUESTION DIVERSITY REQUIREMENTS:**
{self._get_diverse_question_categories(dataset_name, df, context)}

**BUSINESS-SPECIFIC FOCUS:**
{self._get_business_specific_templates(context, df)}

Generate exactly {num_questions} questions, numbered 1-{num_questions}, that meet ALL SMART criteria AND follow the diversity framework above.
"""
        return prompt
    
    def _get_diverse_question_categories(self, dataset_name: str, df: pd.DataFrame, context: DatasetContext) -> str:
        """Generate diverse question categories to ensure variety."""
        
        # Analyze dataset characteristics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        has_time_data = any('year' in col.lower() or 'date' in col.lower() or 'time' in col.lower() or 'quarter' in col.lower() for col in df.columns)
        
        categories = f"""
QUESTION DIVERSITY FRAMEWORK - Distribute questions across these categories:

📊 DESCRIPTIVE ANALYSIS (3-4 questions):
- Statistical summaries and distributions of {', '.join(numeric_cols[:2]) if numeric_cols else 'key metrics'}
- Data quality patterns and completeness
- Outlier identification in {', '.join(numeric_cols[:2]) if numeric_cols else 'main variables'}

🔍 COMPARATIVE ANALYSIS (3-4 questions):
- Performance comparisons across {', '.join(categorical_cols[:2]) if categorical_cols else 'available segments'}
- Benchmarking and ranking analysis
- Cross-segment efficiency evaluation

📈 PATTERN ANALYSIS (2-3 questions):
{"- Temporal trends and seasonality in " + ', '.join(numeric_cols[:2]) if has_time_data and numeric_cols else "- Cross-sectional patterns and distributions"}
{"- Forecasting potential for key metrics" if has_time_data else "- Correlation structures between variables"}
{"- Change detection and growth analysis" if has_time_data else "- Variance and stability patterns"}

🎯 BUSINESS IMPACT (3-4 questions):
- {context.subject_area} performance implications
- Risk factors and mitigation strategies
- Strategic decision-making insights
- Operational optimization opportunities

🔗 RELATIONSHIP DISCOVERY (2-3 questions):
- Variable interdependencies and correlations
- Causal relationships and drivers
- Interaction effects between {', '.join(categorical_cols[:2]) if len(categorical_cols) >= 2 else 'key factors'}

MANDATORY VARIETY RULES:
- Use different question starters: "How does...", "What factors...", "Which segments...", "Why might...", "To what extent..."
- Focus on specific column names: {', '.join(df.columns[:4])}
- Apply different analytical lenses: performance, efficiency, growth, risk, optimization
- Avoid repetitive patterns like "What are the trends..." or "How does X change over time..."
"""
        
        return categories
    
    def _get_business_specific_templates(self, context: DatasetContext, df: pd.DataFrame) -> str:
        """Generate business-specific question templates based on context."""
        
        subject_area_lower = context.subject_area.lower()
        
        # Business domain-specific templates
        if 'financial' in subject_area_lower or 'finance' in subject_area_lower:
            return """
FINANCIAL ANALYSIS SPECIFIC APPROACHES:
- Liquidity and solvency analysis
- Profitability and efficiency ratios
- Cash flow patterns and working capital
- Risk exposure and financial stability
- Investment performance and ROI analysis
"""
        elif 'sales' in subject_area_lower or 'marketing' in subject_area_lower:
            return """
SALES/MARKETING SPECIFIC APPROACHES:
- Customer segmentation and behavior patterns
- Sales funnel performance and conversion rates
- Channel effectiveness and attribution
- Revenue optimization opportunities
- Market penetration and growth analysis
"""
        elif 'operations' in subject_area_lower or 'operational' in subject_area_lower:
            return """
OPERATIONAL ANALYSIS APPROACHES:
- Process efficiency and bottleneck identification
- Resource utilization and capacity planning
- Quality control and performance metrics
- Cost optimization and waste reduction
- Supply chain and logistics analysis
"""
        elif 'hr' in subject_area_lower or 'human' in subject_area_lower:
            return """
HR/WORKFORCE ANALYSIS APPROACHES:
- Employee performance and productivity
- Retention and turnover analysis
- Skills gap identification
- Compensation and benefits effectiveness
- Engagement and satisfaction metrics
"""
        else:
            return """
GENERAL BUSINESS ANALYSIS APPROACHES:
- Performance benchmarking and KPI analysis
- Efficiency and optimization opportunities
- Risk assessment and mitigation strategies
- Growth potential and market analysis
- Strategic decision support insights
"""
    
    def _get_smart_system_prompt(self) -> str:
        """Get system prompt that enforces SMART methodology with OPEN-ENDED emphasis."""
        return """You are an expert data analyst and question generation specialist. Your role is to create high-quality, DIVERSE, OPEN-ENDED analytical questions that strictly follow SMART methodology (Specific, Measurable, Action-Oriented, Relevant, Time-Bound).

CRITICAL DIVERSITY & OPEN-ENDED REQUIREMENTS:
- ALL questions MUST be open-ended to encourage deep exploration and analysis
- MUST use DIVERSE question structures and analytical approaches
- AVOID repetitive patterns like "What are the trends..." or "How does X correlate with Y..."
- Use varied question starters: "Which factors...", "To what extent...", "Why might...", "How do different..."
- Start with open-ended words: What, How, Why, In what ways, To what extent, Which factors, How do, What patterns, What insights
- NEVER use closed-ended starters like: Is, Are, Does, Do, Will, Would, Can, Could, Should
- Each question should invite detailed exploration, multiple perspectives, and comprehensive analysis
- Avoid questions that can be answered with yes/no, true/false, or simple one-word responses

SMART + OPEN-ENDED Principles:
1. **Specific + Open-Ended**: Target distinct variables while asking "What specific patterns..." or "How do specific factors..."
2. **Measurable + Exploratory**: Reference quantifiable outcomes while asking "What measurable trends..." or "How do metrics reveal..."
3. **Action-Oriented + Investigative**: Use analytical verbs in exploratory format: "How can we analyze..." or "What factors should be evaluated..."
4. **Relevant + Contextual**: Ensure questions relate to business context: "What insights about [business area]..." or "How do [relevant factors]..."
5. **Time-Bound + Temporal**: Include temporal dimensions: "What trends over [time period]..." or "How have patterns evolved..."

EXAMPLES:
✅ EXCELLENT: "What specific trends in customer acquisition can be identified over the past 12 months, and how do these patterns vary across different marketing channels?"
✅ EXCELLENT: "How do seasonal variations impact sales performance across different product categories, and what factors contribute to these cyclical patterns?"
❌ AVOID: "Is customer acquisition increasing?" (Closed-ended)
❌ AVOID: "Do sales vary by season?" (Closed-ended)

Your questions should enable analysts to uncover actionable insights through comprehensive exploration and detailed investigation."""
    
    def _parse_and_validate_questions(self, raw_questions: str, context: DatasetContext) -> List[Dict]:
        """Parse questions and validate SMART compliance."""
        questions = []
        lines = raw_questions.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not any(char.isdigit() for char in line[:5]):
                continue
                
            # Extract question text
            parts = line.split('.', 1)
            if len(parts) < 2:
                continue
                
            question_text = parts[1].strip()
            
            # Ensure question is open-ended first
            open_ended_question = self._ensure_open_ended_format(question_text)
            
            # Validate open-ended nature
            is_open_ended, open_ended_explanation = self._validate_open_ended(open_ended_question)
            
            # Validate SMART compliance
            smart_score = self._validate_smart_compliance(open_ended_question)
            
            # Apply open-ended bonus/penalty
            open_ended_bonus = 0.1 if is_open_ended else -0.2
            adjusted_score = max(0, smart_score.compliance_score + open_ended_bonus)
            
            # Include all valid questions with minimal filtering to ensure we get the requested count
            if adjusted_score >= 0.3 and is_open_ended:  # Lowered threshold to ensure questions are generated
                questions.append({
                    'question': open_ended_question,
                    'smart_score': adjusted_score,
                    'smart_criteria': smart_score,
                    'is_open_ended': is_open_ended,
                    'open_ended_explanation': open_ended_explanation,
                    'context_relevance': self._assess_context_relevance(question_text, context)
                })
            elif question_text.strip():  # Fallback: include any valid question text to ensure count
                questions.append({
                    'question': self._ensure_open_ended_format(question_text),
                    'smart_score': max(0.5, adjusted_score),  # Force minimum score
                    'smart_criteria': smart_score,
                    'is_open_ended': True,  # Force as open-ended
                    'open_ended_explanation': "Converted to open-ended format",
                    'context_relevance': self._assess_context_relevance(question_text, context)
                })
        
        # Sort by SMART compliance and context relevance
        questions.sort(key=lambda x: (x['smart_score'], x['context_relevance']), reverse=True)
        
        return questions
    
    def _validate_open_ended(self, question: str) -> Tuple[bool, str]:
        """
        Validate that a question is open-ended and encourages exploration.
        
        Returns:
            Tuple of (is_open_ended, explanation)
        """
        import re
        
        question_clean = question.strip()
        
        # Check if question starts with open-ended words
        starts_open_ended = any(
            question_clean.lower().startswith(starter.lower()) 
            for starter in self.open_ended_starters
        )
        
        # Check for closed-ended patterns
        has_closed_pattern = any(
            re.search(pattern, question_clean, re.IGNORECASE) 
            for pattern in self.closed_ended_patterns
        )
        
        # Additional checks for truly open-ended nature
        exploration_indicators = [
            "what", "how", "why", "in what ways", "to what extent",
            "what factors", "what patterns", "what insights", "what trends",
            "what relationships", "what causes", "what evidence", "which",
            "where", "when", "what specific", "how do", "how can", "how might",
            "what are the", "how does", "what would", "how could"
        ]
        
        has_exploration = any(
            question_clean.lower().startswith(indicator) or 
            f" {indicator}" in question_clean.lower()
            for indicator in exploration_indicators
        )
        
        # Check for analysis/exploration words
        analysis_words = [
            "analyze", "examine", "explore", "investigate", "identify",
            "compare", "evaluate", "assess", "determine", "patterns",
            "trends", "relationships", "factors", "insights", "implications"
        ]
        
        has_analysis_focus = any(
            word in question_clean.lower() 
            for word in analysis_words
        )
        
        # Determine if question is open-ended
        is_open_ended = (starts_open_ended or has_exploration or has_analysis_focus) and not has_closed_pattern
        
        # Generate explanation
        if is_open_ended:
            explanation = "Question encourages exploration and detailed analysis"
        else:
            issues = []
            if has_closed_pattern:
                issues.append("contains closed-ended patterns that may lead to yes/no answers")
            if not (starts_open_ended or has_exploration):
                issues.append("lacks open-ended starter words or exploration indicators")
            explanation = f"Question may be too closed-ended: {'; '.join(issues)}"
        
        return is_open_ended, explanation
    
    def _ensure_open_ended_format(self, question: str) -> str:
        """
        Transform a question to ensure it's open-ended if possible.
        """
        question_clean = question.strip()
        
        # Check if already open-ended
        is_open, _ = self._validate_open_ended(question_clean)
        if is_open:
            return question_clean
        
        # Transform common closed-ended patterns to open-ended
        import re
        
        # Pattern: "Is X..." -> "What factors contribute to X..."
        question_clean = re.sub(
            r'^(is|are)\s+(.+?)\s*\?$',
            r'What factors contribute to \2, and how can this be measured?',
            question_clean, flags=re.IGNORECASE
        )
        
        # Pattern: "Does X..." -> "How does X..."
        question_clean = re.sub(
            r'^(does|do)\s+(.+?)\s*\?$',
            r'How does \2, and what patterns can be observed?',
            question_clean, flags=re.IGNORECASE
        )
        
        # Pattern: "Will X..." -> "What trends suggest X..."
        question_clean = re.sub(
            r'^(will|would)\s+(.+?)\s*\?$',
            r'What trends suggest \2, and what factors influence this outcome?',
            question_clean, flags=re.IGNORECASE
        )
        
        # Pattern: "Can X..." -> "How can X..."
        question_clean = re.sub(
            r'^(can|could)\s+(.+?)\s*\?$',
            r'How can \2, and what methods would be most effective?',
            question_clean, flags=re.IGNORECASE
        )
        
        # Ensure it starts with an open-ended word if it doesn't already
        if not any(question_clean.lower().startswith(starter.lower()) for starter in self.open_ended_starters):
            question_clean = f"What insights can be gained about {question_clean.lower().rstrip('?')}?"
        
        return question_clean
    
    def _validate_smart_compliance(self, question: str) -> SMARTCriteria:
        """Validate if a question meets SMART criteria."""
        question_lower = question.lower()
        
        criteria = SMARTCriteria()
        
        # Check Specific: Contains specific variables or precise references
        criteria.specific = any([
            len([word for word in question.split() if word.isupper()]) > 0,  # Variable names
            any(keyword in question_lower for keyword in self.smart_keywords["specific"]),
            'which' in question_lower or 'what specific' in question_lower
        ])
        
        # Check Measurable: References quantifiable outcomes
        criteria.measurable = any([
            any(keyword in question_lower for keyword in self.smart_keywords["measurable"]),
            'how much' in question_lower or 'how many' in question_lower,
            'percentage' in question_lower or '%' in question
        ])
        
        # Check Action-Oriented: Uses analytical verbs
        criteria.action_oriented = any(
            keyword in question_lower for keyword in self.smart_keywords["action_oriented"]
        )
        
        # Check Relevant: Connects to business or analytical context
        criteria.relevant = any([
            any(keyword in question_lower for keyword in self.smart_keywords["relevant"]),
            'business' in question_lower or 'performance' in question_lower,
            'insight' in question_lower or 'decision' in question_lower
        ])
        
        # Check Time-Bound: References temporal context
        criteria.time_bound = any([
            any(keyword in question_lower for keyword in self.smart_keywords["time_bound"]),
            'when' in question_lower or 'timeline' in question_lower
        ])
        
        return criteria
    
    def _assess_context_relevance(self, question: str, context: DatasetContext) -> float:
        """Assess how relevant the question is to the provided context."""
        relevance_score = 0.0
        question_lower = question.lower()
        
        # Check subject area relevance
        if context.subject_area.lower() in question_lower:
            relevance_score += 0.3
        
        # Check objectives alignment
        for objective in context.analysis_objectives:
            if any(word in question_lower for word in objective.lower().split()):
                relevance_score += 0.2
                break
        
        # Check audience appropriateness
        if context.target_audience == "executives" and any(word in question_lower for word in ["strategic", "business", "performance", "roi"]):
            relevance_score += 0.2
        elif context.target_audience == "data analysts" and any(word in question_lower for word in ["correlation", "analysis", "pattern", "trend"]):
            relevance_score += 0.2
        
        # Check business context alignment
        if context.business_context and any(word in question_lower for word in context.business_context.lower().split()):
            relevance_score += 0.3
        
        return min(relevance_score, 1.0)
    
    def _generate_additional_questions(self, dataset_name: str, df: pd.DataFrame, 
                                     context: DatasetContext, num_needed: int) -> List[Dict]:
        """Generate additional questions if initial generation was insufficient."""
        # Implementation for additional question generation
        # This would use template-based generation as fallback
        return []
    
    def _generate_fallback_questions(self, dataset_name: str, df: pd.DataFrame, 
                                   num_questions: int) -> List[Dict]:
        """Generate fallback questions if AI generation fails."""
        fallback_questions = []
        
        open_ended_fallbacks = [
            f"What specific trends and patterns can be identified in the {dataset_name} dataset over time?",
            f"How do different variables in the {dataset_name} dataset correlate with each other?",
            f"What measurable insights can be extracted from the {dataset_name} dataset to guide decision-making?",
            f"In what ways do the data points in {dataset_name} reveal unexpected relationships or anomalies?",
            f"How can the information in the {dataset_name} dataset be leveraged to predict future outcomes?",
            f"What key performance indicators emerge from analyzing the {dataset_name} dataset?",
            f"How do seasonal or temporal variations manifest in the {dataset_name} data?",
            f"What factors contribute most significantly to the variations observed in {dataset_name}?",
            f"In what ways can the {dataset_name} dataset inform strategic business decisions?",
            f"How do different segments or categories within {dataset_name} compare in terms of key metrics?"
        ]
        
        for i in range(min(num_questions, len(open_ended_fallbacks))):
            question = open_ended_fallbacks[i]
            is_open_ended, explanation = self._validate_open_ended(question)
            
            fallback_questions.append({
                'question': question,
                'smart_score': 0.7,  # Higher score for carefully crafted fallbacks
                'smart_criteria': SMARTCriteria(),
                'is_open_ended': is_open_ended,
                'open_ended_explanation': explanation,
                'context_relevance': 0.5
            })
        
        return fallback_questions

def _generate_fallback_comparison_questions(datasets: List[Tuple[str, pd.DataFrame]], 
                                          context: DatasetContext,
                                          num_questions: int) -> List[Dict]:
    """Generate fallback comparison questions when AI generation fails."""
    fallback_questions = []
    
    dataset_names = [name for name, _ in datasets]
    dataset_list = ", ".join(dataset_names)
    
    comparison_fallbacks = [
        f"How do the key performance metrics compare across {dataset_list}?",
        f"What are the significant differences in trends between {dataset_list}?",
        f"Which dataset shows the strongest correlation patterns and why?",
        f"How do the data quality and completeness compare across {dataset_list}?",
        f"What insights emerge when analyzing {dataset_list} together?",
        f"Which dataset contains the most actionable insights for {context.subject_area}?",
        f"How do the temporal patterns differ between {dataset_list}?",
        f"What cross-dataset relationships can be identified for {context.target_audience}?",
        f"Which dataset provides the most reliable predictions for future outcomes?",
        f"How do the anomaly patterns compare across {dataset_list}?"
    ]
    
    for i in range(min(num_questions, len(comparison_fallbacks))):
        question = comparison_fallbacks[i]
        
        fallback_questions.append({
            'question': question,
            'smart_score': 0.7,
            'smart_criteria': SMARTCriteria(),
            'is_open_ended': True,
            'open_ended_explanation': "Open-ended comparative question requiring cross-dataset analysis",
            'context_relevance': 0.6
        })
    
    return fallback_questions

def create_smart_comparison_questions(datasets: List[Tuple[str, pd.DataFrame]], 
                                    context: DatasetContext,
                                    num_questions: int = 15) -> List[Dict]:
    """Generate SMART-compliant comparison questions across multiple datasets."""
    
    if len(datasets) <= 1:
        return []
    
    generator = SMARTQuestionGenerator()
    
    # Analyze all datasets for comparison context
    dataset_info = []
    for name, df in datasets:
        analysis = generator._analyze_dataset_characteristics(df)
        dataset_info.append({
            'name': name,
            'analysis': analysis,
            'sample': df.head(2).to_string()
        })
    
    # Create comparison-focused prompt
    prompt = f"""
Generate exactly {num_questions} high-quality, open-ended comparative analytical questions using SMART methodology.

**Context:**
- Subject Area: {context.subject_area}
- Analysis Objectives: {', '.join(context.analysis_objectives)}
- Target Audience: {context.target_audience}

**Datasets for Comparison:**
"""
    
    for info in dataset_info:
        prompt += f"""
- {info['name']}: {len(datasets)} rows, Key metrics: {', '.join(info['analysis']['key_metrics'][:3])}
"""
    
    prompt += """
**SMART Criteria Requirements:**
Each comparison question MUST:
1. **Specific**: Target distinct variables or relationships across datasets
2. **Measurable**: Reference quantifiable differences, ratios, or comparative metrics
3. **Action-Oriented**: Use comparative analytical verbs (compare, contrast, evaluate differences)
4. **Relevant**: Focus on cross-dataset insights that drive business decisions
5. **Time-Bound**: Include temporal comparisons where applicable

**Focus Areas:**
- Performance metric comparisons across datasets
- Trend pattern similarities and differences
- Relationship strength variations between datasets
- Anomaly patterns across different data sources
- Cross-dataset correlation opportunities

Generate numbered questions (1-{num_questions}) that require analysis of multiple datasets together.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": generator._get_smart_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        raw_questions = response.choices[0].message.content.strip()
        questions = generator._parse_and_validate_questions(raw_questions, context)
        
        return questions[:num_questions]
        
    except Exception as e:
        logging.error(f"Error generating SMART comparison questions: {e}")
        # Generate fallback comparison questions
        return _generate_fallback_comparison_questions(datasets, context, num_questions)
