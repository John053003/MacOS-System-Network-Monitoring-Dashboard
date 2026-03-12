from __future__ import annotations

import json
from flask import Flask, jsonify, render_template

from collector import MetricCollector
from config import HISTORY_LIMIT
from database import (
    fetch_latest_metric,
    fetch_recent_alerts,
    fetch_recent_metrics,
    init_db,
)

app = Flask(__name__)
collector = MetricCollector()


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/current')
def api_current():
    metric = fetch_latest_metric()
    if not metric:
        return jsonify({'status': 'warming_up'})

    metric['top_processes'] = json.loads(metric['top_processes'])
    return jsonify(metric)


@app.route('/api/history')
def api_history():
    metrics = fetch_recent_metrics(HISTORY_LIMIT)
    for metric in metrics:
        metric['top_processes'] = json.loads(metric['top_processes'])
    return jsonify(metrics)


@app.route('/api/alerts')
def api_alerts():
    return jsonify(fetch_recent_alerts(20))


@app.route('/healthz')
def healthcheck():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    init_db()
    collector.start()
    app.run(debug=True, host='127.0.0.1', port=5000)