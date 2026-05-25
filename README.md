---

SysLens — Linux System Intelligence & Log Analysis Engine

A Python-based system monitoring tool that continuously collects CPU, memory, disk, process, and network metrics, stores them in a structured SQLite database, detects anomalies, and visualizes everything through a live dashboard.

---

## Architecture

```
main.py
├── Engine/scheduler.py       → runs all collectors every 30s
├── Collectors/
│   ├── cpu_collector.py      → CPU metrics via psutil
│   ├── memory_collector.py   → RAM + swap metrics
│   ├── disk_collector.py     → disk usage per partition
│   ├── process_collector.py  → top 20 processes by memory
│   └── network_collector.py  → active TCP/UDP connections
├── Engine/alert_engine.py    → threshold-based alert rules
├── Database/db_manager.py    → SQLite CRUD operations
├── Api/routes.py             → Flask REST API (6 endpoints)
└── dashboard/app.py          → Streamlit live dashboard
```

---

## Tech Stack

| Component | Technology | Reason |
|---|---|---|
| Language | Python 3.10 | Rich ecosystem, psutil support |
| Monitoring | psutil | Industry-standard system lib |
| Database | SQLite | Zero-config, full SQL support |
| Scheduler | APScheduler | Background thread scheduling |
| API | Flask | Lightweight REST API |
| Dashboard | Streamlit+Plotly | Fast Python-native UI |
| Config | PyYAML | Human-readable configuration |

---

## Features

- [x] CPU, RAM, Disk monitoring every 30 seconds
- [x] Top 20 process tracking by memory usage
- [x] Active network connection monitoring (TCP/UDP)
- [x] Time-series data storage in SQLite
- [x] Threshold-based alert engine (CPU/RAM/Disk)
- [x] REST API with 6 endpoints
- [x] Live Streamlit dashboard with Plotly charts
- [x] Structured logging to file and terminal

---

## Installation

```bash
git clone https://github.com/Sushant-69x/syslens.git
cd syslens
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running

Terminal 1 — Start API:
```bash
python -c "from Api.routes import app; app.run(port=5000)"
```

Terminal 2 — Start collector engine:
```bash
python main.py
```

Terminal 3 — Start dashboard:
```bash
streamlit run dashboard/app.py
```

Open browser: http://localhost:8501

---

## API Endpoints

| Endpoint | Description |
|---|---|
| GET /api/status | Health check |
| GET /api/metrics/latest | Latest CPU, RAM, Disk snapshot |
| GET /api/metrics/history | Last 1 hour time-series data |
| GET /api/processes | Top processes by memory |
| GET /api/network | Active network connections |
| GET /api/alerts | All generated alerts |

---

## Database Schema

7 tables: cpu_metrics, memory_metrics, disk_metrics, process_snapshots, network_connections, alerts

All time-series tables indexed on timestamp for fast range queries.

---

## Sample SQL Queries

```sql
-- Average CPU last 1 hour
SELECT AVG(cpu_percent) FROM cpu_metrics
WHERE timestamp >= datetime('now', '-1 hour');

-- Top memory processes right now
SELECT name, memory_percent FROM process_snapshots
WHERE timestamp = (SELECT MAX(timestamp) FROM process_snapshots)
ORDER BY memory_percent DESC LIMIT 5;

-- All critical alerts
SELECT * FROM alerts WHERE severity = 'CRITICAL' ORDER BY timestamp DESC;
```

---

## Key Design Decisions

- SQLite over PostgreSQL — portable, zero-config for development. Schema designed for easy PostgreSQL migration.
- APScheduler over cron — runs in-process background thread, no OS-level setup needed.
- psutil over raw /proc parsing — cross-platform, maintained, handles edge cases.
- Streamlit over React — Python-native, eliminates JavaScript context switching.

---

