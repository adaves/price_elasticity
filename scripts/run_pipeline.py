#!/usr/bin/env python3
"""
Main Pipeline Orchestrator for Price Elasticity Analysis
Runs all 7 notebooks in sequence with comprehensive error handling and logging.
"""

import os
import sys
import subprocess
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
import json
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.data_refresh import refresh_data_and_notebooks
from scripts.performance_tracker import PerformanceTracker
from scripts.cleanup_outputs import cleanup_old_outputs

class PipelineOrchestrator:
    """Orchestrates the complete elasticity analysis pipeline."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.notebooks_dir = self.project_root / "notebooks"
        self.outputs_dir = self.project_root / "outputs"
        self.logs_dir = self.outputs_dir / "logs"
        
        # Create directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Get current week date
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.week_output_dir = self.outputs_dir / self.current_date
        
        # Performance tracker
        self.performance_tracker = PerformanceTracker()
        
        self.logger.info(f"Pipeline initialized for week ending: {self.current_date}")
    
    def setup_logging(self):
        """Configure comprehensive logging."""
        log_file = self.logs_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger('PipelineOrchestrator')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
        
        self.logger.info(f"Logging initialized. Log file: {log_file}")
    
    def run_notebook(self, notebook_name):
        """Execute a single notebook with error handling."""
        notebook_path = self.notebooks_dir / notebook_name
        
        if not notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")
        
        self.logger.info(f"Starting execution: {notebook_name}")
        start_time = time.time()
        
        try:
            # Execute notebook using nbconvert
            cmd = [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--inplace",
                "--ExecutePreprocessor.timeout=3600",  # 1 hour timeout
                str(notebook_path)
            ]
            
            # Change to notebooks directory for execution
            result = subprocess.run(
                cmd,
                cwd=self.notebooks_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            execution_time = time.time() - start_time
            self.logger.info(f"✅ Completed: {notebook_name} ({execution_time:.1f}s)")
            
            return {
                'notebook': notebook_name,
                'status': 'success',
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            execution_time = time.time() - start_time
            error_msg = f"❌ Failed: {notebook_name} ({execution_time:.1f}s)"
            self.logger.error(error_msg)
            self.logger.error(f"Return code: {e.returncode}")
            self.logger.error(f"STDOUT: {e.stdout}")
            self.logger.error(f"STDERR: {e.stderr}")
            
            return {
                'notebook': notebook_name,
                'status': 'failed',
                'execution_time': execution_time,
                'error': str(e),
                'stdout': e.stdout,
                'stderr': e.stderr,
                'return_code': e.returncode
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"❌ Exception in {notebook_name}: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return {
                'notebook': notebook_name,
                'status': 'error',
                'execution_time': execution_time,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def run_complete_pipeline(self):
        """Execute the complete 7-notebook pipeline."""
        pipeline_start = time.time()
        
        # Notebook execution order
        notebooks = [
            "01_data_loading.ipynb",
            "02_data_cleaning.ipynb", 
            "03_eda.ipynb",
            "04_feature_engineering.ipynb",
            "05_modeling.ipynb",
            "06_evaluation.ipynb",
            "07_visualization.ipynb"
        ]
        
        results = []
        failed_notebooks = []
        
        self.logger.info("🚀 Starting complete pipeline execution")
        self.logger.info(f"📋 Notebooks to execute: {len(notebooks)}")
        
        # Execute each notebook in sequence
        for i, notebook in enumerate(notebooks, 1):
            self.logger.info(f"📓 Step {i}/{len(notebooks)}: {notebook}")
            
            result = self.run_notebook(notebook)
            results.append(result)
            
            if result['status'] != 'success':
                failed_notebooks.append(notebook)
                self.logger.error(f"⚠️ Pipeline failure at step {i}")
                break  # Stop on first failure
        
        # Calculate total time
        total_time = time.time() - pipeline_start
        
        # Create summary
        summary = {
            'pipeline_date': self.current_date,
            'total_execution_time': total_time,
            'notebooks_attempted': len(results),
            'notebooks_succeeded': len([r for r in results if r['status'] == 'success']),
            'notebooks_failed': len(failed_notebooks),
            'failed_notebooks': failed_notebooks,
            'detailed_results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save execution summary
        summary_file = self.week_output_dir / "execution_summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Log final results
        if failed_notebooks:
            self.logger.error(f"❌ Pipeline FAILED after {total_time:.1f}s")
            self.logger.error(f"Failed notebooks: {failed_notebooks}")
            return False, summary
        else:
            self.logger.info(f"✅ Pipeline COMPLETED successfully in {total_time:.1f}s")
            return True, summary
    
    def run_full_workflow(self):
        """Run the complete weekly workflow."""
        workflow_start = time.time()
        
        try:
            self.logger.info("=" * 60)
            self.logger.info("🏁 STARTING WEEKLY ELASTICITY ANALYSIS WORKFLOW")
            self.logger.info("=" * 60)
            
            # Step 1: Data refresh
            self.logger.info("📊 Step 1: Refreshing data and updating notebooks...")
            data_success = refresh_data_and_notebooks()
            if not data_success:
                raise Exception("Data refresh failed")
            
            # Step 2: Execute pipeline
            self.logger.info("⚙️ Step 2: Executing analysis pipeline...")
            pipeline_success, summary = self.run_complete_pipeline()
            if not pipeline_success:
                raise Exception("Pipeline execution failed")
            
            # Step 3: Track performance (if modeling completed)
            if summary['notebooks_succeeded'] >= 6:  # At least through evaluation
                self.logger.info("📈 Step 3: Tracking model performance...")
                self.performance_tracker.log_weekly_performance(self.current_date)
            
            # Step 4: Cleanup old outputs
            self.logger.info("🧹 Step 4: Cleaning up old outputs...")
            cleanup_old_outputs(keep_weeks=3)
            
            # Step 5: Create 'latest' symlink
            self.logger.info("🔗 Step 5: Updating latest results...")
            self.create_latest_symlink()
            
            total_time = time.time() - workflow_start
            
            self.logger.info("=" * 60)
            self.logger.info(f"✅ WORKFLOW COMPLETED SUCCESSFULLY in {total_time:.1f}s")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            total_time = time.time() - workflow_start
            self.logger.error("=" * 60)
            self.logger.error(f"❌ WORKFLOW FAILED after {total_time:.1f}s")
            self.logger.error(f"Error: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.logger.error("=" * 60)
            
            # Re-raise for GitHub Actions to catch
            raise
    
    def create_latest_symlink(self):
        """Create/update symlink to latest results."""
        latest_dir = self.outputs_dir / "latest"
        
        # Remove existing symlink
        if latest_dir.exists() or latest_dir.is_symlink():
            if latest_dir.is_symlink():
                latest_dir.unlink()
            else:
                import shutil
                shutil.rmtree(latest_dir)
        
        # Create new symlink (Windows compatible)
        try:
            # Try symbolic link first
            latest_dir.symlink_to(self.week_output_dir, target_is_directory=True)
        except OSError:
            # Fallback to copying on Windows
            import shutil
            shutil.copytree(self.week_output_dir, latest_dir)
        
        self.logger.info(f"✅ Latest results linked to: {self.week_output_dir}")


def main():
    """Main entry point for pipeline execution."""
    try:
        orchestrator = PipelineOrchestrator()
        success = orchestrator.run_full_workflow()
        
        if success:
            print("🎉 Weekly elasticity analysis completed successfully!")
            sys.exit(0)
        else:
            print("💥 Weekly elasticity analysis failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Critical error in pipeline: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main() 