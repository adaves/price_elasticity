# Price Elasticity Analysis Methodology

## 📊 Overview
This document outlines the methodology for analyzing price elasticity of demand for Thai Union Group products. Price elasticity measures how responsive quantity demanded is to changes in price.

## 🎯 Theoretical Foundation

### Price Elasticity of Demand (PED)
Price elasticity of demand is calculated as:

```
PED = (% Change in Quantity Demanded) / (% Change in Price)
```

Or in mathematical terms:
```
PED = (ΔQ/Q) / (ΔP/P) = (ΔQ/ΔP) × (P/Q)
```

### Interpretation
- **Elastic (PED < -1)**: Demand is sensitive to price changes
- **Inelastic (-1 < PED < 0)**: Demand is relatively insensitive to price changes
- **Unitary Elastic (PED = -1)**: Proportional response to price changes

## 🔬 Analysis Approach

### 1. Data Preparation
- **Historical Data**: Price and quantity data over time
- **Time Series**: Daily/weekly/monthly granularity
- **Product Segmentation**: Category-level analysis
- **External Factors**: Seasonality, promotions, competitors

### 2. Feature Engineering
- **Lag Variables**: Price and demand lags to capture delayed responses
- **Rolling Averages**: Smooth short-term fluctuations
- **Seasonality Components**: Weekly, monthly, yearly patterns
- **Price Change Indicators**: Magnitude and direction of changes

### 3. Modeling Approaches

#### Linear Regression
Basic elasticity model:
```
log(Quantity) = β₀ + β₁ × log(Price) + β₂ × Controls + ε
```
Where β₁ represents the price elasticity coefficient.

#### Time Series Models
- **ARIMA**: Autoregressive Integrated Moving Average
- **Vector Autoregression (VAR)**: Multiple time series
- **Error Correction Models**: Long-run relationships

#### Machine Learning Models
- **Random Forest**: Non-linear relationships
- **Gradient Boosting**: Complex interactions
- **Ridge/Lasso**: Regularized linear models

### 4. Validation Strategy
- **Time-based Cross-validation**: Respect temporal order
- **Out-of-sample Testing**: Future period validation
- **Robustness Checks**: Different time periods and specifications

## 📈 Business Applications

### Pricing Strategy
- **Optimal Pricing**: Maximize revenue using elasticity insights
- **Price Sensitivity**: Identify products with pricing flexibility
- **Competitive Response**: Understand market dynamics

### Revenue Optimization
- **Demand Forecasting**: Predict quantity changes
- **Scenario Analysis**: Impact of different pricing strategies
- **Portfolio Management**: Balance elastic and inelastic products

## 🎯 Success Criteria

### Statistical Criteria
- **Model Fit**: R² > 0.7 for primary models
- **Significance**: p-values < 0.05 for key coefficients
- **Stability**: Consistent results across time periods

### Business Criteria
- **Actionable Insights**: Clear pricing recommendations
- **Economic Significance**: Meaningful impact on revenue
- **Practical Implementation**: Feasible pricing changes

## ⚠️ Limitations and Assumptions

### Assumptions
- **Ceteris Paribus**: Other factors remain constant
- **Linear Relationships**: Log-linear demand function
- **Representative Data**: Historical patterns continue

### Limitations
- **External Shocks**: Economic events, pandemics
- **Competitive Response**: Competitor price changes
- **Consumer Behavior**: Changing preferences over time

## 📚 References
- Varian, H.R. (2014). Intermediate Microeconomics
- Wooldridge, J.M. (2015). Introductory Econometrics
- Company-specific pricing research and guidelines 