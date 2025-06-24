# Utility functions for price elasticity analysis
"""
Helper functions for data processing, visualization, and modeling
used across the price elasticity analysis notebooks.
"""

# Import all functions to make them available at package level
try:
    from .data_helpers import *
    from .plot_helpers import *
    from .model_helpers import *
except ImportError:
    # If relative imports fail, try absolute imports
    pass

# Console-safe logging for Windows compatibility
CONSOLE_SAFE_EMOJIS = {
    '✅': '[OK]',
    '❌': '[ERROR]', 
    '🔄': '[PROCESSING]',
    '📊': '[INFO]',
    '🚨': '[WARNING]',
    '💾': '[SAVE]',
    '⏱️': '[TIME]',
    '📋': '[DATA]'
}

def make_console_safe(message):
    """Replace emojis with console-safe alternatives for Windows."""
    for emoji, replacement in CONSOLE_SAFE_EMOJIS.items():
        message = message.replace(emoji, replacement)
    return message 