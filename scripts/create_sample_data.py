#!/usr/bin/env python3
"""
Create sample data for price elasticity analysis notebooks.

This script generates sample sales data that matches the expected structure
from the original IRI database, allowing the notebooks to run in the Linux environment.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def generate_sample_data(n_rows=100000):
    """Generate sample sales data that matches IRI format."""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Product categories (Thai Union products)
    products = [
        "CHICKEN OF THE SEA CHUNK LIGHT WATER 5 OZ 1 CT CAN LOW SODIUM - 00014800025455",
        "CHICKEN OF THE SEA CHUNK LIGHT OIL 5 OZ 1 CT CAN REGULAR - 00014800000195",
        "CHICKEN OF THE SEA SALMON PINK 14.75 OZ 1 CT CAN - 00014800012415",
        "CHICKEN OF THE SEA PREMIUM WHITE MEAT 5 OZ 1 CT CAN - 00014800320558",
        "CHICKEN OF THE SEA CHUNK LIGHT WATER 12 OZ 1 CT CAN - 00014800025820",
        "CHICKEN OF THE SEA TUNA SALAD KIT 3.5 OZ 1 CT POUCH - 00014800321685",
        "CHICKEN OF THE SEA SWEET & SPICY 2.5 OZ 1 CT POUCH - 00014800321678",
        "CHICKEN OF THE SEA PREMIUM WILD PINK SALMON 5 OZ CAN - 00014800012422",
        "CHICKEN OF THE SEA CHUNK WHITE ALBACORE 5 OZ CAN - 00014800320565",
        "CHICKEN OF THE SEA INFUSIONS LEMON PEPPER 2.5 OZ POUCH - 00014800321661"
    ]
    
    # Geographic regions
    geographies = [
        "ATLANTA", "BOSTON", "CHICAGO", "CLEVELAND", "DALLAS", "DENVER", 
        "DETROIT", "HOUSTON", "LOS ANGELES", "MIAMI", "NEW YORK", "PHILADELPHIA",
        "PHOENIX", "PITTSBURGH", "PORTLAND", "SAN DIEGO", "SAN FRANCISCO", 
        "SEATTLE", "ST LOUIS", "TAMPA", "WASHINGTON DC"
    ]
    
    # Generate time series (weekly data for ~3.5 years)
    start_date = datetime(2022, 1, 2)  # Sunday
    end_date = datetime(2025, 6, 8)    # Sunday
    weeks = []
    current_date = start_date
    while current_date <= end_date:
        weeks.append(current_date)
        current_date += timedelta(days=7)
    
    print(f"Generating {n_rows} rows of sample data...")
    print(f"Products: {len(products)}")
    print(f"Geographies: {len(geographies)}")
    print(f"Time periods: {len(weeks)} weeks")
    
    # Generate base data
    data = []
    
    for i in range(n_rows):
        # Random selections
        product = np.random.choice(products)
        geography = np.random.choice(geographies)
        week = np.random.choice(weeks)
        
        # Base price varies by product (realistic ranges)
        base_price = np.random.uniform(0.89, 17.82)
        
        # Price elasticity simulation
        # Higher prices generally lead to lower quantities (with noise)
        price_factor = 1 + np.random.uniform(-0.3, 0.3)  # ±30% variation
        unit_price = base_price * price_factor
        
        # Quantity inversely related to price (elastic demand)
        base_quantity = np.random.uniform(10, 10000)
        price_elasticity = -1.2 + np.random.uniform(-0.5, 0.5)  # Elastic goods
        quantity_factor = (base_price / unit_price) ** abs(price_elasticity)
        quantity_sold = max(1, base_quantity * quantity_factor * np.random.uniform(0.5, 1.5))
        
        # Volume (assuming variable volume per unit)
        volume_per_unit = np.random.uniform(5, 50)  # oz or similar
        volume = quantity_sold * volume_per_unit
        
        # Revenue calculation
        revenue = unit_price * quantity_sold
        
        # Distribution metrics
        store_penetration = np.random.uniform(0.1, 1.0)
        distribution_acv = np.random.uniform(0.05, 0.95)
        
        # Promotional variables (many will be zero/null)
        has_promotion = np.random.random() < 0.15  # 15% chance of promotion
        
        record = {
            'ID': i + 1,
            'Geography': geography,
            'Product': product,
            'Time': f"Week Ending {week.strftime('%m-%d-%y')}",
            'Geography Key': float(hash(geography) % 1000),
            'Product Key': product.split(' - ')[-1] if ' - ' in product else str(hash(product) % 100000),
            'Unit Sales': quantity_sold,
            'Unit Sales Year Ago': quantity_sold * np.random.uniform(0.8, 1.2),
            'Unit Sales 2 Years Ago': quantity_sold * np.random.uniform(0.7, 1.3),
            'Unit Sales 3 Years Ago': quantity_sold * np.random.uniform(0.6, 1.4),
            'Base Unit Sales': quantity_sold * np.random.uniform(0.7, 1.0) if has_promotion else quantity_sold,
            'Incremental Units': quantity_sold * np.random.uniform(0.1, 0.3) if has_promotion else 0,
            'Volume Sales': volume,
            '% Stores': store_penetration,
            'ACV Weighted Distribution Feature Only': distribution_acv * 0.2 if has_promotion else 0,
            'ACV Weighted Distribution Feature and Display': distribution_acv * 0.1 if has_promotion else 0,
            'ACV Weighted Distribution Display Only': distribution_acv * 0.15 if has_promotion else 0,
            'ACV Weighted Distribution Price Reductions Only': distribution_acv * 0.25 if has_promotion else 0,
            'ACV Weighted Distribution': distribution_acv,
            'Price per Unit': unit_price,
            'Price per Unit Year Ago': unit_price * np.random.uniform(0.9, 1.1),
            'Price per Unit Any Merch': unit_price * 0.9 if has_promotion else unit_price,
            'Price per Unit No Merch': unit_price,
            'Total Points of Distribution': distribution_acv * 1000,
            'Total Points of Distribution Change vs YA': np.random.uniform(-50, 50),
            'Dollar Sales': revenue,
            'Dollar Sales Year Ago': revenue * np.random.uniform(0.8, 1.2),
            'Dollar Sales 2 Years Ago': revenue * np.random.uniform(0.7, 1.3),
            'Dollar Sales 3 Years Ago': revenue * np.random.uniform(0.6, 1.4),
            'Incremental Dollars': revenue * np.random.uniform(0.1, 0.3) if has_promotion else 0,
            'Base Dollar Sales': revenue * np.random.uniform(0.7, 1.0) if has_promotion else revenue,
            'Unit Sales per Pt of Distribution': quantity_sold / max(1, distribution_acv * 1000),
            'Weighted Average Base Price Per Unit': unit_price,
            'Opportunity Dollars': revenue * np.random.uniform(0.05, 0.2),
            'Dollar Trade Efficiency': np.random.uniform(0.5, 2.0) if has_promotion else np.nan,
            'Unit Trade Efficiency': np.random.uniform(0.5, 2.0) if has_promotion else np.nan
        }
        
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # Add some realistic missing values
    missing_cols = ['Unit Sales Year Ago', 'Unit Sales 2 Years Ago', 'Unit Sales 3 Years Ago',
                   'ACV Weighted Distribution Feature Only', 'ACV Weighted Distribution Feature and Display',
                   'ACV Weighted Distribution Display Only', 'ACV Weighted Distribution Price Reductions Only',
                   'Price per Unit Any Merch', 'Incremental Units', 'Incremental Dollars',
                   'Dollar Trade Efficiency', 'Unit Trade Efficiency']
    
    for col in missing_cols:
        if col in df.columns:
            missing_mask = np.random.random(len(df)) < 0.1  # 10% missing for some columns
            df.loc[missing_mask, col] = np.nan
    
    return df


def save_sample_data():
    """Generate and save sample data files."""
    
    # Create directories
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sample data
    df_raw = generate_sample_data(n_rows=100000)
    
    # Save raw data
    raw_file = raw_dir / "iri_sales_data.parquet"
    df_raw.to_parquet(raw_file, index=False)
    print(f"✅ Saved raw data: {raw_file}")
    print(f"   Shape: {df_raw.shape}")
    print(f"   Size: {raw_file.stat().st_size / 1024**2:.1f} MB")
    
    # Create a "cleaned" version for processed data
    # This simulates what notebook 02 would produce
    df_clean = df_raw.copy()
    
    # Parse time column and add date
    df_clean['date_str'] = df_clean['Time'].str.replace('Week Ending ', '')
    df_clean['date'] = pd.to_datetime(df_clean['date_str'], format='%m-%d-%y')
    
    # Standardize some column names
    column_mapping = {
        'Unit Sales': 'quantity_sold',
        'Price per Unit': 'unit_price',
        'Dollar Sales': 'revenue',
        'Volume Sales': 'volume',
        '% Stores': 'store_penetration',
        'ACV Weighted Distribution': 'distribution_acv',
        'Product': 'product_name',
        'Geography': 'geography'
    }
    
    df_clean = df_clean.rename(columns=column_mapping)
    
    # Drop some rows to simulate cleaning
    df_clean = df_clean.dropna(subset=['quantity_sold', 'unit_price', 'revenue'])
    
    # Save cleaned data
    clean_file = processed_dir / "iri_sales_data_clean.parquet"
    df_clean.to_parquet(clean_file, index=False)
    print(f"✅ Saved cleaned data: {clean_file}")
    print(f"   Shape: {df_clean.shape}")
    print(f"   Size: {clean_file.stat().st_size / 1024**2:.1f} MB")
    
    # Update cleaning summary
    cleaning_summary = {
        "cleaning_timestamp": datetime.now().isoformat(),
        "original_shape": list(df_raw.shape),
        "final_shape": list(df_clean.shape),
        "rows_removed": len(df_raw) - len(df_clean),
        "columns_added": len(df_clean.columns) - len(df_raw.columns),
        "memory_before_mb": df_raw.memory_usage(deep=True).sum() / 1024**2,
        "memory_after_mb": df_clean.memory_usage(deep=True).sum() / 1024**2,
        "missing_values_handled": len([col for col in df_clean.columns if df_clean[col].isnull().sum() > 0]),
        "outliers_capped": 2,
        "categorical_columns_optimized": 2
    }
    
    import json
    summary_file = processed_dir / "cleaning_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(cleaning_summary, f, indent=2, default=str)
    print(f"✅ Updated cleaning summary: {summary_file}")
    
    print("\n🎉 Sample data generation complete!")
    print("All notebooks should now be able to import data correctly.")


if __name__ == "__main__":
    save_sample_data()