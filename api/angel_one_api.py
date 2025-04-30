import logging
import pyotp
from smartapi import SmartConnect
from trading_automation.config.config import API_KEY, CLIENT_ID, PASSWORD, TOTP_KEY

logger = logging.getLogger(__name__)

class AngelOneAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.client_id = CLIENT_ID
        self.password = PASSWORD
        self.totp_key = TOTP_KEY
        self.smart_api = None
        self.session_id = None
        self.refresh_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Angel One API using credentials"""
        try:
            totp = pyotp.TOTP(self.totp_key).now()
            self.smart_api = SmartConnect(api_key=self.api_key)
            data = self.smart_api.generateSession(self.client_id, self.password, totp)
            
            if data['status']:
                self.session_id = data['data']['sessionID']
                self.refresh_token = data['data']['refreshToken']
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {data['message']}")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_profile(self):
        """Get user profile information"""
        try:
            return self.smart_api.getProfile()
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return None
    
    def place_order(self, symbol, exchange, transaction_type, quantity, price, order_type="LIMIT"):
        """
        Place an order
        
        Parameters:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, BSE, NFO, etc)
            transaction_type (str): BUY or SELL
            quantity (int): Number of shares/contracts
            price (float): Price for limit order
            order_type (str): LIMIT, MARKET, etc
        
        Returns:
            dict: Order response
        """
        try:
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": self._get_token(symbol, exchange),
                "transactiontype": transaction_type,
                "exchange": exchange,
                "ordertype": order_type,
                "producttype": "DELIVERY",
                "duration": "DAY",
                "price": price,
                "quantity": quantity
            }
            
            response = self.smart_api.placeOrder(order_params)
            logger.info(f"Order placed: {response}")
            return response
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {"status": False, "error": str(e)}
    
    def get_order_book(self):
        """Get list of orders"""
        try:
            return self.smart_api.orderBook()
        except Exception as e:
            logger.error(f"Error fetching order book: {str(e)}")
            return None
    
    def get_trade_book(self):
        """Get list of trades"""
        try:
            return self.smart_api.tradeBook()
        except Exception as e:
            logger.error(f"Error fetching trade book: {str(e)}")
            return None
    
    def get_holdings(self):
        """Get user holdings"""
        try:
            return self.smart_api.holding()
        except Exception as e:
            logger.error(f"Error fetching holdings: {str(e)}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            return self.smart_api.position()
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            return None
    
    def cancel_order(self, order_id):
        """Cancel an order by order ID"""
        try:
            return self.smart_api.cancelOrder(order_id, "NORMAL")
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return {"status": False, "error": str(e)}
    
    def _get_token(self, symbol, exchange):
        """Get token for a symbol (implementation requires Angel One's symbol lookup)"""
        # This is a placeholder. In a real implementation, you'd fetch the token
        # from Angel One's symbol lookup service or maintain a local database
        # of symbols and tokens
        raise NotImplementedError("Symbol token lookup not implemented") 