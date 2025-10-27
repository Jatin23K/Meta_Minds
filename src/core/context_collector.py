# =========================================================
# context_collector.py: Context Collection for Enhanced Question Generation
# =========================================================
# This module collects user context to improve question relevance and quality
# including subject area, analysis objectives, target audience, and dataset background

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
import os
from datetime import datetime
from smart_question_generator import DatasetContext

class ContextCollector:
    """Collects and manages user context for enhanced question generation."""
    
    def __init__(self, context_file: str = "user_context.json", input_folder: str = "input"):
        self.context_file = context_file
        self.input_folder = input_folder
        self.predefined_contexts = self._load_predefined_contexts()
        
    def read_input_folder_context(self) -> Optional[DatasetContext]:
        """Read context from input folder files if they exist and contain data.
        
        Returns:
            DatasetContext if valid context found, None otherwise
        """
        try:
            # Get the project root directory (2 levels up from this script)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            input_folder_path = os.path.join(project_root, self.input_folder)
            
            dataset_bg_path = os.path.join(input_folder_path, "Dataset_Background.txt")
            message_path = os.path.join(input_folder_path, "message.txt")
            
            # Check if input folder and files exist
            logging.info(f"Looking for input folder at: {input_folder_path}")
            if not os.path.exists(input_folder_path):
                logging.info(f"Input folder not found at {input_folder_path}, using interactive context collection")
                return None
            else:
                logging.info(f"SUCCESS: Found input folder at: {input_folder_path}")
                
            dataset_background = ""
            senior_message = ""
            
            # Read Dataset_Background.txt
            if os.path.exists(dataset_bg_path):
                with open(dataset_bg_path, 'r', encoding='utf-8') as f:
                    dataset_background = f.read().strip()
                    
            # Read message.txt  
            if os.path.exists(message_path):
                with open(message_path, 'r', encoding='utf-8') as f:
                    senior_message = f.read().strip()
            
            # Parse context from the background file
            if dataset_background and len(dataset_background) > 50:  # Basic validation
                context = self._parse_dataset_background(dataset_background, senior_message)
                if context:
                    logging.info("SUCCESS: Successfully loaded context from input folder")
                    return context
                    
            logging.info("Input folder files exist but lack sufficient context data")
            return None
            
        except Exception as e:
            logging.error(f"Error reading input folder context: {e}")
            return None
    
    def _parse_dataset_background(self, background_text: str, message_text: str = "") -> Optional[DatasetContext]:
        """Parse the Dataset_Background.txt content to extract context information.
        
        Args:
            background_text: Content from Dataset_Background.txt
            message_text: Content from message.txt
            
        Returns:
            DatasetContext if parsing successful, None otherwise
        """
        try:
            # Extract key information from the background text
            lines = background_text.lower().split('\n')
            
            # Default values
            subject_area = "general analysis"
            analysis_objectives = []
            target_audience = "analysts"
            business_context = background_text[:500] + "..." if len(background_text) > 500 else background_text
            dataset_background = background_text
            time_sensitivity = "medium"
            
            # Parse subject area and objectives from the text
            for line in lines:
                line = line.strip()
                
                # Look for subject area indicators
                if any(keyword in line for keyword in ["financial", "finance", "asset", "revenue", "profit"]):
                    subject_area = "financial analysis"
                elif any(keyword in line for keyword in ["sales", "revenue", "pipeline", "customer"]):
                    subject_area = "sales performance"
                elif any(keyword in line for keyword in ["marketing", "campaign", "brand", "customer acquisition"]):
                    subject_area = "marketing analytics"
                elif any(keyword in line for keyword in ["operational", "operations", "efficiency", "process"]):
                    subject_area = "operational analytics"
                    
                # Look for analysis objectives
                if "risk" in line and "assessment" in line:
                    analysis_objectives.append("risk assessment")
                if "performance" in line and ("evaluation" in line or "analysis" in line):
                    analysis_objectives.append("performance evaluation")
                if "trend" in line:
                    analysis_objectives.append("trend analysis")
                if "optimization" in line:
                    analysis_objectives.append("optimization analysis")
                    
                # Look for target audience
                if "executive" in line:
                    target_audience = "executives"
                elif "manager" in line:
                    target_audience = "managers"
                elif "analyst" in line:
                    target_audience = "analysts"
                    
                # Look for time sensitivity
                if "urgent" in line or "high" in line:
                    time_sensitivity = "high"
                elif "low" in line:
                    time_sensitivity = "low"
            
            # Ensure we have at least one objective
            if not analysis_objectives:
                analysis_objectives = ["general analysis"]
            
            # Include senior message in business context if provided
            if message_text:
                business_context = f"Senior Instructions: {message_text[:200]}... | Background: {background_text[:300]}..."
            
            context = DatasetContext(
                subject_area=subject_area,
                analysis_objectives=analysis_objectives,
                target_audience=target_audience,
                business_context=business_context,
                dataset_background=dataset_background,
                time_sensitivity=time_sensitivity
            )
            
            logging.info(f"Parsed context - Subject: {subject_area}, Objectives: {analysis_objectives}, Audience: {target_audience}")
            return context
            
        except Exception as e:
            logging.error(f"Error parsing dataset background: {e}")
            return None
    
    def _load_predefined_contexts(self) -> Dict[str, DatasetContext]:
        """Load predefined context templates for common analysis scenarios."""
        return {
            "financial_analysis": DatasetContext(
                subject_area="financial analysis",
                analysis_objectives=["performance evaluation", "risk assessment", "trend analysis", "ROI optimization"],
                target_audience="financial analysts",
                business_context="Investment decisions, portfolio management, and financial planning",
                time_sensitivity="high"
            ),
            "marketing_analytics": DatasetContext(
                subject_area="marketing analytics", 
                analysis_objectives=["campaign effectiveness", "customer segmentation", "ROI analysis", "brand performance"],
                target_audience="marketing managers",
                business_context="Marketing strategy optimization, budget allocation, and customer acquisition",
                time_sensitivity="medium"
            ),
            "operational_analytics": DatasetContext(
                subject_area="operational analytics",
                analysis_objectives=["efficiency optimization", "cost reduction", "process improvement", "quality control"],
                target_audience="operations managers",
                business_context="Operational excellence, resource optimization, and process automation",
                time_sensitivity="high"
            ),
            "sales_analytics": DatasetContext(
                subject_area="sales analytics",
                analysis_objectives=["sales performance", "pipeline analysis", "forecasting", "territory optimization"],
                target_audience="sales managers",
                business_context="Sales strategy, revenue optimization, and performance management",
                time_sensitivity="high"
            ),
            "customer_analytics": DatasetContext(
                subject_area="customer analytics",
                analysis_objectives=["customer behavior", "retention analysis", "satisfaction measurement", "lifetime value"],
                target_audience="customer success managers",
                business_context="Customer experience improvement, retention strategies, and loyalty programs",
                time_sensitivity="medium"
            ),
            "hr_analytics": DatasetContext(
                subject_area="human resources analytics",
                analysis_objectives=["employee performance", "retention analysis", "workforce planning", "diversity metrics"],
                target_audience="HR managers",
                business_context="Talent management, organizational development, and employee engagement",
                time_sensitivity="medium"
            ),
            "supply_chain_analytics": DatasetContext(
                subject_area="supply chain analytics",
                analysis_objectives=["inventory optimization", "demand forecasting", "supplier performance", "logistics efficiency"],
                target_audience="supply chain managers",
                business_context="Supply chain optimization, cost reduction, and risk mitigation",
                time_sensitivity="high"
            ),
            "healthcare_analytics": DatasetContext(
                subject_area="healthcare analytics",
                analysis_objectives=["patient outcomes", "cost analysis", "resource utilization", "quality improvement"],
                target_audience="healthcare administrators",
                business_context="Healthcare delivery optimization, cost management, and patient care improvement",
                time_sensitivity="high"
            ),
            "retail_analytics": DatasetContext(
                subject_area="retail analytics",
                analysis_objectives=["sales optimization", "inventory management", "customer insights", "pricing strategy"],
                target_audience="retail managers",
                business_context="Retail performance optimization, customer experience, and profitability",
                time_sensitivity="medium"
            ),
            "manufacturing_analytics": DatasetContext(
                subject_area="manufacturing analytics",
                analysis_objectives=["production efficiency", "quality control", "equipment maintenance", "cost optimization"],
                target_audience="manufacturing managers",
                business_context="Manufacturing excellence, productivity improvement, and operational efficiency",
                time_sensitivity="high"
            ),
            "energy_analytics": DatasetContext(
                subject_area="energy analytics",
                analysis_objectives=["consumption optimization", "efficiency analysis", "sustainability metrics", "cost reduction"],
                target_audience="energy managers",
                business_context="Energy management, sustainability initiatives, and operational cost optimization",
                time_sensitivity="medium"
            ),
            "cybersecurity_analytics": DatasetContext(
                subject_area="cybersecurity analytics",
                analysis_objectives=["threat detection", "risk assessment", "incident analysis", "security metrics"],
                target_audience="security analysts",
                business_context="Cybersecurity posture improvement, threat mitigation, and risk management",
                time_sensitivity="high"
            ),
            "education_analytics": DatasetContext(
                subject_area="education analytics",
                analysis_objectives=["student performance", "learning outcomes", "resource allocation", "engagement analysis"],
                target_audience="education administrators",
                business_context="Educational excellence, student success, and institutional effectiveness",
                time_sensitivity="medium"
            ),
            "real_estate_analytics": DatasetContext(
                subject_area="real estate analytics",
                analysis_objectives=["market analysis", "price prediction", "investment optimization", "portfolio performance"],
                target_audience="real estate analysts",
                business_context="Real estate investment decisions, market insights, and portfolio optimization",
                time_sensitivity="medium"
            ),
            "transportation_analytics": DatasetContext(
                subject_area="transportation analytics",
                analysis_objectives=["route optimization", "fleet management", "safety analysis", "efficiency improvement"],
                target_audience="transportation managers",
                business_context="Transportation efficiency, cost optimization, and safety improvement",
                time_sensitivity="high"
            ),
            "telecommunications_analytics": DatasetContext(
                subject_area="telecommunications analytics",
                analysis_objectives=["network performance", "customer churn", "service quality", "capacity planning"],
                target_audience="telecom analysts",
                business_context="Network optimization, customer retention, and service quality improvement",
                time_sensitivity="medium"
            )
        }
    
    def collect_context_hybrid(self) -> DatasetContext:
        """Hybrid context collection - tries input folder first, falls back to interactive.
        
        Returns:
            DatasetContext with complete business context
        """
        # Try to read from input folder first
        folder_context = self.read_input_folder_context()
        
        if folder_context:
            print("SUCCESS: Using business context from input folder")
            print(f"   Subject Area: {folder_context.subject_area}")
            print(f"   Objectives: {', '.join(folder_context.analysis_objectives)}")
            print(f"   Audience: {folder_context.target_audience}")
            print()
            return folder_context
        else:
            print("NOTE: Input folder context not available, collecting interactively...")
            return self.collect_context_interactive()
    
    def collect_context_interactive(self) -> DatasetContext:
        """Collect context through interactive user prompts."""
        print("\n" + "="*60)
        print("META MINDS - ENHANCED CONTEXT COLLECTION")
        print("="*60)
        print("To generate the most relevant analytical questions, please provide some context:")
        print()
        
        # Option for predefined contexts
        use_predefined = self._get_predefined_context_choice()
        if use_predefined:
            return use_predefined
        
        # Collect custom context
        context = DatasetContext()
        
        # Subject Area
        context.subject_area = self._get_subject_area()
        
        # Analysis Objectives  
        context.analysis_objectives = self._get_analysis_objectives()
        
        # Target Audience
        context.target_audience = self._get_target_audience()
        
        # Dataset Background
        context.dataset_background = self._get_dataset_background()
        
        # Business Context
        context.business_context = self._get_business_context()
        
        # Time Sensitivity
        context.time_sensitivity = self._get_time_sensitivity()
        
        # ===== ENHANCED CONTEXT FOR 9.5/10 QUALITY (OPTIONAL) =====
        print("\n" + "="*60)
        print("ENHANCED CONTEXT (OPTIONAL)")
        print("="*60)
        print()
        print("Do you want to answer additional questions for higher quality?")
        print()
        print("  y = Yes, ask me detailed questions (8.5-9.5/10 quality)")
        print("  n = No, use what I've provided (7.0-7.5/10 quality - FASTEST)")
        print()
        
        want_enhanced = input("Answer enhanced questions? (y/n): ").strip().lower()
        
        if want_enhanced not in ['y', 'yes']:
            print("\nSUCCESS: Using basic context. Questions will be 7.0-7.5/10 quality.")
            enhanced_choice = 'skip'
        else:
            print()
            print("Great! Choose your level of detail:")
            print()
            print("  1. QUICK (3 simple questions - ~2 min) - 7.5-9.0/10 quality")
            print("  2. COMPREHENSIVE (6 question sets - ~10 min) - 9.0-9.5/10 quality")
            print("  3. CUSTOM (pick specific questions) - 7.5-9.5/10 quality")
            print()
            
            detail_choice = input("Select level (1-3): ").strip()
            
            if detail_choice == '1':
                enhanced_choice = 'must_have'
            elif detail_choice == '2':
                enhanced_choice = 'all'
            elif detail_choice == '3':
                enhanced_choice = 'custom'
            else:
                print("Invalid choice. Using QUICK mode.")
                enhanced_choice = 'must_have'
        
        if enhanced_choice == 'skip':
            print("\nSUCCESS: Using basic context. Questions will be 7.0-7.5/10 quality.")
        elif enhanced_choice == 'must_have':
            print("\nCollecting 3 QUICK questions for enhanced quality...")
            # 1. Problem Definition (MUST-HAVE)
            problem_context = self._get_problem_definition()
            context.problem_statement = problem_context['statement']
            context.problem_symptoms = problem_context['symptoms']
            context.success_criteria = problem_context['success']
            
            # 4. Benchmarks & Thresholds (MUST-HAVE)
            benchmarks = self._get_benchmarks()
            context.comparison_benchmarks = benchmarks['benchmarks']
            context.performance_thresholds = benchmarks['thresholds']
            context.performance_definition = benchmarks['definition']
            
            # 5. Decision Impact (MUST-HAVE)
            decisions = self._get_decision_impact()
            context.key_decisions = decisions['decisions']
            context.decision_makers = decisions['makers']
            context.decision_urgency = decisions['urgency']
            
            # Calculate actual quality based on what was provided
            fields_provided = sum([
                1 if problem_context['statement'] else 0,
                1 if problem_context['success'] else 0,
                1 if benchmarks['benchmarks'] else 0,
                1 if decisions['decisions'] else 0
            ])
            
            if fields_provided >= 3:
                quality_msg = "8.5-9.0/10 quality"
            elif fields_provided >= 1:
                quality_msg = "7.5-8.0/10 quality (partial context)"
            else:
                quality_msg = "7.0-7.5/10 quality (no enhanced info - same as skipping)"
            
            print(f"\nSUCCESS: Quick enhanced context collected. Questions will be {quality_msg}")
        elif enhanced_choice == 'all':
            print("\nCollecting ALL enhanced context for 9.5/10 premium quality...")
            # 1. Problem Definition
            problem_context = self._get_problem_definition()
            context.problem_statement = problem_context['statement']
            context.problem_symptoms = problem_context['symptoms']
            context.success_criteria = problem_context['success']
            
            # 2. Hypotheses & Assumptions
            hypothesis_context = self._get_hypotheses()
            context.hypotheses = hypothesis_context['hypotheses']
            context.key_factors = hypothesis_context['factors']
            context.constraints = hypothesis_context['constraints']
            
            # 3. Expected Data Profile
            data_profile = self._get_data_profile()
            context.expected_data_type = data_profile['type']
            context.time_span = data_profile['timespan']
            context.data_granularity = data_profile['granularity']
            
            # 4. Benchmarks & Thresholds
            benchmarks = self._get_benchmarks()
            context.comparison_benchmarks = benchmarks['benchmarks']
            context.performance_thresholds = benchmarks['thresholds']
            context.performance_definition = benchmarks['definition']
            
            # 5. Decision Impact
            decisions = self._get_decision_impact()
            context.key_decisions = decisions['decisions']
            context.decision_makers = decisions['makers']
            context.decision_urgency = decisions['urgency']
            
            # 6. Risk & Priorities
            risks = self._get_risk_priorities()
            context.high_risk_areas = risks['high_risk']
            context.critical_insights = risks['critical']
            context.sensitive_areas = risks['sensitive']
            
            # Calculate actual quality based on what was provided
            fields_provided = sum([
                1 if problem_context['statement'] else 0,
                1 if problem_context['success'] else 0,
                1 if hypothesis_context['hypotheses'] else 0,
                1 if hypothesis_context['factors'] else 0,
                1 if data_profile['type'] else 0,
                1 if data_profile['timespan'] else 0,
                1 if benchmarks['benchmarks'] else 0,
                1 if decisions['decisions'] else 0,
                1 if risks['high_risk'] else 0,
                1 if risks['critical'] else 0
            ])
            
            if fields_provided >= 8:
                quality_msg = "9.0-9.5/10 premium quality"
            elif fields_provided >= 5:
                quality_msg = "8.5-9.0/10 quality (strong context)"
            elif fields_provided >= 2:
                quality_msg = "7.5-8.0/10 quality (partial context)"
            elif fields_provided >= 1:
                quality_msg = "7.0-7.5/10 quality (minimal enhancement)"
            else:
                quality_msg = "7.0-7.5/10 quality (no enhanced info - same as skipping)"
            
            print(f"\nSUCCESS: Comprehensive enhanced context collected. Questions will be {quality_msg}")
        elif enhanced_choice == 'custom':
            print("\nCustom selection - Choose which questions to answer:")
            selected = self._get_custom_enhanced_selection()
            
            if 'problem' in selected:
                problem_context = self._get_problem_definition()
                context.problem_statement = problem_context['statement']
                context.problem_symptoms = problem_context['symptoms']
                context.success_criteria = problem_context['success']
            
            if 'hypotheses' in selected:
                hypothesis_context = self._get_hypotheses()
                context.hypotheses = hypothesis_context['hypotheses']
                context.key_factors = hypothesis_context['factors']
                context.constraints = hypothesis_context['constraints']
            
            if 'data_profile' in selected:
                data_profile = self._get_data_profile()
                context.expected_data_type = data_profile['type']
                context.time_span = data_profile['timespan']
                context.data_granularity = data_profile['granularity']
            
            if 'benchmarks' in selected:
                benchmarks = self._get_benchmarks()
                context.comparison_benchmarks = benchmarks['benchmarks']
                context.performance_thresholds = benchmarks['thresholds']
                context.performance_definition = benchmarks['definition']
            
            if 'decisions' in selected:
                decisions = self._get_decision_impact()
                context.key_decisions = decisions['decisions']
                context.decision_makers = decisions['makers']
                context.decision_urgency = decisions['urgency']
            
            if 'risks' in selected:
                risks = self._get_risk_priorities()
                context.high_risk_areas = risks['high_risk']
                context.critical_insights = risks['critical']
                context.sensitive_areas = risks['sensitive']
            
            # Calculate actual quality based on what was actually filled
            total_fields = 0
            for category in selected:
                if category == 'problem' and (problem_context.get('statement') or problem_context.get('success')):
                    total_fields += sum([1 if problem_context.get('statement') else 0, 1 if problem_context.get('success') else 0])
                elif category == 'hypotheses' and (hypothesis_context.get('hypotheses') or hypothesis_context.get('factors')):
                    total_fields += sum([1 if hypothesis_context.get('hypotheses') else 0, 1 if hypothesis_context.get('factors') else 0])
                elif category == 'data_profile' and (data_profile.get('type') or data_profile.get('timespan')):
                    total_fields += sum([1 if data_profile.get('type') else 0, 1 if data_profile.get('timespan') else 0])
                elif category == 'benchmarks' and benchmarks.get('benchmarks'):
                    total_fields += 1
                elif category == 'decisions' and decisions.get('decisions'):
                    total_fields += 1
                elif category == 'risks' and (risks.get('high_risk') or risks.get('critical')):
                    total_fields += sum([1 if risks.get('high_risk') else 0, 1 if risks.get('critical') else 0])
            
            if total_fields >= 6:
                quality_msg = "9.0-9.5/10 quality (excellent context)"
            elif total_fields >= 3:
                quality_msg = "8.5-9.0/10 quality (good context)"
            elif total_fields >= 1:
                quality_msg = "7.5-8.0/10 quality (partial context)"
            else:
                quality_msg = "7.0-7.5/10 quality (no enhanced info - same as skipping)"
            
            print(f"\nSUCCESS: Custom context collected. Questions will be {quality_msg}")
        
        # Save context for future use
        self._save_context(context)
        
        print("\nSUCCESS: Context collection complete!")
        print(f"Analysis Focus: {context.subject_area}")
        print(f"Primary Objectives: {', '.join(context.analysis_objectives[:2])}...")
        print(f"Target Audience: {context.target_audience}")
        print()
        
        return context
    
    def _get_predefined_context_choice(self) -> Optional[DatasetContext]:
        """Allow user to choose from predefined contexts."""
        print("Would you like to use a predefined context template? (recommended for faster setup)")
        print()
        
        contexts = list(self.predefined_contexts.keys())
        for i, context_name in enumerate(contexts, 1):
            context = self.predefined_contexts[context_name]
            print(f"{i}. {context.subject_area.title()}")
            print(f"   Focus: {', '.join(context.analysis_objectives[:2])}")
            print(f"   Audience: {context.target_audience}")
            print()
        
        print(f"{len(contexts) + 1}. Custom context (I'll provide my own details)")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (1-{}) or press Enter for custom: ".format(len(contexts) + 1)).strip()
                
                if not choice:  # Enter pressed - use custom
                    return None
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(contexts):
                    selected_context = self.predefined_contexts[contexts[choice_num - 1]]
                    print(f"\nSUCCESS: Selected: {selected_context.subject_area.title()}")
                    
                    # Allow minor customizations
                    if self._confirm_customization():
                        return self._customize_predefined_context(selected_context)
                    else:
                        return selected_context
                        
                elif choice_num == len(contexts) + 1:
                    return None  # Use custom context
                else:
                    print("ERROR: Invalid choice. Please select a valid option.")
                    
            except ValueError:
                print("ERROR: Please enter a valid number.")
    
    def _confirm_customization(self) -> bool:
        """Ask if user wants to customize the predefined context."""
        while True:
            customize = input("Would you like to customize this template? (y/n): ").strip().lower()
            if customize in ['y', 'yes']:
                return True
            elif customize in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def _customize_predefined_context(self, base_context: DatasetContext) -> DatasetContext:
        """Allow user to customize a predefined context."""
        print(f"\nCustomizing {base_context.subject_area} template:")
        print()
        
        # Create a copy to modify
        context = DatasetContext(
            subject_area=base_context.subject_area,
            analysis_objectives=base_context.analysis_objectives.copy(),
            target_audience=base_context.target_audience,
            dataset_background=base_context.dataset_background,
            business_context=base_context.business_context,
            time_sensitivity=base_context.time_sensitivity
        )
        
        # Allow modifications
        new_objectives = input(f"Analysis objectives (current: {', '.join(context.analysis_objectives)})\nEnter new objectives (comma-separated) or press Enter to keep current: ").strip()
        if new_objectives:
            context.analysis_objectives = [obj.strip() for obj in new_objectives.split(',')]
        
        new_audience = input(f"Target audience (current: {context.target_audience})\nEnter new audience or press Enter to keep current: ").strip()
        if new_audience:
            context.target_audience = new_audience
            
        new_business_context = input(f"Business context (current: {context.business_context})\nEnter new context or press Enter to keep current: ").strip()
        if new_business_context:
            context.business_context = new_business_context
            
        return context
    
    def _get_subject_area(self) -> str:
        """Get the subject area for analysis."""
        print("SUBJECT AREA")
        print("What domain or field does your data relate to?")
        print("Examples: financial analysis, marketing analytics, sales performance, customer behavior, etc.")
        print()
        
        while True:
            subject_area = input("Subject area: ").strip()
            if subject_area:
                return subject_area.lower()
            print("ERROR: Please provide a subject area.")
    
    def _get_analysis_objectives(self) -> List[str]:
        """Get the analysis objectives."""
        print("\nANALYSIS OBJECTIVES")
        print("What are your main goals for analyzing this data? (separate multiple objectives with commas)")
        print("Examples: trend analysis, performance evaluation, risk assessment, forecasting, etc.")
        print()
        
        while True:
            objectives_input = input("Analysis objectives: ").strip()
            if objectives_input:
                objectives = [obj.strip().lower() for obj in objectives_input.split(',')]
                return [obj for obj in objectives if obj]  # Remove empty strings
            print("ERROR: Please provide at least one analysis objective.")
    
    def _get_target_audience(self) -> str:
        """Get the target audience for the analysis."""
        print("\nTARGET AUDIENCE")
        print("Who will be using these analytical insights?")
        print("Examples: executives, data analysts, marketing managers, financial analysts, etc.")
        print()
        
        while True:
            audience = input("Target audience: ").strip()
            if audience:
                return audience.lower()
            print("ERROR: Please specify the target audience.")
    
    def _get_dataset_background(self) -> str:
        """Get background information about the dataset."""
        print("\nDATASET BACKGROUND")
        print("Please provide some background about your dataset(s):")
        print("Examples: source of data, time period covered, data collection method, etc.")
        print("(Optional - press Enter to skip)")
        print()
        
        background = input("Dataset background: ").strip()
        return background if background else "No background information provided"
    
    def _get_business_context(self) -> str:
        """Get business context for the analysis."""
        print("\nBUSINESS CONTEXT")
        print("What business decisions or strategies will this analysis support?")
        print("Examples: budget allocation, strategic planning, process optimization, etc.")
        print("(Optional - press Enter to skip)")
        print()
        
        context = input("Business context: ").strip()
        return context if context else "General business analysis"
    
    def _get_time_sensitivity(self) -> str:
        """Get the time sensitivity of the analysis."""
        print("\n⏰ TIME SENSITIVITY")
        print("How time-sensitive is this analysis?")
        print("1. High (urgent, immediate decisions)")
        print("2. Medium (important, near-term planning)")
        print("3. Low (exploratory, long-term insights)")
        print()
        
        while True:
            try:
                choice = input("Time sensitivity (1-3): ").strip()
                if choice == '1':
                    return "high"
                elif choice == '2':
                    return "medium"
                elif choice == '3':
                    return "low"
                else:
                    print("ERROR: Please enter 1, 2, or 3.")
            except:
                print("ERROR: Please enter a valid choice.")
    
    def _save_context(self, context: DatasetContext) -> None:
        """Save context to file for future reference."""
        try:
            context_data = asdict(context)
            context_data['timestamp'] = datetime.now().isoformat()
            
            # Load existing contexts if file exists
            existing_contexts = []
            if os.path.exists(self.context_file):
                try:
                    with open(self.context_file, 'r', encoding='utf-8') as f:
                        existing_contexts = json.load(f)
                except:
                    existing_contexts = []
            
            # Add new context
            existing_contexts.append(context_data)
            
            # Keep only last 10 contexts
            existing_contexts = existing_contexts[-10:]
            
            # Save updated contexts
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(existing_contexts, f, indent=2, ensure_ascii=False)
                
            logging.info(f"Context saved to {self.context_file}")
            
        except Exception as e:
            logging.warning(f"Could not save context: {e}")
    
    def load_recent_context(self) -> Optional[DatasetContext]:
        """Load the most recent context from saved contexts."""
        try:
            if not os.path.exists(self.context_file):
                return None
                
            with open(self.context_file, 'r', encoding='utf-8') as f:
                contexts = json.load(f)
                
            if not contexts:
                return None
                
            # Get most recent context
            recent_context_data = contexts[-1]
            
            # Remove timestamp for DatasetContext creation
            recent_context_data.pop('timestamp', None)
            
            return DatasetContext(**recent_context_data)
            
        except Exception as e:
            logging.warning(f"Could not load recent context: {e}")
            return None
    
    def get_quick_context(self, dataset_names: List[str]) -> DatasetContext:
        """Get a quick context based on dataset names and minimal input."""
        print("\n⚡ QUICK CONTEXT SETUP")
        print("For faster processing, we'll infer context from your dataset names:")
        print(f"Datasets: {', '.join(dataset_names)}")
        print()
        
        # Try to infer subject area from dataset names
        inferred_subject = self._infer_subject_area(dataset_names)
        
        print(f"Inferred subject area: {inferred_subject}")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            # Use predefined context if available
            for key, context in self.predefined_contexts.items():
                if inferred_subject in context.subject_area:
                    print(f"Using {context.subject_area} template")
                    return context
        
        # Fallback to minimal custom context
        subject_area = input("Enter subject area: ").strip() or inferred_subject
        objectives = input("Main objective (e.g., trend analysis): ").strip() or "exploratory analysis"
        
        return DatasetContext(
            subject_area=subject_area,
            analysis_objectives=[objectives],
            target_audience="data analysts",
            dataset_background=f"Analysis of {', '.join(dataset_names)}",
            business_context="Data-driven insights and decision support"
        )
    
    def _infer_subject_area(self, dataset_names: List[str]) -> str:
        """Infer subject area from dataset names."""
        combined_names = ' '.join(dataset_names).lower()
        
        if any(word in combined_names for word in ['stock', 'price', 'financial', 'revenue', 'profit']):
            return "financial analysis"
        elif any(word in combined_names for word in ['sales', 'customer', 'marketing', 'campaign']):
            return "sales and marketing analytics"
        elif any(word in combined_names for word in ['employee', 'hr', 'payroll', 'performance']):
            return "human resources analytics"
        elif any(word in combined_names for word in ['inventory', 'supply', 'logistics', 'operations']):
            return "operational analytics"
        else:
            return "general data analytics"
    
    # ===== ENHANCED CONTEXT COLLECTION METHODS FOR 9.5/10 QUALITY =====
    
    def _get_enhanced_context_choice(self) -> str:
        """Get user's choice for enhanced context collection."""
        while True:
            choice = input("Select option (1-4): ").strip()
            if choice == '1':
                return 'skip'
            elif choice == '2':
                return 'must_have'
            elif choice == '3':
                return 'all'
            elif choice == '4':
                return 'custom'
            else:
                print("ERROR: Please enter 1, 2, 3, or 4")
    
    def _get_custom_enhanced_selection(self) -> List[str]:
        """Allow user to select specific enhanced questions."""
        print()
        print("Select which enhanced questions to answer:")
        print("  1. Problem Definition (MUST-HAVE - High impact)")
        print("  2. Hypotheses & Assumptions")
        print("  3. Expected Data Profile")
        print("  4. Benchmarks & Thresholds (MUST-HAVE - High impact)")
        print("  5. Decision Impact (MUST-HAVE - High impact)")
        print("  6. Risk & Priorities")
        print()
        print("Enter numbers separated by commas (e.g., 1,4,5 for must-haves only):")
        print("Or press Enter to answer all")
        print()
        
        selection = input("Your selection: ").strip()
        
        if not selection:
            return ['problem', 'hypotheses', 'data_profile', 'benchmarks', 'decisions', 'risks']
        
        question_map = {
            '1': 'problem',
            '2': 'hypotheses',
            '3': 'data_profile',
            '4': 'benchmarks',
            '5': 'decisions',
            '6': 'risks'
        }
        
        selected = []
        for num in selection.split(','):
            num = num.strip()
            if num in question_map:
                selected.append(question_map[num])
        
        if not selected:
            print("WARNING: No valid selections. Using all questions.")
            return ['problem', 'hypotheses', 'data_profile', 'benchmarks', 'decisions', 'risks']
        
        return selected
    
    def _get_problem_definition(self) -> Dict[str, str]:
        """Get detailed problem statement and success criteria."""
        print("\n" + "="*60)
        print("1. PROBLEM DEFINITION (Quick Version)")
        print("="*60)
        print()
        
        print("What problem are you trying to solve?")
        print("Example: 'Declining profitability - need to identify cost drivers'")
        print("(Press Enter to skip - will use basic context only)")
        print()
        statement = input("Problem: ").strip()
        
        print("\nWhat do you want to achieve?")
        print("Example: 'Identify 10% cost reduction opportunities'")
        print("(Press Enter to skip - will use basic context only)")
        print()
        success = input("Goal: ").strip()
        
        return {
            'statement': statement,
            'symptoms': "",
            'success': success
        }
    
    def _get_hypotheses(self) -> Dict[str, any]:
        """Get hypotheses and key factors to investigate."""
        print("\n" + "="*60)
        print("2. HYPOTHESES & ASSUMPTIONS")
        print("="*60)
        print()
        
        print("Do you have any hypotheses about what might be causing the issue?")
        print("Example: 'Market competition increased' or 'Costs rising faster than revenue'")
        print("(Press Enter to skip)")
        print()
        
        hypotheses = []
        h = input("Main hypothesis: ").strip()
        if h:
            hypotheses.append(h)
        
        print("\nWhat factors are most important to investigate?")
        print("Example: 'pricing strategy, customer segments, seasonal patterns'")
        print("(Press Enter to skip)")
        print()
        factors = input("Key factors: ").strip()
        
        return {
            'hypotheses': hypotheses,
            'factors': factors,
            'constraints': ""
        }
    
    def _get_data_profile(self) -> Dict[str, str]:
        """Get expected data characteristics."""
        print("\n" + "="*60)
        print("3. EXPECTED DATA PROFILE")
        print("="*60)
        print()
        
        print("What type of data will you analyze?")
        print("1. Financial  2. Operational  3. Customer  4. Market  5. Mixed")
        print("(Press Enter to skip)")
        print()
        
        data_type_map = {
            '1': 'financial',
            '2': 'operational',
            '3': 'customer',
            '4': 'market',
            '5': 'mixed'
        }
        
        choice = input("Type (1-5): ").strip()
        data_type = data_type_map.get(choice, '')
        
        print("\nWhat time span will the data cover?")
        print("Example: '5 years historical', '2020-2023'")
        print("(Press Enter to skip)")
        print()
        timespan = input("Time span: ").strip()
        
        return {
            'type': data_type,
            'timespan': timespan,
            'granularity': ""
        }
    
    def _get_benchmarks(self) -> Dict[str, any]:
        """Get comparison benchmarks and performance thresholds."""
        print("\n" + "="*60)
        print("2. BENCHMARKS (Quick Version)")
        print("="*60)
        print()
        
        print("What should we compare against?")
        print("Example: 'Previous year performance and industry average'")
        print("(Press Enter to skip)")
        print()
        
        comparison = input("Compare to: ").strip()
        
        return {
            'benchmarks': [comparison] if comparison else [],
            'thresholds': "",
            'definition': ""
        }
    
    def _get_decision_impact(self) -> Dict[str, any]:
        """Get decision-making context and urgency."""
        print("\n" + "="*60)
        print("3. DECISIONS (Quick Version)")
        print("="*60)
        print()
        
        print("What decision will this analysis support?")
        print("Example: 'Budget allocation for next quarter'")
        print("(Press Enter to skip)")
        print()
        
        decision = input("Key decision: ").strip()
        
        return {
            'decisions': [decision] if decision else [],
            'makers': "",
            'urgency': ''
        }
    
    def _get_risk_priorities(self) -> Dict[str, any]:
        """Get risk factors and critical priorities."""
        print("\n" + "="*60)
        print("6. RISK FACTORS & PRIORITIES")
        print("="*60)
        print()
        
        print("What are the highest-risk areas to investigate?")
        print("Example: 'liquidity risks, customer retention, competitive threats'")
        print("(Press Enter to skip)")
        print()
        high_risk = input("High-risk areas: ").strip()
        
        print("\nWhat must-know insight is most critical?")
        print("Example: 'Which factors drive profitability most'")
        print("(Press Enter to skip)")
        print()
        critical = input("Critical insight: ").strip()
        
        return {
            'high_risk': high_risk,
            'critical': [critical] if critical else [],
            'sensitive': ""
        }

# Import pandas here to avoid circular imports
import pandas as pd
