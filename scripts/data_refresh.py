#!/usr/bin/env python3
"""
Data Refresh Module for Price Elasticity Analysis
Handles database extraction and notebook date updates.
"""

import os
import sys
import pyodbc
import pandas as pd
import time
import logging
import re
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DataRefresher:
    """Handles data extraction and notebook updates."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.raw_data_dir = self.project_root / "data" / "raw"
        self.notebooks_dir = self.project_root / "notebooks"
        
        # Database configuration
        self.db_path = r"C:\Users\adaves\Thai Union Group\COSI - Sales Planning Team - General\Sales Toolbox 2020 - IRI.accdb"
        self.table_name = "tblIRI2"
        self.output_file = self.raw_data_dir / "iri_sales_data.parquet"
        
        # Create directories
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('DataRefresher')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
    def validate_database_connection(self):
        """Check if database file exists and is accessible."""
        db_path = Path(self.db_path)
        
        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        if not db_path.is_file():
            raise ValueError(f"Database path is not a file: {self.db_path}")
        
        # Test connection
        try:
            conn_string = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.db_path};'
            conn = pyodbc.connect(conn_string)
            conn.close()
            self.logger.info("✅ Database connection validated")
            return True
        except Exception as e:
            raise ConnectionError(f"Cannot connect to database: {str(e)}")
    
    def extract_data_from_access(self):
        """Extract data from Access database and save as Parquet."""
        self.logger.info("🔄 Starting data extraction from Access database...")
        start_time = time.time()
        
        try:
            # Validate connection first
            self.validate_database_connection()
            
            # Connect and extract
            conn_string = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.db_path};'
            conn = pyodbc.connect(conn_string)
            
            self.logger.info(f"📊 Extracting data from table: {self.table_name}")
            
            # Extract data
            query = f"SELECT * FROM {self.table_name}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Validate data
            self.validate_extracted_data(df)
            
            # Save as Parquet
            df.to_parquet(self.output_file, index=False)
            
            # Performance metrics
            extraction_time = time.time() - start_time
            file_size = self.output_file.stat().st_size / (1024**2)  # MB
            
            self.logger.info("✅ Data extraction completed successfully!")
            self.logger.info(f"   📋 Rows extracted: {len(df):,}")
            self.logger.info(f"   📋 Columns: {len(df.columns)}")
            self.logger.info(f"   💾 File size: {file_size:.1f} MB")
            self.logger.info(f"   ⏱️ Extraction time: {extraction_time:.1f} seconds")
            
            return True, {
                'rows': len(df),
                'columns': len(df.columns),
                'file_size_mb': file_size,
                'extraction_time': extraction_time
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data extraction failed: {str(e)}")
            raise
    
    def validate_extracted_data(self, df):
        """Validate the extracted data meets expectations."""
        # Expected weekly data: ~18,900 rows
        min_expected_rows = 1000000  # Minimum total rows (historical + new)
        max_expected_rows = 3000000  # Maximum reasonable rows
        
        if len(df) < min_expected_rows:
            raise ValueError(f"Too few rows extracted: {len(df):,}. Expected at least {min_expected_rows:,}")
        
        if len(df) > max_expected_rows:
            self.logger.warning(f"⚠️ More rows than expected: {len(df):,}. Expected max {max_expected_rows:,}")
        
        # Check for required columns (add based on your actual schema)
        required_columns = ['ID', 'Geography', 'Product', 'Time']  # Update with actual required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for null IDs
        if df['ID'].isnull().any():
            raise ValueError("Found null values in ID column")
        
        self.logger.info("✅ Data validation passed")
    
    def update_notebook_refresh_date(self, notebook_path):
        """Update the data refresh date in a notebook."""
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse notebook JSON
            import json
            notebook = json.loads(content)
            
            # Find the first code cell with imports
            for cell in notebook['cells']:
                if cell['cell_type'] == 'code' and cell['source']:
                    source_lines = cell['source'] if isinstance(cell['source'], list) else cell['source'].split('\n')
                    
                    # Look for import statements
                    has_imports = any(line.strip().startswith(('import ', 'from ')) for line in source_lines)
                    
                    if has_imports:
                        # Check if refresh date already exists
                        refresh_line_exists = any('# Data refreshed:' in line for line in source_lines)
                        
                        if refresh_line_exists:
                            # Update existing line
                            for i, line in enumerate(source_lines):
                                if '# Data refreshed:' in line:
                                    source_lines[i] = f"# Data refreshed: {self.current_date}\n"
                                    break
                        else:
                            # Add new line at the beginning
                            source_lines.insert(0, f"# Data refreshed: {self.current_date}\n")
                        
                        # Update cell source
                        cell['source'] = source_lines
                        break
            
            # Save updated notebook
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
            
            self.logger.debug(f"✅ Updated refresh date in: {notebook_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update {notebook_path.name}: {str(e)}")
            return False
    
    def update_all_notebooks(self):
        """Update data refresh date in all 7 notebooks."""
        self.logger.info("📝 Updating data refresh dates in notebooks...")
        
        notebooks = [
            "01_data_loading.ipynb",
            "02_data_cleaning.ipynb",
            "03_eda.ipynb", 
            "04_feature_engineering.ipynb",
            "05_modeling.ipynb",
            "06_evaluation.ipynb",
            "07_visualization.ipynb"
        ]
        
        updated_count = 0
        
        for notebook_name in notebooks:
            notebook_path = self.notebooks_dir / notebook_name
            
            if notebook_path.exists():
                if self.update_notebook_refresh_date(notebook_path):
                    updated_count += 1
            else:
                self.logger.warning(f"⚠️ Notebook not found: {notebook_name}")
        
        self.logger.info(f"✅ Updated {updated_count}/{len(notebooks)} notebooks")
        return updated_count == len([n for n in notebooks if (self.notebooks_dir / n).exists()])
    
    def check_for_missed_weeks(self):
        """Check if any weeks were missed and should be processed."""
        # This is a placeholder for future enhancement
        # Could check for gaps in data dates and alert
        pass
    
    def refresh_data_and_notebooks(self):
        """Complete data refresh workflow."""
        try:
            self.logger.info("🚀 Starting data refresh workflow...")
            
            # Step 1: Extract data
            success, metrics = self.extract_data_from_access()
            if not success:
                return False
            
            # Step 2: Update notebooks
            notebook_success = self.update_all_notebooks()
            if not notebook_success:
                self.logger.error("❌ Failed to update all notebooks")
                return False
            
            # Step 3: Check for missed weeks (future enhancement)
            self.check_for_missed_weeks()
            
            self.logger.info("✅ Data refresh workflow completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Data refresh workflow failed: {str(e)}")
            return False


def refresh_data_and_notebooks():
    """Main function for data refresh - called by pipeline orchestrator."""
    refresher = DataRefresher()
    return refresher.refresh_data_and_notebooks()


def main():
    """Main entry point for standalone execution."""
    try:
        success = refresh_data_and_notebooks()
        
        if success:
            print("🎉 Data refresh completed successfully!")
            sys.exit(0)
        else:
            print("💥 Data refresh failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Critical error in data refresh: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 