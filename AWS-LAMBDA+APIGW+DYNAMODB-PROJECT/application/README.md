# Python Web Application Client

This is a Python client application that demonstrates how to interact with AWS API Gateway, which triggers Lambda functions and stores data in DynamoDB.

## 📋 Project Structure

```
application/
├── app.py              # Main application with interactive menu
├── client.py           # API Gateway client class
├── config.py           # Configuration and settings
├── test_client.py      # Unit tests
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
└── README.md           # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- AWS API Gateway endpoint URL (from your AWS setup)

### Installation

1. **Clone or navigate to this directory:**

```bash
cd AWS-LAMBDA+APIGW+DYNAMODB-PROJECT/application
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure your API Gateway endpoint:**

```bash
# Create .env file from example
cp .env.example .env

# Edit .env and add your API Gateway URL
# Example: API_GATEWAY_URL=https://abc123def456.execute-api.us-east-1.amazonaws.com
```

## 🏃 Running the Application

### Interactive Mode (Recommended)

```bash
python app.py
```

This launches an interactive menu where you can:
- Place sample orders
- Create custom orders
- Check order status
- Exit

### Example Flow

```
1. Select "Place Sample Order"
2. App sends JSON order to API Gateway
3. Lambda function receives and processes the request
4. Order stored in DynamoDB
5. Immediate response returned with order ID
```

## 📚 Project Components

### app.py
- Main entry point
- Interactive menu system
- User-friendly interface
- Error handling

### client.py
- `APIGatewayClient` class
- Handles HTTP requests to API Gateway
- Supports placing orders and checking status
- Comprehensive logging
- Exception handling

### config.py
- Centralized configuration
- Environment variable management
- API endpoint configuration
- Sample order data

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Your API Gateway endpoint
API_GATEWAY_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com

# Enable debug logging
DEBUG=True
```

### Modifying Sample Order

Edit `SAMPLE_ORDER` in `config.py`:

```python
SAMPLE_ORDER = {
    "items": [
        {
            "productId": "PROD-001",
            "qty": 2,
            "price": 29.99
        }
    ],
    "paymentMethod": "card",
    "customerEmail": "customer@example.com"
}
```

## 📤 API Request Format

The application sends POST requests with this JSON structure:

```json
{
  "items": [
    {
      "productId": "PROD-001",
      "qty": 2,
      "price": 29.99
    }
  ],
  "paymentMethod": "card",
  "customerEmail": "customer@example.com"
}
```

## 📥 API Response Format

Expected response from Lambda/API Gateway:

```json
{
  "orderId": "ORD-123456",
  "status": "PENDING",
  "timestamp": "2024-01-19T10:30:00Z"
}
```

## 🧪 Testing

Run unit tests:

```bash
python -m pytest test_client.py -v
```

Or use unittest:

```bash
python -m unittest test_client.py
```

## 🔍 Debugging

Enable debug logging by setting in `.env`:

```env
DEBUG=True
```

This will show:
- Detailed request/response information
- Timestamps for each operation
- Full request payloads
- Error stack traces

## 📊 Architecture Flow

```
Python App (This)
    ↓ POST /orders
API Gateway
    ↓ Triggers
Lambda Function (order_intake)
    ↓ Stores
DynamoDB (Orders Table)
    ↓ Response
API Gateway
    ↓ Response
Python App (orderId, status)
```

## ❌ Troubleshooting

### "API Gateway endpoint not configured"
- Edit `.env` and set `API_GATEWAY_URL`
- Make sure the URL doesn't contain `YOUR_API_ID`

### "Connection error: Failed to establish a new connection"
- Verify API Gateway endpoint is correct
- Check internet connectivity
- Ensure the endpoint is publicly accessible

### "HTTP 403 Forbidden"
- Check API Gateway permissions
- Verify CORS settings (if needed)
- Check IAM role permissions for Lambda

### "HTTP 500 Internal Server Error"
- Check Lambda function logs in CloudWatch
- Verify DynamoDB table exists and has correct permissions
- Check IAM role attached to Lambda

## 📝 Logging

The application uses Python's built-in logging module:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Error message")
```

Check logs for:
- Request/response details
- Timing information
- Error details with stack traces

## 🤝 Integration with AWS

This client integrates with:

1. **API Gateway** - Public HTTP endpoint
2. **Lambda** - Serverless compute function
3. **DynamoDB** - NoSQL database
4. **SQS** - Asynchronous queue (optional)
5. **SNS** - Notifications (optional)

## 📖 Additional Resources

- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Python Requests Library](https://requests.readthedocs.io/)

## 📄 License

This is a demonstration project for learning purposes.

## 👨‍💻 Author Notes

- This client demonstrates best practices for API integration
- Includes error handling and logging
- Supports both one-time and interactive modes
- Easily extensible for additional features
- Production-ready code structure
