from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from config import ALERT_THRESHOLDS


def evaluate_alerts(metric: Dict) -> List[Dict]:
    alerts: List[Dict] = []
    now = datetime.now().isoformat(timespec='seconds')

    checks = {
        'cpu_percent': (
            'warning',
            metric['cpu_percent'],
            f"High CPU usage detected: {metric['cpu_percent']:.1f}%"
        ),
        'memory_percent': (
            'warning',
            metric['memory_percent'],
            f"High memory usage detected: {metric['memory_percent']:.1f}%"
        ),
        'disk_percent': (
            'critical',
            metric['disk_percent'],
            f"Disk usage is critically high: {metric['disk_percent']:.1f}%"
        ),
    }

    if metric.get('latency_ms') is not None:
        checks['latency_ms'] = (
            'warning',
            metric['latency_ms'],
            f"Network latency is elevated: {metric['latency_ms']:.1f} ms"
        )

    if metric.get('download_mbps') is not None:
        checks['download_mbps'] = (
            'warning',
            metric['download_mbps'],
            f"Download speed dropped below threshold: {metric['download_mbps']:.1f} Mbps"
        )

    for metric_name, (severity, value, message) in checks.items():
        threshold = ALERT_THRESHOLDS.get(metric_name)
        if threshold is None:
            continue

        if metric_name == 'download_mbps':
            triggered = value < threshold
        else:
            triggered = value > threshold

        if triggered:
            alerts.append(
                {
                    'created_at': now,
                    'severity': severity,
                    'metric_name': metric_name,
                    'metric_value': value,
                    'message': message,
                }
            )

    return alerts