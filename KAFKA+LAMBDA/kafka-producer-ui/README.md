# Kafka Producer UI

A web-based Kafka producer application that can send high-volume messages to a Kafka topic. Designed to achieve up to 0.25 GB per minute throughput.

## Features

- **Beautiful Modern UI**: Sleek, responsive web interface with Bootstrap styling and animations
- **Real-time Monitoring**: Live status updates and throughput calculations
- **Configurable Settings**: Adjust message size and rate to meet your throughput requirements
- **High Throughput**: Uses threading to send messages asynchronously without blocking the UI
- **EC2 Ready**: Dockerized for easy deployment on EC2 instances

## Requirements

- Python 3.9+
- Kafka cluster accessible from the deployment environment

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open http://localhost:5000 in your browser

## Deployment on EC2

1. Build the Docker image:
   ```
   docker build -t kafka-producer-ui .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 kafka-producer-ui
   ```

3. Access the UI at http://your-ec2-public-ip:5000

## Configuration

- **Bootstrap Servers**: Comma-separated list of Kafka brokers (e.g., `b-1.cluster.kafka.amazonaws.com:9092,b-2.cluster.kafka.amazonaws.com:9092`)
- **Topic**: The Kafka topic to send messages to
- **Message Size (KB)**: Size of each message in KB
- **Messages per Second**: Number of messages to send per second

## Throughput Calculation

To achieve 0.25 GB/minute:
- 0.25 GB = 250 MB = 262,144,000 bytes/minute
- Per second: ~4,369,000 bytes/second
- With 1KB messages: ~4,267 messages/second

Adjust the settings accordingly based on your message size.

## Notes

- Ensure the EC2 instance has security group rules allowing outbound connections to Kafka brokers
- For high throughput, consider instance size and network bandwidth
- The producer runs in a separate thread to avoid blocking the UI