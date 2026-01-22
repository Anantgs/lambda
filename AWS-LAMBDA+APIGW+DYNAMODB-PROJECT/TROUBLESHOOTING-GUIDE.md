# AWS Lambda + API Gateway Troubleshooting Guide

This guide addresses common issues when deploying serverless order processing applications with Lambda, API Gateway, and DynamoDB.

---

## 🔴 Current Issues You're Experiencing

### Issue 1: Lambda Returns "Hello from Lambda!" Instead of Order Data

**Symptoms:**
```
Order placed successfully: "Hello from Lambda!"
```

**Root Cause:**
Your Lambda function still has the **default/template code** instead of the actual order processing code.

**Solution:**

1. **Go to Lambda Console**
2. Click on **`order-intake`** function
3. Look at the code editor
4. **If you see:**
   ```python
   def lambda_handler(event, context):
       return 'Hello from Lambda!'
   ```
   Then your code wasn't updated!

5. **Replace with this code:**

```python
import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

def lambda_handler(event, context):
    """
    Handler for API Gateway POST requests
    Receives order data and stores in DynamoDB
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse incoming request - handle both proxy and non-proxy integration
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare order item
        order_item = {
            'orderId': order_id,
            'timestamp': timestamp,
            'items': body.get('items', []),
            'paymentMethod': body.get('paymentMethod', 'card'),
            'customerEmail': body.get('customerEmail', 'unknown@example.com'),
            'status': 'PENDING',
            'totalAmount': sum(
                item.get('price', 0) * item.get('qty', 0) 
                for item in body.get('items', [])
            )
        }
        
        print(f"Storing order: {json.dumps(order_item, default=str)}")
        
        # Store in DynamoDB
        orders_table.put_item(Item=order_item)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Order received successfully',
                'orderId': order_id,
                'status': 'PENDING',
                'timestamp': timestamp,
                'totalAmount': order_item['totalAmount']
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e)
            })
        }
```

6. Click **"Deploy"** button
7. Test again

---

### Issue 2: 403 Forbidden Error on GET Requests

**Symptoms:**
```
Error fetching order status: 403 Client Error: Forbidden for url: ...
```

**Root Cause:**
The **GET method** is either:
1. Not configured in API Gateway
2. Not integrated with `order-status` Lambda function
3. Missing proper permissions

**Solutions:**

#### Solution A: Verify GET Method Exists in API Gateway

1. Go to **API Gateway Console**
2. Click on **`order-api`**
3. Click on **`/orders`** resource in the left sidebar
4. Look for **GET** method (should be listed under `/orders`)
5. If **GET is missing**, create it:
   - Click **"Create method"** → Select **"GET"**
   - **Integration type**: Lambda function
   - **Lambda function**: `order-status`
   - Check **"Lambda proxy integration"**
   - Click **"Create method"**

#### Solution B: Verify order-status Lambda Function Exists

1. Go to **Lambda Console**
2. Search for **`order-status`** function
3. If it **doesn't exist**, create it:
   - Click **"Create function"**
   - **Name**: `order-status`
   - **Runtime**: Python 3.12
   - **Create new role**
   - Click **"Create function"**

4. **Add this code to order-status:**

```python
import json
import boto3

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

def lambda_handler(event, context):
    """
    Get order status by order ID
    Supports both query parameters and path parameters
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Get order ID from different sources
        order_id = None
        
        # Check query parameters first (?orderId=xxx)
        if event.get('queryStringParameters') and event['queryStringParameters'].get('orderId'):
            order_id = event['queryStringParameters']['orderId']
        
        # Check path parameters ({id})
        elif event.get('pathParameters') and event['pathParameters'].get('id'):
            order_id = event['pathParameters']['id']
        
        # Extract from URL path (e.g., /orders/PROD-001)
        elif event.get('path'):
            path_parts = event['path'].split('/')
            if len(path_parts) > 2:
                order_id = path_parts[-1]
        
        print(f"Looking for order: {order_id}")
        
        if not order_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'orderId parameter required'})
            }
        
        # Fetch from DynamoDB
        response = orders_table.get_item(Key={'orderId': order_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Order {order_id} not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response['Item'], default=str)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
```

5. Click **"Deploy"**

#### Solution C: Add DynamoDB Permissions to order-status Lambda

1. Go to **Lambda Console** → **`order-status`** function
2. Scroll to **"Execution role"**
3. Click on the role name
4. Go to **"Permissions"** tab
5. Click **"Add permissions"** → **"Attach policies"**
6. Search for **`AmazonDynamoDBFullAccess`**
7. Select and click **"Attach policies"**

#### Solution D: Redeploy API Gateway

After updating Lambda functions, **redeploy your API**:

1. Go to **API Gateway** → **`order-api`**
2. Click **"Deploy API"** button
3. Select stage **`dev`**
4. Click **"Deploy"**

---

### Issue 3: Lambda Timeout Error

**Symptoms:**
```
Error: Task timed out after X seconds
```

**Solution:**

1. Go to **Lambda Console** → your function
2. Click **"Configuration"** tab
3. Click **"General configuration"** on left
4. Click **"Edit"**
5. Increase **"Timeout"** to **30 seconds** (from default 3 seconds)
6. Click **"Save"**

---

### Issue 4: "Invalid Lambda function" Error in API Gateway

**Symptoms:**
```
Error: Invalid Lambda function specified in target
```

**Solution:**

1. Ensure Lambda function exists in **same AWS region** as API Gateway
2. Ensure Lambda function name is spelled correctly
3. In API Gateway, delete the broken integration
4. Create it again:
   - **Integration type**: Lambda function
   - Select function from **dropdown** (don't type)
   - Check **"Lambda proxy integration"**
   - Click **"Create method"**

---

### Issue 5: CORS Errors in Browser

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**

1. Go to **API Gateway** → **`order-api`**
2. Click on **`/orders`** resource
3. Click **"Enable CORS"** button
4. Check all methods (POST, GET, OPTIONS)
5. Click **"Enable CORS and replace existing CORS headers"**
6. Go back and **"Deploy API"** again

---

### Issue 6: DynamoDB "Validation Exception" or "Table not found"

**Symptoms:**
```
ValidationException: Requested resource not found
```

**Solution:**

1. Go to **DynamoDB Console** → **"Tables"**
2. Verify table **`orders`** exists and is **"Active"**
3. If not active, wait a few more seconds
4. If table doesn't exist, create it:
   - **Table name**: `orders`
   - **Partition key**: `orderId` (String)
   - **Billing**: On-demand
   - **Create table**

---

### Issue 8: NameError: name 'python' is not defined

**Symptoms:**
```
[ERROR] NameError: name 'python' is not defined
File "/var/task/lambda_function.py", line 1, in <module>
    python
```

**Root Cause:**
Your Lambda code wasn't properly updated. The code file has just the word **`python`** on line 1, which is invalid Python syntax.

**Solution:**

#### Step 1: Clear the Lambda Code

1. Go to **Lambda Console** → **`order-intake`**
2. In the code editor, **select all text** (Ctrl+A)
3. **Delete everything**

#### Step 2: Paste Complete Code

Copy this **entire code** and paste it into the Lambda editor:

```python
import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

def lambda_handler(event, context):
    """
    Handler for API Gateway POST requests
    Receives order data and stores in DynamoDB
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse incoming request - handle both proxy and non-proxy integration
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare order item
        order_item = {
            'orderId': order_id,
            'timestamp': timestamp,
            'items': body.get('items', []),
            'paymentMethod': body.get('paymentMethod', 'card'),
            'customerEmail': body.get('customerEmail', 'unknown@example.com'),
            'status': 'PENDING',
            'totalAmount': sum(
                item.get('price', 0) * item.get('qty', 0) 
                for item in body.get('items', [])
            )
        }
        
        print(f"Storing order: {json.dumps(order_item, default=str)}")
        
        # Store in DynamoDB
        orders_table.put_item(Item=order_item)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Order received successfully',
                'orderId': order_id,
                'status': 'PENDING',
                'timestamp': timestamp,
                'totalAmount': order_item['totalAmount']
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e)
            })
        }
```

#### Step 3: Deploy

1. Click **"Deploy"** button
2. Wait for **"Changes deployed successfully"** message
3. Scroll down and check there are **no red errors**

#### Step 4: Test

Go back to your application and try placing an order again.

---

### Issue 8: Float types are not supported. Use Decimal types instead

**Symptoms:**
```
Error: Float types are not supported. Use Decimal types instead.
ValidationException: One or more parameter values were invalid
```

**Root Cause:**
DynamoDB doesn't support Python's native `float` type. You're trying to store price/quantity as floats, but DynamoDB requires `Decimal` type for numeric values.

**Solution:**

Update your `order-intake` Lambda code to use `Decimal`:

```python
import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

def lambda_handler(event, context):
    """
    Handler for API Gateway POST requests
    Receives order data and stores in DynamoDB
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse incoming request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Convert items and calculate total using Decimal
        items = []
        total_amount = Decimal('0')
        
        for item in body.get('items', []):
            qty = Decimal(str(item.get('qty', 0)))
            price = Decimal(str(item.get('price', 0)))
            
            items.append({
                'productId': item.get('productId', ''),
                'qty': qty,
                'price': price
            })
            total_amount += qty * price
        
        # Prepare order item
        order_item = {
            'orderId': order_id,
            'timestamp': timestamp,
            'items': items,
            'paymentMethod': body.get('paymentMethod', 'card'),
            'customerEmail': body.get('customerEmail', 'unknown@example.com'),
            'status': 'PENDING',
            'totalAmount': total_amount
        }
        
        print(f"Storing order: {json.dumps(order_item, default=str)}")
        
        # Store in DynamoDB
        orders_table.put_item(Item=order_item)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Order received successfully',
                'orderId': order_id,
                'status': 'PENDING',
                'timestamp': timestamp,
                'totalAmount': str(total_amount)
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e)
            })
        }
```

**Key changes:**
1. Added `from decimal import Decimal` at the top
2. Converted all numeric values to `Decimal` type
3. Use `Decimal(str(value))` to convert floats safely
4. When returning in JSON response, convert Decimal back to string: `str(total_amount)`

**Steps to fix order-intake:**

1. Go to **Lambda Console** → **`order-intake`**
2. **Select all code** (Ctrl+A) and **delete**
3. **Paste the corrected code** (with Decimal) from above
4. Click **"Deploy"**
5. Verify: **"Changes deployed successfully"** message appears

**Also update order-status Lambda:**

1. Go to **Lambda Console** → **`order-status`**
2. Replace with this code:

```python
import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

def decimal_default(obj):
    """JSON serializer for Decimal types"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def lambda_handler(event, context):
    """Get order status by order ID"""
    try:
        print(f"Received event: {json.dumps(event)}")
        
        order_id = None
        
        # Check query parameters
        if event.get('queryStringParameters') and event['queryStringParameters'].get('orderId'):
            order_id = event['queryStringParameters']['orderId']
        
        # Check path parameters
        elif event.get('pathParameters') and event['pathParameters'].get('id'):
            order_id = event['pathParameters']['id']
        
        # Extract from URL path
        elif event.get('path'):
            path_parts = event['path'].split('/')
            if len(path_parts) > 2:
                order_id = path_parts[-1]
        
        print(f"Looking for order: {order_id}")
        
        if not order_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'orderId parameter required'})
            }
        
        # Fetch from DynamoDB
        response = orders_table.get_item(Key={'orderId': order_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Order {order_id} not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response['Item'], default=decimal_default)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
```

3. Click **"Deploy"**

**Test again** - should work now!

---

### Issue 9: 403 Forbidden Error on GET Requests for Order Status

**Symptoms:**
```
Error fetching order status: 403 Client Error: Forbidden
```

**Root Cause:**
The GET method is either:
1. **Not properly configured** in API Gateway
2. **Missing authorization configuration**
3. **Not integrated with `order-status` Lambda**
4. **Authorization checks are blocking the request**

**Solution:**

#### Step 1: Verify GET Method Exists in API Gateway

1. Go to **API Gateway Console**
2. Click on **`order-api`**
3. Look at the **Resource tree** on the left
4. Click on **`/orders`** resource
5. You should see both **POST** and **GET** methods
6. If **GET is missing**, create it:
   - Click **"Create method"** → Select **"GET"**
   - **Integration type**: Lambda function
   - **Lambda function**: `order-status`
   - Check **"Lambda proxy integration"**
   - Click **"Create method"**
   - Click **"OK"** when prompted

#### Step 2: Remove Authorization from GET Method (if present)

1. Click on the **GET** method under `/orders`
2. Look for **"Authorization"** settings
3. If **"Authorization"** is set to anything other than **"NONE"**:
   - Click **"Authorization"**
   - Change to **"NONE"**
   - Click the **✓** checkmark to save
4. Scroll down and click **"Method Response"**
5. Expand **"200"** response
6. Make sure **"Content-Type"** is **"application/json"**

#### Step 3: Update Integration Response

1. Still on the GET method, click **"Integration Response"**
2. Expand **"200"** response
3. Under **"Header Mappings"**, verify:
   - `Content-Type` = `'application/json'`
4. Under **"Body Mapping Templates"**:
   - **Content-Type**: `application/json`
   - **Template**: Should be empty or have the response mapping

#### Step 4: Enable CORS (if needed)

1. Go back to `/orders` resource
2. Click **"Enable CORS"**
3. Check all boxes (GET, POST, OPTIONS, etc.)
4. Click **"Enable CORS and replace existing CORS headers"**
5. Click **"Yes, replace existing values"**

#### Step 5: Redeploy API Gateway

1. Click **"Deploy API"**
2. Select stage: **`dev`**
3. Click **"Deploy"**
4. Wait for **"Deployment successful"** message

#### Step 6: Test the GET Request

```bash
# Get your Order ID from a previous POST
curl "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders?orderId=YOUR_ORDER_ID"
```

**Expected response:**
```json
{
  "orderId": "012a7520-8592-4660-a06b-7692eb587c2e",
  "timestamp": "2026-01-20T19:23:19.028287",
  "items": [...],
  "status": "PENDING",
  "totalAmount": 109.97
}
```

**If still getting 403:**

#### Step 7: Check CloudWatch Logs

1. Go to **CloudWatch Console** → **"Logs"**
2. Find **`/aws/lambda/order-status`** log group
3. Click on the **latest log stream**
4. Look for error messages
5. If you see **permission errors**, verify the Lambda role has `AmazonDynamoDBFullAccess`

#### Step 8: Manually Test Lambda Function

1. Go to **Lambda Console** → **`order-status`**
2. Click **"Test"** tab
3. Create test event:

```json
{
  "queryStringParameters": {
    "orderId": "YOUR_ORDER_ID"
  }
}
```

4. Click **"Test"**
5. Look at **Execution result**
6. If it works, the issue is API Gateway configuration
7. If it fails, the issue is the Lambda function itself

---

### Issue 7: 502 Bad Gateway Error

**Symptoms:**
```
Response Status Code: 502
Error details: {
  "message": "Internal server error"
}
```

**Root Cause:**
Lambda function is throwing an **exception/error** and not returning a valid response. Most common reasons:
1. DynamoDB table doesn't exist
2. Lambda doesn't have DynamoDB permissions
3. Lambda code has syntax errors
4. Lambda times out
5. Lambda can't parse the request body

**Solution - Quick Debug Steps:**

#### Step 1: Check CloudWatch Logs

1. Go to **CloudWatch Console**
2. Click **"Logs"** → **"Log groups"**
3. Search for **`/aws/lambda/order-intake`**
4. Click on the log group
5. Click on the **latest log stream**
6. **Read the error message** - this tells you exactly what's wrong!

**Common error messages you might see:**

```
ResourceNotFoundException: Requested resource not found
```
→ **DynamoDB table doesn't exist**. Create it using DynamoDB Console.

```
User: arn:aws:iam::123456789:role/lambda-order-intake-role is not authorized to perform: dynamodb:PutItem
```
→ **Missing DynamoDB permissions**. Add `AmazonDynamoDBFullAccess` policy to Lambda role.

```
SyntaxError: invalid syntax
```
→ **Code has Python errors**. Fix the code syntax.

```
ConnectionError: Failed to establish a new connection
```
→ **Lambda can't reach DynamoDB** (rare, usually VPC issue)

#### Step 2: Verify DynamoDB Table Exists

```bash
# Using AWS CLI
aws dynamodb describe-table --table-name orders --region us-east-1
```

If table doesn't exist:
1. Go to **DynamoDB Console** → **"Tables"**
2. Click **"Create table"**
3. **Table name**: `orders`
4. **Partition key**: `orderId` (String)
5. **Billing mode**: On-demand
6. Click **"Create table"**
7. **Wait for status to become "Active"** (takes ~30 seconds)

#### Step 3: Verify Lambda Permissions

1. Go to **Lambda Console** → **`order-intake`**
2. Scroll to **"Execution role"**
3. Click on **role name** (opens in new tab)
4. Go to **"Permissions"** tab
5. Verify **`AmazonDynamoDBFullAccess`** is listed
6. If not, click **"Add permissions"** → **"Attach policies"**
7. Search and select **`AmazonDynamoDBFullAccess`**

#### Step 4: Test Lambda Directly

1. Go to **Lambda Console** → **`order-intake`**
2. Click **"Test"** tab
3. Create a test event with this JSON:
```json
{
  "body": "{\"items\": [{\"productId\": \"P1\", \"qty\": 1, \"price\": 29.99}], \"paymentMethod\": \"card\", \"customerEmail\": \"test@example.com\"}"
}
```
4. Click **"Test"**
5. Look at the **"Execution result"**
6. If it shows **error details**, read them carefully

#### Step 5: Check Lambda Code

Make sure your `order-intake` function has this structure:

```python
def lambda_handler(event, context):
    try:
        # Your code here
        return {
            'statusCode': 200,
            'body': json.dumps({...})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**Important:** Must return a dict with `statusCode` and `body` keys!

#### Step 6: Increase Timeout

1. Lambda Console → `order-intake`
2. Click **"Configuration"**
3. Click **"General configuration"** → **"Edit"**
4. Set **Timeout** to **30 seconds**
5. Click **"Save"**

#### Step 7: Redeploy API Gateway

1. Go to **API Gateway** → **`order-api`**
2. Click **"Deploy API"**
3. Select stage **`dev`**
4. Click **"Deploy"**

**Expected result after all steps:**
- CloudWatch logs show **no errors**
- Response should be `statusCode: 200`
- Response should include `orderId`

---

## ✅ Complete Verification Checklist

Use this checklist to verify your setup:

- [ ] **Lambda: order-intake**
  - [ ] Function exists
  - [ ] Code is NOT "Hello from Lambda!"
  - [ ] Has DynamoDB permissions
  - [ ] Timeout: 30 seconds
  - [ ] Deployed (shows "Changes deployed" message)

- [ ] **Lambda: order-status**
  - [ ] Function exists
  - [ ] Code is NOT "Hello from Lambda!"
  - [ ] Has DynamoDB permissions
  - [ ] Timeout: 30 seconds
  - [ ] Deployed

- [ ] **API Gateway: order-api**
  - [ ] API exists
  - [ ] Resource `/orders` exists
  - [ ] POST method exists and integrated with `order-intake`
  - [ ] GET method exists and integrated with `order-status`
  - [ ] Both methods have "Lambda proxy integration" enabled
  - [ ] Stage `dev` deployed
  - [ ] CORS enabled

- [ ] **DynamoDB: orders table**
  - [ ] Table exists
  - [ ] Status is "Active"
  - [ ] Partition key: `orderId` (String)
  - [ ] Billing: On-demand

- [ ] **IAM Permissions**
  - [ ] Both Lambda roles have DynamoDB read/write permissions

---

## 🔧 Step-by-Step Fix (Quick Start)

Follow these steps in order to fix your current issues:

### Step 1: Fix order-intake Lambda

1. Lambda Console → `order-intake`
2. **Clear the code** and paste the complete code from **Issue 1** above
3. Click **"Deploy"**
4. Verify no errors

### Step 2: Create/Fix order-status Lambda

1. Lambda Console → `order-status` (create if missing)
2. **Replace code** with code from **Solution B** above
3. Add **DynamoDB permissions** from **Solution C** above
4. Click **"Deploy"**

### Step 3: Verify API Gateway Methods

1. API Gateway → `order-api` → `/orders`
2. Verify **GET** and **POST** methods exist
3. Both should have green checkmarks

### Step 4: Redeploy API Gateway

1. Click **"Deploy API"**
2. Stage: `dev`
3. Click **"Deploy"**

### Step 5: Test

```bash
# Test POST
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders \
  -H "Content-Type: application/json" \
  -d '{"items": [{"productId": "P1", "qty": 1, "price": 29.99}], "paymentMethod": "card", "customerEmail": "test@example.com"}'

# Test GET
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders?orderId=YOUR_ORDER_ID
```

---

## 📊 Debug Output

To see what's happening inside Lambda:

1. Go to **CloudWatch Logs**
2. Search for your **Lambda function name** (e.g., `/aws/lambda/order-intake`)
3. Click on the latest **log stream**
4. Look for `print()` statements in the code output

This shows you exactly what data is being received and processed.

---

## 🆘 Still Stuck?

Provide these details:

1. What's the **exact error message**?
2. Screenshot of **Lambda code** (to verify it was updated)
3. Screenshot of **API Gateway methods** (POST, GET, etc.)
4. Output of:
   ```bash
   curl -v https://YOUR_API.execute-api.us-east-1.amazonaws.com/dev/orders
   ```
5. **CloudWatch Logs** from the Lambda function

---

## 📚 Useful Links

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Proxy Integration](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)
- [CloudWatch Logs for Lambda](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
