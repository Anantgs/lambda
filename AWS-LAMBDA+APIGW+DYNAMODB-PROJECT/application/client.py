"""
AWS API Gateway Client
Handles HTTP requests to the Lambda-backed API Gateway endpoint
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from config import API_ENDPOINT, TIMEOUT, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIGatewayClient:
    """Client for communicating with API Gateway"""

    def __init__(self, endpoint: str = API_ENDPOINT, timeout: int = TIMEOUT):
        """
        Initialize the API Gateway client

        Args:
            endpoint: The API Gateway endpoint URL
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.session = requests.Session()

    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order by sending a POST request to API Gateway

        Args:
            order_data: Dictionary containing order information

        Returns:
            Response from the API Gateway (containing orderId and status)

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            logger.info(f"Sending order request to {self.endpoint}")
            logger.debug(f"Order data: {json.dumps(order_data, indent=2)}")

            response = self.session.post(
                self.endpoint,
                json=order_data,
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            # Log response details
            logger.info(f"Response Status Code: {response.status_code}")

            # Raise exception for bad status codes
            response.raise_for_status()

            response_data = response.json()
            logger.info(f"Order placed successfully: {json.dumps(response_data, indent=2)}")

            return response_data

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout} seconds")
            raise

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            logger.error("Make sure the API Gateway endpoint is correct and accessible")
            raise

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {response.status_code}")
            try:
                error_response = response.json()
                logger.error(f"Error details: {json.dumps(error_response, indent=2)}")
            except:
                logger.error(f"Error response: {response.text}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of an existing order

        Args:
            order_id: The order ID to check

        Returns:
            Order details including current status

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            url = f"{self.endpoint}/{order_id}"
            logger.info(f"Fetching order status from {url}")

            response = self.session.get(
                url,
                timeout=self.timeout,
                headers={'Accept': 'application/json'}
            )

            response.raise_for_status()
            order_status = response.json()
            logger.info(f"Order status: {json.dumps(order_status, indent=2)}")

            return order_status

        except Exception as e:
            logger.error(f"Error fetching order status: {str(e)}")
            raise

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
