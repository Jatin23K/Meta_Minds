"""
Automated script to run META_MINDS analysis on airline datasets without interactive prompts.
"""
import sys
import os

# Add src/core to path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'core'))

from context_collector import ContextCollector, DatasetContext
import data_loader
from agents import create_agents
from tasks import create_smart_tasks, create_smart_comparison_task
from output_handler import save_separate_reports
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Run META_MINDS analysis with predefined settings."""
    
    print("="*60)
    print("META MINDS - AIRLINE FINANCIAL ANALYSIS (2013-2023)")
    print("="*60)
    print()
    
    # 1. Load context from input folder
    print("Loading business context from input folder...")
    context_collector = ContextCollector()
    context = context_collector.read_input_folder_context()
    
    if not context:
        print("ERROR: Could not load context from input folder!")
        print("Please ensure input folder contains:")
        print("  - Business_Background.txt")
        print("  - Dataset_Background.txt")
        print("  - Message.txt")
        return
    
    print(f"SUCCESS: Loaded context for {context.subject_area} analysis")
    print(f"Target Audience: {context.target_audience}")
    print()
    
    # 2. Set question counts (predefined)
    individual_question_count = 20  # 20 questions per dataset
    comparison_question_count = 15  # 15 comparison questions
    
    print(f"Configuration:")
    print(f"  - Individual dataset questions: {individual_question_count}")
    print(f"  - Cross-dataset comparison questions: {comparison_question_count}")
    print()
    
    # 3. Get dataset file paths
    dataset_folder = os.path.join(os.path.dirname(__file__), 'dataset')
    dataset_files = [
        os.path.join(dataset_folder, 'Assets.csv'),
        os.path.join(dataset_folder, 'Liabilities.csv'),
        os.path.join(dataset_folder, 'Top_10_Ratio.csv')
    ]
    
    print("Loading airline datasets...")
    for f in dataset_files:
        print(f"  - {os.path.basename(f)}")
    print()
    
    # 4. Load datasets
    datasets = {}
    
    for file_path in dataset_files:
        if not os.path.exists(file_path):
            print(f"ERROR: Dataset not found: {file_path}")
            continue
            
        dataset_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            df = data_loader.read_file(file_path)
            if df is not None and not df.empty:
                datasets[dataset_name] = df
                print(f"SUCCESS: Loaded {dataset_name} - {len(df)} records, {len(df.columns)} columns")
        except Exception as e:
            print(f"ERROR loading {dataset_name}: {e}")
    
    if not datasets:
        print("ERROR: No datasets loaded successfully!")
        return
    
    print()
    print(f"Total datasets loaded: {len(datasets)}")
    print()
    
    # 5. Create agents
    print("Creating AI agents...")
    schema_sleuth, question_genius = create_agents()
    agents = [schema_sleuth, question_genius]
    print("SUCCESS: Agents created")
    print()
    
    # 6. Create tasks (SMART analysis)
    print("Generating SMART analysis questions...")
    quality_reports = {}
    
    # Convert datasets dict to list of tuples for create_smart_tasks
    datasets_list = [(name, df) for name, df in datasets.items()]
    
    individual_tasks, individual_headers, quality_reports = create_smart_tasks(
        datasets_list, schema_sleuth, question_genius, context, individual_question_count
    )
    
    comparison_task, comparison_quality = create_smart_comparison_task(
        datasets_list, question_genius, context, comparison_question_count
    )
    
    if comparison_quality:
        quality_reports['comparison'] = comparison_quality
    
    print(f"SUCCESS: Generated questions for {len(datasets)} datasets")
    if comparison_task:
        print("SUCCESS: Generated cross-dataset comparison questions")
    print()
    
    # 7. Combine tasks
    all_tasks = individual_tasks + ([comparison_task] if comparison_task else [])
    all_headers = individual_headers + (["Cross-Dataset Analysis"] if comparison_task else [])
    
    # 8. Execute tasks (using offline mode for consistency)
    print("="*60)
    print("EXECUTING ANALYSIS (OFFLINE MODE)")
    print("="*60)
    print()
    
    from main import _generate_offline_results
    task_results = _generate_offline_results(all_tasks, context)
    
    # 9. Generate reports
    print()
    print("="*60)
    print("GENERATING REPORTS")
    print("="*60)
    print()
    
    individual_task_results = task_results[:-1] if comparison_task else task_results
    individual_headers_final = all_headers[:-1] if comparison_task else all_headers
    comparison_result = task_results[-1] if comparison_task else None
    comparison_quality_final = quality_reports.get('comparison') if quality_reports else None
    
    # Save reports
    output_folder = os.path.join(os.path.dirname(__file__), 'Output')
    os.makedirs(output_folder, exist_ok=True)
    
    # Create dataset summaries
    dataset_summaries = {}
    for name, df in datasets.items():
        dataset_summaries[name] = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict()
        }
    
    save_separate_reports(
        dataset_summaries=dataset_summaries,
        individual_task_results=individual_task_results,
        individual_headers=individual_headers_final,
        comparison_result=comparison_result,
        quality_reports=quality_reports,
        comparison_quality=comparison_quality_final,
        context=context,
        base_filename="airline_financial_analysis"
    )
    
    print()
    print("="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print()
    print("Reports generated in Output folder:")
    print(f"  - airline_financial_analysis_individual_datasets.txt")
    if comparison_result:
        print(f"  - airline_financial_analysis_cross_dataset_comparison.txt")
    print()
    
    # Display quality summary
    if quality_reports:
        print("="*60)
        print("QUALITY SUMMARY")
        print("="*60)
        
        all_scores = []
        for dataset_name, report in quality_reports.items():
            if 'summary' in report:
                score = report['summary']['average_score']
                all_scores.append(score)
                print(f"{dataset_name}: {score:.2f}/1.00")
        
        if all_scores:
            overall_avg = sum(all_scores) / len(all_scores)
            print(f"\nOverall Quality Score: {overall_avg:.2f}/1.00")
            
            if overall_avg >= 0.8:
                print("STATUS: Excellent question quality!")
            elif overall_avg >= 0.7:
                print("STATUS: Good question quality!")
            else:
                print("STATUS: Acceptable quality")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
    except Exception as e:
        logging.critical(f"Critical error: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        print("Check logs for details.")

