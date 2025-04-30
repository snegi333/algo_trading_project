import logging
import time
import schedule
from datetime import datetime
from trading_automation.api.angel_one_api import AngelOneAPI
from trading_automation.utils.data_fetcher import DataFetcher
from trading_automation.models.symbol import SymbolStore

logger = logging.getLogger(__name__)

class Trader:
    """Automated trader class to execute trading strategies"""
    
    def __init__(self, api=None, symbol_store=None):
        """
        Initialize trader
        
        Parameters:
            api (AngelOneAPI, optional): Instance of AngelOneAPI
            symbol_store (SymbolStore, optional): Instance of SymbolStore
        """
        self.api = api or AngelOneAPI()
        self.symbol_store = symbol_store or SymbolStore()
        self.data_fetcher = DataFetcher(api=self.api)
        self.strategies = {}  # Map of symbol to strategy
        self.active_jobs = {}  # Map of symbol to scheduled jobs
        self.position_sizes = {}  # Map of symbol to position size
    
    def add_strategy(self, symbol, exchange, strategy, position_size=1):
        """
        Add a trading strategy for a symbol
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            strategy: Strategy instance
            position_size (int): Number of shares/contracts to trade
        """
        key = f"{symbol}:{exchange}"
        self.strategies[key] = strategy
        self.position_sizes[key] = position_size
        logger.info(f"Added strategy for {symbol} {exchange}")
    
    def run_strategy(self, symbol, exchange):
        """
        Run a strategy for a symbol once
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            
        Returns:
            dict: Result of the strategy execution
        """
        key = f"{symbol}:{exchange}"
        
        if key not in self.strategies:
            logger.error(f"No strategy defined for {symbol} {exchange}")
            return {"status": False, "error": "No strategy defined"}
        
        try:
            # Get historical data
            data = self.data_fetcher.get_historical_data(symbol, exchange)
            
            if data.empty:
                logger.warning(f"No data available for {symbol} {exchange}")
                return {"status": False, "error": "No data available"}
            
            # Get signal from strategy
            strategy = self.strategies[key]
            signal = strategy.get_latest_signal(data)
            
            if signal == 0:
                logger.info(f"No trade signal for {symbol} {exchange}")
                return {"status": True, "action": "none"}
            
            # Execute trade based on signal
            position_size = self.position_sizes.get(key, 1)
            
            if signal == 1:  # Buy
                result = self._execute_buy(symbol, exchange, position_size)
                logger.info(f"Buy signal executed for {symbol} {exchange}: {result}")
                return {"status": True, "action": "buy", "result": result}
                
            elif signal == -1:  # Sell
                result = self._execute_sell(symbol, exchange, position_size)
                logger.info(f"Sell signal executed for {symbol} {exchange}: {result}")
                return {"status": True, "action": "sell", "result": result}
            
        except Exception as e:
            logger.error(f"Error running strategy for {symbol} {exchange}: {str(e)}")
            return {"status": False, "error": str(e)}
    
    def schedule_strategy(self, symbol, exchange, interval_minutes=15):
        """
        Schedule a strategy to run at regular intervals
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            interval_minutes (int): How often to run the strategy in minutes
        """
        key = f"{symbol}:{exchange}"
        
        if key not in self.strategies:
            logger.error(f"No strategy defined for {symbol} {exchange}")
            return False
        
        # Create job
        job = schedule.every(interval_minutes).minutes.do(
            self.run_strategy, symbol=symbol, exchange=exchange
        )
        
        # Store job
        self.active_jobs[key] = job
        
        logger.info(f"Scheduled strategy for {symbol} {exchange} every {interval_minutes} minutes")
        return True
    
    def cancel_schedule(self, symbol, exchange):
        """
        Cancel a scheduled strategy
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
        """
        key = f"{symbol}:{exchange}"
        
        if key in self.active_jobs:
            schedule.cancel_job(self.active_jobs[key])
            del self.active_jobs[key]
            logger.info(f"Cancelled scheduled strategy for {symbol} {exchange}")
            return True
        
        logger.warning(f"No scheduled strategy found for {symbol} {exchange}")
        return False
    
    def start_scheduler(self, run_once=False):
        """
        Start the scheduler to run all scheduled strategies
        
        Parameters:
            run_once (bool): If True, runs all strategies once and exits
        """
        logger.info("Starting scheduler")
        
        if run_once:
            # Run all strategies once
            for key in self.strategies:
                symbol, exchange = key.split(':')
                self.run_strategy(symbol, exchange)
            return
        
        # Run continuously
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
    
    def _execute_buy(self, symbol, exchange, quantity=1, price=None):
        """
        Execute a buy order
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            quantity (int): Number of shares/contracts
            price (float, optional): Limit price. If None, uses market order
            
        Returns:
            dict: Order result
        """
        order_type = "MARKET" if price is None else "LIMIT"
        
        # For limit orders, we need the price
        if order_type == "LIMIT" and price is None:
            # Try to get the latest price
            try:
                ltp_data = self.api.smart_api.ltpData(exchange, symbol, self._get_token(symbol, exchange))
                price = ltp_data['data']['ltp']
            except Exception as e:
                logger.error(f"Error getting LTP for {symbol}: {str(e)}")
                return {"status": False, "error": "Unable to determine price for limit order"}
        
        return self.api.place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type="BUY",
            quantity=quantity,
            price=price,
            order_type=order_type
        )
    
    def _execute_sell(self, symbol, exchange, quantity=1, price=None):
        """
        Execute a sell order
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            quantity (int): Number of shares/contracts
            price (float, optional): Limit price. If None, uses market order
            
        Returns:
            dict: Order result
        """
        order_type = "MARKET" if price is None else "LIMIT"
        
        # For limit orders, we need the price
        if order_type == "LIMIT" and price is None:
            # Try to get the latest price
            try:
                ltp_data = self.api.smart_api.ltpData(exchange, symbol, self._get_token(symbol, exchange))
                price = ltp_data['data']['ltp']
            except Exception as e:
                logger.error(f"Error getting LTP for {symbol}: {str(e)}")
                return {"status": False, "error": "Unable to determine price for limit order"}
        
        return self.api.place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type="SELL",
            quantity=quantity,
            price=price,
            order_type=order_type
        )
    
    def _get_token(self, symbol, exchange):
        """Get token for a symbol from symbol store"""
        symbol_obj = self.symbol_store.get_by_symbol(symbol, exchange)
        if symbol_obj:
            return symbol_obj.token
        raise ValueError(f"Token not found for {symbol} {exchange}") 