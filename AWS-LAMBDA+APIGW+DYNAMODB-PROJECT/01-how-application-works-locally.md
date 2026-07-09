# AWS Serverless Order Application - Setup & Run Guide

## Overview

This is a Flask-based web application that integrates with AWS API Gateway, Lambda functions, and DynamoDB. The application provides a modern web interface to place orders and check their status.

---

## System Requirements

- **OS**: Linux (Ubuntu, CentOS, Debian, etc.)
- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Browser**: Any modern web browser
- **Internet**: Connection to AWS API Gateway endpoint

---

## Quick Setup (One Command)

Run this single command to set up and start the application:

```bash
cd AWS-LAMBDA+APIGW+DYNAMODB-PROJECT/application && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cp .env.example .env && echo "✓ Setup complete! Edit .env with your API Gateway URL, then run: python web_app.py"
```

---

## Step-by-Step Setup Instructions

### Step 1: Navigate to Application Directory

```bash
cd AWS-LAMBDA+APIGW+DYNAMODB-PROJECT/application
```

### Step 2: Create Python Virtual Environment

```bash
python3 -m venv venv
```

This creates an isolated Python environment for the project.

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt, indicating the virtual environment is active.

### Step 4: Upgrade pip (Recommended)

```bash
pip install --upgrade pip
```

### Step 5: Install Project Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- requests (HTTP client)
- python-dotenv (environment configuration)

### Step 6: Configure API Gateway Endpoint

```bash
cp .env.example .env
```

Edit the `.env` file with your text editor:

```bash
nano .env
```

Update the following values:

```env
# Replace YOUR_API_ID with your actual API Gateway ID
API_GATEWAY_URL=https://abc123def456.execute-api.us-east-1.amazonaws.com

# Set to True if you want debug logging
DEBUG=False
```

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 7: Run the Web Application

```bash
python web_app.py
```

You should see output similar to:

```
 * Running on http://0.0.0.0:5000
 * Debug mode: off
```

### Step 8: Access the Application

Open your browser and navigate to:

```
http://localhost:5000
```

Or if running on a remote server:

```
http://<server-ip>:5000
```

### Step 9: Deactivate Virtual Environment (When Done)

```bash
deactivate
```

---

## Automated Setup Script

Create a file named `run.sh`:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AWS Serverless Order Application - Setup         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"

# Step 1: Create virtual environment
echo -e "${BLUE}[1/4]${NC} Creating virtual environment..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}✗ Failed to create virtual environment${NC}"
    exit 1
fi

# Step 2: Activate virtual environment
echo -e "${BLUE}[2/4]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Step 3: Install dependencies
echo -e "${BLUE}[3/4]${NC} Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Step 4: Setup configuration
echo -e "${BLUE}[4/4]${NC} Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Configuration file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your API Gateway URL:${NC}"
    echo -e "  nano .env"
    echo ""
    echo -e "${YELLOW}Then run:${NC}"
    echo -e "  python web_app.py"
else
    echo -e "${GREEN}✓ Configuration already exists${NC}"
    echo -e "${BLUE}Starting application...${NC}"
    python web_app.py
fi
```

Make it executable and run:

```bash
chmod +x run.sh
./run.sh
```

---

## Project Structure

```
application/
├── web_app.py              # Main Flask application
├── client.py               # API Gateway client library
├── config.py               # Configuration management
├── test_client.py          # Unit tests
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .env                    # Your configuration (create from example)
├── templates/
│   └── index.html          # Web UI (HTML, CSS, JavaScript)
├── venv/                   # Virtual environment (created by setup)
├── app-setup.md            # This file
└── README.md               # Project documentation
```

---

## Application Features

### 📦 Place Order
- Add multiple items to an order
- Set product ID, quantity, and price for each item
- Choose payment method (Card, Bank Transfer, PayPal)
- Enter customer email
- Submit order to API Gateway
- Receive order ID and status

### 📋 Check Order Status
- Look up existing orders by Order ID
- View current order status
- See order details and timestamps

### 🔒 Error Handling
- Connection error alerts
- Timeout handling
- API error messages
- User-friendly error display

### 📊 Real-time Logging
- Request/response logging
- Debug mode for detailed output
- Timestamp tracking

---

## Configuration (.env File)

The `.env` file controls application behavior:

```env
# Your AWS API Gateway endpoint (REQUIRED)
API_GATEWAY_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com

# Enable debug logging (True/False)
DEBUG=False
```

### How to Find Your API Gateway URL

1. Go to [AWS Console](https://console.aws.amazon.com)
2. Navigate to **API Gateway**
3. Select your API
4. Go to **Stages**
5. Copy the **Invoke URL** for your stage
6. Add `/orders` endpoint to the base URL

Example:
```
Base URL:    https://abc123def456.execute-api.us-east-1.amazonaws.com/prod
Orders URL:  https://abc123def456.execute-api.us-east-1.amazonaws.com/prod/orders
```

Set in `.env`:
```env
API_GATEWAY_URL=https://abc123def456.execute-api.us-east-1.amazonaws.com/prod
```

---

## Running the Application

### Normal Mode

```bash
source venv/bin/activate
python web_app.py
```

### Debug Mode

Edit `.env`:
```env
DEBUG=True
```

Then run:
```bash
python web_app.py
```

You'll see detailed logging of all requests and responses.

### Background Execution

Run the application in the background:

```bash
source venv/bin/activate
nohup python web_app.py > app.log 2>&1 &
```

Check logs:
```bash
tail -f app.log
```

Stop the application:
```bash
pkill -f "python web_app.py"
```

---

## Troubleshooting

### Python 3 Not Found

```bash
# Check Python version
python3 --version

# If not installed
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

### Permission Denied on run.sh

```bash
chmod +x run.sh
./run.sh
```

### Port 5000 Already in Use

Option 1: Stop the process using port 5000
```bash
lsof -i :5000
kill -9 <PID>
```

Option 2: Change Flask port in `web_app.py`
```bash
nano web_app.py
# Find: app.run(host='0.0.0.0', port=5000, ...)
# Change to: app.run(host='0.0.0.0', port=8000, ...)
```

### ModuleNotFoundError: No module named 'flask'

Ensure virtual environment is activated:
```bash
source venv/bin/activate
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Connection Error to API Gateway

- Verify `.env` file has correct API Gateway URL
- Check internet connectivity
- Ensure API Gateway endpoint is publicly accessible
- Check AWS security groups and CORS settings

### Timeout Error

Increase timeout in `config.py`:
```python
TIMEOUT = 30  # seconds (default is 10)
```

### Can't Access from Remote Server

1. Ensure Flask is listening on all interfaces (already configured)
2. Check firewall rules:
   ```bash
   sudo ufw allow 5000
   ```
3. Access using server IP:
   ```
   http://<server-ip>:5000
   ```

### API Gateway Returns 403 Forbidden

- Check API Gateway CORS settings
- Verify IAM permissions for Lambda execution
- Ensure API Key is not required (or add it to requests)

---

## Testing the Application

### Run Unit Tests

```bash
source venv/bin/activate
python -m unittest test_client.py -v
```

### Manual Testing

1. Open `http://localhost:5000` in browser
2. Fill in order details
3. Click "Place Order"
4. Copy the returned Order ID
5. Go to "Check Status" tab
6. Paste Order ID and check status

---

## Monitoring and Logs

### Application Logs

When running normally, logs appear in the terminal. For persistent logs:

```bash
python web_app.py > app.log 2>&1
```

View logs:
```bash
tail -f app.log
```

### AWS CloudWatch Logs

View Lambda execution logs in AWS CloudWatch:
1. Go to [CloudWatch Console](https://console.aws.amazon.com/cloudwatch)
2. Select **Log Groups**
3. Find `/aws/lambda/your-function-name`
4. View execution details

---

## Performance Tips

1. **Connection Pooling**: The client reuses HTTP connections
2. **Timeout Settings**: Adjust based on Lambda execution time
3. **Error Handling**: Graceful fallback for API failures
4. **Logging**: Disable debug mode in production

---

## Security Considerations

1. **Never commit `.env` file** to version control
2. **Use HTTPS** for production (API Gateway provides this)
3. **Restrict API Gateway** access with API keys or IAM
4. **Validate input** on both client and server
5. **Use environment variables** for sensitive data
6. **Enable AWS CloudTrail** for audit logging

---

## Advanced Configuration

### Custom Application Port

```bash
# Edit web_app.py
nano web_app.py

# Find and modify:
# app.run(host='0.0.0.0', port=5000, debug=DEBUG)

# Restart application
python web_app.py
```

### Using Gunicorn (Production)

```bash
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Using Nginx as Reverse Proxy

```bash
# Install Nginx
sudo apt-get install nginx

# Configure /etc/nginx/sites-available/default
# Proxy requests to localhost:5000
```

---

## Deployment Options

### Option 1: AWS EC2

1. Create EC2 instance (Ubuntu)
2. SSH into instance
3. Follow setup instructions
4. Expose port 5000 in security group

### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "web_app.py"]
```

Build and run:
```bash
docker build -t order-app .
docker run -p 5000:5000 order-app
```

### Option 3: Heroku

```bash
# Install Heroku CLI
# Create Procfile with: web: python web_app.py
# Deploy: git push heroku main
```

---

## Support and Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)

---

## License

This is a demonstration project for learning AWS serverless architecture.

---

## Quick Reference Commands

```bash
# Setup and activate
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your API Gateway URL

# Run application
python web_app.py

# Run tests
python -m unittest test_client.py -v

# Deactivate virtual environment
deactivate
```
