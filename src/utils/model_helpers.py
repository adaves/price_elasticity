"""
Model helper functions for price elasticity analysis.

This module contains utility functions for model training,
evaluation, and elasticity calculations.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


def calculate_price_elasticity(df: pd.DataFrame,
                             price_column: str = 'Price per Unit',
                             quantity_column: str = 'Unit Sales',
                             group_column: Optional[str] = None) -> pd.DataFrame:
    """
    Calculate price elasticity using log-log regression.
    
    Args:
        df (pd.DataFrame): Input dataframe
        price_column (str): Price column name
        quantity_column (str): Quantity column name
        group_column (str, optional): Column to group by
        
    Returns:
        pd.DataFrame: Elasticity results
    """
    # Prepare data with log transformation
    df_calc = df.copy()
    df_calc = df_calc[(df_calc[price_column] > 0) & (df_calc[quantity_column] > 0)]
    df_calc['log_price'] = np.log(df_calc[price_column])
    df_calc['log_quantity'] = np.log(df_calc[quantity_column])
    
    results = []
    
    if group_column:
        for group in df_calc[group_column].unique():
            group_data = df_calc[df_calc[group_column] == group]
            if len(group_data) > 10:  # Minimum observations
                elasticity = _calculate_elasticity_for_group(group_data)
                elasticity['group'] = group
                results.append(elasticity)
    else:
        elasticity = _calculate_elasticity_for_group(df_calc)
        elasticity['group'] = 'Overall'
        results.append(elasticity)
    
    return pd.DataFrame(results)


def _calculate_elasticity_for_group(df: pd.DataFrame) -> Dict:
    """Calculate elasticity for a single group."""
    try:
        X = df[['log_price']]
        y = df['log_quantity']
        
        model = LinearRegression()
        model.fit(X, y)
        
        y_pred = model.predict(X)
        
        return {
            'price_elasticity': model.coef_[0],
            'r_squared': r2_score(y, y_pred),
            'observations': len(df),
            'mean_price': df['Price per Unit'].mean(),
            'mean_quantity': df['Unit Sales'].mean()
        }
    except Exception as e:
        logger.error(f"Error calculating elasticity: {e}")
        return {
            'price_elasticity': np.nan,
            'r_squared': np.nan,
            'observations': len(df),
            'mean_price': df['Price per Unit'].mean() if 'Price per Unit' in df.columns else np.nan,
            'mean_quantity': df['Unit Sales'].mean() if 'Unit Sales' in df.columns else np.nan
        }


def prepare_features_for_modeling(df: pd.DataFrame,
                                target_column: str,
                                feature_columns: List[str],
                                scale_features: bool = True) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
    """
    Prepare features and target for modeling.
    
    Args:
        df (pd.DataFrame): Input dataframe
        target_column (str): Target variable column
        feature_columns (List[str]): Feature columns
        scale_features (bool): Whether to scale features
        
    Returns:
        tuple: (X, y, scaler)
    """
    # Remove rows with missing values
    df_clean = df[feature_columns + [target_column]].dropna()
    
    X = df_clean[feature_columns].values
    y = df_clean[target_column].values
    
    scaler = None
    if scale_features:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
    
    logger.info(f"Prepared {X.shape[0]} samples with {X.shape[1]} features")
    return X, y, scaler


def train_multiple_models(X: np.ndarray, 
                         y: np.ndarray,
                         test_size: float = 0.2,
                         random_state: int = 42) -> Dict[str, Dict]:
    """
    Train multiple regression models and compare performance.
    
    Args:
        X (np.ndarray): Feature matrix
        y (np.ndarray): Target vector
        test_size (float): Test set proportion
        random_state (int): Random seed
        
    Returns:
        Dict: Model results
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Define models
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Lasso Regression': Lasso(alpha=1.0),
        'Elastic Net': ElasticNet(alpha=1.0, l1_ratio=0.5),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=random_state),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=random_state)
    }
    
    results = {}
    
    for name, model in models.items():
        try:
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # Calculate metrics
            results[name] = {
                'model': model,
                'train_r2': r2_score(y_train, y_train_pred),
                'test_r2': r2_score(y_test, y_test_pred),
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
                'train_mae': mean_absolute_error(y_train, y_train_pred),
                'test_mae': mean_absolute_error(y_test, y_test_pred)
            }
            
        except Exception as e:
            logger.error(f"Error training {name}: {e}")
            results[name] = {'error': str(e)}
    
    return results


def perform_cross_validation(X: np.ndarray,
                           y: np.ndarray,
                           model: Any,
                           cv_folds: int = 5,
                           scoring: str = 'r2') -> Dict:
    """
    Perform cross-validation for model evaluation.
    
    Args:
        X (np.ndarray): Feature matrix
        y (np.ndarray): Target vector
        model: Sklearn model
        cv_folds (int): Number of CV folds
        scoring (str): Scoring metric
        
    Returns:
        Dict: CV results
    """
    cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring)
    
    return {
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'cv_scores': cv_scores.tolist()
    }


def time_series_cross_validation(df: pd.DataFrame,
                               feature_columns: List[str],
                               target_column: str,
                               date_column: str,
                               model: Any,
                               n_splits: int = 5) -> Dict:
    """
    Perform time series cross-validation.
    
    Args:
        df (pd.DataFrame): Input dataframe
        feature_columns (List[str]): Feature columns
        target_column (str): Target column
        date_column (str): Date column
        model: Sklearn model
        n_splits (int): Number of splits
        
    Returns:
        Dict: Time series CV results
    """
    # Sort by date
    df_sorted = df.sort_values(date_column)
    
    X = df_sorted[feature_columns].values
    y = df_sorted[target_column].values
    
    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_scores = []
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        score = r2_score(y_test, y_pred)
        cv_scores.append(score)
    
    return {
        'ts_cv_mean': np.mean(cv_scores),
        'ts_cv_std': np.std(cv_scores),
        'ts_cv_scores': cv_scores
    }


def calculate_feature_importance(model: Any,
                               feature_names: List[str]) -> pd.DataFrame:
    """
    Calculate and return feature importance.
    
    Args:
        model: Trained sklearn model
        feature_names (List[str]): Feature names
        
    Returns:
        pd.DataFrame: Feature importance dataframe
    """
    if hasattr(model, 'feature_importances_'):
        # Tree-based models
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        # Linear models
        importance = np.abs(model.coef_)
    else:
        logger.warning("Model does not have feature importance")
        return pd.DataFrame()
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    return importance_df


def predict_demand_change(elasticity: float,
                        price_change_pct: float,
                        current_demand: float) -> Dict:
    """
    Predict demand change based on price elasticity.
    
    Args:
        elasticity (float): Price elasticity coefficient
        price_change_pct (float): Price change percentage
        current_demand (float): Current demand level
        
    Returns:
        Dict: Demand change predictions
    """
    # Calculate percentage change in demand
    demand_change_pct = elasticity * price_change_pct
    
    # Calculate new demand level
    new_demand = current_demand * (1 + demand_change_pct / 100)
    
    return {
        'current_demand': current_demand,
        'price_change_pct': price_change_pct,
        'demand_change_pct': demand_change_pct,
        'new_demand': new_demand,
        'demand_difference': new_demand - current_demand
    }


def optimize_price_for_revenue(elasticity: float,
                             current_price: float,
                             current_demand: float,
                             price_bounds: Tuple[float, float] = (0.5, 2.0)) -> Dict:
    """
    Find optimal price for revenue maximization.
    
    Args:
        elasticity (float): Price elasticity coefficient
        current_price (float): Current price
        current_demand (float): Current demand
        price_bounds (tuple): Price multiplier bounds
        
    Returns:
        Dict: Optimization results
    """
    # Revenue function: R = P * Q = P * Q0 * (P/P0)^elasticity
    # For revenue maximization: dR/dP = 0
    # Optimal price multiplier = -1 / (elasticity + 1)
    
    if elasticity >= -1:
        logger.warning("Elasticity >= -1, revenue increases with price")
        optimal_multiplier = price_bounds[1]  # Maximum allowed
    else:
        optimal_multiplier = -1 / (elasticity + 1)
        optimal_multiplier = np.clip(optimal_multiplier, price_bounds[0], price_bounds[1])
    
    optimal_price = current_price * optimal_multiplier
    price_change_pct = (optimal_multiplier - 1) * 100
    
    demand_prediction = predict_demand_change(
        elasticity, price_change_pct, current_demand
    )
    
    current_revenue = current_price * current_demand
    optimal_revenue = optimal_price * demand_prediction['new_demand']
    revenue_change_pct = (optimal_revenue / current_revenue - 1) * 100
    
    return {
        'current_price': current_price,
        'optimal_price': optimal_price,
        'price_change_pct': price_change_pct,
        'current_revenue': current_revenue,
        'optimal_revenue': optimal_revenue,
        'revenue_change_pct': revenue_change_pct,
        'demand_prediction': demand_prediction
    }


def create_model_summary(model_results: Dict) -> pd.DataFrame:
    """
    Create summary dataframe of model results.
    
    Args:
        model_results (Dict): Results from train_multiple_models
        
    Returns:
        pd.DataFrame: Summary dataframe
    """
    summary_data = []
    
    for model_name, results in model_results.items():
        if 'error' not in results:
            summary_data.append({
                'model': model_name,
                'train_r2': results['train_r2'],
                'test_r2': results['test_r2'],
                'train_rmse': results['train_rmse'],
                'test_rmse': results['test_rmse'],
                'overfitting': results['train_r2'] - results['test_r2']
            })
    
    return pd.DataFrame(summary_data).sort_values('test_r2', ascending=False) 