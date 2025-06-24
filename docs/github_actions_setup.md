# GitHub Actions Setup Guide

## Current Status: ⚠️ DISABLED 

The GitHub Actions workflow is **currently disabled** because it cannot access the local Access database required for data refresh.

## What Exists

### ✅ Complete Workflow Configuration
- **File**: `.github/workflows/weekly_analysis.yml`
- **Features**: Automated Tuesday runs, artifact storage, error handling, performance tracking
- **Status**: Configured but **scheduled runs disabled**

### 🔧 Automation Features (Ready to Use)
- **Smart data refresh**: Only refreshes if data >6 days old
- **Environment caching**: Faster runs with dependency caching  
- **Results archival**: Saves outputs for 30 days, logs for 7 days
- **Error reporting**: Creates GitHub issues on failures
- **Performance tracking**: Logs execution metrics
- **Cleanup automation**: Removes old outputs

## ❌ Current Blocker: Database Access

### The Problem
```python
# In scripts/data_refresh.py line 29-30:
self.db_path = r"C:\Users\adaves\Thai Union Group\COSI - Sales Planning Team - General\Sales Toolbox 2020 - IRI.accdb"
```

**GitHub Actions runs in the cloud** and cannot access:
- ❌ Your local OneDrive files
- ❌ Thai Union Group network drives  
- ❌ Your computer's C: drive

## 🔧 Solutions to Enable GitHub Actions

### Option 1: Use Cloud Database (Recommended)
- **Action**: Migrate Access database to Azure SQL, AWS RDS, or similar
- **Pros**: Scalable, accessible from anywhere, better performance
- **Setup**: Requires IT support to host database in cloud

### Option 2: Self-Hosted Runner (Advanced)
- **Action**: Configure your computer as a GitHub Actions runner
- **Pros**: Can access local files
- **Cons**: Requires your computer to be always on
- **Setup**:
  ```bash
  # Download runner from GitHub repository settings
  # Register runner with your organization
  # Run as Windows service
  ```

### Option 3: Manual Data Upload (Workaround)
- **Action**: Manually upload parquet files to repository
- **Pros**: Simple, works immediately
- **Cons**: Manual process, large files in git

### Option 4: Keep Local-Only (Current Setup)
- **Action**: Continue running pipeline locally
- **Pros**: No additional setup required
- **Use**: Run `python scripts/run_pipeline.py` weekly

## 🎯 Recommended Approach

**For now**: Keep the current local setup since it works perfectly.

**For future**: Consider Option 1 (cloud database) if you want true automation.

## 💡 Manual Trigger Option

Even without scheduled runs, you can still:
1. **Push to GitHub**: Your code and workflow are version controlled
2. **Manual trigger**: Run workflow manually if database access is configured
3. **Documentation**: The workflow serves as excellent documentation

## ⚡ Quick Enable (When Ready)

When database access is configured, simply uncomment lines 5-9 in `.github/workflows/weekly_analysis.yml`:

```yaml
schedule:
  # Primary run: Tuesday 9 AM CST (4 PM UTC)
  - cron: '0 16 * * 2'
  # Backup run: Tuesday 3 PM CST (10 PM UTC)  
  - cron: '0 22 * * 2'
```

## 📊 Current Working Setup

Your **local automation** is excellent:
- ✅ Complete pipeline: `scripts/run_pipeline.py`
- ✅ Performance tracking: `scripts/performance_tracker.py`
- ✅ Cleanup automation: `scripts/cleanup_outputs.py`
- ✅ Data refresh: `scripts/data_refresh.py`

**No action required** - your automation works perfectly locally! 