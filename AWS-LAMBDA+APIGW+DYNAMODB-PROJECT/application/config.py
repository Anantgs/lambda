import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Gateway Configuration
API_GATEWAY_URL = os.getenv(
    'API_GATEWAY_URL',
    'https://e5l851853a.execute-api.us-east-1.amazonaws.com/dev'
)

API_ENDPOINT = f"{API_GATEWAY_URL}/orders"

# Application settings
TIMEOUT = 10  # seconds
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Sample order data
SAMPLE_ORDER = {
    "items": [
        {
            "productId": "PROD-001",
            "qty": 2,
            "price": 29.99
        },
        {
            "productId": "PROD-002",
            "qty": 1,
            "price": 49.99
        }
    ],
    "paymentMethod": "card",
    "customerEmail": "customer@example.com"
}
