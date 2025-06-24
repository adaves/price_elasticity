#!/usr/bin/env python3
"""
Output Cleanup Module for Price Elasticity Analysis
Manages output retention and cleanup of old analysis results.
"""

import os
import sys
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class OutputCleaner:
    """Manages cleanup and retention of analysis outputs."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.outputs_dir = self.project_root / "outputs"
        
        # Setup logging
        self.logger = logging.getLogger('OutputCleaner')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def get_dated_output_directories(self):
        """Get all directories with date format (YYYY-MM-DD)."""
        if not self.outputs_dir.exists():
            return []
        
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        dated_dirs = []
        
        for item in self.outputs_dir.iterdir():
            if item.is_dir() and date_pattern.match(item.name):
                try:
                    # Validate it's a proper date
                    date_obj = datetime.strptime(item.name, "%Y-%m-%d")
                    dated_dirs.append((item, date_obj))
                except ValueError:
                    # Skip directories that look like dates but aren't valid
                    continue
        
        # Sort by date (newest first)
        dated_dirs.sort(key=lambda x: x[1], reverse=True)
        return dated_dirs
    
    def calculate_directory_size(self, directory):
        """Calculate total size of a directory in MB."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0
    
    def cleanup_old_outputs(self, keep_weeks=3):
        """Remove output directories older than keep_weeks."""
        try:
            self.logger.info(f"🧹 Starting cleanup - keeping latest {keep_weeks} weeks")
            
            dated_dirs = self.get_dated_output_directories()
            
            if len(dated_dirs) <= keep_weeks:
                self.logger.info(f"✅ Only {len(dated_dirs)} week(s) found - no cleanup needed")
                return True
            
            # Directories to keep (newest)
            dirs_to_keep = dated_dirs[:keep_weeks]
            dirs_to_remove = dated_dirs[keep_weeks:]
            
            self.logger.info(f"📋 Found {len(dated_dirs)} dated directories")
            self.logger.info(f"📋 Keeping {len(dirs_to_keep)} directories")
            self.logger.info(f"📋 Removing {len(dirs_to_remove)} directories")
            
            # Log what we're keeping
            for dir_path, date_obj in dirs_to_keep:
                self.logger.info(f"   ✅ Keeping: {dir_path.name}")
            
            # Remove old directories
            total_freed_mb = 0
            removal_count = 0
            
            for dir_path, date_obj in dirs_to_remove:
                try:
                    # Calculate size before removal
                    size_mb = self.calculate_directory_size(dir_path)
                    
                    # Remove directory
                    shutil.rmtree(dir_path)
                    
                    total_freed_mb += size_mb
                    removal_count += 1
                    
                    self.logger.info(f"   🗑️ Removed: {dir_path.name} ({size_mb:.1f} MB)")
                    
                except Exception as e:
                    self.logger.error(f"   ❌ Failed to remove {dir_path.name}: {str(e)}")
            
            self.logger.info("✅ Cleanup completed successfully!")
            self.logger.info(f"   📊 Removed {removal_count} directories")
            self.logger.info(f"   💾 Freed {total_freed_mb:.1f} MB of disk space")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {str(e)}")
            return False
    
    def cleanup_log_files(self, keep_days=30):
        """Remove log files older than keep_days."""
        try:
            logs_dir = self.outputs_dir / "logs"
            
            if not logs_dir.exists():
                self.logger.info("📋 No logs directory found")
                return True
            
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            removed_count = 0
            freed_mb = 0
            
            for log_file in logs_dir.glob("*.log"):
                try:
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if mod_time < cutoff_date:
                        file_size = log_file.stat().st_size / (1024 * 1024)  # MB
                        log_file.unlink()
                        removed_count += 1
                        freed_mb += file_size
                        self.logger.debug(f"   🗑️ Removed old log: {log_file.name}")
                
                except Exception as e:
                    self.logger.warning(f"   ⚠️ Could not process log file {log_file.name}: {str(e)}")
            
            if removed_count > 0:
                self.logger.info(f"✅ Removed {removed_count} old log files ({freed_mb:.1f} MB)")
            else:
                self.logger.info("📋 No old log files to remove")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Log cleanup failed: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """Remove temporary files and cache directories."""
        try:
            temp_patterns = [
                "**/.ipynb_checkpoints",
                "**/__pycache__",
                "**/*.pyc",
                "**/*.pyo",
                "**/temp_*",
                "**/.DS_Store",
                "**/Thumbs.db"
            ]
            
            removed_count = 0
            
            for pattern in temp_patterns:
                for temp_item in self.outputs_dir.glob(pattern):
                    try:
                        if temp_item.is_file():
                            temp_item.unlink()
                        elif temp_item.is_dir():
                            shutil.rmtree(temp_item)
                        removed_count += 1
                        self.logger.debug(f"   🗑️ Removed temp: {temp_item}")
                    except Exception as e:
                        self.logger.debug(f"   ⚠️ Could not remove {temp_item}: {str(e)}")
            
            if removed_count > 0:
                self.logger.info(f"✅ Removed {removed_count} temporary files/directories")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Temp file cleanup failed: {str(e)}")
            return False
    
    def get_storage_summary(self):
        """Get summary of current storage usage."""
        try:
            dated_dirs = self.get_dated_output_directories()
            
            summary = {
                'total_weeks': len(dated_dirs),
                'total_size_mb': 0,
                'weeks_detail': []
            }
            
            for dir_path, date_obj in dated_dirs:
                size_mb = self.calculate_directory_size(dir_path)
                summary['total_size_mb'] += size_mb
                summary['weeks_detail'].append({
                    'week': dir_path.name,
                    'size_mb': size_mb
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get storage summary: {str(e)}")
            return None
    
    def comprehensive_cleanup(self, keep_weeks=3, keep_log_days=30):
        """Perform comprehensive cleanup of all output types."""
        try:
            self.logger.info("🧹 Starting comprehensive cleanup...")
            
            # Get storage summary before cleanup
            before_summary = self.get_storage_summary()
            
            # Cleanup dated output directories
            success1 = self.cleanup_old_outputs(keep_weeks)
            
            # Cleanup old log files
            success2 = self.cleanup_log_files(keep_log_days)
            
            # Cleanup temporary files
            success3 = self.cleanup_temp_files()
            
            # Get storage summary after cleanup
            after_summary = self.get_storage_summary()
            
            # Report results
            if before_summary and after_summary:
                space_freed = before_summary['total_size_mb'] - after_summary['total_size_mb']
                self.logger.info(f"📊 Storage before cleanup: {before_summary['total_size_mb']:.1f} MB")
                self.logger.info(f"📊 Storage after cleanup: {after_summary['total_size_mb']:.1f} MB")
                self.logger.info(f"📊 Space freed: {space_freed:.1f} MB")
            
            overall_success = success1 and success2 and success3
            
            if overall_success:
                self.logger.info("✅ Comprehensive cleanup completed successfully!")
            else:
                self.logger.warning("⚠️ Some cleanup operations had issues")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive cleanup failed: {str(e)}")
            return False


def cleanup_old_outputs(keep_weeks=3):
    """Main function for output cleanup - called by pipeline orchestrator."""
    cleaner = OutputCleaner()
    return cleaner.comprehensive_cleanup(keep_weeks=keep_weeks)


def main():
    """Main entry point for standalone execution."""
    try:
        cleaner = OutputCleaner()
        
        # Show current storage
        summary = cleaner.get_storage_summary()
        if summary:
            print(f"📊 Current storage: {summary['total_size_mb']:.1f} MB across {summary['total_weeks']} weeks")
        
        # Perform cleanup
        success = cleaner.comprehensive_cleanup(keep_weeks=3)
        
        if success:
            print("🎉 Cleanup completed successfully!")
            sys.exit(0)
        else:
            print("💥 Cleanup failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Critical error in cleanup: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 