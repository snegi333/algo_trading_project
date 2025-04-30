class Symbol:
    def __init__(self, symbol, token, exchange, name=None, series=None, lot_size=1):
        """
        Symbol model for storing market symbol information
        
        Parameters:
            symbol (str): Trading symbol (e.g. RELIANCE-EQ)
            token (str): Symbol token used by Angel One API
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            name (str, optional): Company/security name
            series (str, optional): Series (EQ, BE, etc)
            lot_size (int, optional): Lot size for F&O contracts
        """
        self.symbol = symbol
        self.token = token
        self.exchange = exchange
        self.name = name
        self.series = series
        self.lot_size = lot_size
    
    def __str__(self):
        return f"{self.symbol} ({self.exchange})"
    
    def __repr__(self):
        return f"Symbol(symbol='{self.symbol}', token='{self.token}', exchange='{self.exchange}')"


class SymbolStore:
    """A simple in-memory store for symbols"""
    
    def __init__(self):
        self.symbols = {}  # Dictionary to store symbols by their token
        self.symbol_to_token = {}  # Mapping from symbol-exchange to token
    
    def add_symbol(self, symbol):
        """Add a symbol to the store"""
        self.symbols[symbol.token] = symbol
        key = f"{symbol.symbol}:{symbol.exchange}"
        self.symbol_to_token[key] = symbol.token
    
    def get_by_token(self, token):
        """Get symbol by token"""
        return self.symbols.get(token)
    
    def get_by_symbol(self, symbol, exchange):
        """Get symbol by symbol name and exchange"""
        key = f"{symbol}:{exchange}"
        token = self.symbol_to_token.get(key)
        if token:
            return self.symbols.get(token)
        return None
    
    def load_from_file(self, filename):
        """Load symbols from a CSV file"""
        import csv
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    symbol = Symbol(
                        symbol=row['symbol'],
                        token=row['token'],
                        exchange=row['exchange'],
                        name=row.get('name'),
                        series=row.get('series'),
                        lot_size=int(row.get('lot_size', 1))
                    )
                    self.add_symbol(symbol)
            return True
        except Exception as e:
            print(f"Error loading symbols: {str(e)}")
            return False
    
    def save_to_file(self, filename):
        """Save symbols to a CSV file"""
        import csv
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['symbol', 'token', 'exchange', 'name', 'series', 'lot_size'])
                for symbol in self.symbols.values():
                    writer.writerow([
                        symbol.symbol,
                        symbol.token,
                        symbol.exchange,
                        symbol.name or '',
                        symbol.series or '',
                        symbol.lot_size
                    ])
            return True
        except Exception as e:
            print(f"Error saving symbols: {str(e)}")
            return False 