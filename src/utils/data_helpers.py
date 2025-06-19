"""
Data helper functions for price elasticity analysis.

This module contains utility functions for data loading, cleaning,
and preprocessing used across the analysis notebooks.
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "configs/analysis_config.yaml") -> Dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        Dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        raise


def load_sales_data(file_path: str, date_column: str = 'date') -> pd.DataFrame:
    """
    Load sales data from CSV file with proper date parsing.
    
    Args:
        file_path (str): Path to the sales data file
        date_column (str): Name of the date column
        
    Returns:
        pd.DataFrame: Loaded sales data
    """
    try:
        # Detect file format and load accordingly
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, parse_dates=[date_column])
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path, parse_dates=[date_column])
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
            df[date_column] = pd.to_datetime(df[date_column])
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
            
        logger.info(f"Loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise


def validate_data_quality(df: pd.DataFrame, 
                         required_columns: List[str],
                         price_column: str = 'Price per Unit',
                         quantity_column: str = 'Unit Sales') -> Dict:
    """
    Validate data quality and return summary of issues.
    
    Args:
        df (pd.DataFrame): Input dataframe
        required_columns (List[str]): List of required columns
        price_column (str): Name of price column
        quantity_column (str): Name of quantity column
        
    Returns:
        Dict: Dictionary containing validation results
    """
    validation_results = {
        'total_rows': len(df),
        'missing_columns': [],
        'missing_values': {},
        'negative_prices': 0,
        'zero_quantities': 0,
        'outliers': {}
    }
    
    # Check for missing columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    validation_results['missing_columns'] = missing_cols
    
    # Check for missing values
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            validation_results['missing_values'][col] = missing_count
    
    # Check for data quality issues
    if price_column in df.columns:
        validation_results['negative_prices'] = (df[price_column] <= 0).sum()
        
        # Identify price outliers (beyond 3 standard deviations)
        price_mean = df[price_column].mean()
        price_std = df[price_column].std()
        price_outliers = df[
            (df[price_column] > price_mean + 3 * price_std) |
            (df[price_column] < price_mean - 3 * price_std)
        ]
        validation_results['outliers']['price'] = len(price_outliers)
    
    if quantity_column in df.columns:
        validation_results['zero_quantities'] = (df[quantity_column] == 0).sum()
        
        # Identify quantity outliers
        qty_mean = df[quantity_column].mean()
        qty_std = df[quantity_column].std()
        qty_outliers = df[df[quantity_column] > qty_mean + 3 * qty_std]
        validation_results['outliers']['quantity'] = len(qty_outliers)
    
    logger.info(f"Data validation completed. Found {len(missing_cols)} missing columns, "
                f"{sum(validation_results['missing_values'].values())} missing values")
    
    return validation_results


def clean_sales_data(df: pd.DataFrame, 
                    price_column: str = 'Price per Unit',
                    quantity_column: str = 'Unit Sales',
                    date_column: str = 'date') -> pd.DataFrame:
    """
    Clean sales data by handling missing values and outliers.
    
    Args:
        df (pd.DataFrame): Input dataframe
        price_column (str): Name of price column
        quantity_column (str): Name of quantity column
        date_column (str): Name of date column
        
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    df_clean = df.copy()
    original_rows = len(df_clean)
    
    # Remove rows with missing critical values
    df_clean = df_clean.dropna(subset=[price_column, quantity_column, date_column])
    
    # Remove negative prices and quantities
    df_clean = df_clean[df_clean[price_column] > 0]
    df_clean = df_clean[df_clean[quantity_column] >= 0]
    
    # Remove extreme outliers (beyond 5 standard deviations)
    for col in [price_column, quantity_column]:
        mean_val = df_clean[col].mean()
        std_val = df_clean[col].std()
        df_clean = df_clean[
            (df_clean[col] <= mean_val + 5 * std_val) &
            (df_clean[col] >= mean_val - 5 * std_val)
        ]
    
    # Sort by date
    df_clean = df_clean.sort_values(date_column).reset_index(drop=True)
    
    rows_removed = original_rows - len(df_clean)
    logger.info(f"Data cleaning completed. Removed {rows_removed} rows "
                f"({rows_removed/original_rows*100:.1f}%)")
    
    return df_clean


def create_time_features(df: pd.DataFrame, 
                        date_column: str = 'date') -> pd.DataFrame:
    """
    Create time-based features from date column.
    
    Args:
        df (pd.DataFrame): Input dataframe
        date_column (str): Name of date column
        
    Returns:
        pd.DataFrame: Dataframe with additional time features
    """
    df_time = df.copy()
    
    # Extract time components
    df_time['year'] = df_time[date_column].dt.year
    df_time['month'] = df_time[date_column].dt.month
    df_time['day'] = df_time[date_column].dt.day
    df_time['day_of_week'] = df_time[date_column].dt.dayofweek + 1  # 1=Monday
    df_time['week_of_year'] = df_time[date_column].dt.isocalendar().week
    df_time['quarter'] = df_time[date_column].dt.quarter
    
    # Create binary indicators
    df_time['is_weekend'] = df_time['day_of_week'].isin([6, 7])
    df_time['is_month_start'] = df_time[date_column].dt.is_month_start
    df_time['is_month_end'] = df_time[date_column].dt.is_month_end
    df_time['is_quarter_start'] = df_time[date_column].dt.is_quarter_start
    df_time['is_quarter_end'] = df_time[date_column].dt.is_quarter_end
    
    logger.info("Time features created successfully")
    return df_time


def create_lag_features(df: pd.DataFrame, 
                       columns: List[str],
                       lags: List[int],
                       group_column: Optional[str] = None) -> pd.DataFrame:
    """
    Create lag features for specified columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str]): Columns to create lags for
        lags (List[int]): List of lag periods
        group_column (str, optional): Column to group by for lags
        
    Returns:
        pd.DataFrame: Dataframe with lag features
    """
    df_lag = df.copy()
    
    for col in columns:
        for lag in lags:
            if group_column:
                df_lag[f'{col}_lag_{lag}'] = df_lag.groupby(group_column)[col].shift(lag)
            else:
                df_lag[f'{col}_lag_{lag}'] = df_lag[col].shift(lag)
    
    logger.info(f"Created lag features for {len(columns)} columns with lags {lags}")
    return df_lag


def create_rolling_features(df: pd.DataFrame, 
                           columns: List[str],
                           windows: List[int],
                           group_column: Optional[str] = None) -> pd.DataFrame:
    """
    Create rolling window features for specified columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str]): Columns to create rolling features for
        windows (List[int]): List of window sizes
        group_column (str, optional): Column to group by for rolling
        
    Returns:
        pd.DataFrame: Dataframe with rolling features
    """
    df_rolling = df.copy()
    
    for col in columns:
        for window in windows:
            if group_column:
                df_rolling[f'{col}_ma_{window}'] = (
                    df_rolling.groupby(group_column)[col]
                    .rolling(window=window, min_periods=1)
                    .mean()
                    .reset_index(0, drop=True)
                )
                df_rolling[f'{col}_std_{window}'] = (
                    df_rolling.groupby(group_column)[col]
                    .rolling(window=window, min_periods=1)
                    .std()
                    .reset_index(0, drop=True)
                )
            else:
                df_rolling[f'{col}_ma_{window}'] = (
                    df_rolling[col].rolling(window=window, min_periods=1).mean()
                )
                df_rolling[f'{col}_std_{window}'] = (
                    df_rolling[col].rolling(window=window, min_periods=1).std()
                )
    
    logger.info(f"Created rolling features for {len(columns)} columns with windows {windows}")
    return df_rolling


def save_processed_data(df: pd.DataFrame, 
                       file_path: str,
                       file_format: str = 'parquet') -> None:
    """
    Save processed data to file.
    
    Args:
        df (pd.DataFrame): Dataframe to save
        file_path (str): Output file path
        file_format (str): File format ('csv', 'parquet', 'excel')
    """
    try:
        if file_format.lower() == 'csv':
            df.to_csv(file_path, index=False)
        elif file_format.lower() == 'parquet':
            df.to_parquet(file_path, index=False)
        elif file_format.lower() in ['excel', 'xlsx']:
            df.to_excel(file_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
            
        logger.info(f"Data saved to {file_path} ({file_format} format)")
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        raise


def get_data_summary(df: pd.DataFrame) -> Dict:
    """
    Get comprehensive summary of dataframe.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        Dict: Summary statistics and information
    """
    summary = {
        'shape': df.shape,
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_summary': df.describe().to_dict(),
        'date_range': {}
    }
    
    # Add date range information if date columns exist
    date_columns = df.select_dtypes(include=['datetime64']).columns
    for col in date_columns:
        summary['date_range'][col] = {
            'min': df[col].min(),
            'max': df[col].max(),
            'days': (df[col].max() - df[col].min()).days
        }
    
    return summary


def parse_iri_time_column(df: pd.DataFrame, time_column: str = 'Time') -> pd.DataFrame:
    """
    Parse IRI time format 'Week Ending MM-DD-YY' to proper datetime.
    
    Args:
        df (pd.DataFrame): Input dataframe
        time_column (str): Name of the time column
        
    Returns:
        pd.DataFrame: Dataframe with parsed date column
    """
    df_parsed = df.copy()
    
    try:
        # Extract date part from "Week Ending MM-DD-YY" format
        df_parsed['date_str'] = df_parsed[time_column].str.replace('Week Ending ', '')
        df_parsed['parsed_date'] = pd.to_datetime(df_parsed['date_str'], format='%m-%d-%y')
        
        # Create clean date column
        df_parsed['date'] = df_parsed['parsed_date']
        
        # Drop temporary columns
        df_parsed = df_parsed.drop(['date_str', 'parsed_date'], axis=1)
        
        logger.info(f"Successfully parsed IRI time format from {time_column}")
        return df_parsed
        
    except Exception as e:
        logger.error(f"Error parsing IRI time format: {e}")
        # Fallback: try standard datetime parsing
        df_parsed['date'] = pd.to_datetime(df_parsed[time_column], errors='coerce')
        return df_parsed


def standardize_iri_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize IRI column names to match utility function expectations.
    
    Args:
        df (pd.DataFrame): Input dataframe with IRI column names
        
    Returns:
        pd.DataFrame: Dataframe with standardized column names
    """
    df_std = df.copy()
    
    # Create column mapping for IRI data
    column_mapping = {
        'Price per Unit': 'unit_price',
        'Unit Sales': 'quantity_sold',
        'Time': 'time_original',
        'Product': 'product_name',
        'Geography': 'geography',
        'Dollar Sales': 'revenue',
        'Volume Sales': 'volume',
        '% Stores': 'store_penetration',
        'ACV Weighted Distribution': 'distribution_acv'
    }
    
    # Rename columns that exist
    existing_renames = {k: v for k, v in column_mapping.items() if k in df_std.columns}
    df_std = df_std.rename(columns=existing_renames)
    
    logger.info(f"Standardized {len(existing_renames)} IRI column names")
    return df_std 