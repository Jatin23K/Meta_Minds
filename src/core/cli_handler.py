# =========================================================
# cli_handler.py: Command-Line Interface Support
# =========================================================
# This module adds CLI arguments for automation and batch processing

import argparse
import json
import os
import logging
from typing import Dict, Any, Optional

# Import constants from data_loader
try:
    from data_loader import MAX_FILE_SIZE_MB, MAX_ROWS_DEFAULT
except ImportError:
    # Fallback constants if data_loader not available
    MAX_FILE_SIZE_MB = 50
    MAX_ROWS_DEFAULT = 100000
try:
    from context_collector import DatasetContext
except ImportError:
    from smart_question_generator import DatasetContext

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for META_MINDS.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='META_MINDS - AI-Powered SMART Data Analysis Question Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python main.py
  
  # Quick mode with config file
  python main.py --config airline_analysis.json
  
  # Automated mode with all parameters
  python main.py --template 1 --datasets data1.csv data2.csv --questions 20
  
  # Batch processing
  python main.py --batch configs/
        """
    )
    
    # Mode selection
    parser.add_argument('--quick', action='store_true',
                       help='Quick mode: skip all prompts, use defaults')
    
    parser.add_argument('--config', type=str,
                       help='Path to JSON config file with all settings')
    
    parser.add_argument('--batch', type=str,
                       help='Path to folder containing multiple config files for batch processing')
    
    # Context parameters
    parser.add_argument('--template', type=int, choices=range(1, 18),
                       help='Predefined template number (1-17)')
    
    parser.add_argument('--subject', type=str,
                       help='Subject area for analysis')
    
    parser.add_argument('--objectives', type=str, nargs='+',
                       help='Analysis objectives (space-separated)')
    
    parser.add_argument('--audience', type=str,
                       help='Target audience')
    
    # Dataset parameters
    parser.add_argument('--datasets', type=str, nargs='+',
                       help='Paths to dataset files (space-separated)')
    
    parser.add_argument('--dataset-folder', type=str,
                       help='Folder containing all dataset files')
    
    # Question parameters
    parser.add_argument('--questions', type=int,
                       help='Number of questions per dataset')
    
    parser.add_argument('--comparison', type=int,
                       help='Number of cross-dataset comparison questions')
    
    # Output parameters
    parser.add_argument('--output', type=str,
                       help='Output folder path')
    
    parser.add_argument('--export-excel', action='store_true',
                       help='Also export to Excel format')
    
    parser.add_argument('--export-json', action='store_true',
                       help='Also export to JSON format')
    
    parser.add_argument('--export-html', action='store_true',
                       help='Also export to HTML dashboard')
    
    parser.add_argument('--export-all', action='store_true',
                       help='Export to all formats (TXT, Excel, JSON, HTML)')
    
    # Advanced options
    parser.add_argument('--max-rows', type=int,
                       help='Maximum rows to load per dataset (default: 1,000,000)')
    
    parser.add_argument('--skip-duplicates', action='store_true',
                       help='Automatically remove duplicate questions')
    
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed progress messages')
    
    return parser.parse_args()

def load_config_file(config_path: str) -> Optional[Dict[str, Any]]:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to JSON config file
    
    Returns:
        Dict with configuration or None if error
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logging.info(f"Loaded configuration from: {config_path}")
        return config
        
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config file: {e}")
        return None
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return None

def apply_config_to_args(args: argparse.Namespace, config: Dict[str, Any]):
    """Apply settings from a config dictionary to the argparse Namespace."""
    for key, value in config.items():
        if hasattr(args, key) and value is not None:
            # Special handling for lists/tuples if needed, otherwise direct assignment
            if isinstance(getattr(args, key), list) and isinstance(value, str):
                setattr(args, key, value.split(',')) # Assume comma-separated string for lists
            else:
                setattr(args, key, value)
    logging.info("Configuration applied to arguments.")

def create_context_from_config(config: Dict[str, Any]) -> Optional[DatasetContext]:
    """Create DatasetContext from configuration dict.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        DatasetContext object or None
    """
    try:
        context = DatasetContext(
            subject_area=config.get('subject_area', 'general'),
            analysis_objectives=config.get('analysis_objectives', ['exploratory analysis']),
            target_audience=config.get('target_audience', 'data analysts'),
            dataset_background=config.get('dataset_background', ''),
            business_context=config.get('business_context', ''),
            time_sensitivity=config.get('time_sensitivity', 'medium')
        )
        
        return context
        
    except Exception as e:
        logging.error(f"Error creating context from config: {e}")
        return None

def save_config_template(output_path: str = "meta_minds_config_template.json"):
    """Save a template configuration file for users to fill out.
    
    Args:
        output_path: Where to save the template
    """
    template = {
        "subject_area": "financial analysis",
        "analysis_objectives": ["trend analysis", "risk assessment", "performance evaluation"],
        "target_audience": "executives",
        "dataset_background": "Quarterly financial data from 2013-2023",
        "business_context": "Investment decision support and portfolio management",
        "time_sensitivity": "high",
        "datasets": [
            "path/to/dataset1.csv",
            "path/to/dataset2.csv"
        ],
        "questions_per_dataset": 20,
        "comparison_questions": 15,
        "output_folder": "Output",
        "export_formats": ["txt", "excel", "json", "html"],
        "max_rows_per_dataset": 1000000,
        "skip_duplicate_detection": false
    }
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        
        print(f"✅ Config template saved to: {output_path}")
        logging.info(f"Saved config template to: {output_path}")
        
    except Exception as e:
        logging.error(f"Error saving config template: {e}")

