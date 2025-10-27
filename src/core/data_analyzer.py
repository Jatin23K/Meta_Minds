from config import client # Import the pre-initialized OpenAI client
import pandas as pd # Needed for DataFrame type hinting and operations
import logging

def _analyze_column_intelligently(column_name: str, series: pd.Series) -> str:
    """Intelligently analyze a column and generate a meaningful description.
    
    Args:
        column_name: Name of the column
        series: Pandas Series containing the column data
    
    Returns:
        Intelligent description of what the column represents
    """
    import re
    
    dtype = str(series.dtype)
    non_null_count = series.notna().sum()
    total_count = len(series)
    null_percentage = ((total_count - non_null_count) / total_count * 100) if total_count > 0 else 0
    
    # Get statistics based on data type
    if pd.api.types.is_numeric_dtype(series):
        unique_count = series.nunique()
        min_val = series.min()
        max_val = series.max()
        mean_val = series.mean()
        
        # Determine column purpose based on name and characteristics
        name_lower = column_name.lower()
        
        # Temporal columns
        if any(term in name_lower for term in ['year', 'yr']):
            return f"Temporal identifier representing calendar year. Range: {int(min_val)}-{int(max_val)}. Used for time-series analysis and year-over-year comparisons."
        
        elif any(term in name_lower for term in ['quarter', 'qtr', 'q']):
            return f"Quarterly time period identifier (1-4). Enables seasonal analysis and quarterly performance tracking."
        
        elif any(term in name_lower for term in ['month', 'mon']):
            return f"Monthly identifier (1-12). Supports monthly trend analysis and seasonal pattern detection."
        
        elif any(term in name_lower for term in ['day', 'date']):
            return f"Daily identifier. Supports granular time-series analysis and day-level patterns."
        
        # Financial metrics
        elif any(term in name_lower for term in ['ratio', 'rate', 'percent', 'pct']):
            return f"Financial ratio/rate metric. Range: {min_val:.2f} to {max_val:.2f}, Avg: {mean_val:.2f}. Used for financial health assessment and comparative analysis."
        
        elif any(term in name_lower for term in ['revenue', 'sales', 'income']):
            return f"Revenue/income metric. Range: {min_val:,.0f} to {max_val:,.0f}. Key performance indicator for financial performance evaluation."
        
        elif any(term in name_lower for term in ['cost', 'expense', 'expenditure']):
            return f"Cost/expense metric. Range: {min_val:,.0f} to {max_val:,.0f}. Used for cost analysis and budgeting."
        
        elif any(term in name_lower for term in ['asset', 'liability', 'equity']):
            return f"Balance sheet item. Range: {min_val:,.0f} to {max_val:,.0f}. Critical for financial position analysis."
        
        elif any(term in name_lower for term in ['profit', 'margin', 'earnings']):
            return f"Profitability metric. Range: {min_val:.2f} to {max_val:.2f}. Measures business profitability and operational efficiency."
        
        # ID columns
        elif unique_count == total_count or 'id' in name_lower:
            return f"Unique identifier with {unique_count:,} distinct values. Used for record identification and data joining."
        
        # General numeric
        else:
            return f"Numeric metric. Range: {min_val:,.2f} to {max_val:,.2f}, Mean: {mean_val:,.2f}. {unique_count:,} unique values."
    
    # Categorical columns
    elif pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
        unique_count = series.nunique()
        top_value = series.mode()[0] if len(series.mode()) > 0 else "N/A"
        
        name_lower = column_name.lower()
        
        # Identifier columns
        if any(term in name_lower for term in ['id', 'code', 'key', 'carrier', 'ticker', 'symbol']):
            return f"Categorical identifier. {unique_count} unique values (e.g., '{top_value}'). Used for grouping and entity identification."
        
        elif any(term in name_lower for term in ['name', 'title', 'label']):
            return f"Descriptive name/label field. {unique_count} unique values. Used for display and reference purposes."
        
        elif any(term in name_lower for term in ['category', 'type', 'class', 'group']):
            return f"Classification/category field. {unique_count} categories (most common: '{top_value}'). Enables segmentation and comparative analysis."
        
        elif any(term in name_lower for term in ['status', 'state', 'flag']):
            return f"Status/state indicator. {unique_count} possible states (e.g., '{top_value}'). Tracks entity state or condition."
        
        elif any(term in name_lower for term in ['location', 'region', 'city', 'country']):
            return f"Geographic identifier. {unique_count} locations. Supports geographic analysis and regional comparisons."
        
        else:
            return f"Categorical text field. {unique_count} unique values (most common: '{top_value}'). Useful for grouping and filtering."
    
    # DateTime columns
    elif pd.api.types.is_datetime64_any_dtype(series):
        min_date = series.min()
        max_date = series.max()
        return f"Datetime field. Range: {min_date} to {max_date}. Enables temporal analysis and time-based filtering."
    
    # Boolean columns
    elif pd.api.types.is_bool_dtype(series):
        true_count = series.sum()
        true_pct = (true_count / total_count * 100) if total_count > 0 else 0
        return f"Boolean flag. {true_pct:.1f}% True, {100-true_pct:.1f}% False. Used for binary classification and filtering."
    
    # Fallback for unknown types
    else:
        unique_count = series.nunique()
        return f"Data field of type {dtype}. {unique_count} unique values. Requires domain knowledge for interpretation."


def generate_column_descriptions(data: pd.DataFrame) -> dict:
    """Generates intelligent descriptions for each column in a DataFrame.

    Args:
        data (pandas.DataFrame): The DataFrame to analyze.

    Returns:
        dict: A dictionary mapping column names to their intelligent descriptions.
    """
    logging.info("Generating intelligent column descriptions...")
    descriptions = {}
    
    # Check if data is empty before proceeding
    if data.empty:
        logging.warning("DataFrame is empty, cannot generate column descriptions.")
        return descriptions

    for column in data.columns:
        try:
            description = _analyze_column_intelligently(column, data[column])
            descriptions[column] = description
            logging.debug(f"Generated intelligent description for '{column}'")
        except Exception as e:
            logging.warning(f"Could not generate intelligent description for column '{column}': {e}")
            # Fallback to simple description
            try:
                sample_values = data[column].dropna().astype(str).head(3).tolist()
                sample_text = ", ".join(sample_values)
                descriptions[column] = f"Data field with sample values: {sample_text}"
            except:
                descriptions[column] = "Data field (analysis failed)"

    logging.info(f"Finished generating descriptions for {len(descriptions)} columns.")
    return descriptions


def generate_summary(df: pd.DataFrame) -> dict:
    """Generates a summary of the DataFrame, including row count, column count, and column descriptions.

    Args:
        df (pandas.DataFrame): The DataFrame to summarize.

    Returns:
        dict: A dictionary containing the summary information.
    """
    logging.info("Generating data summary...")
    if df.empty:
        logging.warning("DataFrame is empty, generating empty summary.")
        return {
            "rows": 0,
            "columns": 0,
            "column_info": {}
        }

    meta = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_info": {}
    }

    # This calls the GPT description function
    descriptions = generate_column_descriptions(df)

    for col in df.columns:
        meta["column_info"][col] = {
            "dtype": str(df[col].dtype),
            # Use the description from the GPT call, or a fallback if generation failed for this column
            "description": descriptions.get(col, "Description unavailable")
        }
    logging.info("Finished generating data summary.")
    return meta