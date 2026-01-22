"""
Flask Web Application for AWS Serverless Order Processing
Provides a web interface to place orders via API Gateway → Lambda → DynamoDB
"""

from flask import Flask, render_template, request, jsonify
from client import APIGatewayClient
from config import API_ENDPOINT, SAMPLE_ORDER, DEBUG
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def index():
    """Render the main order form page"""
    api_configured = "YOUR_API_ID" not in API_ENDPOINT
    return render_template('index.html', api_configured=api_configured, api_endpoint=API_ENDPOINT)


@app.route('/api/place-order', methods=['POST'])
def place_order():
    """Handle order placement via API Gateway"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No order data provided'}), 400
        
        # Validate order data
        if 'items' not in data or not data['items']:
            return jsonify({'error': 'Order must contain items'}), 400
        
        logger.info(f"Received order placement request")
        
        # Call API Gateway via client
        client = APIGatewayClient()
        try:
            response = client.place_order(data)
            return jsonify(response), 200
        finally:
            client.close()
    
    except Exception as e:
        logger.error(f"Error placing order: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-order/<order_id>', methods=['GET'])
def check_order(order_id):
    """Check order status via API Gateway"""
    try:
        if not order_id:
            return jsonify({'error': 'Order ID required'}), 400
        
        logger.info(f"Checking status for order: {order_id}")
        
        # Call API Gateway via client
        client = APIGatewayClient()
        try:
            response = client.get_order_status(order_id)
            return jsonify(response), 200
        finally:
            client.close()
    
    except Exception as e:
        logger.error(f"Error checking order status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sample-order', methods=['GET'])
def get_sample_order():
    """Get sample order data"""
    return jsonify(SAMPLE_ORDER), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting AWS Serverless Order Web Application")
    logger.info(f"API Gateway Endpoint: {API_ENDPOINT}")
    
    # Check if API endpoint is configured
    if "YOUR_API_ID" in API_ENDPOINT:
        logger.warning("⚠️  API Gateway endpoint not configured!")
        logger.warning("Please set API_GATEWAY_URL in .env file")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=DEBUG,
        use_reloader=True
    )
