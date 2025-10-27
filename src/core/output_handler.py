import logging
import os # Good practice to import os if dealing with file paths
from datetime import datetime
from typing import Dict, List, Any
from export_utils import export_to_excel, export_to_json, export_to_html
import re

def save_output(filename: str, output_lines: list[str]):
    """Saves the output lines to a file.

    Args:
        filename (str): The name of the file to save the output to.
        output_lines (list): A list of strings, where each string is a line to write to the file.
    """
    if not output_lines:
        logging.warning(f"No output lines to save to '{filename}'. Skipping file creation.")
        return

    try:
        # Ensure the directory exists if filename includes a path
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logging.info(f"Created output directory: {output_dir}")
            except PermissionError as e:
                logging.warning(f"Permission denied creating directory {output_dir}: {e}. Trying alternate location.")
                # Try user's Documents folder
                import pathlib
                docs_folder = pathlib.Path.home() / "Documents" / "META_MINDS_Output"
                docs_folder.mkdir(parents=True, exist_ok=True)
                filename = str(docs_folder / os.path.basename(filename))
                logging.info(f"Using alternate location: {filename}")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print(f"\n✅ Report saved successfully!")
        print(f"   Location: {os.path.abspath(filename)}")
        logging.info(f"Meta Minds output successfully saved to '{filename}'")
    except PermissionError as e:
        # Try one more time in Documents folder
        try:
            import pathlib
            docs_folder = pathlib.Path.home() / "Documents" / "META_MINDS_Output"
            docs_folder.mkdir(parents=True, exist_ok=True)
            alt_filename = str(docs_folder / os.path.basename(filename))
            with open(alt_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines))
            print(f"\n✅ Report saved to alternate location!")
            print(f"   Location: {alt_filename}")
            logging.info(f"Saved to alternate location: {alt_filename}")
        except Exception as e2:
            logging.error(f"CRITICAL: Could not save file anywhere. Permission errors: {e}, {e2}")
            print(f"\n❌ ERROR: Could not save report due to permission issues.")
            print(f"   Please check folder permissions or run as administrator.")
    except IOError as e:
        logging.error(f"IOError occurred while saving output to '{filename}': {e}")
        print(f"\n❌ ERROR: Could not save report: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while saving output to '{filename}': {e}")
        print(f"\n❌ ERROR: Unexpected error: {e}")

def _clean_filename_component(component: str) -> str:
    """Clean a string component for use in filename."""
    if not component:
        return "Unknown"
    
    # Remove/replace problematic characters for filenames
    # Convert to title case and remove spaces, special chars
    cleaned = re.sub(r'[^\w\s-]', '', component)  # Remove special chars except spaces and hyphens
    cleaned = re.sub(r'\s+', '', cleaned)         # Remove all spaces
    cleaned = cleaned.title()                     # Convert to TitleCase
    
    # Limit length to avoid very long filenames
    if len(cleaned) > 20:
        cleaned = cleaned[:20]
    
    return cleaned if cleaned else "Unknown"

def _limit_questions(formatted_questions: list, max_count: int = None) -> list:
    """Limit the number of questions to exactly max_count if specified.
    
    Args:
        formatted_questions: List of formatted question strings
        max_count: Maximum number of questions to keep (None = keep all)
    
    Returns:
        Limited list of questions
    """
    if max_count is None or max_count <= 0:
        return formatted_questions
    
    # Only keep the first max_count questions
    limited = formatted_questions[:max_count]
    
    if len(formatted_questions) > max_count:
        logging.warning(f"Trimmed {len(formatted_questions) - max_count} excess questions (kept {max_count})")
    
    return limited

def _adjust_quality_report_for_actual_count(quality_report: dict, actual_question_count: int) -> dict:
    """Adjust quality report metrics to reflect the actual number of questions displayed.
    
    Args:
        quality_report: Original quality report
        actual_question_count: Actual number of questions displayed
    
    Returns:
        Adjusted quality report
    """
    if not quality_report or 'summary' not in quality_report:
        return quality_report
    
    summary = quality_report['summary']
    original_total = summary.get('total_questions', actual_question_count)
    
    # If counts match, no adjustment needed
    if original_total == actual_question_count:
        return quality_report
    
    # Calculate ratio for adjustment
    if original_total > 0:
        ratio = actual_question_count / original_total
        
        # Adjust counts proportionally
        adjusted_summary = summary.copy()
        adjusted_summary['total_questions'] = actual_question_count
        adjusted_summary['high_quality_count'] = int(summary.get('high_quality_count', 0) * ratio)
        adjusted_summary['needs_improvement_count'] = int(summary.get('needs_improvement_count', 0) * ratio)
        
        # Create adjusted report
        adjusted_report = quality_report.copy()
        adjusted_report['summary'] = adjusted_summary
        
        return adjusted_report
    
    return quality_report

def generate_individual_datasets_report(dataset_summaries: Dict[str, Any], 
                                       individual_task_results: List[str], 
                                       individual_headers: List[str],
                                       quality_reports: Dict[str, Any] = None) -> List[str]:
    """Generate clean individual datasets report.
    
    Format:
    - Dataset 1 Summary
    - Dataset 1 Questions  
    - Dataset 2 Summary
    - Dataset 2 Questions
    - ... and so on
    """
    logging.info("Generating Individual Datasets Report...")
    output_lines = []
    
    # Header
    output_lines.append("╔" + "═" * 78 + "╗")
    output_lines.append("║" + " " * 20 + "📊 META MINDS INDIVIDUAL DATASETS REPORT" + " " * 16 + "║")
    output_lines.append("╚" + "═" * 78 + "╝")
    output_lines.append("")
    output_lines.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"📊 Total Datasets Analyzed: {len(dataset_summaries)}")
    output_lines.append(f"📋 Questions Generated: {len(individual_task_results)} datasets analyzed")
    output_lines.append("")
    
    # Overall Summary Section
    output_lines.append("📋 OVERALL SUMMARY")
    output_lines.append("=" * 80)
    
    # Calculate total rows and columns across all datasets
    total_rows = 0
    total_columns = 0
    valid_datasets = 0
    
    for summary in dataset_summaries.values():
        if "error" not in summary:
            rows = summary.get('rows', 0)
            cols = summary.get('columns', 0)
            if isinstance(rows, (int, float)) and isinstance(cols, (int, float)):
                total_rows += rows
                total_columns += cols
                valid_datasets += 1
    
    output_lines.append(f"📊 Total Records Across All Datasets: {total_rows:,}")
    output_lines.append(f"📊 Total Unique Columns: {total_columns}")
    output_lines.append(f"📊 Successfully Processed: {valid_datasets}/{len(dataset_summaries)} datasets")
    
    # Quality summary if available (ONLY for individual datasets, excluding comparison questions)
    if quality_reports:
        total_score = 0
        high_quality_count = 0
        total_questions = 0
        individual_datasets = 0
        
        for dataset_name, report in quality_reports.items():
            # Only count individual dataset reports, skip comparison reports
            if 'summary' in report and dataset_name != 'comparison':
                total_score += report['summary'].get('average_score', 0)
                high_quality_count += report['summary'].get('high_quality_count', 0)
                total_questions += report['summary'].get('total_questions', 0)
                individual_datasets += 1
        
        if individual_datasets > 0:
            avg_quality = total_score / individual_datasets
            output_lines.append(f"📊 Overall Quality Score: {avg_quality:.2f}/1.00")
            output_lines.append(f"📊 High Quality Questions: {high_quality_count}/{total_questions}")
            
            if avg_quality >= 0.97:
                output_lines.append("✅ Overall Status: Excellent Analysis Quality")
            elif avg_quality >= 0.8:
                output_lines.append("⚠️ Overall Status: Good Analysis Quality")
            else:
                output_lines.append("❌ Overall Status: Analysis Quality Needs Improvement")
    
    output_lines.append("")
    output_lines.append("🎯 All individual dataset analyses complete!")
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Group summaries and questions by dataset
    dataset_data = {}
    for i, (header, result) in enumerate(zip(individual_headers, individual_task_results)):
        # Extract dataset name from header like "--- Enhanced Questions for Assets.csv" or "--- Questions for dataset1.csv ---"
        if "--- Enhanced Questions for " in header:
            dataset_name = header.replace("--- Enhanced Questions for ", "").replace(" ---", "").strip()
        elif "--- Questions for " in header:
            dataset_name = header.replace("--- Questions for ", "").replace(" ---", "").strip()
        else:
            # Fallback: try to extract filename from any format
            import re
            # Extract filename from the header using regex
            match = re.search(r'([^/\\]+\.csv)', header, re.IGNORECASE)
            dataset_name = match.group(1) if match else header.replace("---", "").replace("Questions for", "").replace("Enhanced", "").strip()
        
        # Debug: uncomment below for troubleshooting dataset name extraction
        # print(f"DEBUG: Header='{header}' -> Dataset='{dataset_name}'")
        dataset_data[dataset_name] = {
            'header': header,
            'questions': result,
            'summary': dataset_summaries.get(dataset_name, {})
        }
    
    # Generate report for each dataset
    for i, (dataset_name, data) in enumerate(dataset_data.items(), 1):
        # Dataset Header
        output_lines.append(f"📊 DATASET {i}: {dataset_name}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # Dataset Summary
        output_lines.append(f"📋 DATA SUMMARY:")
        output_lines.append("-" * 40)
        
        summary = data['summary']
        if "error" in summary:
            output_lines.append(f"❌ Error generating summary: {summary['error']}")
        else:
            output_lines.append(f"📊 Rows: {summary.get('rows', 'N/A')}")
            output_lines.append(f"📊 Columns: {summary.get('columns', 'N/A')}")
            output_lines.append("")
            output_lines.append("📊 Column Information:")
            
            column_info = summary.get('column_info')
            if column_info and isinstance(column_info, dict):
                for col, info in column_info.items():
                    if isinstance(info, dict):
                        output_lines.append(f"   • {col} ({info.get('dtype', 'N/A')}): {info.get('description', 'Description unavailable')}")
                    else:
                        output_lines.append(f"   • {col}: Info structure error")
            else:
                output_lines.append("   • Column info unavailable or malformed")
        
        output_lines.append("")
        
        # Dataset Questions
        output_lines.append(f"🔍 GENERATED QUESTIONS:")
        output_lines.append("-" * 40)
        
        questions_content = str(data['questions']).strip()
        
        # Check for errors
        if questions_content.lower().startswith("error executing task"):
            output_lines.append(f"❌ {questions_content}")
        else:
            # Clean and format questions
            cleaned_lines = [
                line for line in questions_content.split("\n")
                if data['header'].strip() not in line and line.strip() != ""
            ]
            
            formatted_questions = []
            for line in cleaned_lines:
                # Remove leading numbering and clean up
                parts = line.split('. ', 1)
                if len(parts) > 1 and parts[0].strip().isdigit():
                    formatted_questions.append(parts[1].strip())
                else:
                    line_stripped = line.strip()
                    if line_stripped and line_stripped[0].isdigit():
                        import re
                        match = re.match(r'^\d+\W*\s*', line_stripped)
                        if match:
                            formatted_questions.append(line_stripped[match.end():].strip())
                        else:
                            formatted_questions.append(line_stripped)
                    else:
                        formatted_questions.append(line_stripped)
            
            if formatted_questions:
                for idx, question in enumerate(formatted_questions, start=1):
                    if question.strip():
                        output_lines.append(f"   {idx:2d}. {question}")
            else:
                output_lines.append("   ❌ No questions generated or parsing failed")
        
        # Quality Report for this dataset (if available)
        if quality_reports and dataset_name in quality_reports:
            quality = quality_reports[dataset_name]
            if 'summary' in quality:
                # Adjust quality report to match actual question count
                actual_question_count = len(formatted_questions)
                adjusted_quality = _adjust_quality_report_for_actual_count(quality, actual_question_count)
                
                output_lines.append("")
                output_lines.append("📊 QUALITY ASSESSMENT:")
                output_lines.append("-" * 40)
                summary_data = adjusted_quality['summary']
                output_lines.append(f"   📈 Average Score: {summary_data['average_score']:.2f}/1.00")
                output_lines.append(f"   ✅ High Quality Questions: {summary_data['high_quality_count']}/{summary_data['total_questions']}")
                output_lines.append(f"   ⚠️  Needs Improvement: {summary_data['needs_improvement_count']}")
                
                # Quality status
                score = summary_data['average_score']
                if score >= 0.8:
                    output_lines.append("   🌟 Status: Excellent Quality")
                elif score >= 0.7:
                    output_lines.append("   ✅ Status: Good Quality")
                elif score >= 0.6:
                    output_lines.append("   ⚠️  Status: Acceptable Quality")
                else:
                    output_lines.append("   ❌ Status: Needs Improvement")
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("")
    
    # Overall Summary
    output_lines.append("📊 OVERALL SUMMARY")
    output_lines.append("=" * 80)
    output_lines.append(f"📊 Total Datasets: {len(dataset_summaries)}")
    output_lines.append(f"📋 Total Questions: Dynamic per user preference")
    
    if quality_reports:
        all_scores = []
        for dataset_name, report in quality_reports.items():
            if 'summary' in report:
                all_scores.append(report['summary']['average_score'])
        
        if all_scores:
            overall_avg = sum(all_scores) / len(all_scores)
            output_lines.append(f"📈 Overall Quality Score: {overall_avg:.2f}/1.00")
            
            if overall_avg >= 0.8:
                output_lines.append("🌟 Overall Status: Excellent Analysis Quality")
            elif overall_avg >= 0.7:
                output_lines.append("✅ Overall Status: Good Analysis Quality")
            elif overall_avg >= 0.6:
                output_lines.append("⚠️  Overall Status: Acceptable Analysis Quality")
            else:
                output_lines.append("❌ Overall Status: Analysis Quality Needs Improvement")
    
    output_lines.append("")
    output_lines.append("🎯 All individual dataset analyses complete!")
    output_lines.append("")
    
    logging.info("Individual Datasets Report generated successfully")
    return output_lines

def generate_cross_dataset_comparison_report(comparison_result: str, 
                                           dataset_summaries: Dict[str, Any],
                                           comparison_quality: Dict[str, Any] = None) -> List[str]:
    """Generate dedicated cross-dataset comparison report."""
    logging.info("Generating Cross-Dataset Comparison Report...")
    output_lines = []
    
    # Header
    output_lines.append("╔" + "═" * 78 + "╗")
    output_lines.append("║" + " " * 18 + "🔄 META MINDS CROSS-DATASET ANALYSIS REPORT" + " " * 17 + "║")
    output_lines.append("╚" + "═" * 78 + "╝")
    output_lines.append("")
    output_lines.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"🔄 Datasets Compared: {len(dataset_summaries)}")
    output_lines.append("🎯 Focus: Cross-dataset relationships and comparative insights")
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Dataset Overview
    output_lines.append("📊 DATASETS IN COMPARISON")
    output_lines.append("=" * 80)
    for i, (name, summary) in enumerate(dataset_summaries.items(), 1):
        rows = summary.get('rows', 'N/A') if 'error' not in summary else 'Error'
        cols = summary.get('columns', 'N/A') if 'error' not in summary else 'Error'
        output_lines.append(f"{i:2d}. {name}")
        output_lines.append(f"    📊 Dimensions: {rows} rows × {cols} columns")
    
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Cross-Dataset Questions
    output_lines.append("🔄 CROSS-DATASET COMPARISON QUESTIONS")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("🎯 These questions explore relationships, patterns, and insights")
    output_lines.append("   that emerge when analyzing your datasets together:")
    output_lines.append("")
    
    if comparison_result:
        comparison_content = str(comparison_result).strip()
        
        if comparison_content.lower().startswith("error executing task"):
            output_lines.append(f"❌ {comparison_content}")
        else:
            # Clean and format comparison questions
            cleaned_lines = []
            for line in comparison_content.split("\n"):
                line = line.strip()
                if (line and 
                    "--- Enhanced Comparison Questions ---" not in line and 
                    "--- Comparison Questions ---" not in line and
                    not line.startswith("1. --- Enhanced")):
                    cleaned_lines.append(line)
            
            formatted_questions = []
            for line in cleaned_lines:
                # Clean quotes and extract actual questions
                line = line.strip().strip('"').strip("'")
                
                # Skip if it's a header line or empty
                if not line or line.startswith("---"):
                    continue
                    
                # Remove leading numbering if present
                import re
                match = re.match(r'^\d+\.\s*["\']?', line)
                if match:
                    question = line[match.end():].strip().strip('"').strip("'")
                    if question:
                        formatted_questions.append(question)
                elif line and not line.isdigit():
                    formatted_questions.append(line)
            
            if formatted_questions:
                for idx, question in enumerate(formatted_questions, start=1):
                    if question.strip():
                        output_lines.append(f"{idx:2d}. {question}")
            else:
                output_lines.append("❌ No comparison questions generated or parsing failed")
    else:
        output_lines.append("❌ No comparison analysis available")
    
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Quality Assessment for Comparison
    if comparison_quality and 'summary' in comparison_quality:
        # Adjust quality report to match actual question count
        actual_comparison_count = len(formatted_questions) if 'formatted_questions' in locals() else 0
        adjusted_comparison_quality = _adjust_quality_report_for_actual_count(comparison_quality, actual_comparison_count)
        
        output_lines.append("📊 COMPARISON ANALYSIS QUALITY")
        output_lines.append("=" * 80)
        summary_data = adjusted_comparison_quality['summary']
        output_lines.append(f"📈 Quality Score: {summary_data['average_score']:.2f}/1.00")
        output_lines.append(f"✅ High Quality Questions: {summary_data['high_quality_count']}/{summary_data['total_questions']}")
        
        score = summary_data['average_score']
        if score >= 0.8:
            output_lines.append("🌟 Assessment: Excellent cross-dataset analysis quality")
        elif score >= 0.7:
            output_lines.append("✅ Assessment: Good cross-dataset analysis quality")
        elif score >= 0.6:
            output_lines.append("⚠️  Assessment: Acceptable cross-dataset analysis quality")
        else:
            output_lines.append("❌ Assessment: Cross-dataset analysis needs improvement")
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("")
    
    # Analysis Insights
    output_lines.append("💡 CROSS-DATASET ANALYSIS INSIGHTS")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("🔍 This analysis reveals:")
    output_lines.append("   • Hidden relationships between your datasets")
    output_lines.append("   • Patterns that emerge across multiple data sources")
    output_lines.append("   • Opportunities for data integration and correlation")
    output_lines.append("   • Comparative insights impossible with individual analysis")
    output_lines.append("")
    output_lines.append("🎯 Use these questions to:")
    output_lines.append("   • Discover unexpected connections in your data")
    output_lines.append("   • Validate assumptions across multiple sources")
    output_lines.append("   • Identify opportunities for business optimization")
    output_lines.append("   • Create comprehensive business intelligence")
    output_lines.append("")
    output_lines.append("Cross-dataset analysis complete!")
    output_lines.append("")
    
    logging.info("Cross-Dataset Comparison Report generated successfully")
    return output_lines

def save_separate_reports(dataset_summaries: Dict[str, Any], 
                         individual_task_results: List[str], 
                         individual_headers: List[str],
                         comparison_result: str = None,
                         quality_reports: Dict[str, Any] = None,
                         comparison_quality: Dict[str, Any] = None,
                         context: 'DatasetContext' = None,
                         base_filename: str = "meta_minds_analysis"):
    """Save both individual and comparison reports as separate TXT files with structured naming."""
    
    import os
    from datetime import datetime
    
    # Use existing Output directory 
    output_dir = "Output"
    
    # Get absolute path to ensure we're in the right location
    # If running from src/core, go up two levels to find Output
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_file_dir))
    output_dir_abs = os.path.join(project_root, "Output")
    
    # Try to use the absolute path first
    if os.path.exists(output_dir_abs):
        output_dir = output_dir_abs
    elif os.path.exists(output_dir):
        output_dir = os.path.abspath(output_dir)
    else:
        # Try to create it at project root
        try:
            os.makedirs(output_dir_abs, exist_ok=True)
            output_dir = output_dir_abs
            logging.info(f"Created output directory at: {output_dir}")
        except (PermissionError, OSError) as e:
            logging.warning(f"Could not create {output_dir_abs}: {e}")
            # Fallback to current directory
            output_dir = os.path.abspath(".")
            logging.info(f"Using current directory for output: {output_dir}")
    
    # Verify we can write to the directory
    if not os.access(output_dir, os.W_OK):
        logging.warning(f"Cannot write to {output_dir}. Trying user's Documents folder...")
        # Try user's Documents folder as last resort
        try:
            import pathlib
            docs_folder = pathlib.Path.home() / "Documents" / "META_MINDS_Output"
            docs_folder.mkdir(parents=True, exist_ok=True)
            output_dir = str(docs_folder)
            logging.info(f"Using Documents folder: {output_dir}")
        except Exception as e:
            logging.error(f"Could not create output directory anywhere: {e}")
            output_dir = os.path.abspath(".")
    
    # Generate structured filename based on context
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    if context:
        # Clean and format context components for filename
        analysis_focus = _clean_filename_component(context.subject_area)
        primary_objective = _clean_filename_component(", ".join(context.analysis_objectives) if context.analysis_objectives else "GeneralAnalysis")
        target_audience = _clean_filename_component(context.target_audience)
        
        filename_base = f"{analysis_focus}_{primary_objective}_{target_audience}_{timestamp}"
    else:
        filename_base = f"Analysis_{timestamp}"
    
    # Generate Individual Datasets Report
    individual_report = generate_individual_datasets_report(
        dataset_summaries, individual_task_results, individual_headers, quality_reports
    )
    
    # Save Individual Report with structured naming
    individual_filename = os.path.join(output_dir, f"Individual_{filename_base}.txt")
    save_output(individual_filename, individual_report)
    
    # Generate and Save Comparison Report (only if comparison data exists)
    if comparison_result and len(dataset_summaries) > 1:
        comparison_report = generate_cross_dataset_comparison_report(
            comparison_result, dataset_summaries, comparison_quality
        )
        comparison_filename = os.path.join(output_dir, f"Cross-Dataset_{filename_base}.txt")
        save_output(comparison_filename, comparison_report)
        
        logging.info(f"✅ Generated 2 separate reports:")
        logging.info(f"   📊 Individual Datasets: {individual_filename}")
        logging.info(f"   🔄 Cross-Dataset Analysis: {comparison_filename}")
    else:
        logging.info(f"✅ Generated 1 report:")
        logging.info(f"   📊 Individual Datasets: {individual_filename}")
        logging.info("   🔄 Cross-Dataset Analysis: Skipped (single dataset or no comparison data)")
    
    return filename_base