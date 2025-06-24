#!/usr/bin/env python3
"""
Test script to verify that all notebooks can import data correctly.
This simulates the import patterns used in each notebook.
"""

import sys
import os
from pathlib import Path

# Add project root to path (simulate notebook behavior)
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def test_data_loading():
    """Test 01_data_loading.ipynb patterns"""
    print("🧪 Testing data loading patterns...")
    
    try:
        # Test raw data loading
        import pandas as pd
        raw_file = Path("data/raw/iri_sales_data.parquet")
        
        if raw_file.exists():
            df_raw = pd.read_parquet(raw_file)
            print(f"✅ Raw data loaded: {df_raw.shape}")
            
            # Test basic structure
            expected_cols = ['ID', 'Geography', 'Product', 'Time', 'Unit Sales', 'Price per Unit', 'Dollar Sales']
            missing_cols = [col for col in expected_cols if col not in df_raw.columns]
            if missing_cols:
                print(f"⚠ Missing expected columns: {missing_cols}")
            else:
                print("✅ All expected columns present")
        else:
            print("❌ Raw data file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error in data loading test: {e}")
        return False
    
    return True


def test_data_cleaning():
    """Test 02_data_cleaning.ipynb patterns"""
    print("\n🧪 Testing data cleaning patterns...")
    
    try:
        from src.utils.data_helpers import parse_iri_time_column, standardize_iri_columns
        import pandas as pd
        
        # Load raw data
        raw_file = Path("data/raw/iri_sales_data.parquet")
        df_raw = pd.read_parquet(raw_file)
        
        # Test time parsing
        df_parsed = parse_iri_time_column(df_raw, time_column='Time')
        if 'date' in df_parsed.columns:
            print("✅ Time parsing works")
        else:
            print("❌ Time parsing failed")
            return False
            
        # Test column standardization
        df_std = standardize_iri_columns(df_parsed)
        print(f"✅ Column standardization works: {len(df_std.columns)} columns")
        
    except Exception as e:
        print(f"❌ Error in data cleaning test: {e}")
        return False
    
    return True


def test_eda():
    """Test 03_eda.ipynb patterns"""
    print("\n🧪 Testing EDA patterns...")
    
    try:
        from src.utils.data_helpers import load_cleaned_data, get_cleaned_data_summary
        
        # Test cleaned data loading
        df_clean = load_cleaned_data()
        print(f"✅ Cleaned data loaded: {df_clean.shape}")
        
        # Test summary function
        summary = get_cleaned_data_summary(df_clean)
        required_keys = ['total_records', 'date_range', 'geographic_coverage', 'product_coverage']
        if all(key in summary for key in required_keys):
            print("✅ Data summary function works")
        else:
            print("❌ Data summary function missing keys")
            return False
            
    except Exception as e:
        print(f"❌ Error in EDA test: {e}")
        return False
    
    return True


def test_feature_engineering():
    """Test 04_feature_engineering.ipynb patterns"""
    print("\n🧪 Testing feature engineering patterns...")
    
    try:
        from src.utils.data_helpers import create_time_features, create_lag_features, create_rolling_features
        import pandas as pd
        
        # Create sample data for testing
        dates = pd.date_range('2022-01-01', periods=100, freq='W')
        df_test = pd.DataFrame({
            'date': dates,
            'price': [1.0, 2.0, 3.0] * 33 + [1.0],
            'quantity': [10, 20, 30] * 33 + [10]
        })
        
        # Test time features
        df_time = create_time_features(df_test, date_column='date')
        if 'year' in df_time.columns and 'month' in df_time.columns:
            print("✅ Time features creation works")
        else:
            print("❌ Time features creation failed")
            return False
            
        # Test lag features  
        df_lag = create_lag_features(df_test, columns=['price'], lags=[1, 2])
        if 'price_lag_1' in df_lag.columns:
            print("✅ Lag features creation works")
        else:
            print("❌ Lag features creation failed")
            return False
            
        # Test rolling features
        df_rolling = create_rolling_features(df_test, columns=['price'], windows=[4])
        if 'price_ma_4' in df_rolling.columns:
            print("✅ Rolling features creation works")
        else:
            print("❌ Rolling features creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in feature engineering test: {e}")
        return False
    
    return True


def test_modeling():
    """Test 05_modeling.ipynb patterns"""
    print("\n🧪 Testing modeling patterns...")
    
    try:
        import src.utils.model_helpers
        print("✅ Model helpers imported successfully")
        
    except Exception as e:
        print(f"❌ Error in modeling test: {e}")
        return False
    
    return True


def test_evaluation():
    """Test 06_evaluation.ipynb patterns"""
    print("\n🧪 Testing evaluation patterns...")
    
    try:
        import src.utils.model_helpers
        print("✅ Evaluation imports work")
        
    except Exception as e:
        print(f"❌ Error in evaluation test: {e}")
        return False
    
    return True


def test_visualization():
    """Test 07_visualization.ipynb patterns"""
    print("\n🧪 Testing visualization patterns...")
    
    try:
        import src.utils.plot_helpers
        print("✅ Visualization imports work")
        
    except Exception as e:
        print(f"❌ Error in visualization test: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("🔬 Testing notebook import patterns...\n")
    
    tests = [
        ("Data Loading", test_data_loading),
        ("Data Cleaning", test_data_cleaning), 
        ("EDA", test_eda),
        ("Feature Engineering", test_feature_engineering),
        ("Modeling", test_modeling),
        ("Evaluation", test_evaluation),
        ("Visualization", test_visualization)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "="*50)
    print("📋 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All notebook import patterns work correctly!")
        print("All notebooks should now be able to import data without errors.")
    else:
        print(f"\n⚠ {total - passed} tests failed. Some notebooks may have import issues.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)