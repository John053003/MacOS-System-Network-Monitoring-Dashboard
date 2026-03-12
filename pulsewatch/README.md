# PulseWatch

PulseWatch is a Python-based macOS monitoring dashboard built for system engineering portfolio work. It tracks system utilization and network performance, stores historical metrics in SQLite, and exposes a simple dashboard you can demo on LinkedIn and GitHub.

## Features
- Live CPU, memory, disk, latency, upload, and download monitoring
- Historical metrics stored in SQLite
- Top process visibility
- Threshold-based alerting
- Health score for quick status checks
- Flask dashboard with charts

## Stack
- Python
- Flask
- SQLite
- psutil
- speedtest-cli
- HTML / CSS / JavaScript
- Chart.js

## Project Structure
```text
pulsewatch/
├── app.py
├── alerts.py
├── collector.py
├── config.py
├── database.py
├── monitor.py
├── requirements.txt
├── README.md
├── data/
├── static/
│   ├── app.js
│   └── style.css
└── templates/
    └── dashboard.html