from flask import Flask, render_template, request
from producer import KafkaMessageProducer

app = Flask(__name__)

producer = None
status = "Stopped"
current_config = {
    'bootstrap_servers': '',
    'topic': '',
    'message_size_kb': 1,
    'messages_per_second': 1000
}

@app.route('/', methods=['GET', 'POST'])
def index():
    global producer, status, current_config
    throughput_gb_min = 0
    if request.method == 'POST':
        action = request.form['action']
        if action == 'start':
            if producer and producer.running:
                status = "Already running"
            else:
                current_config['bootstrap_servers'] = request.form['bootstrap_servers']
                current_config['topic'] = request.form['topic']
                current_config['message_size_kb'] = int(request.form['message_size_kb'])
                current_config['messages_per_second'] = int(request.form['messages_per_second'])
                producer = KafkaMessageProducer(
                    current_config['bootstrap_servers'],
                    current_config['topic'],
                    current_config['message_size_kb'],
                    current_config['messages_per_second']
                )
                producer.start()
                status = "Running"
        elif action == 'stop':
            if producer:
                producer.stop()
                producer = None
            status = "Stopped"

    # Calculate throughput
    bytes_per_second = current_config['messages_per_second'] * current_config['message_size_kb'] * 1024
    throughput_gb_min = (bytes_per_second * 60) / (1024 * 1024 * 1024)

    return render_template('index.html',
                           status=status,
                           bootstrap_servers=current_config['bootstrap_servers'],
                           topic=current_config['topic'],
                           message_size_kb=current_config['message_size_kb'],
                           messages_per_second=current_config['messages_per_second'],
                           throughput_gb_min=throughput_gb_min)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)