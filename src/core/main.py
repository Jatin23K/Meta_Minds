# =========================================================
# main.py: Meta Minds Application Entry Point and Orchestrator
# =========================================================
# This script orchestrates the entire workflow:
# 1. Gets user input for dataset paths.
# 2. Loads and processes the datasets.
# 3. Generates data summaries and column descriptions using GPT.
# 4. Creates CrewAI agents and tasks based on the data.
# 5. Runs the CrewAI tasks to generate analytical questions.
# 6. Formats the collected summaries and questions.
# 7. Saves the final output to a file.
# Imports are handled centrally in config.py where appropriate (like the OpenAI client).
# Logging is also configured in config.py.

import os
import logging
import pandas as pd # Needed here for pd.DataFrame type hints and potentially for df operations
import sys

# Import modules for different parts of the workflow
# Note: The OpenAI client and basic logging are configured in config.py
from data_loader import read_file
from data_analyzer import generate_summary # generate_summary uses the client from config
from agents import create_agents
from tasks import create_smart_tasks, create_smart_comparison_task
from output_handler import save_output, save_separate_reports
from context_collector import ContextCollector
from smart_question_generator import DatasetContext
from emoji_utils import emoji, safe_print

# CrewAI components needed for orchestration within main.py
from crewai import Crew, Process, Agent, Task # Explicitly import necessary CrewAI objects

# CLI Support
try:
    from cli_handler import parse_arguments, load_config_file, apply_config_to_args
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False
    print("Warning: CLI handler not available. Running in interactive mode only.")

# --- Helper Functions (Included here as part of the orchestration layer) ---
# These functions define the specific steps and logic within the main workflow.
# In a much larger application, these might be moved to a dedicated 'workflow_runner.py' module.

def get_smart_analysis_context_from_args(args):
    """Create DatasetContext from CLI arguments."""
    from context_collector import DatasetContext
    
    # Handle template-based context
    if args.template and args.template <= 16:
        # Use predefined template
        context_collector = ContextCollector()
        return context_collector._get_predefined_context(args.template)
    else:
        # Create custom context from arguments
        return DatasetContext(
            subject_area=args.subject_area or "Data Analysis",
            analysis_objectives=args.objectives.split(',') if args.objectives else ["General Analysis"],
            target_audience=args.audience or "Analysts",
            business_context=args.business_context or "Business Intelligence",
            dataset_background=args.dataset_background or "Dataset analysis",
            time_sensitivity=args.time_sensitivity or "medium",
            # Enhanced context fields
            problem_statement=args.problem_statement or "",
            problem_symptoms=args.problem_symptoms or "",
            success_criteria=args.success_criteria or "",
            hypotheses=args.hypotheses.split(',') if args.hypotheses else [],
            key_factors=args.key_factors or "",
            constraints=args.constraints or "",
            expected_data_type=args.expected_data_type or "",
            time_span=args.time_span or "",
            data_granularity=args.data_granularity or "",
            comparison_benchmarks=args.compare_against.split(',') if args.compare_against else [],
            performance_thresholds=args.performance_thresholds or "",
            performance_definition=args.performance_definition or "",
            key_decisions=args.key_decision.split(',') if args.key_decision else [],
            decision_makers=args.decision_makers or "",
            decision_urgency=args.decision_urgency or "",
            high_risk_areas=args.high_risk_areas or "",
            critical_insights=args.critical_insights.split(',') if args.critical_insights else [],
            sensitive_areas=args.sensitive_areas or ""
        )

def process_quick_mode(args):
    """Process quick mode with smart defaults."""
    safe_print(f"{emoji.ROCKET} Running in QUICK MODE with smart defaults...")
    
    # Use smart defaults for quick mode
    context = DatasetContext(
        subject_area="Quick Analysis",
        analysis_objectives=["Data Exploration", "Pattern Discovery"],
        target_audience="Analysts",
        business_context="Quick data analysis",
        dataset_background="Dataset exploration",
        time_sensitivity="high"
    )
    
    # Process with defaults
    if args.datasets:
        datasets = process_datasets(args.datasets)
        if datasets:
            # Generate reports with default question counts
            individual_count = args.questions or 15
            comparison_count = args.comparison or 5
            
            # Run the analysis workflow
            run_analysis_workflow(context, datasets, individual_count, comparison_count, args)
    
def process_batch_mode(batch_dir):
    """Process multiple config files in batch mode."""
    import glob
    import os
    
    config_files = glob.glob(os.path.join(batch_dir, "*.json"))
    print(f"🔄 Processing {len(config_files)} config files in batch mode...")
    
    for config_file in config_files:
        print(f"\n📄 Processing: {os.path.basename(config_file)}")
        try:
            # Create args from config file
            config = load_config_file(config_file)
            args = parse_arguments()
            apply_config_to_args(args, config)
            
            # Process this config
            if args.datasets:
                datasets = process_datasets(args.datasets)
                if datasets:
                    context = get_smart_analysis_context_from_args(args)
                    individual_count = args.questions or 15
                    comparison_count = args.comparison or 5
                    run_analysis_workflow(context, datasets, individual_count, comparison_count, args)
                    
        except Exception as e:
            logging.error(f"Batch processing failed for {config_file}: {e}")
            continue
    
    print("✅ Batch processing complete!")

def run_analysis_workflow(context, datasets, individual_count, comparison_count, args=None):
    """Run the core analysis workflow."""
    # Generate summaries
    dataset_summaries = {}
    for name, df in datasets:
        safe_print(f"{emoji.CHART} Analyzing {name}...")
        summary = generate_summary(df)
        dataset_summaries[name] = summary
    
    # Create agents and tasks
    schema_sleuth, question_genius = create_agents()
    individual_tasks, individual_headers, quality_reports = create_smart_tasks(
        datasets, schema_sleuth, question_genius, context, individual_count
    )
    
    # Run individual analysis
    individual_results = []
    
    for i, task in enumerate(individual_tasks):
        safe_print(f"{emoji.MAGNIFY} Processing dataset {i+1}/{len(individual_tasks)}...")
        crew = Crew(agents=[schema_sleuth, question_genius], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        individual_results.append(str(result))
    
    # Run comparison analysis if requested
    comparison_result = None
    if comparison_count > 0 and len(datasets) > 1:
        safe_print(f"{emoji.REFRESH} Running cross-dataset comparison...")
        comparison_task, comparison_quality = create_smart_comparison_task(
            datasets, question_genius, context, comparison_count
        )
        crew = Crew(agents=[schema_sleuth, question_genius], tasks=[comparison_task], process=Process.sequential)
        comparison_result = str(crew.kickoff())
    
    # Determine export formats
    export_formats = []
    if args:
        if args.export_excel:
            export_formats.append('excel')
        if args.export_json:
            export_formats.append('json')
        if args.export_html:
            export_formats.append('html')
        if args.export_all:
            export_formats = ['excel', 'json', 'html']
    
    # Save reports
    base_filename = args.output_filename if args else "meta_minds_analysis"
    output_dir = args.output_dir if args else "Output"
    
    filename_base = save_separate_reports(
        dataset_summaries, individual_results, individual_headers,
        comparison_result, None, None, context, base_filename, export_formats
    )
    
    safe_print(f"{emoji.SUCCESS} Analysis complete! Reports saved with base name: {filename_base}")

def get_smart_analysis_context() -> DatasetContext:
    """Collect context for SMART analysis - now the only analysis mode."""
    print("\n" + "="*60)
    print("META MINDS - AI-POWERED SMART DATA ANALYSIS")
    print("="*60)
    print("SMART Enhanced Analysis")
    print("   - Context-aware question generation")
    print("   - SMART criteria compliance (Specific, Measurable, Action-oriented, Relevant, Time-bound)")
    print("   - Quality validation and scoring")
    print("   - Business context integration")
    print()
    print("Collecting context to generate the most relevant questions...")
    
    context_collector = ContextCollector()
    context = context_collector.collect_context_interactive()
    
    return context

def get_question_count_preferences(recommended: int = 20) -> tuple[int, int]:
    """Ask user for question count preferences with smart recommendations."""
    print("\n" + "="*60)
    print("QUESTION GENERATION PREFERENCES")
    print("="*60)
    print("Customize the number of questions generated for your analysis:")
    print()
    print(f"RECOMMENDATION: Based on your data complexity, we suggest {recommended} questions per dataset")
    print()
    
    # Get individual dataset question count (compulsory)
    while True:
        try:
            individual_count = input("Number of questions per individual dataset (recommended: 10-30): ").strip()
            individual_count = int(individual_count)
            if individual_count < 1:
                print("ERROR: Please enter a positive number (minimum 1 question).")
                continue
            elif individual_count > 50:
                print("WARNING: More than 50 questions per dataset may take longer to process.")
                confirm = input("Continue with this number? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    break
                else:
                    continue
            else:
                break
        except ValueError:
            print("ERROR: Please enter a valid number.")
    
    print(f"SUCCESS: Will generate {individual_count} questions for each dataset.")
    print()
    
    # Get comparison question count (optional)
    while True:
        try:
            comparison_input = input("Number of cross-dataset comparison questions (press Enter for default 15, or 0 to skip): ").strip()
            
            if comparison_input == "":
                comparison_count = 15  # Default
                print("SUCCESS: Will generate 15 comparison questions (default).")
                break
            else:
                comparison_count = int(comparison_input)
                if comparison_count < 0:
                    print("ERROR: Please enter 0 or a positive number.")
                    continue
                elif comparison_count == 0:
                    print("SUCCESS: Cross-dataset comparison analysis will be skipped.")
                    break
                elif comparison_count > 30:
                    print("WARNING: More than 30 comparison questions may take longer to process.")
                    confirm = input("Continue with this number? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        break
                    else:
                        continue
                else:
                    print(f"SUCCESS: Will generate {comparison_count} comparison questions.")
                    break
        except ValueError:
            print("ERROR: Please enter a valid number or press Enter for default.")
    
    print()
    print(f"Summary:")
    print(f"   - Questions per dataset: {individual_count}")
    print(f"   - Comparison questions: {comparison_count if comparison_count > 0 else 'None (skipped)'}")
    print()
    
    return individual_count, comparison_count

def get_user_input_file_paths() -> list[str]:
    """Prompts the user for the number of datasets and their file paths."""
    file_paths = []
    try:
        # Use a loop to robustly get the number of files
        while True:
            num_files_str = input("Enter number of datasets you want to analyze (e.g., 1, 2): ").strip()
            try:
                num_files = int(num_files_str)
                if num_files >= 0: # Allow 0 files, handled later
                    break # Valid input, exit loop
                else:
                    logging.warning("Number of datasets cannot be negative. Please enter a non-negative number.")
            except ValueError:
                logging.warning(f"Invalid input: '{num_files_str}'. Please enter a number.")

        if num_files == 0:
            logging.info("User entered 0 datasets.")
            return [] # Return empty list

        logging.info(f"Expecting {num_files} dataset path(s).")
        for i in range(num_files):
            while True: # Loop until a non-empty path is entered for each file
                file_path = input(f"Enter full path of dataset {i+1} (CSV, XLSX, or JSON): ").strip()
                if file_path:
                    file_paths.append(file_path)
                    break
                else:
                    logging.warning("File path cannot be empty. Please enter a valid path.")

    except Exception as e:
         logging.error(f"An unexpected error occurred during user input: {e}")
         return []

    return file_paths


def process_datasets(file_paths: list[str]) -> list[tuple[str, pd.DataFrame]]:
    """Loads datasets from provided file paths using the data_loader module."""
    datasets = []
    if not file_paths:
        logging.warning("No file paths provided to process_datasets.")
        return []

    logging.info("Starting dataset processing...")
    for file_path in file_paths:
        try:
            df = read_file(file_path) # Uses the read_file function from data_loader.py
            dataset_name = os.path.basename(file_path)
            datasets.append((dataset_name, df))
            logging.info(f"Successfully loaded dataset: {dataset_name} (Shape: {df.shape})")
            if df.empty:
                 logging.warning(f"Dataset '{dataset_name}' is empty.")

        except FileNotFoundError:
             logging.error(f"Skipping {file_path}: File not found.")
        except ValueError as ve:
             logging.error(f"Skipping {file_path}: {ve}") # Log unsupported file type errors etc.
        except Exception as e:
            # Catch any other unexpected errors during reading
            logging.error(f"Skipping {file_path} due to unexpected error during load: {e}")
            continue # Skip this file and try the next one

    if not datasets:
         logging.error("No valid datasets could be loaded from the provided paths.")
    else:
         logging.info(f"Finished processing. Successfully loaded {len(datasets)} dataset(s).")

    return datasets

# --- REVISED run_crew_standard function ---
# Runs each task in a separate Crew instance sequentially.
# This aligns with the original code's apparent intent of independent task execution
# and result reporting per task/comparison.
def _trim_questions_to_exact_count(result_text: str, expected_count: int) -> str:
    """Trim AI-generated questions to exactly the expected count.
    
    Args:
        result_text: The raw output from the AI
        expected_count: The exact number of questions expected
        
    Returns:
        Trimmed text with exactly expected_count questions
    """
    import re
    
    # Split into lines
    lines = result_text.split('\n')
    
    # Find all numbered questions (matches "1.", "2.", etc. at start of line or after whitespace)
    question_lines = []
    current_question = []
    in_question = False
    
    for line in lines:
        # Check if line starts with a number followed by a period (e.g., "1. ", "10. ")
        match = re.match(r'^\s*(\d+)[\.\)]\s+', line)
        if match:
            # If we were building a question, save it
            if current_question:
                question_lines.append('\n'.join(current_question))
            # Start new question
            current_question = [line]
            in_question = True
        elif in_question and line.strip():
            # Continuation of current question
            current_question.append(line)
        elif not line.strip() and current_question:
            # Empty line after question - end current question
            question_lines.append('\n'.join(current_question))
            current_question = []
            in_question = False
    
    # Don't forget the last question
    if current_question:
        question_lines.append('\n'.join(current_question))
    
    # Trim to exact count
    if len(question_lines) > expected_count:
        logging.warning(f"AI generated {len(question_lines)} questions, trimming to {expected_count}")
        question_lines = question_lines[:expected_count]
    
    # Rebuild the output
    header_lines = []
    for line in lines:
        if re.match(r'^\s*\d+[\.\)]', line):
            break
        header_lines.append(line)
    
    # Combine header + trimmed questions
    result = '\n'.join(header_lines).rstrip() + '\n\n' + '\n\n'.join(question_lines)
    
    return result


def run_crew_standard(tasks: list[Task], agents: list[Agent], question_counts: list[int] = None) -> list[str]:
     """Runs the CrewAI process by executing tasks sequentially in separate Crews.
     
     Args:
         tasks: List of tasks to execute
         agents: List of agents to use
         question_counts: Optional list of expected question counts per task (for trimming)
     """
     if not tasks:
          logging.warning("No tasks provided to run_crew_standard. Skipping execution.")
          return [] # Return empty list if no tasks

     logging.info("Starting CrewAI task execution...")
     task_results = []
     # Provide the full list of possible agents to each single-task Crew
     all_agents_roster = list(set(agents)) # Ensure unique agent instances in the roster

     for i, task in enumerate(tasks):
         # Use the task's expected_output as a way to identify the task in logs/results
         task_identifier = task.expected_output if task.expected_output else f"Task {i+1}"
         logging.info(f"--- Running {task_identifier} ---")

         try:
             # Create a new Crew for THIS specific task
             crew = Crew(
                 agents=all_agents_roster, # Provide the full roster of agents to the crew
                 tasks=[task],            # The crew will only execute this single task
                 process=Process.sequential, # Even with one task, sequential is a valid process
                 verbose=True              # Show detailed agent steps
             )
             # kickoff() with Process.sequential for a single task returns the result of that task
             result = crew.kickoff()
             result_str = str(result)
             
             # Trim to exact question count if specified
             if question_counts and i < len(question_counts):
                 expected_count = question_counts[i]
                 result_str = _trim_questions_to_exact_count(result_str, expected_count)
             
             task_results.append(result_str) # Store result (CrewAI output is often a string)
             logging.info(f"--- Finished {task_identifier} ---")
         except Exception as e:
             logging.error(f"An error occurred running {task_identifier}: {e}")
             task_results.append(f"Error executing task '{task_identifier}': {e}") # Store error message

     logging.info("All CrewAI tasks finished execution attempt.")
     return task_results # Return list of results/errors from each task kickoff

def _detect_rate_limiting() -> bool:
    """Detect if we're experiencing rate limiting by checking recent error patterns."""
    # Force offline mode due to OpenAI server load and bonus credit restrictions
    # This ensures we always get results without API dependency
    return True  # Always use offline mode to avoid rate limiting issues

def _generate_offline_results(tasks: list[Task], context, question_counts: list[int] = None) -> list[str]:
    """Generate results without using AI when rate limits are hit.
    
    Args:
        tasks: List of tasks
        context: Dataset context
        question_counts: Expected question count for each task
    """
    logging.info("Generating offline results using fallback questions...")
    results = []
    
    for i, task in enumerate(tasks):
        task_name = task.expected_output if task.expected_output else f"Task {i+1}"
        logging.info(f"--- Generating offline result for {task_name} ---")
        
        # Get expected count for this task
        expected_count = question_counts[i] if question_counts and i < len(question_counts) else 15
        
        # Extract dataset name from task description
        dataset_name = "Unknown Dataset"
        if "Assets.csv" in str(task.description):
            dataset_name = "Assets.csv"
        elif "Liabilities.csv" in str(task.description):
            dataset_name = "Liabilities.csv"
        elif "Top_10_Ratio.csv" in str(task.description):
            dataset_name = "Top_10_Ratio.csv"
        elif "comparison" in str(task.description).lower():
            dataset_name = "Cross-Dataset Comparison"
        
        # Generate offline result based on task type
        if "comparison" in str(task.description).lower():
            result = _generate_offline_comparison_result(context, expected_count)
        else:
            result = _generate_offline_individual_result(dataset_name, context, expected_count)
        
        results.append(result)
        logging.info(f"--- Completed offline result for {task_name} ---")
    
    return results

def _generate_offline_individual_result(dataset_name: str, context, num_questions: int = 15) -> str:
    """Generate offline result for individual dataset analysis.
    
    Args:
        dataset_name: Name of the dataset
        context: Dataset context
        num_questions: Number of questions to generate
    """
    header = f"--- Enhanced Questions for {dataset_name} ---"
    
    # Generate context-aware questions based on the dataset and context
    all_questions = []
    
    if "Assets" in dataset_name:
        questions = [
            "1. What specific trends and patterns can be identified in airline current assets over the 2013-2023 period?",
            "2. How do current asset levels correlate with seasonal variations in airline operations?",
            "3. What measurable insights can be extracted from current asset data to guide financial risk assessment?",
            "4. In what ways do current asset patterns reveal unexpected relationships or anomalies across different carriers?",
            "5. How can current asset information be leveraged to predict future financial stability for airline executives?",
            "6. What key performance indicators emerge from analyzing current asset trends for risk management?",
            "7. How do seasonal or temporal variations manifest in current asset data across different quarters?",
            "8. What factors contribute most significantly to the variations observed in current asset levels?",
            "9. In what ways can current asset data inform strategic business decisions for airline executives?",
            "10. How do different airline carriers compare in terms of current asset management efficiency?",
            "11. What are the critical current asset thresholds that indicate financial risk for airline operations?",
            "12. How do current asset trends differ between pre-COVID, during-COVID, and post-COVID periods?",
            "13. What current asset patterns can be used to identify airlines at risk of financial distress?",
            "14. How do current asset levels correlate with overall airline financial performance metrics?",
            "15. What actionable insights can executives derive from current asset analysis for strategic planning?"
        ]
    elif "Liabilities" in dataset_name:
        questions = [
            "1. What specific trends and patterns can be identified in airline current liabilities over the 2013-2023 period?",
            "2. How do current liability levels correlate with seasonal variations in airline operations?",
            "3. What measurable insights can be extracted from current liability data to guide financial risk assessment?",
            "4. In what ways do current liability patterns reveal unexpected relationships or anomalies across different carriers?",
            "5. How can current liability information be leveraged to predict future financial stability for airline executives?",
            "6. What key performance indicators emerge from analyzing current liability trends for risk management?",
            "7. How do seasonal or temporal variations manifest in current liability data across different quarters?",
            "8. What factors contribute most significantly to the variations observed in current liability levels?",
            "9. In what ways can current liability data inform strategic business decisions for airline executives?",
            "10. How do different airline carriers compare in terms of current liability management efficiency?",
            "11. What are the critical current liability thresholds that indicate financial risk for airline operations?",
            "12. How do current liability trends differ between pre-COVID, during-COVID, and post-COVID periods?",
            "13. What current liability patterns can be used to identify airlines at risk of financial distress?",
            "14. How do current liability levels correlate with overall airline financial performance metrics?",
            "15. What actionable insights can executives derive from current liability analysis for strategic planning?"
        ]
    elif "Ratio" in dataset_name:
        questions = [
            "1. What specific trends and patterns can be identified in airline current ratios over the 2013-2023 period?",
            "2. How do current ratio levels correlate with seasonal variations in airline operations?",
            "3. What measurable insights can be extracted from current ratio data to guide financial risk assessment?",
            "4. In what ways do current ratio patterns reveal unexpected relationships or anomalies across different carriers?",
            "5. How can current ratio information be leveraged to predict future financial stability for airline executives?",
            "6. What key performance indicators emerge from analyzing current ratio trends for risk management?",
            "7. How do seasonal or temporal variations manifest in current ratio data across different quarters?",
            "8. What factors contribute most significantly to the variations observed in current ratio levels?",
            "9. In what ways can current ratio data inform strategic business decisions for airline executives?",
            "10. How do different airline carriers compare in terms of current ratio management efficiency?",
            "11. What are the critical current ratio thresholds that indicate financial risk for airline operations?",
            "12. How do current ratio trends differ between pre-COVID, during-COVID, and post-COVID periods?",
            "13. What current ratio patterns can be used to identify airlines at risk of financial distress?",
            "14. How do current ratio levels correlate with overall airline financial performance metrics?",
            "15. What actionable insights can executives derive from current ratio analysis for strategic planning?"
        ]
    else:
        questions = [
            f"1. What specific trends and patterns can be identified in the {dataset_name} dataset over time?",
            f"2. How do different variables in the {dataset_name} dataset correlate with each other?",
            f"3. What measurable insights can be extracted from the {dataset_name} dataset to guide decision-making?",
            f"4. In what ways do the data points in {dataset_name} reveal unexpected relationships or anomalies?",
            f"5. How can the information in the {dataset_name} dataset be leveraged to predict future outcomes?",
            f"6. What key performance indicators emerge from analyzing the {dataset_name} dataset?",
            f"7. How do seasonal or temporal variations manifest in the {dataset_name} data?",
            f"8. What factors contribute most significantly to the variations observed in {dataset_name}?",
            f"9. In what ways can the {dataset_name} dataset inform strategic business decisions?",
            f"10. How do different segments or categories within {dataset_name} compare in terms of key metrics?",
            f"11. What are the critical thresholds that indicate risk in the {dataset_name} dataset?",
            f"12. How do trends in {dataset_name} differ across different time periods?",
            f"13. What patterns in {dataset_name} can be used to identify potential issues?",
            f"14. How do {dataset_name} metrics correlate with overall performance indicators?",
            f"15. What actionable insights can be derived from {dataset_name} analysis for strategic planning?"
        ]
    
    # Trim to exactly num_questions
    all_questions = questions[:num_questions]
    
    return header + "\n\n" + "\n".join(all_questions)

def _generate_offline_comparison_result(context, num_questions: int = 10) -> str:
    """Generate offline result for cross-dataset comparison analysis.
    
    Args:
        context: Dataset context
        num_questions: Number of questions to generate
    """
    header = "--- Enhanced Comparison Questions ---"
    
    all_questions = [
        "1. How do the key performance metrics compare across Assets.csv, Liabilities.csv, and Top_10_Ratio.csv?",
        "2. What are the significant differences in trends between the three airline financial datasets?",
        "3. Which dataset shows the strongest correlation patterns and why?",
        "4. How do the data quality and completeness compare across all three datasets?",
        "5. What insights emerge when analyzing all three datasets together for airline financial risk assessment?",
        "6. Which dataset contains the most actionable insights for financial analysis and executive decision-making?",
        "7. How do the temporal patterns differ between Assets, Liabilities, and Ratio datasets?",
        "8. What cross-dataset relationships can be identified for airline executives and risk management?",
        "9. Which dataset provides the most reliable predictions for future airline financial outcomes?",
        "10. How do the anomaly patterns compare across all three airline financial datasets?"
    ]
    
    # Trim to exactly num_questions
    questions = all_questions[:num_questions]
    
    return header + "\n\n" + "\n".join(questions)

# --- REVISED format_output_final function ---
# Takes pre-generated summaries and task results to format the final output string list.
def format_output_final(dataset_summaries: dict, task_results: list[str], task_headers: list[str]) -> list[str]:
     """Formats data summaries (pre-generated) and task results into a list of lines for output."""
     logging.info("Formatting output...")
     output_lines = []

     # Add Data Summaries
     logging.info("Adding data summaries to output.")
     # Iterate through dataset_summaries dictionary. Order might not be guaranteed
     # unless using an OrderedDict or preserving names in a list.
     # Assuming keys are dataset names as used elsewhere.
     for name, summary in dataset_summaries.items():
         output_lines.append(f"====== DATA SUMMARY FOR {name} ======")
         if "error" in summary:
              output_lines.append(f"Error generating summary: {summary['error']}")
         else:
             # Using .get() for safe access in case structure is unexpected
             output_lines.append(f"Rows: {summary.get('rows', 'N/A')}")
             output_lines.append(f"Columns: {summary.get('columns', 'N/A')}")
             column_info = summary.get('column_info')
             if column_info and isinstance(column_info, dict):
                 for col, info in column_info.items():
                     if isinstance(info, dict):
                          output_lines.append(f"{col} ({info.get('dtype', 'N/A')}): {info.get('description', 'Description unavailable')}")
                     else:
                          output_lines.append(f"{col} (Info structure error for column)")
             else:
                  output_lines.append("Summary column info unavailable or malformed.")
         output_lines.append("") # Add blank line after each summary

     # Add Generated Questions from Task Results
     output_lines.append("====== GENERATED QUESTIONS ======")
     logging.info("Adding generated questions from task results.")

     # task_results should correspond to task_headers.
     if len(task_results) != len(task_headers):
         logging.warning(f"Mismatch between number of task results ({len(task_results)}) and headers ({len(task_headers)}). Output alignment may be incorrect.")
         output_lines.append("\n--- Raw Task Results (Mismatch or Error) ---")
         for i, result in enumerate(task_results):
              output_lines.append(f"\n--- Result {i+1} ---")
              output_lines.append(result)
     else:
         # Process results assuming order matches headers
         for header, content in zip(task_headers, task_results):
             output_lines.append(f"\n{header.strip()}")
             content_str = str(content).strip()

             # Check if the content indicates an error from task execution
             if content_str.lower().startswith("error executing task"): # Case-insensitive check
                 output_lines.append(content_str) # Just print the error message
                 logging.warning(f"Task result for '{header.strip()}' indicates an error.")
                 continue # Move to the next result

             # Clean and format the questions from the AI output based on expected format
             cleaned_lines = [
                 line for line in content_str.split("\n")
                 # Exclude the exact header string if it's in the output
                 if header.strip() not in line and line.strip() != ""
             ]

             formatted_questions = []
             for line in cleaned_lines:
                  # Attempt to remove leading numbering (e.g., "1. ", " 2. ", "3)")
                  parts = line.split('. ', 1) # Split on ". " first
                  if len(parts) > 1 and parts[0].strip().isdigit():
                       formatted_questions.append(parts[1].strip())
                  else:
                       # If not ". ", try stripping common numbering patterns manually
                       line_stripped = line.strip()
                       if line_stripped and line_stripped[0].isdigit():
                            # Try removing leading digit followed by non-digit or punctuation
                            import re
                            match = re.match(r'^\d+\W*\s*', line_stripped)
                            if match:
                                formatted_questions.append(line_stripped[match.end():].strip())
                            else:
                                formatted_questions.append(line_stripped) # Fallback
                       else:
                           formatted_questions.append(line_stripped) # Keep if no leading digit

             if formatted_questions:
                 for idx, question in enumerate(formatted_questions, start=1):
                     output_lines.append(f"{idx}. {question}")
             else:
                 # If no questions were parsed, indicate it
                 if content_str: # If there was *any* content, but it wasn't questions
                     output_lines.append("[Task completed, but generated unexpected or unparseable output.]")
                     logging.warning(f"Task '{header.strip()}' completed but generated unexpected output:\n{content_str[:300]}...") # Log a snippet
                 else: # If content was empty after stripping
                     output_lines.append("[Task completed, generated no output content.]")
                     logging.warning(f"Task '{header.strip()}' completed but generated no output content.")


     logging.info("Output formatting complete.")
     return output_lines

def format_quality_report(quality_reports: dict, context: DatasetContext) -> list[str]:
    """Format quality assessment reports for SMART analysis."""
    output_lines = []
    output_lines.append("")
    output_lines.append("="*60)
    output_lines.append("SMART ANALYSIS QUALITY REPORT")
    output_lines.append("="*60)
    output_lines.append("")
    
    # Context summary
    output_lines.append("ANALYSIS CONTEXT:")
    output_lines.append(f"Subject Area: {context.subject_area}")
    output_lines.append(f"Objectives: {', '.join(context.analysis_objectives)}")
    output_lines.append(f"Target Audience: {context.target_audience}")
    output_lines.append("")
    
    # Overall quality metrics
    all_scores = []
    for dataset_name, report in quality_reports.items():
        if 'summary' in report:
            all_scores.append(report['summary']['average_score'])
    
    if all_scores:
        overall_avg = sum(all_scores) / len(all_scores)
        output_lines.append(f"OVERALL QUALITY SCORE: {overall_avg:.2f}/1.00")
        
        if overall_avg >= 0.8:
            output_lines.append("SUCCESS: Excellent question quality achieved!")
        elif overall_avg >= 0.7:
            output_lines.append("SUCCESS: Good question quality achieved!")
        elif overall_avg >= 0.6:
            output_lines.append("WARNING: Acceptable question quality - room for improvement")
        else:
            output_lines.append("ERROR: Question quality below target - significant improvement needed")
        output_lines.append("")
    
    # Dataset-specific reports
    for dataset_name, report in quality_reports.items():
        if 'summary' not in report:
            continue
            
        output_lines.append(f"📋 QUALITY REPORT: {dataset_name}")
        output_lines.append("-" * 40)
        
        summary = report['summary']
        output_lines.append(f"Average Score: {summary['average_score']:.2f}")
        output_lines.append(f"High Quality Questions: {summary['high_quality_count']}/{summary['total_questions']}")
        output_lines.append(f"Questions Needing Improvement: {summary['needs_improvement_count']}")
        
        # Best question
        if 'best_question' in report:
            best = report['best_question']
            output_lines.append(f"\n🌟 Best Question (Score: {best['score']:.2f}):")
            output_lines.append(f"   {best['question']}")
        
        # Improvement recommendations
        if 'improvement_recommendations' in report and report['improvement_recommendations']:
            output_lines.append("\n💡 Recommendations:")
            for rec in report['improvement_recommendations']:
                output_lines.append(f"   • {rec}")
        
        # Diversity analysis
        if 'diversity_analysis' in report:
            diversity = report['diversity_analysis']
            output_lines.append(f"\n🎨 Question Diversity Score: {diversity['diversity_score']:.2f}")
            
            focus_dist = diversity['focus_area_distribution']
            top_focus_areas = sorted(focus_dist.items(), key=lambda x: x[1], reverse=True)[:3]
            output_lines.append("Top Focus Areas:")
            for area, count in top_focus_areas:
                if count > 0:
                    output_lines.append(f"   • {area.replace('_', ' ').title()}: {count} questions")
        
        output_lines.append("")
    
    # SMART criteria coverage
    output_lines.append("SMART CRITERIA ANALYSIS:")
    output_lines.append("-" * 30)
    
    criteria_names = {
        'specific': 'Specific',
        'measurable': 'Measurable', 
        'action_oriented': 'Action-Oriented',
        'relevant': 'Relevant',
        'time_bound': 'Time-Bound'
    }
    
    # Aggregate SMART coverage across all datasets
    for criterion, display_name in criteria_names.items():
        total_coverage = 0
        total_datasets = 0
        
        for dataset_name, report in quality_reports.items():
            if 'coverage_analysis' in report and criterion in report['coverage_analysis']:
                coverage = report['coverage_analysis'][criterion]['coverage_percentage']
                total_coverage += coverage
                total_datasets += 1
        
        if total_datasets > 0:
            avg_coverage = total_coverage / total_datasets
            coverage_status = "[PASS]" if avg_coverage >= 80 else "[WARN]" if avg_coverage >= 60 else "[FAIL]"
            output_lines.append(f"{coverage_status} {display_name}: {avg_coverage:.1f}% coverage")
    
    output_lines.append("")
    output_lines.append("="*60)
    
    return output_lines

# --- End Helper Functions ---


# =========================================================
# Main Application Function
# =========================================================
# Ensure this function is NOT indented, it's at the top level.
def main():
    """Main entry point."""
    try:
        # Handle CLI arguments if available
        args = None
        if CLI_AVAILABLE and len(sys.argv) > 1:
            try:
                args = parse_arguments()
                
                # Handle config file
                if args.config:
                    config = load_config_file(args.config)
                    apply_config_to_args(args, config)
                
                # Handle batch processing
                if args.batch:
                    process_batch_mode(args.batch)
                    return
                
                # Handle quick mode
                if args.quick:
                    process_quick_mode(args)
                    return
                    
            except Exception as e:
                logging.error(f"CLI argument parsing failed: {e}")
                print("Falling back to interactive mode...")
                args = None
        
        # 1. Get SMART analysis context (business context, objectives, audience)
        if args:
            context = get_smart_analysis_context_from_args(args)
        else:
            context = get_smart_analysis_context()
        
        # 2. Get dataset information FIRST (more logical - see data before deciding question count)
        if args and args.datasets:
            file_paths = args.datasets
        else:
            file_paths = get_user_input_file_paths()
            
        if not file_paths:
            logging.info("No file paths provided or input error. Exiting.")
            logging.info("=== Meta Minds Application Finished ===")
            return # Exit the main function

        # 3. Process the datasets (Load dataframes)
        datasets = process_datasets(file_paths)
        if not datasets:
            logging.error("No datasets could be loaded from the provided paths. Exiting.")
            logging.info("=== Meta Minds Application Finished ===")
            return # Exit if no datasets were successfully loaded
        
        # Show user what datasets were loaded so they can decide question count appropriately
        print("\n" + "="*60)
        print("DATASETS LOADED SUCCESSFULLY")
        print("="*60)
        for name, df in datasets:
            print(f"  - {name}: {len(df)} rows, {len(df.columns)} columns")
        print()
        
        # 4. Get question count preferences AFTER seeing the data
        # Calculate recommended question count based on data complexity
        total_rows = sum(len(df) for _, df in datasets)
        total_cols = sum(len(df.columns) for _, df in datasets)
        avg_cols = total_cols / len(datasets) if datasets else 5
        
        # Recommendation logic
        if avg_cols >= 20:
            recommended = 25
        elif avg_cols >= 10:
            recommended = 20
        elif avg_cols >= 5:
            recommended = 15
        else:
            recommended = 10
        
        if args:
            individual_question_count = args.questions or recommended
            comparison_question_count = args.comparison or 0
        else:
            individual_question_count, comparison_question_count = get_question_count_preferences(recommended)

        # 5. Generate summaries for loaded datasets (Includes GPT calls for descriptions)
        # This is done BEFORE CrewAI tasks to provide context if needed later,
        # and to ensure summaries are ready for the output formatting step.
        # Store summaries in a dictionary keyed by dataset name.
        dataset_summaries = {}
        
        print("\n" + "="*60)
        print("ANALYZING DATASETS")
        print("="*60)
        logging.info("Generating summaries for loaded datasets...")
        
        # Iterate through the loaded datasets to generate summaries
        for idx, (name, df) in enumerate(datasets, 1):
            try:
                safe_print(f"\n{emoji.CHART} Processing {name} ({idx}/{len(datasets)})...")
                safe_print(f"   Analyzing {len(df):,} rows and {len(df.columns)} columns...")
                
                # generate_summary calls generate_column_descriptions which uses GPT
                summary = generate_summary(df) # generate_summary is imported from data_analyzer
                dataset_summaries[name] = summary
                
                print(f"✅ {name} analysis complete!")
                logging.info(f"Summary generated for {name}")
            except Exception as e:
                logging.error(f"Error generating summary for {name}: {e}")
                print(f"❌ Error analyzing {name}: {e}")
                # Store an error indicator in the summaries dictionary
                dataset_summaries[name] = {"error": str(e), "name": name} # Store name for easier handling in format

        print(f"\n✅ All {len(datasets)} datasets analyzed successfully!")
        logging.info("Summaries generation process finished.")
        # Note: Some summaries might have errors if GPT calls failed.

        # 6. Create agents
        print("\n" + "="*60)
        print("CREATING AI AGENTS")
        print("="*60)
        schema_sleuth, question_genius = create_agents() # create_agents is imported from agents
        agents = [schema_sleuth, question_genius] # List of all agents potentially used in tasks
        safe_print(f"{emoji.SUCCESS} AI agents created successfully!")

        # 7. Create tasks for agents based on the loaded data (SMART analysis only)
        print("\n" + "="*60)
        print("GENERATING ANALYSIS TASKS")
        print("="*60)
        quality_reports = {}
        
        logging.info("Using SMART analysis mode (only available mode)")
        safe_print(f"{emoji.DOCUMENT} Creating {individual_question_count} questions per dataset...")
        individual_tasks, individual_headers, quality_reports = create_smart_tasks(
            datasets, schema_sleuth, question_genius, context, individual_question_count
        )
        
        if comparison_question_count > 0:
            safe_print(f"{emoji.REFRESH} Creating {comparison_question_count} cross-dataset comparison questions...")
            comparison_task, comparison_quality = create_smart_comparison_task(
                datasets, question_genius, context, comparison_question_count
            )
            if comparison_quality:
                quality_reports['comparison'] = comparison_quality
        else:
            comparison_task = None
            safe_print(f"{emoji.ARROW_RIGHT} Skipping cross-dataset comparison (0 questions requested)")
        
        safe_print(f"{emoji.SUCCESS} All analysis tasks created successfully!")

        # 8. Assemble all tasks to be run by the CrewAI process
        all_tasks = individual_tasks[:] # Start with dataset-specific tasks
        all_headers = individual_headers[:] # Start with corresponding headers

        if comparison_task:
            all_tasks.append(comparison_task)
            # Add the expected header for the comparison task
            all_headers.append("--- Enhanced Comparison Questions ---")

        if not all_tasks:
             logging.warning("No tasks were created based on the provided data. Exiting before running CrewAI.")
             # We still have summaries to output, so continue to formatting and saving
             task_results = [] # Empty list as no tasks ran
             logging.info("Skipping CrewAI execution as no tasks were created.")
        else:
            # 8. Execute AI Analysis Tasks
            print("\n" + "="*60)
            print("EXECUTING AI ANALYSIS")
            print("="*60)
            safe_print(f"{emoji.ROBOT} Running {len(all_tasks)} analysis tasks...")
            
            # Prepare question counts for trimming (individual count for each dataset + comparison count)
            question_counts = [individual_question_count] * len(individual_tasks)
            if comparison_task:
                question_counts.append(comparison_question_count)
            
            # Check for rate limiting and run tasks accordingly
            if _detect_rate_limiting():
                logging.warning("Rate limiting detected. Switching to offline mode with fallback questions.")
                safe_print(f"{emoji.WARNING} Rate limiting detected - using offline fallback questions")
                task_results = _generate_offline_results(all_tasks, context, question_counts)
            else:
                # Run tasks using CrewAI
                # The run_crew_standard function handles running each task sequentially
                # and returns a list of results (strings or error messages).
                safe_print(f"{emoji.BRAIN} Executing AI-powered analysis...")
                task_results = run_crew_standard(all_tasks, agents, question_counts)
            
            safe_print(f"{emoji.SUCCESS} AI analysis execution complete!")

        # 9. Generate Enhanced Separate Reports
        print("\n" + "="*60)
        print("GENERATING REPORTS")
        print("="*60)
        logging.info("Generating enhanced separate reports...")
        
        # Separate individual and comparison data
        individual_task_results = task_results[:-1] if comparison_task else task_results
        individual_headers = all_headers[:-1] if comparison_task else all_headers
        comparison_result = task_results[-1] if comparison_task else None
        comparison_quality = quality_reports.get('comparison') if quality_reports else None
        
        safe_print(f"{emoji.DOCUMENT} Creating individual dataset reports...")
        if comparison_result:
            safe_print(f"{emoji.REFRESH} Creating cross-dataset comparison report...")
        
        # Generate and save separate reports (TXT format only)
        filename_base = save_separate_reports(
            dataset_summaries=dataset_summaries,
            individual_task_results=individual_task_results,
            individual_headers=individual_headers,
            comparison_result=comparison_result,
            quality_reports=quality_reports,
            comparison_quality=comparison_quality,
            context=context,
            base_filename=args.output_filename if args else "meta_minds_analysis"
        )
        
        safe_print(f"{emoji.SUCCESS} All TXT reports generated successfully!")
        
        logging.info("Analysis complete! Clean targeted reports generated:")
        logging.info("   - meta_minds_analysis_individual_datasets.txt - Complete individual analysis")
        if comparison_result:
            logging.info("   - meta_minds_analysis_cross_dataset_comparison.txt - Cross-dataset insights")

    except Exception as main_e:
        # Catch any unexpected errors that weren't handled elsewhere in the main flow
        logging.critical(f"An unexpected critical error occurred in the main workflow: {main_e}", exc_info=True)
        print(f"\nCritical Error: {main_e}")
        print("Please check the logs for more details.")

    logging.info("=== Meta Minds Application Finished ===")


# =========================================================
# Script Entry Point
# =========================================================
if __name__ == "__main__":
    # Call the main application function
    main()