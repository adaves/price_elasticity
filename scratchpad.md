# Price Elasticity Analysis - Project Scratchpad

## 📝 Project Context
- **Start Date**: 6.19.2025
- **Employer**: Thai Union Group
- **Project Type**: Price Elasticity Analysis
- **Project Goal**: Analyze price elasticity for Thai Union products to optimize pricing strategies
- **Business Question**: How does demand respond to price changes across different product categories?
- **Success Metrics**: 
  - Accurate elasticity coefficients (R² > 0.7) --> ???
  - Actionable pricing recommendations
  - Clear business insights presentation

## 📊 Data Information
- **Data Sources**: Sales Toolbox 2020 - IRI (Access Database)
- **Database Path**: `C:\Users\adaves\Thai Union Group\COSI - Sales Planning Team - General\Sales Toolbox 2020 - IRI.accdb`
- **Table**: `tblIRI2` (1,960,393 rows, 36 columns)
- **Time Period**: Weekly data from 12/31/2023 to recent weeks
- **Data Format**: Extracted to Parquet (100.8 MB) for analysis
- **Product Categories**: Tuna products (Chicken of the Sea, StarKist, Ace of Diamonds, etc.)
- **Key Variables**: Unit Sales, Price per Unit, Dollar Sales, Volume Sales, Distribution metrics

## ⚡ Critical Project Steps
*[Essential steps to maintain code quality and alignment]*

### 🔍 Codebase Management
- [x] **Index codebase structure** - Comprehensive review of all modules, functions, and capabilities
- [x] **Validate utility function alignment** - Ensure all helper functions match actual data structure and requirements
- [x] **Update function defaults** - Modify default parameters to reflect real data column names and formats
- [x] **Document data-specific modifications** - Track any project-specific adaptations for future reference

### 📋 Quality Assurance Checklist
- [x] All utility functions tested with actual data structure
- [x] Column name mappings verified and documented
- [x] Date parsing functions handle actual format
- [ ] Error handling covers discovered edge cases

## 🎯 Progress Tracking

### Phase 1: Project Setup & Data Loading (Week 1) ✅ COMPLETE
- [x] Environment setup and dependencies installation (pyodbc, pyarrow)
- [x] Data source identification and access (Access database connection)
- [x] Initial data loading and format assessment (Parquet extraction successful)
- [x] Data quality preliminary assessment (1.96M rows, 36 columns, 100.8MB)
- [ ] Stakeholder alignment on scope

**Notes**: 
- Successfully extracted 1,960,393 rows from Access database `tblIRI2`
- Data saved as `data/raw/iri_sales_data.parquet` (100.8 MB)
- Extraction completed in 265.8 seconds
- 86 geographic regions, 3,575 unique products, 180 time periods
- Weekly transaction data for tuna products (Chicken of the Sea, StarKist, etc.)
- **CODEBASE INDEXED**: Comprehensive review of all 19 utility functions completed
- **UTILITY FUNCTIONS UPDATED**: Modified default column names to match IRI data structure
- **NEW FUNCTIONS ADDED**: `parse_iri_time_column()` and `standardize_iri_columns()`

### Phase 2: Data Cleaning & EDA (Week 1-2)
- [ ] Data cleaning pipeline development
- [ ] Missing data analysis and handling strategy
- [ ] Outlier detection and treatment
- [ ] Exploratory data analysis
- [ ] Initial insights documentation
- [ ] Data validation and quality checks

**Notes**: 
- 

### Phase 3: Feature Engineering & Modeling (Week 2-3)
- [ ] Price elasticity feature creation
- [ ] Seasonality and trend analysis
- [ ] Model selection and justification
- [ ] Initial model training
- [ ] Cross-validation setup
- [ ] Hyperparameter tuning

**Notes**: 
- 

### Phase 4: Evaluation & Visualization (Week 3-4)
- [ ] Model performance evaluation
- [ ] Business metrics calculation
- [ ] Results visualization creation
- [ ] Executive summary preparation
- [ ] Stakeholder presentation prep
- [ ] Documentation finalization

**Notes**: 
- 

## 🔍 Key Findings
*[Update this section as the project progresses]*

### Data Insights
- **Scale**: 1.96M weekly transaction records across 86 geographic regions
- **Products**: 3,575 unique tuna products (Chicken of the Sea, StarKist, Ace of Diamonds)
- **Price Range**: $0.10 to $137.46 per unit (significant variety in product sizes/types)
- **Average Unit Sales**: 4,246 units per week (highly variable: std=31,494)
- **Key Columns**: Unit Sales, Price per Unit, Dollar Sales, Volume Sales, Distribution metrics
- **Time Coverage**: 180 time periods (weekly data from late 2023 onwards)

### Model Performance
- TBD (modeling phase not started)

### Business Insights
- High variability in sales volumes suggests different product categories/market segments
- Price elasticity analysis will be critical given wide price range ($0.10-$137.46)
- Geographic coverage (86 regions) allows for regional elasticity comparisons

## 🚧 Challenges & Solutions
*[Document obstacles and how they were overcome]*

### Challenge 1: [Description]
**Solution**: 

### Challenge 2: [Description]
**Solution**: 

## 📋 Next Steps
*[Always maintain a prioritized list of immediate next actions]*

1. **Execute `02_data_cleaning.ipynb`** - Clean and preprocess the extracted data using updated utility functions
2. **Test IRI-specific functions** - Validate `parse_iri_time_column()` and `standardize_iri_columns()` with real data
3. **Data quality analysis** - Handle missing values, outliers, and data validation
4. **Run `03_eda.ipynb`** - Perform exploratory data analysis on clean data
5. **Identify product categories** - Group products for category-level elasticity analysis
6. **Feature engineering** - Create time-based and lag features for modeling

## 💡 Ideas & Hypotheses
*[Capture ideas for testing or future exploration]*

- 
- 
- 

## 📚 Resources & References
*[Links to helpful materials, tutorials, company docs]*

### Learning Resources
- [Price Elasticity Theory](https://en.wikipedia.org/wiki/Price_elasticity_of_demand)
- [Econometrics for Data Science](link)
- 

### Company Resources
- 
- 

### Technical Resources
- 
- 

## 🎯 Stakeholder Information
- **Primary Stakeholder**: [Name, Role]
- **Secondary Stakeholders**: [Names, Roles]
- **Reporting Schedule**: [Frequency and format]
- **Presentation Date**: [Target date for final presentation]

## ⚠️ Important Notes
*[Critical information to remember]*

- 
- 
- 

---
**Last Updated**: June 19, 2025  
**Project Status**: In Progress - Data Loading Complete, Moving to Data Cleaning 