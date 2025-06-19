# Data Dictionary - Price Elasticity Analysis

## 📊 Overview
This document defines all data fields, sources, and transformations used in the price elasticity analysis.

## 🗂️ Raw Data Sources

### Primary Sales Data
| Field Name | Type | Description | Source | Example |
|------------|------|-------------|---------|---------|
| `date` | Date | Transaction date | Sales System | 2024-01-15 |
| `product_id` | String | Unique product identifier | Product Master | TU_CT_001 |
| `product_name` | String | Product name | Product Master | Tuna Chunks in Oil 185g |
| `category` | String | Product category | Product Master | Canned Tuna |
| `brand` | String | Brand name | Product Master | Chicken of the Sea |
| `unit_price` | Float | Price per unit (THB) | Sales System | 45.50 |
| `quantity_sold` | Integer | Units sold | Sales System | 1250 |
| `revenue` | Float | Total revenue (THB) | Calculated | 56,875.00 |
| `store_id` | String | Store identifier | Store Master | ST_001 |
| `region` | String | Geographic region | Store Master | Bangkok |

### External Data (Optional)
| Field Name | Type | Description | Source | Example |
|------------|------|-------------|---------|---------|
| `competitor_price` | Float | Competitor pricing | Market Research | 48.00 |
| `promotion_flag` | Boolean | Promotion indicator | Marketing | True |
| `economic_index` | Float | Economic indicator | Government | 102.5 |

## 🔧 Processed Features

### Time-based Features
| Field Name | Type | Description | Calculation |
|------------|------|-------------|-------------|
| `year` | Integer | Year | Extract from date |
| `month` | Integer | Month (1-12) | Extract from date |
| `day_of_week` | Integer | Day of week (1-7) | Extract from date |
| `week_of_year` | Integer | Week number | Extract from date |
| `is_weekend` | Boolean | Weekend indicator | day_of_week in [6,7] |
| `is_holiday` | Boolean | Holiday indicator | Holiday calendar lookup |

### Price Features
| Field Name | Type | Description | Calculation |
|------------|------|-------------|-------------|
| `log_price` | Float | Natural log of price | ln(unit_price) |
| `price_lag_1` | Float | Price 1 period ago | Lag(unit_price, 1) |
| `price_lag_7` | Float | Price 7 periods ago | Lag(unit_price, 7) |
| `price_change` | Float | Price change from previous | unit_price - price_lag_1 |
| `price_change_pct` | Float | Percentage price change | (price_change / price_lag_1) × 100 |
| `price_ma_7` | Float | 7-day moving average | Rolling mean(unit_price, 7) |
| `price_ma_30` | Float | 30-day moving average | Rolling mean(unit_price, 30) |

### Demand Features
| Field Name | Type | Description | Calculation |
|------------|------|-------------|-------------|
| `log_quantity` | Float | Natural log of quantity | ln(quantity_sold) |
| `quantity_lag_1` | Float | Quantity 1 period ago | Lag(quantity_sold, 1) |
| `quantity_lag_7` | Float | Quantity 7 periods ago | Lag(quantity_sold, 7) |
| `quantity_ma_7` | Float | 7-day moving average | Rolling mean(quantity_sold, 7) |
| `quantity_ma_30` | Float | 30-day moving average | Rolling mean(quantity_sold, 30) |
| `demand_volatility` | Float | Demand volatility | Rolling std(quantity_sold, 30) |

### Business Features
| Field Name | Type | Description | Calculation |
|------------|------|-------------|-------------|
| `revenue_per_unit` | Float | Revenue per unit | revenue / quantity_sold |
| `market_share` | Float | Product market share | quantity_sold / total_category_quantity |
| `relative_price` | Float | Price vs category average | unit_price / avg_category_price |
| `price_rank` | Integer | Price ranking in category | Rank by price within category |

## 🎯 Target Variables

### Primary Targets
| Field Name | Type | Description | Business Meaning |
|------------|------|-------------|------------------|
| `price_elasticity` | Float | Elasticity coefficient | % change in demand per % change in price |
| `demand_forecast` | Integer | Predicted quantity | Forecasted units for next period |
| `revenue_impact` | Float | Revenue change | Expected revenue change from price change |

## 📏 Data Quality Rules

### Validation Rules
| Field | Rule | Action |
|-------|------|--------|
| `unit_price` | > 0 and < 1000 | Flag outliers |
| `quantity_sold` | >= 0 and < 10000 | Flag outliers |
| `date` | Within analysis period | Exclude |
| `product_id` | Not null | Exclude |
| `category` | In approved list | Flag for review |

### Missing Data Handling
| Field | Strategy | Justification |
|-------|----------|---------------|
| `unit_price` | Forward fill | Prices don't change daily |
| `quantity_sold` | Set to 0 | No sales = zero quantity |
| `competitor_price` | Interpolate | Gradual price changes |
| `promotion_flag` | Set to False | Conservative assumption |

## 📊 Business Definitions

### Product Categories
- **Canned Tuna**: All canned tuna products
- **Canned Salmon**: All canned salmon products  
- **Pet Food**: Pet food products
- **Frozen Seafood**: Frozen seafood items

### Time Periods
- **Analysis Period**: [Define specific dates]
- **Training Period**: [Define training window]
- **Validation Period**: [Define validation window]
- **Forecast Horizon**: [Define forecast period]

### Business Metrics
- **Price Elasticity**: Economic responsiveness measure
- **Cross-Price Elasticity**: Response to competitor prices
- **Revenue Elasticity**: Revenue response to price changes

## 🔄 Data Updates
- **Frequency**: Daily/Weekly
- **Source System**: [Specify system]
- **Update Process**: [Define ETL process]
- **Data Validation**: Automated quality checks

## 📝 Notes
- All monetary values in Thai Baht (THB)
- All dates in YYYY-MM-DD format
- Null values handled according to business rules
- Historical data available from [start date] to [end date] 