#!/usr/bin/env python3
"""
Performance Tracking Module for Price Elasticity Analysis
Monitors model performance and tracks trends over time.
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class PerformanceTracker:
    """Tracks and monitors model performance across weekly runs."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.outputs_dir = self.project_root / "outputs"
        self.performance_log_file = self.outputs_dir / "performance_log.csv"
        
        # Create outputs directory
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('PerformanceTracker')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Performance thresholds (placeholders - will be refined as project matures)
        self.performance_thresholds = {
            'r_squared_min': 0.7,        # Minimum acceptable R²
            'r_squared_drop_alert': 0.05, # Alert if R² drops by 5%
            'mae_increase_alert': 0.10,   # Alert if MAE increases by 10%
            'elasticity_change_alert': 0.20 # Alert if elasticity changes by 20%
        }
    
    def initialize_performance_log(self):
        """Initialize the performance log CSV if it doesn't exist."""
        if not self.performance_log_file.exists():
            columns = [
                'week_ending',
                'timestamp',
                'model_type',
                'r_squared',
                'mae',
                'mse',
                'rmse',
                'elasticity_coefficient',
                'elasticity_std_error',
                'data_points_training',
                'data_points_validation',
                'training_time_seconds',
                'cross_validation_score',
                'feature_count',
                'notes'
            ]
            
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.performance_log_file, index=False)
            self.logger.info(f"✅ Initialized performance log: {self.performance_log_file}")
    
    def extract_model_metrics(self, week_ending_date):
        """Extract model performance metrics from the weekly analysis."""
        week_output_dir = self.outputs_dir / week_ending_date
        
        # This will be populated once modeling notebooks generate standard output files
        # For now, create placeholder structure
        
        metrics = {
            'week_ending': week_ending_date,
            'timestamp': datetime.now().isoformat(),
            'model_type': 'linear_regression',  # Default - will be dynamic later
            'r_squared': None,
            'mae': None,
            'mse': None,
            'rmse': None,
            'elasticity_coefficient': None,
            'elasticity_std_error': None,
            'data_points_training': None,
            'data_points_validation': None,
            'training_time_seconds': None,
            'cross_validation_score': None,
            'feature_count': None,
            'notes': 'Placeholder metrics - modeling pipeline in development'
        }
        
        # Look for standard model output files (to be created by modeling notebooks)
        model_results_file = week_output_dir / "models" / "model_results.json"
        
        if model_results_file.exists():
            try:
                with open(model_results_file, 'r') as f:
                    model_data = json.load(f)
                
                # Update metrics with actual values
                metrics.update({
                    'model_type': model_data.get('model_type', 'linear_regression'),
                    'r_squared': model_data.get('r_squared'),
                    'mae': model_data.get('mae'),
                    'mse': model_data.get('mse'),
                    'rmse': model_data.get('rmse'),
                    'elasticity_coefficient': model_data.get('elasticity_coefficient'),
                    'elasticity_std_error': model_data.get('elasticity_std_error'),
                    'data_points_training': model_data.get('training_samples'),
                    'data_points_validation': model_data.get('validation_samples'),
                    'training_time_seconds': model_data.get('training_time'),
                    'cross_validation_score': model_data.get('cv_score'),
                    'feature_count': model_data.get('feature_count'),
                    'notes': model_data.get('notes', '')
                })
                
                self.logger.info("✅ Extracted actual model metrics")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load model results: {str(e)}")
                metrics['notes'] = f"Error loading metrics: {str(e)}"
        else:
            self.logger.info("📋 Model results file not found - using placeholder metrics")
        
        return metrics
    
    def log_weekly_performance(self, week_ending_date):
        """Log performance metrics for the current week."""
        try:
            self.logger.info(f"📊 Logging performance metrics for week: {week_ending_date}")
            
            # Initialize log file if needed
            self.initialize_performance_log()
            
            # Extract metrics
            metrics = self.extract_model_metrics(week_ending_date)
            
            # Load existing log
            df_log = pd.read_csv(self.performance_log_file)
            
            # Check if this week already exists
            if week_ending_date in df_log['week_ending'].values:
                # Update existing entry
                idx = df_log[df_log['week_ending'] == week_ending_date].index[0]
                for key, value in metrics.items():
                    if key in df_log.columns:
                        df_log.loc[idx, key] = value
                self.logger.info("✅ Updated existing performance entry")
            else:
                # Add new entry
                new_row = pd.DataFrame([metrics])
                df_log = pd.concat([df_log, new_row], ignore_index=True)
                self.logger.info("✅ Added new performance entry")
            
            # Save updated log
            df_log.to_csv(self.performance_log_file, index=False)
            
            # Analyze performance trends
            self.analyze_performance_trends(df_log)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log performance: {str(e)}")
            return False
    
    def analyze_performance_trends(self, df_log):
        """Analyze performance trends and generate alerts."""
        if len(df_log) < 2:
            self.logger.info("📈 Insufficient data for trend analysis")
            return
        
        # Sort by date
        df_log['week_ending'] = pd.to_datetime(df_log['week_ending'])
        df_log = df_log.sort_values('week_ending')
        
        # Get current and previous week
        current_week = df_log.iloc[-1]
        previous_week = df_log.iloc[-2]
        
        self.logger.info("📈 Analyzing performance trends...")
        
        # R² trend analysis
        if pd.notna(current_week['r_squared']) and pd.notna(previous_week['r_squared']):
            r_squared_change = current_week['r_squared'] - previous_week['r_squared']
            r_squared_pct_change = (r_squared_change / previous_week['r_squared']) * 100
            
            if abs(r_squared_change) > self.performance_thresholds['r_squared_drop_alert']:
                if r_squared_change < 0:
                    self.logger.warning(f"⚠️ R² DECREASED by {abs(r_squared_change):.3f} ({r_squared_pct_change:.1f}%)")
                else:
                    self.logger.info(f"📈 R² IMPROVED by {r_squared_change:.3f} ({r_squared_pct_change:.1f}%)")
            
            # Check minimum threshold
            if current_week['r_squared'] < self.performance_thresholds['r_squared_min']:
                self.logger.warning(f"⚠️ R² BELOW THRESHOLD: {current_week['r_squared']:.3f} < {self.performance_thresholds['r_squared_min']}")
        
        # MAE trend analysis
        if pd.notna(current_week['mae']) and pd.notna(previous_week['mae']):
            mae_change = current_week['mae'] - previous_week['mae']
            mae_pct_change = (mae_change / previous_week['mae']) * 100
            
            if abs(mae_pct_change) > (self.performance_thresholds['mae_increase_alert'] * 100):
                if mae_change > 0:
                    self.logger.warning(f"⚠️ MAE INCREASED by {mae_change:.3f} ({mae_pct_change:.1f}%)")
                else:
                    self.logger.info(f"📉 MAE IMPROVED by {abs(mae_change):.3f} ({abs(mae_pct_change):.1f}%)")
        
        # Elasticity coefficient trend analysis
        if pd.notna(current_week['elasticity_coefficient']) and pd.notna(previous_week['elasticity_coefficient']):
            elasticity_change = current_week['elasticity_coefficient'] - previous_week['elasticity_coefficient']
            elasticity_pct_change = (elasticity_change / abs(previous_week['elasticity_coefficient'])) * 100
            
            if abs(elasticity_pct_change) > (self.performance_thresholds['elasticity_change_alert'] * 100):
                self.logger.warning(f"⚠️ ELASTICITY COEFFICIENT CHANGED by {elasticity_change:.3f} ({elasticity_pct_change:.1f}%)")
        
        # Data volume trends
        if pd.notna(current_week['data_points_training']) and pd.notna(previous_week['data_points_training']):
            data_change = current_week['data_points_training'] - previous_week['data_points_training']
            self.logger.info(f"📊 Training data changed by {data_change:,} rows")
    
    def generate_performance_summary(self):
        """Generate a summary of recent performance trends."""
        if not self.performance_log_file.exists():
            return "No performance data available yet."
        
        try:
            df_log = pd.read_csv(self.performance_log_file)
            
            if len(df_log) == 0:
                return "Performance log is empty."
            
            # Get last 4 weeks for summary
            df_recent = df_log.tail(4)
            
            summary = []
            summary.append("📊 RECENT PERFORMANCE SUMMARY")
            summary.append("=" * 40)
            
            for _, row in df_recent.iterrows():
                week_date = row['week_ending']
                r_squared = row['r_squared'] if pd.notna(row['r_squared']) else 'N/A'
                mae = row['mae'] if pd.notna(row['mae']) else 'N/A'
                elasticity = row['elasticity_coefficient'] if pd.notna(row['elasticity_coefficient']) else 'N/A'
                
                summary.append(f"Week {week_date}:")
                summary.append(f"  R²: {r_squared}")
                summary.append(f"  MAE: {mae}")
                summary.append(f"  Elasticity: {elasticity}")
                summary.append("")
            
            return "\n".join(summary)
            
        except Exception as e:
            return f"Error generating performance summary: {str(e)}"
    
    def export_performance_report(self, output_dir):
        """Export a detailed performance report."""
        if not self.performance_log_file.exists():
            self.logger.warning("⚠️ No performance data to export")
            return False
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Copy performance log
            import shutil
            shutil.copy2(self.performance_log_file, output_path / "performance_log.csv")
            
            # Generate summary report
            summary = self.generate_performance_summary()
            with open(output_path / "performance_summary.txt", 'w') as f:
                f.write(summary)
            
            self.logger.info(f"✅ Performance report exported to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export performance report: {str(e)}")
            return False


def main():
    """Main entry point for standalone testing."""
    tracker = PerformanceTracker()
    
    # Test with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    success = tracker.log_weekly_performance(current_date)
    
    if success:
        print("🎉 Performance tracking test completed!")
        print(tracker.generate_performance_summary())
    else:
        print("💥 Performance tracking test failed!")


if __name__ == "__main__":
    main() 