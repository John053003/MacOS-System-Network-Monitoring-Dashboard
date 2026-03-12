import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'metrics.db')

COLLECTION_INTERVAL_SECONDS = 15
HISTORY_LIMIT = 120
PING_HOST = '1.1.1.1'
PING_COUNT = 2
SPEEDTEST_INTERVAL_MINUTES = 30

ALERT_THRESHOLDS = {
    'cpu_percent': 85,
    'memory_percent': 85,
    'disk_percent': 90,
    'latency_ms': 100,
    'download_mbps': 50,
}