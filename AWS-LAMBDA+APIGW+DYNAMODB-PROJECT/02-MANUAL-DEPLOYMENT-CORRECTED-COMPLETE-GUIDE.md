# ✅ Complete Corrected Guide: Lambda → API Gateway → DynamoDB

**Status:** Fixes all issues from previous guide  
**Last Updated:** January 21, 2026

---

## 📋 Quick Overview

```
POST /orders              → order-intake Lambda → DynamoDB (STORE)
GET  /orders/{orderId}    → order-status Lambda → DynamoDB (RETRIEVE)
```

**Key Fix:** GET endpoint uses PATH PARAMETER `{orderId}`, NOT query string!

---

# PART 1: CREATE DYNAMODB TABLE FIRST

## Step 1: Create DynamoDB Table

1. **AWS Console** → Search **"DynamoDB"** → Click **DynamoDB**
2. Click **"Create table"** button
3. **Fill in:**

   | Field | Value |
   |-------|-------|
   | **Table name** | `orders` |
   | **Partition key** | `orderId` |
   | **Key type** | String |
   | **Billing mode** | Pay-per-request (On-demand) |

4. Click **"Create table"** button
5. **Wait** for status to show **"ACTIVE"** (takes ~30 seconds)

**✅ DynamoDB table ready!**

---

# PART 2: CREATE LAMBDA FUNCTION #1 - order-intake

## Step 1: Create Lambda Function

1. **AWS Console** → Search **"Lambda"** → Click **Lambda**
2. Click **"Create function"** button (orange)
3. **Configure:**

   | Field | Value |
   |-------|-------|
   | **Function name** | `order-intake` |
   | **Runtime** | Python 3.12 |
   | **Architecture** | x86_64 |
   | **Permissions** | Create new role with basic Lambda permissions |

4. Click **"Create function"**

## Step 2: Add Code to order-intake

Replace the default code with this:

```python
import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")
        
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
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
        orders_table.put_item(Item=order_item)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
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
            'body': json.dumps({'error': str(e)})
        }
```

## Step 3: Deploy order-intake

1. Click **"Deploy"** button (top right)
2. Wait for **"Changes deployed successfully"** message

## Step 4: Add DynamoDB Permissions

1. Scroll down to **"Execution role"** section
2. Click on the **role name** (looks like `order-intake-role-xxxxxxxxx`)
3. New tab opens → **IAM Console**
4. Click **"Add permissions"** → **"Attach policies"**
5. Search: `AmazonDynamoDBFullAccess`
6. Check the checkbox and click **"Attach policies"**

**✅ order-intake Lambda ready!**

---

# PART 3: CREATE LAMBDA FUNCTION #2 - order-status

## Step 1: Create Lambda Function

1. **AWS Console** → **Lambda** → **"Create function"** button
2. **Configure:**

   | Field | Value |
   |-------|-------|
   | **Function name** | `order-status` |
   | **Runtime** | Python 3.12 |
   | **Architecture** | x86_64 |
   | **Permissions** | Create new role |

3. Click **"Create function"**

## Step 2: Add Code to order-status

Replace the default code with this:

```python
import json
import boto3

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('orders')

def lambda_handler(event, context):
    """
    Get order status by order ID from path parameter
    """
    try:
        # Get order ID from path parameter (not query string!)
        path_parameters = event.get('pathParameters', {})
        order_id = path_parameters.get('orderId') if path_parameters else None
        
        if not order_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'orderId path parameter required'})
            }
        
        # Fetch from DynamoDB
        response = orders_table.get_item(Key={'orderId': order_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Order not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(response['Item'], default=str)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
```

## Step 3: Deploy order-status

1. Click **"Deploy"** button (top right)
2. Wait for success message

## Step 4: Add DynamoDB Permissions

1. Scroll to **"Execution role"**
2. Click the **role name**
3. **"Add permissions"** → **"Attach policies"**
4. Search: `AmazonDynamoDBFullAccess`
5. Check and click **"Attach policies"**

**✅ order-status Lambda ready!**

---

# PART 4: CREATE API GATEWAY

## Step 1: Create REST API

1. **AWS Console** → Search **"API Gateway"** → Click **API Gateway**
2. Click **"Create API"** button
3. Choose **"REST API"** → Click **"Build"**
4. **Configure:**

   | Field | Value |
   |-------|-------|
   | **API name** | `order-api` |
   | **Endpoint type** | Regional |
   | **Description** | Serverless Order Processing |

5. Click **"Create API"**

## Step 2: Create /orders Resource

1. In the left panel, right-click **"/"** (root)
2. Click **"Create resource"**
3. **Fill in:**
   - **Resource name**: `orders`
   - **Resource path**: `/`
   - **CORS**: Leave unchecked
4. Click **"Create resource"**

**✅ `/orders` resource created**

## Step 3: Create POST Method on /orders

1. Click on **`/orders`** resource (in left panel)
2. Click **"Create method"** → Select **"POST"**
3. **Fill in:**

   | Field | Value |
   |-------|-------|
   | **Integration type** | Lambda function |
   | **Lambda function** | `order-intake` |
   | **Lambda proxy integration** | ✅ CHECK THIS |

4. Click **"Create method"**
5. **Popup appears:** Click **"OK"** to grant permissions

**✅ POST /orders → order-intake**

---

## Step 4: Create {orderId} Path Parameter Resource

⭐ **THIS IS THE KEY FIX FROM THE OLD GUIDE!**

1. Click on **`/orders`** resource (in left panel)
2. Right-click **`/orders`** → **"Create resource"**
3. **Fill in:**
   - **Resource name**: `{orderId}`
   - **Resource path**: `{orderId}` (will auto-fill as `/orders/{orderId}`)
   - **CORS**: Leave unchecked
4. Click **"Create resource"**

**✅ `/orders/{orderId}` resource created**

---

## Step 5: Create GET Method on {orderId}

1. Click on **`{orderId}`** resource (in left panel)
2. Click **"Create method"** → Select **"GET"**
3. **Fill in:**

   | Field | Value |
   |-------|-------|
   | **Integration type** | Lambda function |
   | **Lambda function** | `order-status` |
   | **Lambda proxy integration** | ✅ CHECK THIS |

4. Click **"Create method"**
5. **Popup appears:** Click **"OK"** to grant permissions

**✅ GET /orders/{orderId} → order-status**

---

## Step 6: Deploy API

1. Click **"Deploy API"** button (top right, orange)
2. **Configure deployment:**
   - **Stage name**: `dev`
   - **Description**: Development stage
3. Click **"Deploy"**
4. **Copy the Invoke URL** - this is your API endpoint!

Example:
```
https://e5l851853a.execute-api.us-east-1.amazonaws.com/dev
```

**✅ API Gateway deployed!**

---

# PART 5: TEST YOUR API

## Test 1: Create an Order (POST)

```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "productId": "PROD-001",
        "qty": 2,
        "price": 29.99
      }
    ],
    "paymentMethod": "card",
    "customerEmail": "customer@example.com"
  }'
```

**Expected Response:**
```json
{
  "message": "Order received successfully",
  "orderId": "96d0f981-fb95-4b85-aedd-0aeb16b5bdef",
  "status": "PENDING",
  "timestamp": "2026-01-21T04:42:54.444578",
  "totalAmount": "59.98"
}
```

## Test 2: Fetch Order Status (GET)

```bash
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders/96d0f981-fb95-4b85-aedd-0aeb16b5bdef
```

**Expected Response:**
```json
{
  "orderId": "96d0f981-fb95-4b85-aedd-0aeb16b5bdef",
  "timestamp": "2026-01-21T04:42:54.444578",
  "items": [
    {
      "productId": "PROD-001",
      "qty": 2,
      "price": 29.99
    }
  ],
  "paymentMethod": "card",
  "customerEmail": "customer@example.com",
  "status": "PENDING",
  "totalAmount": "59.98"
}
```

---

# PART 6: FINAL CHECKLIST

## ✅ Verification Checklist

- [ ] **DynamoDB Table**
  - [ ] Table name: `orders`
  - [ ] Status: ACTIVE
  - [ ] Partition key: `orderId` (String)

- [ ] **Lambda Function #1 - order-intake**
  - [ ] Runtime: Python 3.12
  - [ ] Role has: AmazonDynamoDBFullAccess
  - [ ] Code deployed successfully
  - [ ] Timeout: 3+ seconds

- [ ] **Lambda Function #2 - order-status**
  - [ ] Runtime: Python 3.12
  - [ ] Role has: AmazonDynamoDBFullAccess
  - [ ] Code deployed successfully
  - [ ] Uses `pathParameters` (NOT queryStringParameters)

- [ ] **API Gateway - order-api**
  - [ ] Resource `/orders` with POST method
  - [ ] Resource `/orders/{orderId}` with GET method
  - [ ] Both methods use Lambda proxy integration
  - [ ] Deployed to `dev` stage
  - [ ] Invoke URL obtained

- [ ] **Testing**
  - [ ] POST request creates order ✅
  - [ ] GET request retrieves order ✅
  - [ ] Order appears in DynamoDB ✅

---

# 🚨 KEY DIFFERENCES FROM OLD GUIDE

| Issue | Old Guide | Corrected Guide |
|-------|-----------|-----------------|
| GET Endpoint | `/orders` (same as POST!) | `/orders/{orderId}` (path parameter) |
| Parameter Extraction | `queryStringParameters` | `pathParameters` |
| Resource Structure | Single `/orders` for POST & GET | Separate `/orders` and `/orders/{orderId}` |
| Lambda Code | Used `queryStringParameters` | Uses `pathParameters` |
| API Gateway | Unclear routing | Clear 2-resource structure |

---

# 📊 Architecture Diagram

```
Client
  │
  ├─→ POST /orders (+ JSON body)
  │      │
  │      └→ API Gateway
  │          │
  │          └→ Lambda: order-intake
  │              │
  │              └→ DynamoDB: stores order
  │                  │
  │                  └→ Returns: orderId
  │
  └─→ GET /orders/{orderId}
         │
         └→ API Gateway
             │
             └→ Lambda: order-status
                 │
                 └→ DynamoDB: retrieves order
                     │
                     └→ Returns: order details
```

---

# 🎯 Summary

You now have:
- ✅ **DynamoDB table** (orders)
- ✅ **2 Lambda functions** (order-intake, order-status)
- ✅ **API Gateway** with proper routing
- ✅ **All permissions configured**
- ✅ **Tested and working**

**Next:** Use this API in your Python applications! 🚀

---

**Questions?** Check CloudWatch logs:
```bash
aws logs tail /aws/lambda/order-status --follow --region us-east-1
```
