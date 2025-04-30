import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class MovingAverageCrossover:
    """
    Simple Moving Average Crossover Strategy
    
    Generates buy signals when the short moving average crosses above the long moving average
    Generates sell signals when the short moving average crosses below the long moving average
    """
    
    def __init__(self, short_window=10, long_window=50):
        """
        Initialize strategy with moving average windows
        
        Parameters:
            short_window (int): Short moving average period
            long_window (int): Long moving average period
        """
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data):
        """
        Generate trading signals based on moving average crossover
        
        Parameters:
            data (pandas.DataFrame): Historical price data with 'close' column
            
        Returns:
            pandas.DataFrame: Original data with added signal columns
        """
        if len(data) < self.long_window:
            logger.warning(f"Insufficient data for MA calculation. Need at least {self.long_window} periods.")
            return data
        
        # Make a copy of the data
        signals = data.copy()
        
        # Create short and long moving averages
        signals['short_ma'] = signals['close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_ma'] = signals['close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Create signals
        signals['signal'] = 0.0
        signals['position'] = 0.0
        
        # Generate signals
        signals.loc[signals['short_ma'] > signals['long_ma'], 'signal'] = 1.0
        signals.loc[signals['short_ma'] < signals['long_ma'], 'signal'] = -1.0
        
        # Generate positions (1 for long, -1 for short, 0 for no position)
        signals['position'] = signals['signal'].diff()
        
        logger.info(f"Generated signals: {sum(signals['position'] == 1)} buy, {sum(signals['position'] == -1)} sell")
        
        return signals
    
    def get_latest_signal(self, data):
        """
        Get the latest trading signal
        
        Parameters:
            data (pandas.DataFrame): Historical price data with 'close' column
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for hold
        """
        signals = self.generate_signals(data)
        latest_position = signals['position'].iloc[-1]
        
        if latest_position == 1:
            return 1  # Buy signal
        elif latest_position == -1:
            return -1  # Sell signal
        else:
            return 0  # Hold/no signal 