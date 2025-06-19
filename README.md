# Price Elasticity Analysis Project

## 📊 Project Overview
This project analyzes price elasticity for Thai Union Group products to understand how demand responds to price changes. This analysis will help inform pricing strategies and revenue optimization decisions.

## 🎯 Business Objective
- Understand price sensitivity across different product categories
- Identify optimal pricing strategies
- Quantify demand response to price changes
- Provide actionable insights for pricing decisions

## 📁 Project Structure
```
elasticity/
├── notebooks/          # Analysis notebooks (run in sequence)
├── src/utils/          # Helper functions for notebooks
├── data/               # Data storage (raw, processed, sample)
├── outputs/            # Analysis outputs (figures, models, reports)
├── docs/               # Documentation and methodology
└── configs/            # Configuration files
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Jupyter Lab/Notebook
- Required packages (see requirements.txt)

### Installation
1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch Jupyter Lab:
   ```bash
   jupyter lab
   ```

## 📓 Notebook Execution Order
Run the notebooks in the following sequence:

1. **01_data_loading.ipynb** - Load and inspect raw data
2. **02_data_cleaning.ipynb** - Clean and preprocess data
3. **03_eda.ipynb** - Exploratory data analysis
4. **04_feature_engineering.ipynb** - Create features for modeling
5. **05_modeling.ipynb** - Build price elasticity models
6. **06_evaluation.ipynb** - Evaluate model performance
7. **07_visualization.ipynb** - Create business-ready visualizations

## 📈 Key Deliverables
- Price elasticity coefficients by product category
- Demand forecasting models
- Pricing optimization recommendations
- Executive summary with actionable insights

## 📋 Progress Tracking
See `scratchpad.md` for detailed progress tracking and project notes.

## 📚 Documentation
- `docs/methodology.md` - Analysis methodology and theory
- `docs/data_dictionary.md` - Data definitions and sources
- `docs/lessons_learned.md` - Project learnings and best practices

## 👤 Contact
**Data Scientist**: [Your Name]  
**Email**: [Your Email]  
**Department**: Thai Union Group  
**Project Start**: [Date]

## 📄 License
Internal use only - Thai Union Group proprietary analysis 