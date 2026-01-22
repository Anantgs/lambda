# KAfka EC2 connectivity commands


### Install java

```
yum install -y java
```

### Install Kafka
```
wget https://archive.apache.org/dist/kafka/3.3.1/kafka_2.12-3.3.1.tgz
```

### Unzip Kafka
```
tar -xzf kafka_2.12-3.3.1.tgz
```

### Change directory
```
cd kafka_2.12-3.3.1
```

### Check kafka connectivity
```
yum install -y telnet
telnet b-1.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com 9092
```

### Check kafka connectivity
```
telnet b-2.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com 9092
```
```
telnet b-1.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com 9092
```


```
bin/kafka-topics.sh   --bootstrap-server b-1.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com:9092,b-2.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com:9092   --list
```

### Create topic
```
bin/kafka-topics.sh   --bootstrap-server b-1.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com:9092   --create   --topic test-topic   --partitions 3   --replication-factor 2
```


### List topics
```
bin/kafka-topics.sh   --bootstrap-server b-1.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com:9092,b-2.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com:9092   --list
```

### Add message on Producer
```
bin/kafka-console-producer.sh   --bootstrap-server b-1.testcluster.0b9dte.c25.kafka.us-east-1.amazonaws.com:9092   --topic test-topic
```

### Check message on Consumer (The consumer is on same ec2 instance as producer)

```
bin/kafka-console-consumer.sh   --bootstrap-server b-1.msktest01.2n0wvk.c25.kafka.us-east-1.amazonaws.com:9092   --topic test-topic   --from-beginning
```
