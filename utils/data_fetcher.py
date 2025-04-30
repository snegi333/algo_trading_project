import logging
import pandas as pd
from datetime import datetime, timedelta
from trading_automation.api.angel_one_api import AngelOneAPI

logger = logging.getLogger(__name__)

class DataFetcher:
    """Utility for fetching historical market data"""
    
    def __init__(self, api=None):
        """
        Initialize data fetcher
        
        Parameters:
            api (AngelOneAPI, optional): Instance of AngelOneAPI
        """
        self.api = api or AngelOneAPI()
    
    def get_historical_data(self, symbol, exchange, timeframe="ONE_DAY", from_date=None, to_date=None, limit=100):
        """
        Fetch historical candle data for a symbol
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            timeframe (str): Candle timeframe (ONE_MINUTE, FIVE_MINUTE, ONE_HOUR, ONE_DAY, etc)
            from_date (datetime, optional): Start date for historical data
            to_date (datetime, optional): End date for historical data
            limit (int, optional): Max number of candles to fetch
            
        Returns:
            pandas.DataFrame: Historical candle data
        """
        try:
            # Set default dates if not provided
            if to_date is None:
                to_date = datetime.now()
            if from_date is None:
                # Go back by limit candles based on timeframe
                if timeframe == "ONE_DAY":
                    from_date = to_date - timedelta(days=limit)
                elif timeframe == "ONE_HOUR":
                    from_date = to_date - timedelta(hours=limit)
                else:  # Default to ONE_MINUTE
                    from_date = to_date - timedelta(minutes=limit)
            
            # Format dates for API
            from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
            to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
            
            # Call historical API
            # Note: The actual parameters may vary based on Angel One's API documentation
            params = {
                "exchange": exchange,
                "symboltoken": self._get_token(symbol, exchange),
                "interval": timeframe,
                "fromdate": from_date_str,
                "todate": to_date_str
            }
            
            candle_data = self.api.smart_api.getCandleData(params)
            
            if not candle_data or 'data' not in candle_data or not candle_data['data']:
                logger.warning(f"No historical data returned for {symbol} {exchange}")
                return pd.DataFrame()
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(candle_data['data'], 
                             columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Set timestamp as index
            df.set_index('timestamp', inplace=True)
            
            # Convert price columns to float
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].astype(float)
            
            # Convert volume to int
            df['volume'] = df['volume'].astype(int)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()
    
    def _get_token(self, symbol, exchange):
        """
        Get token for a symbol (placeholder method)
        
        In a real implementation, this would use the SymbolStore or another method
        to look up the token for a given symbol and exchange
        """
        # This is a placeholder. In production, implement properly
        raise NotImplementedError("Symbol token lookup not implemented") 