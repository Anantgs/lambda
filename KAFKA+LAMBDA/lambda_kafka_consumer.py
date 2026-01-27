"""
AWS Lambda Function for Kafka Message Consumption
This Lambda function consumes messages from a Kafka topic and can:
1. Store them in DynamoDB
2. Log them to CloudWatch
3. Process and transform the data
4. Send notifications on specific event types
"""
import os
import json
import base64
import boto3
import logging
from datetime import datetime
from typing import Dict, List, Any

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables (set these in Lambda configuration)
# DYNAMODB_TABLE_NAME
# SNS_TOPIC_ARN
# S3_BUCKET_NAME
# PROCESS_EVENT_TYPES - comma-separated list of event types to process


class KafkaMessageHandler:
    """Handler for Kafka messages received by Lambda"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.messages_by_type = {}
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a single Kafka message
        
        Args:
            message: Parsed JSON message from Kafka
            
        Returns:
            bool: True if processing successful, False otherwise
        """
        try:
            event_type = message.get('event_type', 'unknown')
            user_id = message.get('user_id')
            timestamp = message.get('timestamp')
            
            # Track event types
            if event_type not in self.messages_by_type:
                self.messages_by_type[event_type] = 0
            self.messages_by_type[event_type] += 1
            
            # Log message details
            logger.info(f"Processing {event_type} event from user {user_id} at {timestamp}")
            
            # Store in DynamoDB
            self._store_in_dynamodb(message)
            
            # Check for alert-worthy events
            self._check_for_alerts(message)
            
            # Send metrics to CloudWatch
            self._send_metrics(event_type)
            
            self.processed_count += 1
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            self.error_count += 1
            return False
    
    def _store_in_dynamodb(self, message: Dict[str, Any]) -> None:
        """Store message in DynamoDB"""
        try:
            table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'kafka-messages')
            table = dynamodb.Table(table_name)
            
            item = {
                'message_id': f"{message.get('id', 'unknown')}#{datetime.now().timestamp()}",
                'timestamp': datetime.now().isoformat(),
                'event_type': message.get('event_type'),
                'user_id': message.get('user_id'),
                'message_data': json.dumps(message),
                'ttl': int(datetime.now().timestamp()) + (30 * 24 * 60 * 60)  # 30 days TTL
            }
            
            table.put_item(Item=item)
            logger.info(f"Stored message {item['message_id']} in DynamoDB")
            
        except Exception as e:
            logger.error(f"DynamoDB storage error: {str(e)}")
            raise
    
    def _check_for_alerts(self, message: Dict[str, Any]) -> None:
        """Check if message should trigger an alert"""
        try:
            event_type = message.get('event_type')
            alert_types = ['error', 'suspicious_login']  # Customize as needed
            
            if event_type in alert_types:
                sns_topic = os.environ.get('SNS_TOPIC_ARN')
                if sns_topic:
                    sns.publish(
                        TopicArn=sns_topic,
                        Subject=f"Alert: {event_type} event detected",
                        Message=f"Event Details:\n{json.dumps(message, indent=2)}"
                    )
                    logger.info(f"Alert sent for {event_type} event")
        
        except Exception as e:
            logger.error(f"Alert check error: {str(e)}")
    
    def _send_metrics(self, event_type: str) -> None:
        """Send custom metrics to CloudWatch"""
        try:
            cloudwatch.put_metric_data(
                Namespace='KafkaConsumer',
                MetricData=[
                    {
                        'MetricName': 'EventCount',
                        'Value': 1,
                        'Unit': 'Count',
                        'Dimensions': [
                            {'Name': 'EventType', 'Value': event_type}
                        ]
                    }
                ]
            )
        except Exception as e:
            logger.warning(f"CloudWatch metric error: {str(e)}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'messages_by_type': self.messages_by_type
        }


def lambda_handler(event, context):
    """
    Main Lambda handler for Kafka event source mapping
    
    AWS Lambda for Apache Kafka works with EventBridge or self-managed Kafka clusters.
    Messages come in as base64-encoded Kafka records.
    
    Args:
        event: Lambda event containing Kafka records
        context: Lambda context object
        
    Returns:
        dict: Response with status and processing summary
    """
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    handler = KafkaMessageHandler()
    
    try:
        # Extract records from event
        records = event.get('records', {})
        
        if not records:
            logger.warning("No records found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No records in event'})
            }
        
        # Process each topic's records
        for topic, message_list in records.items():
            logger.info(f"Processing {len(message_list)} messages from topic: {topic}")
            
            for record in message_list:
                try:
                    # Decode base64 message value
                    message_value = base64.b64decode(record['value']).decode('utf-8')
                    message = json.loads(message_value)
                    
                    # Process the message
                    handler.process_message(message)
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in message: {message_value}")
                    handler.error_count += 1
                except Exception as e:
                    logger.error(f"Error processing record: {str(e)}", exc_info=True)
                    handler.error_count += 1
        
        summary = handler.get_summary()
        logger.info(f"Processing complete. Summary: {summary}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(summary)
        }
    
    except Exception as e:
        logger.error(f"Lambda execution error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def lambda_handler_direct_poll(event, context):
    """
    Alternative handler for direct Kafka polling (self-managed cluster)
    Use this if you're directly polling from Kafka instead of using event source mapping
    
    Args:
        event: Custom event with bootstrap_servers and topic
        context: Lambda context object
    """
    from kafka import KafkaConsumer
    
    bootstrap_servers = event.get('bootstrap_servers', 'localhost:9092')
    topic = event.get('topic', 'default-topic')
    max_records = event.get('max_records', 100)
    timeout_ms = event.get('timeout_ms', 30000)
    
    handler = KafkaMessageHandler()
    
    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id='lambda-consumer-group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            max_poll_records=max_records,
            session_timeout_ms=timeout_ms
        )
        
        logger.info(f"Connected to Kafka cluster: {bootstrap_servers}")
        
        # Poll messages
        message_count = 0
        for message in consumer:
            try:
                handler.process_message(message.value)
                message_count += 1
                if message_count >= max_records:
                    break
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                handler.error_count += 1
        
        consumer.close()
        summary = handler.get_summary()
        
        return {
            'statusCode': 200,
            'body': json.dumps(summary)
        }
    
    except Exception as e:
        logger.error(f"Direct poll handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


# For local testing
if __name__ == '__main__':
    import os
    
    # Mock event for testing
    test_event = {
        'records': {
            'your-topic': [
                {
                    'value': base64.b64encode(json.dumps({
                        'id': 1,
                        'timestamp': datetime.now().isoformat(),
                        'event_type': 'user_login',
                        'user_id': 1001,
                        'message': 'User logged in'
                    }).encode('utf-8')).decode('utf-8')
                }
            ]
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
