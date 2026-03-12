from __future__ import annotations

import threading
import time

from alerts import evaluate_alerts
from config import COLLECTION_INTERVAL_SECONDS, SPEEDTEST_INTERVAL_MINUTES
from database import insert_alert, insert_metric
from monitor import collect_metrics


class MetricCollector:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            metric = collect_metrics(
                speedtest_interval_minutes=SPEEDTEST_INTERVAL_MINUTES
            )
            insert_metric(metric)

            for alert in evaluate_alerts(metric):
                insert_alert(alert)

            time.sleep(COLLECTION_INTERVAL_SECONDS)