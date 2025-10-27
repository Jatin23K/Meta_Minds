import pandas as pd
import os
import logging

# Configuration constants for safety limits
MAX_FILE_SIZE_MB = 500  # Maximum file size in MB
MAX_ROWS_DEFAULT = 1000000  # Default maximum rows to load (1 million)
LARGE_FILE_WARNING_MB = 50  # Warn user if file is larger than this

def check_file_safety(file_path: str) -> tuple[bool, str]:
    """Check if file is safe to load (size and path validation).
    
    Returns:
        tuple: (is_safe: bool, message: str)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    # Check if it's a file (not directory)
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"
    
    # Check file size
    try:
        file_size_bytes = os.path.getsize(file_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {MAX_FILE_SIZE_MB}MB)"
        
        if file_size_mb > LARGE_FILE_WARNING_MB:
            return True, f"WARNING: Large file detected ({file_size_mb:.1f}MB). Loading may take time."
        
        return True, f"File size OK: {file_size_mb:.2f}MB"
        
    except Exception as e:
        return False, f"Cannot check file size: {e}"

def read_file(file_path, max_rows: int = None, interactive: bool = True):
    """Loads data from a CSV, Excel, or JSON file with safety checks.

    Args:
        file_path (str): The path to the data file.
        max_rows (int, optional): Maximum number of rows to load. None = load all.
        interactive (bool): Whether to prompt user for large files. Default True.

    Returns:
        pandas.DataFrame: The loaded DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file type is unsupported or too large.
        Exception: For other errors during file reading (e.g., corrupted file).
    """
    try:
        # SAFETY CHECK 1: Validate file path and size
        is_safe, safety_msg = check_file_safety(file_path)
        
        if not is_safe:
            logging.error(safety_msg)
            raise ValueError(safety_msg)
        
        # If warning message (large file), log it
        if "WARNING" in safety_msg:
            logging.warning(safety_msg)
            print(f"\n⚠️  {safety_msg}")
            
            if interactive:
                proceed = input("    Continue loading? (y/n): ").strip().lower()
                if proceed not in ['y', 'yes']:
                    logging.info(f"User cancelled loading large file: {file_path}")
                    raise ValueError("User cancelled: File too large")
        else:
            logging.info(safety_msg)
        
        ext = os.path.splitext(file_path)[1].lower()
        logging.info(f"Attempting to read file: {file_path} with extension: {ext}")
        
        # Determine row limit
        if max_rows is None:
            max_rows = MAX_ROWS_DEFAULT
        
        if ext == ".csv":
            # Try multiple encodings
            encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, nrows=max_rows)
                    logging.info(f"Successfully read CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                # If all encodings fail, try with error handling
                df = pd.read_csv(file_path, encoding='utf-8', errors='ignore', nrows=max_rows)
                logging.warning(f"Used UTF-8 with error ignore for file: {file_path}")
        elif ext == ".xlsx":
            df = pd.read_excel(file_path, nrows=max_rows)
        elif ext == ".json":
            df = pd.read_json(file_path, nrows=max_rows)
        else:
            logging.error(f"Unsupported file type: {ext} for file: {file_path}")
            raise ValueError(f"Unsupported file type: {ext}")

        logging.info(f"Successfully read file: {file_path}. Shape: {df.shape}")
        
        # SAFETY CHECK 2: Warn if we hit the row limit
        if len(df) == max_rows:
            logging.warning(f"File may have more rows. Loaded limit: {max_rows:,} rows")
            print(f"\n⚠️  Loaded {max_rows:,} rows (limit reached). Full file may be larger.")
        
        if df.empty:
            logging.warning(f"File {file_path} is empty.")
            raise ValueError(f"File {file_path} is empty - no data to analyze")
        
        return df

    except FileNotFoundError:
        logging.error(f"Error: File not found at path: {file_path}")
        raise # Re-raise the exception after logging
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading file {file_path}: {e}")
        raise # Re-raise the exception after logging