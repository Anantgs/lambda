from flask import Flask, render_template, request, jsonify
from consumer import KafkaMessageConsumer
import json

app = Flask(__name__)

consumer = None
status = "Stopped"
current_config = {
    'bootstrap_servers': '',
    'topic': '',
    'group_id': 'kafka-consumer-ui'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    global consumer, status, current_config
    stats = {}

    if request.method == 'POST':
        action = request.form['action']
        if action == 'start':
            if consumer and consumer.running:
                status = "Already running"
            else:
                current_config['bootstrap_servers'] = request.form['bootstrap_servers']
                current_config['topic'] = request.form['topic']
                current_config['group_id'] = request.form['group_id']
                consumer = KafkaMessageConsumer(
                    current_config['bootstrap_servers'],
                    current_config['topic'],
                    current_config['group_id']
                )
                consumer.start()
                status = "Running"
        elif action == 'stop':
            if consumer:
                consumer.stop()
                consumer = None
            status = "Stopped"

    if consumer and consumer.running:
        stats = consumer.get_stats()

    return render_template('index.html',
                           status=status,
                           bootstrap_servers=current_config['bootstrap_servers'],
                           topic=current_config['topic'],
                           group_id=current_config['group_id'],
                           stats=stats)

@app.route('/api/stats')
def get_stats():
    if consumer and consumer.running:
        return jsonify(consumer.get_stats())
    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)