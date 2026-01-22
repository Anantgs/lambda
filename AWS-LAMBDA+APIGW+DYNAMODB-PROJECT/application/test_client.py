"""
Unit tests for the API Gateway client
"""

import unittest
from unittest.mock import patch, MagicMock
from client import APIGatewayClient
from config import SAMPLE_ORDER


class TestAPIGatewayClient(unittest.TestCase):
    """Test cases for APIGatewayClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.endpoint = "https://test.execute-api.us-east-1.amazonaws.com/orders"
        self.client = APIGatewayClient(endpoint=self.endpoint, timeout=5)

    def tearDown(self):
        """Clean up after tests"""
        self.client.close()

    @patch('client.requests.Session.post')
    def test_place_order_success(self, mock_post):
        """Test successful order placement"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "orderId": "ORD-123456",
            "status": "PENDING",
            "timestamp": "2024-01-19T10:30:00Z"
        }
        mock_post.return_value = mock_response

        # Call the method
        result = self.client.place_order(SAMPLE_ORDER)

        # Assertions
        self.assertEqual(result["orderId"], "ORD-123456")
        self.assertEqual(result["status"], "PENDING")
        mock_post.assert_called_once()

    @patch('client.requests.Session.post')
    def test_place_order_timeout(self, mock_post):
        """Test timeout handling"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(requests.exceptions.Timeout):
            self.client.place_order(SAMPLE_ORDER)

    @patch('client.requests.Session.post')
    def test_place_order_connection_error(self, mock_post):
        """Test connection error handling"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.client.place_order(SAMPLE_ORDER)

    @patch('client.requests.Session.get')
    def test_get_order_status_success(self, mock_get):
        """Test successful status check"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "orderId": "ORD-123456",
            "status": "PAID",
            "items": 3,
            "total": 109.97
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.client.get_order_status("ORD-123456")

        # Assertions
        self.assertEqual(result["status"], "PAID")
        mock_get.assert_called_once()

    def test_context_manager(self):
        """Test context manager support"""
        with APIGatewayClient(endpoint=self.endpoint) as client:
            self.assertIsNotNone(client)
            self.assertEqual(client.endpoint, self.endpoint)


if __name__ == "__main__":
    unittest.main()
