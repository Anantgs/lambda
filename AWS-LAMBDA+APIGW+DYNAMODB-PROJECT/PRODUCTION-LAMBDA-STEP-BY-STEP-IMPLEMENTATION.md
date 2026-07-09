# Production Lambda Concepts - Step By Step Implementation

Use this guide after the basic API is working:

```text
Client / Web App
  -> API Gateway
  -> order-intake Lambda
  -> DynamoDB orders table
```

This guide is manual-first. The purpose is to learn what happens inside AWS before moving to Terraform, SAM, or CI/CD.

---

## Before You Start

Make sure these are already working:

- DynamoDB table: `orders`
- Lambda function: `order-intake`
- Lambda function: `order-status`
- API Gateway: `order-api`
- Endpoint: `POST /orders`
- Endpoint: `GET /orders/{orderId}`

Test one order first:

```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders \
  -H "Content-Type: application/json" \
  -d '{"items":[{"productId":"P1","qty":1,"price":10}],"paymentMethod":"card","customerEmail":"test@example.com"}'
```

If this works, continue.

---

# 1. Implement CloudWatch Logging

## Goal

Add useful logs to Lambda and verify them in CloudWatch.

## Why

In production, logs help you understand what happened inside Lambda.

## Step 1: Open Lambda

1. Go to AWS Console.
2. Search for **Lambda**.
3. Open function **`order-intake`**.
4. Go to the **Code** tab.

## Step 2: Add Logs



Inside `lambda_handler`, add logs like this (add it as it is):

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
        print("START order-intake")
        print(f"AWS Request ID: {context.aws_request_id}")
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

        print("Saving order to DynamoDB")
        orders_table.put_item(Item=order_item)
        print(f"Order saved successfully: {order_id}")

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
        print(f"ERROR in order-intake: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
```

If you do not want to raise the error, keep your existing `return statusCode 500` block. For learning, raising once is useful because CloudWatch shows the failure clearly.

## Step 3: Deploy

1. Click **Deploy**.
2. Wait for success message.

## Step 4: Invoke API

Run your POST request again.

## Step 5: Check Logs

1. Go to **CloudWatch**.
2. Click **Log groups**.
3. Open:

```text
/aws/lambda/order-intake
```

4. Open latest log stream.
5. Observe:

```text
START
Received event
Saving order
Order saved successfully
END
REPORT
```

## What To Teach

CloudWatch logs are the first place to check when Lambda fails.

## Interview Line

CloudWatch Logs capture Lambda execution details, custom application logs, errors, duration, billed duration, and request IDs.

---

# 2. Test Cold Start

## Goal

Observe cold start and warm start behavior.

## Why

Cold starts can cause occasional slow API responses.

## Step 1: Invoke Lambda After Idle Time

1. Wait 10-15 minutes without invoking `order-intake`.
2. Invoke the API once.

## Step 2: Check CloudWatch REPORT Line

In CloudWatch logs, open the latest log stream and check the `REPORT` line.

You may see:

```text
REPORT RequestId: ... Duration: 350 ms Billed Duration: 400 ms Init Duration: 220 ms
```

`Init Duration` means cold start initialization happened.

## Step 3: Invoke Again Immediately

Invoke the API again within a few seconds.

Check the new `REPORT` line.

Usually you will not see `Init Duration`, or the execution will be faster.

## What To Compare

| Invocation | Expected Behavior |
|---|---|
| First after idle | May show Init Duration |
| Immediate second call | Usually faster warm start |

## What To Teach

Cold start is extra startup time before handler execution.

## Interview Line

Cold start happens when Lambda creates a new execution environment and initializes runtime/code before running the handler.

---

# 3. Implement Timeout Test

## Goal

Force a Lambda timeout and observe the production failure.

## Why

Timeout controls maximum Lambda execution time.

## Step 1: Add Temporary Sleep

Open `order-intake` code.

Add this import:

```python
import time
```

At the beginning of `lambda_handler`, add:

```python
print("Sleeping for timeout test")
time.sleep(5)
```

## Step 2: Set Timeout To 2 Seconds

1. Open Lambda **`order-intake`**.
2. Go to **Configuration**.
3. Click **General configuration**.
4. Click **Edit**.
5. Set timeout:

```text
2 seconds
```

6. Save.

## Step 3: Invoke API

Send POST request again.

## Step 4: Observe Error

In CloudWatch logs, observe:

```text
Task timed out after 2.00 seconds
```

The client may receive a 500 or 502 depending on API Gateway behavior.

## Step 5: Clean Up

Remove:

```python
time.sleep(5)
```

Set timeout back to something safe for this demo:

```text
10 seconds or 30 seconds
```

## What To Teach

Timeout prevents stuck execution, but wrong timeout can break valid requests.

## Interview Line

Lambda timeout should be configured based on expected processing time and downstream service behavior.

---

# 4. Implement Memory Tuning Test

## Goal

Compare execution duration at different memory settings.

## Why

Lambda memory also affects CPU. More memory can make code run faster.

## Step 1: Open Memory Setting

1. Lambda -> `order-intake`.
2. Configuration -> General configuration.
3. Click **Edit**.

## Step 2: Test Memory Values

Test these one by one:

```text
128 MB
256 MB
512 MB
1024 MB
```

For each value:

1. Save memory setting.
2. Invoke same POST request 3-5 times.
3. Open CloudWatch logs.
4. Record the `REPORT` values:

```text
Duration
Billed Duration
Max Memory Used
```

## Step 3: Create Comparison Table

Use this table:

| Memory | Duration | Billed Duration | Max Memory Used | Notes |
|---|---:|---:|---:|---|
| 128 MB | | | | |
| 256 MB | | | | |
| 512 MB | | | | |
| 1024 MB | | | | |

## What To Teach

Higher memory can reduce duration. Cost depends on memory and time together.

## Interview Line

Lambda memory tuning is both a performance and cost optimization activity because memory allocation also changes CPU allocation.

---

# 5. Implement Concurrency Test

## Goal

Send multiple requests and observe concurrency/throttling.

## Why

Lambda can scale quickly, but downstream systems may not be able to handle unlimited traffic.

## Step 1: Set Reserved Concurrency

1. Open Lambda -> `order-intake`.
2. Go to **Configuration**.
3. Click **Concurrency**.
4. Click **Edit**.
5. Enable **Reserved concurrency**.
6. Set:

```text
2
```

7. Save.

## Step 2: Send Multiple Requests

Option A: Use `hey` if installed:

```bash
hey -n 50 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"items":[{"productId":"P1","qty":1,"price":10}],"paymentMethod":"card","customerEmail":"test@example.com"}' \
  https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders
```

Option B: Use a simple loop:

```bash
for i in {1..50}; do
  curl -s -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders \
    -H "Content-Type: application/json" \
    -d "{\"items\":[{\"productId\":\"P$i\",\"qty\":1,\"price\":10}],\"paymentMethod\":\"card\",\"customerEmail\":\"test@example.com\"}" &
done
wait
```

## Step 3: Check Metrics

Go to CloudWatch -> Metrics -> Lambda -> By Function Name -> `order-intake`.

Check:

```text
ConcurrentExecutions
Throttles
Errors
Duration
```

## Step 4: Clean Up

After test, remove reserved concurrency or set it to a realistic value.

## What To Teach

Reserved concurrency limits how much a function can scale and protects downstream systems.

## Interview Line

Reserved concurrency is used to control Lambda scaling and prevent a function from overwhelming downstream dependencies.

---

# 6. Implement Retry Behavior Test

## Goal

Understand how retry depends on the event source.

## Why

API Gateway, async Lambda, SQS, and streams do not retry the same way.

## Important For This Project

Your current flow is:

```text
API Gateway -> Lambda
```

This is synchronous.

That means API Gateway waits for Lambda response and returns success or failure to the client.

API Gateway does not keep retrying your Lambda like SQS.

## Step 1: Force Lambda Failure

In `order-intake`, temporarily add:

```python
raise Exception("Testing retry behavior")
```

Place it near the beginning of `lambda_handler`.

## Step 2: Deploy

Click **Deploy**.

## Step 3: Invoke API

Send POST request.

## Step 4: Observe

Client receives an error.

CloudWatch logs show the exception.

You should not expect automatic repeated retries from API Gateway.

## Step 5: Clean Up

Remove:

```python
raise Exception("Testing retry behavior")
```

Deploy again.

## What To Teach

Retry behavior depends on trigger type.

| Trigger | Retry Style |
|---|---|
| API Gateway | No automatic app-level retry; client gets response |
| Async Lambda invoke | AWS retries failed event |
| SQS | Message returns to queue and can go to DLQ |
| Streams | Batch retry behavior applies |

## Interview Line

Lambda retry behavior depends on the event source, so production code must be designed for repeated execution when retries are possible.

---

# 7. Implement Idempotency

## Goal

Prevent duplicate orders when the same request is sent more than once.

## Why

Retries, user double-clicks, and network failures can send the same request again.

## Current Problem

If Lambda always generates a new `orderId`, duplicate requests create duplicate orders.

For idempotency testing, allow the client to send an `orderId`.

## Step 1: Modify Request Body

Use this request format:

```json
{
  "orderId": "ORD-1001",
  "items": [
    {"productId": "P1", "qty": 1, "price": 10}
  ],
  "paymentMethod": "card",
  "customerEmail": "test@example.com"
}
```

## Step 2: Modify Lambda orderId Logic

In `order-intake`, replace always-generated order ID logic with:

```python
order_id = body.get("orderId") or str(uuid.uuid4())
```

## Step 3: Use Conditional Write

Replace:

```python
orders_table.put_item(Item=order_item)
```

With:

```python
orders_table.put_item(
    Item=order_item,
    ConditionExpression="attribute_not_exists(orderId)"
)
```

## Step 4: Handle Duplicate Error

Add import:

```python
from botocore.exceptions import ClientError
```

Wrap DynamoDB write:

```python
try:
    orders_table.put_item(
        Item=order_item,
        ConditionExpression="attribute_not_exists(orderId)"
    )
except ClientError as e:
    if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
        return {
            "statusCode": 409,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": "Duplicate order ignored",
                "orderId": order_id
            })
        }
    raise
```

## Step 5: Test Duplicate Request

Send same request twice:

```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId":"ORD-1001","items":[{"productId":"P1","qty":1,"price":10}],"paymentMethod":"card","customerEmail":"test@example.com"}'
```

Expected:

- First request creates order.
- Second request returns duplicate response or does not create a second item.

## What To Teach

Retries are safe only when operations are idempotent.

## Interview Line

Idempotency ensures repeated invocations do not create duplicate side effects such as duplicate orders or payments.

---

# 8. Implement Versioning And Alias

## Goal

Create safe deployment and rollback using Lambda versions and aliases.

## Why

Production traffic should not point directly to changing code.

## Step 1: Publish Version 1

1. Open Lambda -> `order-intake`.
2. Make sure code is working.
3. Click **Actions**.
4. Click **Publish new version**.
5. Description:

```text
v1 stable order intake
```

6. Publish.

## Step 2: Create Alias

1. Go to **Aliases** tab.
2. Click **Create alias**.
3. Name:

```text
prod
```

4. Point it to version `1`.
5. Save.

## Step 3: Create Version 2

1. Change Lambda response message slightly.
2. Deploy code.
3. Publish new version.
4. Description:

```text
v2 updated response
```

## Step 4: Move Alias

1. Open alias `prod`.
2. Change version from `1` to `2`.
3. Save.

## Step 5: Rollback

If v2 has issue:

1. Open alias `prod`.
2. Change version back to `1`.
3. Save.

## Important Note

If API Gateway is integrated directly with the function name, it invokes `$LATEST` unless configured with alias ARN.

For production, API Gateway should integrate with alias ARN, such as:

```text
arn:aws:lambda:REGION:ACCOUNT_ID:function:order-intake:prod
```

## What To Teach

Aliases make rollback quick and controlled.

## Interview Line

Lambda versions are immutable snapshots, and aliases are movable pointers used for safe deployment and rollback.

---

# 9. Implement Cost Awareness

## Goal

Understand what increases cost in this project.

## Why

Serverless is pay-per-use, not automatically cheap.

## Step 1: Collect Execution Data

From CloudWatch `REPORT` lines, collect:

```text
Duration
Billed Duration
Memory Size
Max Memory Used
```

## Step 2: Compare Memory Tests

Use data from memory tuning:

| Memory | Avg Duration | Billed Duration | Notes |
|---|---:|---:|---|
| 128 MB | | | |
| 256 MB | | | |
| 512 MB | | | |
| 1024 MB | | | |

## Step 3: List Cost Components

For this project, cost can come from:

- Lambda requests
- Lambda GB-seconds
- API Gateway requests
- DynamoDB reads/writes
- CloudWatch log ingestion/storage
- X-Ray traces, if enabled later

## Step 4: Check AWS Cost Explorer

1. Go to AWS Console.
2. Open **Cost Explorer**.
3. Filter by services:
   - Lambda
   - API Gateway
   - DynamoDB
   - CloudWatch

## What To Teach

Cost is affected by architecture and code behavior.

## Interview Line

Lambda cost optimization includes tuning memory, reducing duration, controlling logs, and avoiding unnecessary invocations.

---

# Recommended Class Flow

Use this order during teaching:

```text
1. CloudWatch Logging
2. Cold Start
3. Timeout
4. Memory Tuning
5. Concurrency
6. Retry Behavior
7. Idempotency
8. Versioning and Alias
9. Cost Awareness
```

# Final Production Lesson

A Lambda project becomes production-ready when you can observe it, tune it, control failures, prevent duplicates, deploy safely, and explain its cost.
