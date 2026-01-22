from kafka import KafkaProducer
import time
import threading
import random
import string
import json
from datetime import datetime

class KafkaMessageProducer:
    def __init__(self, bootstrap_servers, topic, message_size_kb=1, messages_per_second=1000):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.message_size_kb = message_size_kb
        self.messages_per_second = messages_per_second
        self.producer = None
        self.running = False
        self.thread = None
        self.message_count = 0

    def start(self):
        if self.running:
            return
        self.running = True
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        self.thread = threading.Thread(target=self._produce_messages)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.producer:
            self.producer.close()

    def _produce_messages(self):
        message_size = self.message_size_kb * 1024
        interval = 1.0 / self.messages_per_second
        while self.running:
            start_time = time.time()
            message = self._generate_message(message_size)
            try:
                self.producer.send(self.topic, message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)

    def _generate_message(self, size):
        self.message_count += 1
        # Generate a meaningful JSON message
        data = {
            "id": self.message_count,
            "timestamp": datetime.now().isoformat(),
            "event_type": random.choice(["user_login", "purchase", "page_view", "error", "signup"]),
            "user_id": random.randint(1000, 9999),
            "message": f"Event {self.message_count} occurred",
            "details": {
                "ip_address": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                "user_agent": "Mozilla/5.0 (compatible; KafkaProducer/1.0)",
                "session_id": ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            }
        }
        json_str = json.dumps(data)
        # If the JSON is smaller than required size, pad with additional data
        if len(json_str) < size:
            padding_size = size - len(json_str)
            data["padding"] = ''.join(random.choices(string.ascii_letters + string.digits, k=padding_size))
            json_str = json.dumps(data)
        return json_str