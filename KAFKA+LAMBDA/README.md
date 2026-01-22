# Kafka + Lambda Integration

This folder contains resources for Kafka integration with AWS Lambda, including setup commands and a high-throughput Kafka producer application with UI.

## Kafka Setup

Refer to [Commands.md](Commands.md) for detailed instructions on installing and configuring Kafka on EC2 instances, including connectivity to AWS MSK clusters.

## Kafka Producer Application

The `kafka-producer-ui` directory contains a web-based Kafka producer application capable of sending high-volume messages (up to 0.25 GB/minute).

### Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- Access to a Kafka cluster

### Local Installation and Setup

1. Navigate to the producer directory:
   ```
   cd kafka-producer-ui
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and go to `http://localhost:5000`

### Deployment on EC2

1. Ensure Docker is installed on your EC2 instance:
   ```
   sudo yum update -y
   sudo yum install -y docker
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. Build the Docker image:
   ```
   cd kafka-producer-ui
   docker build -t kafka-producer-ui .
   ```

3. Run the container:
   ```
   docker run -d -p 5000:5000 kafka-producer-ui
   ```

4. Access the UI at `http://your-ec2-public-ip:5000`

### Configuration

- **Bootstrap Servers**: Enter your Kafka broker endpoints (e.g., from MSK cluster)
- **Topic**: Specify the Kafka topic name
- **Message Size**: Set message size in KB (default: 1 KB)
- **Messages per Second**: Set the sending rate (default: 1000)

For 0.25 GB/minute throughput with 1KB messages, set Messages per Second to 4267.

### Usage

1. Enter the Kafka configuration in the web form
2. Click "Start Producer" to begin sending messages
3. Monitor the status on the page
4. Click "Stop Producer" to halt message sending

### Security Considerations

- Ensure your EC2 security group allows outbound connections to Kafka brokers (port 9092)
- For production, consider using HTTPS and authentication for the web UI
- Limit access to the producer UI to authorized users

## Troubleshooting

- If connection fails, verify Kafka broker endpoints and network connectivity
- Check EC2 instance size for sufficient CPU/memory for high throughput
- Monitor Kafka topic for message ingestion rates