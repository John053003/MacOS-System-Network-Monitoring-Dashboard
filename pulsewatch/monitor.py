from __future__ import annotations

import json
import platform
import socket
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

import psutil

from config import PING_COUNT, PING_HOST


_last_speedtest_timestamp = 0.0
_last_speedtest_result = {'upload_mbps': None, 'download_mbps': None}


def get_top_processes(limit: int = 5) -> str:
    processes: List[Dict] = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            processes.append(
                {
                    'pid': info['pid'],
                    'name': info['name'] or 'unknown',
                    'cpu_percent': info['cpu_percent'] or 0.0,
                    'memory_percent': round(info['memory_percent'] or 0.0, 2),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top = sorted(
        processes,
        key=lambda p: (p['cpu_percent'], p['memory_percent']),
        reverse=True
    )[:limit]

    return json.dumps(top)


def ping_host(host: str = PING_HOST) -> tuple[Optional[float], Optional[float]]:
    try:
        result = subprocess.run(
            ['ping', '-c', str(PING_COUNT), host],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        output = result.stdout
        packet_loss = None
        latency = None

        for line in output.splitlines():
            if 'packet loss' in line:
                packet_loss_text = line.split('%')[0].split()[-1]
                packet_loss = float(packet_loss_text)

            if 'round-trip' in line or 'rtt min/avg/max/stddev' in line:
                stats = line.split('=')[1].strip().split(' ')[0]
                latency = float(stats.split('/')[1])

        return latency, packet_loss

    except Exception:
        return None, None


def run_speedtest(interval_minutes: int = 30) -> Dict[str, Optional[float]]:
    global _last_speedtest_timestamp, _last_speedtest_result

    now = time.time()
    if now - _last_speedtest_timestamp < interval_minutes * 60:
        return _last_speedtest_result

    try:
        import speedtest

        st = speedtest.Speedtest(secure=True)
        st.get_best_server()
        download_mbps = round(st.download() / 1_000_000, 2)
        upload_mbps = round(st.upload() / 1_000_000, 2)

        _last_speedtest_result = {
            'download_mbps': download_mbps,
            'upload_mbps': upload_mbps,
        }
        _last_speedtest_timestamp = now
    except Exception:
        pass

    return _last_speedtest_result


def calculate_health_score(
    cpu: float,
    memory: float,
    disk: float,
    latency: Optional[float],
    download: Optional[float]
) -> int:
    score = 100

    if cpu > 85:
        score -= 20
    elif cpu > 70:
        score -= 10

    if memory > 85:
        score -= 20
    elif memory > 70:
        score -= 10

    if disk > 90:
        score -= 20
    elif disk > 80:
        score -= 10

    if latency is not None:
        if latency > 100:
            score -= 15
        elif latency > 60:
            score -= 8

    if download is not None:
        if download < 25:
            score -= 15
        elif download < 50:
            score -= 8

    return max(0, score)


def collect_metrics(speedtest_interval_minutes: int = 30) -> Dict:
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    latency_ms, packet_loss_percent = ping_host()
    speed_result = run_speedtest(speedtest_interval_minutes)

    metric = {
        'created_at': datetime.now().isoformat(timespec='seconds'),
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'cpu_percent': round(cpu_percent, 2),
        'memory_percent': round(memory.percent, 2),
        'disk_percent': round(disk.percent, 2),
        'net_sent_mb': round(net_io.bytes_sent / (1024 * 1024), 2),
        'net_recv_mb': round(net_io.bytes_recv / (1024 * 1024), 2),
        'upload_mbps': speed_result.get('upload_mbps'),
        'download_mbps': speed_result.get('download_mbps'),
        'latency_ms': latency_ms,
        'packet_loss_percent': packet_loss_percent,
        'top_processes': get_top_processes(),
    }

    metric['health_score'] = calculate_health_score(
        metric['cpu_percent'],
        metric['memory_percent'],
        metric['disk_percent'],
        metric['latency_ms'],
        metric['download_mbps'],
    )

    return metric