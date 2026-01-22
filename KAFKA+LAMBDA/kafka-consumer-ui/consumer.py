from kafka import KafkaConsumer
import json
import threading
import time
from collections import defaultdict, deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaMessageConsumer:
    def __init__(self, bootstrap_servers, topic, group_id='kafka-consumer-ui'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer = None
        self.running = False
        self.thread = None

        # Statistics
        self.messages_consumed = 0
        self.messages_per_second = 0
        self.event_type_counts = defaultdict(int)
        self.recent_messages = deque(maxlen=100)  # Keep last 100 messages
        self.start_time = None
        self.last_calc_time = time.time()

    def start(self):
        if self.running:
            return
        self.running = True
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._consume_messages)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.thread:
            self.thread.join(timeout=5)

    def _consume_messages(self):
        try:
            for message in self.consumer:
                if not self.running:
                    break

                self.messages_consumed += 1
                message_data = message.value

                # Track event types
                if 'event_type' in message_data:
                    self.event_type_counts[message_data['event_type']] += 1

                # Add to recent messages
                message_display = {
                    'id': message_data.get('id', 'N/A'),
                    'timestamp': message_data.get('timestamp', 'N/A'),
                    'event_type': message_data.get('event_type', 'N/A'),
                    'user_id': message_data.get('user_id', 'N/A'),
                    'message': message_data.get('message', 'N/A'),
                    'kafka_timestamp': message.timestamp,
                    'partition': message.partition,
                    'offset': message.offset
                }
                self.recent_messages.append(message_display)

                # Calculate messages per second every 5 seconds
                current_time = time.time()
                if current_time - self.last_calc_time >= 5:
                    time_diff = current_time - self.last_calc_time
                    self.messages_per_second = (self.messages_consumed - getattr(self, '_last_count', 0)) / time_diff
                    self._last_count = self.messages_consumed
                    self.last_calc_time = current_time

        except Exception as e:
            logger.error(f"Error consuming messages: {e}")

    def get_stats(self):
        runtime = time.time() - self.start_time if self.start_time else 0
        return {
            'messages_consumed': self.messages_consumed,
            'messages_per_second': round(self.messages_per_second, 2),
            'runtime_seconds': round(runtime, 1),
            'event_type_counts': dict(self.event_type_counts),
            'recent_messages': list(self.recent_messages)[-10:]  # Last 10 messages
        }