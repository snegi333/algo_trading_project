import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Angel One API credentials
API_KEY = os.getenv('ANGEL_API_KEY')
CLIENT_ID = os.getenv('ANGEL_CLIENT_ID')
PASSWORD = os.getenv('ANGEL_PASSWORD')
TOTP_KEY = os.getenv('ANGEL_TOTP_KEY')  # for TOTP generation

# Application settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5)) 