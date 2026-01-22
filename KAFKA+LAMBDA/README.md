# Kafka + Lambda Integration

This folder contains resources for Kafka integration with AWS Lambda, including setup commands and a high-throughput Kafka producer application with UI.

## Kafka Message Lifecycle in Production

When you add messages to Kafka in a production environment, here's what happens:

### 1. **Message Ingestion**
- Producer sends messages to Kafka brokers
- Messages are validated and assigned to partitions based on partition key (or round-robin if no key)
- Acknowledgment sent back to producer based on `acks` setting

### 2. **Storage & Partitioning**
- Messages stored in topic partitions across broker nodes
- Each partition is an ordered, immutable sequence of messages
- Partitions distributed across brokers for load balancing

### 3. **Replication**
- Messages replicated to follower replicas (configurable replication factor)
- Leader handles reads/writes, followers sync data
- ISR (In-Sync Replicas) ensure data durability

### 4. **Consumer Processing**
- Consumers subscribe to topics and read from partitions
- Consumer groups coordinate partition assignment
- Offset tracking ensures exactly-once processing
- Messages processed and committed

### 5. **Retention & Cleanup**
- Messages retained based on time or size policies
- Old segments compacted or deleted
- Log compaction for key-based deduplication

### 6. **Monitoring & Operations**
- Metrics collected for throughput, latency, errors
- Alerts for broker failures, high latency, disk usage
- Auto-rebalancing and self-healing capabilities
For a detailed explanation of the complete Kafka message lifecycle in production, see [Kafka-Production-Lifecycle.md](Kafka-Production-Lifecycle.md).

## Kafka Producer Application

The `kafka-producer-ui` directory contains a web-based Kafka producer application capable of sending high-volume messages (up to 0.25 GB/minute).

## Kafka Consumer Application

The `kafka-consumer-ui` directory contains a web-based Kafka consumer application for real-time message consumption and monitoring. Features include:

- Live message consumption with statistics
- Multi-topic support (consume from multiple topics simultaneously)
- Event type analysis and distribution
- Recent message display with metadata
- Real-time performance monitoring per topic
- Beautiful UI matching the producer application

## Integration Example

1. **Start Producer**: Run `kafka-producer-ui` to send test messages
2. **Start Consumer**: Run `kafka-consumer-ui` to view consumed messages
3. **Monitor Pipeline**: Watch real-time statistics on both producer and consumer sides
4. **Test Scenarios**: Validate end-to-end message flow and processing

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