from kafka import KafkaProducer
import time
import threading
import random
import string

class KafkaMessageProducer:
    def __init__(self, bootstrap_servers, topic, message_size_kb=1, messages_per_second=1000):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.message_size_kb = message_size_kb
        self.messages_per_second = messages_per_second
        self.producer = None
        self.running = False
        self.thread = None

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
        # Generate a random message of given size
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size))