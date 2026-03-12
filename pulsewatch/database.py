import os
import sqlite3
from contextlib import closing
from typing import Any, Dict, List, Optional

from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_connection()) as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                hostname TEXT NOT NULL,
                cpu_percent REAL NOT NULL,
                memory_percent REAL NOT NULL,
                disk_percent REAL NOT NULL,
                net_sent_mb REAL NOT NULL,
                net_recv_mb REAL NOT NULL,
                upload_mbps REAL,
                download_mbps REAL,
                latency_ms REAL,
                packet_loss_percent REAL,
                top_processes TEXT NOT NULL,
                health_score INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                severity TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                message TEXT NOT NULL
            );
            '''
        )
        conn.commit()


def insert_metric(metric: Dict[str, Any]) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            '''
            INSERT INTO metrics (
                created_at, hostname, cpu_percent, memory_percent, disk_percent,
                net_sent_mb, net_recv_mb, upload_mbps, download_mbps,
                latency_ms, packet_loss_percent, top_processes, health_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                metric['created_at'],
                metric['hostname'],
                metric['cpu_percent'],
                metric['memory_percent'],
                metric['disk_percent'],
                metric['net_sent_mb'],
                metric['net_recv_mb'],
                metric.get('upload_mbps'),
                metric.get('download_mbps'),
                metric.get('latency_ms'),
                metric.get('packet_loss_percent'),
                metric['top_processes'],
                metric['health_score'],
            ),
        )
        conn.commit()


def insert_alert(alert: Dict[str, Any]) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            '''
            INSERT INTO alerts (created_at, severity, metric_name, metric_value, message)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                alert['created_at'],
                alert['severity'],
                alert['metric_name'],
                alert.get('metric_value'),
                alert['message'],
            ),
        )
        conn.commit()


def fetch_latest_metric() -> Optional[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        row = conn.execute(
            'SELECT * FROM metrics ORDER BY id DESC LIMIT 1'
        ).fetchone()
        return dict(row) if row else None


def fetch_recent_metrics(limit: int = 120) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            'SELECT * FROM metrics ORDER BY id DESC LIMIT ?',
            (limit,),
        ).fetchall()
        return [dict(row) for row in reversed(rows)]


def fetch_recent_alerts(limit: int = 20) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            'SELECT * FROM alerts ORDER BY id DESC LIMIT ?',
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]