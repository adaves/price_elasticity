"""
Plotting helper functions for price elasticity analysis.

This module contains utility functions for creating consistent
visualizations across the analysis notebooks.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Set default style
plt.style.use('default')
sns.set_palette("husl")


def setup_plot_style(style: str = "whitegrid", 
                    palette: str = "husl",
                    figsize: Tuple[int, int] = (12, 8),
                    dpi: int = 100) -> None:
    """
    Set up consistent plotting style.
    
    Args:
        style (str): Seaborn style
        palette (str): Color palette
        figsize (tuple): Default figure size
        dpi (int): Figure DPI
    """
    sns.set_style(style)
    sns.set_palette(palette)
    plt.rcParams['figure.figsize'] = figsize
    plt.rcParams['figure.dpi'] = dpi
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10


def plot_time_series(df: pd.DataFrame,
                    date_column: str,
                    value_column: str,
                    title: str = "Time Series Plot",
                    group_column: Optional[str] = None,
                    figsize: Tuple[int, int] = (15, 6)) -> plt.Figure:
    """
    Create time series plot with optional grouping.
    
    Args:
        df (pd.DataFrame): Input dataframe
        date_column (str): Date column name
        value_column (str): Value column name
        title (str): Plot title
        group_column (str, optional): Column to group by
        figsize (tuple): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if group_column:
        for group in df[group_column].unique():
            group_data = df[df[group_column] == group]
            ax.plot(group_data[date_column], group_data[value_column], 
                   label=group, linewidth=2, alpha=0.8)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        ax.plot(df[date_column], df[value_column], linewidth=2, alpha=0.8)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(date_column.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(value_column.replace('_', ' ').title(), fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def plot_price_quantity_scatter(df: pd.DataFrame,
                               price_column: str = 'unit_price',
                               quantity_column: str = 'quantity_sold',
                               group_column: Optional[str] = None,
                               title: str = "Price vs Quantity",
                               figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
    """
    Create scatter plot of price vs quantity with trend line.
    
    Args:
        df (pd.DataFrame): Input dataframe
        price_column (str): Price column name
        quantity_column (str): Quantity column name
        group_column (str, optional): Column to group by
        title (str): Plot title
        figsize (tuple): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if group_column:
        groups = df[group_column].unique()
        colors = sns.color_palette("husl", len(groups))
        
        for i, group in enumerate(groups):
            group_data = df[df[group_column] == group]
            ax.scatter(group_data[price_column], group_data[quantity_column],
                      alpha=0.6, color=colors[i], label=group, s=50)
            
            # Add trend line for each group
            z = np.polyfit(group_data[price_column], group_data[quantity_column], 1)
            p = np.poly1d(z)
            ax.plot(group_data[price_column], p(group_data[price_column]),
                   color=colors[i], linestyle='--', alpha=0.8)
        
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        ax.scatter(df[price_column], df[quantity_column], alpha=0.6, s=50)
        
        # Add overall trend line
        z = np.polyfit(df[price_column], df[quantity_column], 1)
        p = np.poly1d(z)
        ax.plot(df[price_column], p(df[price_column]), 'r--', alpha=0.8)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(price_column.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(quantity_column.replace('_', ' ').title(), fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(df: pd.DataFrame,
                           columns: Optional[List[str]] = None,
                           title: str = "Correlation Heatmap",
                           figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
    """
    Create correlation heatmap for numeric columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str], optional): Specific columns to include
        title (str): Plot title
        figsize (tuple): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    if columns:
        corr_df = df[columns]
    else:
        corr_df = df.select_dtypes(include=[np.number])
    
    correlation_matrix = corr_df.corr()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create mask for upper triangle
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    
    sns.heatmap(correlation_matrix, mask=mask, annot=True, 
                cmap='coolwarm', center=0, square=True,
                fmt='.2f', cbar_kws={"shrink": .8}, ax=ax)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_distribution(df: pd.DataFrame,
                     columns: List[str],
                     ncols: int = 2,
                     title: str = "Distribution Plots",
                     figsize: Tuple[int, int] = (15, 10)) -> plt.Figure:
    """
    Create distribution plots for multiple columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str]): Columns to plot
        ncols (int): Number of columns in subplot grid
        title (str): Overall title
        figsize (tuple): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    nrows = (len(columns) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    
    if nrows == 1:
        axes = [axes] if ncols == 1 else axes
    else:
        axes = axes.flatten()
    
    for i, col in enumerate(columns):
        if i < len(axes):
            ax = axes[i]
            
            # Plot histogram with KDE
            df[col].hist(bins=30, alpha=0.7, ax=ax, density=True)
            df[col].plot.kde(ax=ax, secondary_y=False)
            
            ax.set_title(f'Distribution of {col.replace("_", " ").title()}')
            ax.set_xlabel(col.replace('_', ' ').title())
            ax.set_ylabel('Density')
            ax.grid(True, alpha=0.3)
    
    # Hide empty subplots
    for j in range(len(columns), len(axes)):
        axes[j].set_visible(False)
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_boxplot_by_category(df: pd.DataFrame,
                           category_column: str,
                           value_column: str,
                           title: str = "Boxplot by Category",
                           figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Create boxplot grouped by category.
    
    Args:
        df (pd.DataFrame): Input dataframe
        category_column (str): Category column name
        value_column (str): Value column name
        title (str): Plot title
        figsize (tuple): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.boxplot(data=df, x=category_column, y=value_column, ax=ax)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(category_column.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(value_column.replace('_', ' ').title(), fontsize=12)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def plot_elasticity_results(elasticity_df: pd.DataFrame,
                          category_column: str = 'category',
                          elasticity_column: str = 'price_elasticity',
                          title: str = "Price Elasticity by Category",
                          figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plot price elasticity results with reference lines.
    
    Args:
        elasticity_df (pd.DataFrame): Dataframe with elasticity results
        category_column (str): Category column name
        elasticity_column (str): Elasticity coefficient column
        title (str): Plot title
        figsize (tuple): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create bar plot
    bars = ax.bar(elasticity_df[category_column], elasticity_df[elasticity_column],
                  alpha=0.7, color=['red' if x < -1 else 'orange' if x < 0 else 'green' 
                                   for x in elasticity_df[elasticity_column]])
    
    # Add reference lines
    ax.axhline(y=-1, color='red', linestyle='--', alpha=0.7, 
               label='Elastic Threshold (-1)')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Add value labels on bars
    for bar, value in zip(bars, elasticity_df[elasticity_column]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01 if height > 0 else height - 0.05,
                f'{value:.2f}', ha='center', va='bottom' if height > 0 else 'top')
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(category_column.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel('Price Elasticity Coefficient', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def plot_model_performance(results_df: pd.DataFrame,
                         model_column: str = 'model',
                         metric_column: str = 'r2_score',
                         title: str = "Model Performance Comparison",
                         figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot model performance comparison.
    
    Args:
        results_df (pd.DataFrame): Model results dataframe
        model_column (str): Model name column
        metric_column (str): Performance metric column
        title (str): Plot title
        figsize (tuple): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Sort by performance
    results_sorted = results_df.sort_values(metric_column, ascending=False)
    
    bars = ax.bar(results_sorted[model_column], results_sorted[metric_column],
                  alpha=0.7, color=sns.color_palette("viridis", len(results_sorted)))
    
    # Add value labels
    for bar, value in zip(bars, results_sorted[metric_column]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel(metric_column.replace('_', ' ').title(), fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def save_plot(fig: plt.Figure, 
             filename: str,
             dpi: int = 300,
             format: str = 'png',
             bbox_inches: str = 'tight') -> None:
    """
    Save plot to file with standard settings.
    
    Args:
        fig (plt.Figure): Figure to save
        filename (str): Output filename
        dpi (int): Resolution
        format (str): File format
        bbox_inches (str): Bounding box setting
    """
    fig.savefig(filename, dpi=dpi, format=format, bbox_inches=bbox_inches)
    print(f"Plot saved to {filename}")


def create_dashboard_summary(df: pd.DataFrame,
                           price_col: str = 'unit_price',
                           quantity_col: str = 'quantity_sold',
                           date_col: str = 'date',
                           category_col: str = 'category') -> plt.Figure:
    """
    Create comprehensive dashboard summary.
    
    Args:
        df (pd.DataFrame): Input dataframe
        price_col (str): Price column name
        quantity_col (str): Quantity column name
        date_col (str): Date column name
        category_col (str): Category column name
        
    Returns:
        plt.Figure: Dashboard figure
    """
    fig = plt.figure(figsize=(20, 15))
    
    # Time series of price and quantity
    ax1 = plt.subplot(3, 3, 1)
    df.groupby(date_col)[price_col].mean().plot(ax=ax1)
    ax1.set_title('Average Price Over Time')
    ax1.set_ylabel('Price')
    
    ax2 = plt.subplot(3, 3, 2)
    df.groupby(date_col)[quantity_col].sum().plot(ax=ax2)
    ax2.set_title('Total Quantity Over Time')
    ax2.set_ylabel('Quantity')
    
    # Price distribution by category
    ax3 = plt.subplot(3, 3, 3)
    sns.boxplot(data=df, x=category_col, y=price_col, ax=ax3)
    ax3.set_title('Price Distribution by Category')
    plt.setp(ax3.get_xticklabels(), rotation=45)
    
    # Quantity distribution by category
    ax4 = plt.subplot(3, 3, 4)
    sns.boxplot(data=df, x=category_col, y=quantity_col, ax=ax4)
    ax4.set_title('Quantity Distribution by Category')
    plt.setp(ax4.get_xticklabels(), rotation=45)
    
    # Price vs quantity scatter
    ax5 = plt.subplot(3, 3, 5)
    ax5.scatter(df[price_col], df[quantity_col], alpha=0.5)
    ax5.set_title('Price vs Quantity')
    ax5.set_xlabel('Price')
    ax5.set_ylabel('Quantity')
    
    # Correlation heatmap for numeric columns
    ax6 = plt.subplot(3, 3, 6)
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:6]  # Limit to 6 columns
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax6)
        ax6.set_title('Correlation Matrix')
    
    # Revenue over time
    ax7 = plt.subplot(3, 3, 7)
    if 'revenue' in df.columns:
        df.groupby(date_col)['revenue'].sum().plot(ax=ax7)
    else:
        (df[price_col] * df[quantity_col]).groupby(df[date_col]).sum().plot(ax=ax7)
    ax7.set_title('Revenue Over Time')
    ax7.set_ylabel('Revenue')
    
    # Category performance
    ax8 = plt.subplot(3, 3, 8)
    category_revenue = df.groupby(category_col).apply(
        lambda x: (x[price_col] * x[quantity_col]).sum()
    )
    category_revenue.plot(kind='bar', ax=ax8)
    ax8.set_title('Revenue by Category')
    ax8.set_ylabel('Total Revenue')
    plt.setp(ax8.get_xticklabels(), rotation=45)
    
    # Daily/weekly patterns
    ax9 = plt.subplot(3, 3, 9)
    df['day_of_week'] = df[date_col].dt.dayofweek
    daily_avg = df.groupby('day_of_week')[quantity_col].mean()
    daily_avg.plot(kind='bar', ax=ax9)
    ax9.set_title('Average Quantity by Day of Week')
    ax9.set_xlabel('Day of Week (0=Monday)')
    ax9.set_ylabel('Average Quantity')
    
    plt.tight_layout()
    return fig 