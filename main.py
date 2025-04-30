#!/usr/bin/env python
import os
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

from trading_automation.api.angel_one_api import AngelOneAPI
from trading_automation.utils.trader import Trader
from trading_automation.models.symbol import Symbol, SymbolStore
from trading_automation.strategies.moving_average_crossover import MovingAverageCrossover

# Setup logging
def setup_logging(log_level="INFO"):
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"trading_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Trading Automation with Angel One")
    parser.add_argument("--symbol", help="Trading symbol", default="SBIN-EQ")
    parser.add_argument("--exchange", help="Exchange", default="NSE")
    parser.add_argument("--interval", type=int, help="Strategy run interval in minutes", default=15)
    parser.add_argument("--position-size", type=int, help="Position size (quantity)", default=1)
    parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    parser.add_argument("--log-level", help="Logging level", default="INFO")
    parser.add_argument("--symbols-file", help="CSV file with symbols data")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting trading automation")
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize API
        api = AngelOneAPI()
        
        # Initialize symbol store
        symbol_store = SymbolStore()
        
        # Load symbols from file if provided
        if args.symbols_file and os.path.exists(args.symbols_file):
            logger.info(f"Loading symbols from {args.symbols_file}")
            symbol_store.load_from_file(args.symbols_file)
        else:
            # Add example symbol as a fallback
            # In production, you'd want to use a proper symbol database
            logger.warning("No symbols file provided or file not found. Using example symbol.")
            example_symbol = Symbol(
                symbol=args.symbol,
                token="1234",  # This is a placeholder, you need the actual token
                exchange=args.exchange
            )
            symbol_store.add_symbol(example_symbol)
        
        # Initialize trader
        trader = Trader(api=api, symbol_store=symbol_store)
        
        # Create strategy
        strategy = MovingAverageCrossover(short_window=10, long_window=50)
        
        # Add strategy
        trader.add_strategy(
            symbol=args.symbol,
            exchange=args.exchange,
            strategy=strategy,
            position_size=args.position_size
        )
        
        # Schedule strategy
        if not args.run_once:
            trader.schedule_strategy(
                symbol=args.symbol,
                exchange=args.exchange,
                interval_minutes=args.interval
            )
        
        # Start scheduler
        trader.start_scheduler(run_once=args.run_once)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 