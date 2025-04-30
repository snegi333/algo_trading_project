# Trading Automation with Angel One

A Python-based trading automation system that uses Angel One APIs to execute trading strategies.

## Features

- Automated trading with Angel One APIs
- Moving Average Crossover strategy implementation
- Scheduled trading at specified intervals
- Support for multiple symbols and exchanges
- Configurable position sizes
- Logging and error handling

## Prerequisites

- Python 3.8+
- Angel One trading account with API access
- API key and other credentials from Angel One

## Installation

1. Clone the repository:

```
git clone <repository-url>
cd algo_trading_project
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Create a `.env` file with your Angel One credentials:

```
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_PASSWORD=your_password
ANGEL_TOTP_KEY=your_totp_key
LOG_LEVEL=INFO
MAX_RETRIES=3
RETRY_DELAY=5
```

## Usage

### Running the trading system

```
python main.py --symbol SBIN-EQ --exchange NSE --interval 15 --position-size 1
```

### Command Line Arguments

- `--symbol`: Trading symbol (default: SBIN-EQ)
- `--exchange`: Exchange (default: NSE)
- `--interval`: Strategy run interval in minutes (default: 15)
- `--position-size`: Position size/quantity (default: 1)
- `--run-once`: Run once and exit (default: false)
- `--log-level`: Logging level (default: INFO)
- `--symbols-file`: CSV file with symbols data

### Example for running once

```
python main.py --symbol RELIANCE-EQ --exchange NSE --position-size 2 --run-once
```

## Symbol CSV File Format

For using multiple symbols, create a CSV file with the following columns:

```
symbol,token,exchange,name,series,lot_size
SBIN-EQ,3045,NSE,STATE BANK OF INDIA,EQ,1
RELIANCE-EQ,2885,NSE,RELIANCE INDUSTRIES LTD,EQ,1
```

## Project Structure

- `api/` - API integration code
- `models/` - Data models
- `strategies/` - Trading strategies
- `utils/` - Utility classes
- `config/` - Configuration files

## Implementing New Strategies

To add a new strategy:

1. Create a new strategy class in the `strategies/` directory
2. Implement the `get_latest_signal()` method that returns:
   - `1` for buy signals
   - `-1` for sell signals
   - `0` for no action

## Disclaimer

This software is for educational purposes only. Use at your own risk. Trading in financial markets involves substantial risk and is not suitable for all investors. The developers are not responsible for any financial losses incurred while using this software.

## License

MIT 
