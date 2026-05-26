`
---

# SysLens — Linux System Intelligence & Log Analysis Engine

A Python-based system monitoring tool that continuously collects CPU, memory, disk, process, and network metrics, stores them in a structured SQLite database, detects anomalies, and visualizes everything through a live dashboard.

---

## Architecture

```
main.py
├── Engine/scheduler.py          → runs all collectors every 30s (APScheduler)
├── Collectors/
│   ├── cpu_collector.py         → CPU % + load average via psutil
│   ├── memory_collector.py      → RAM + swap metrics
│   ├── disk_collector.py        → disk usage per partition
│   ├── process_collector.py     → top 20 processes by memory
│   ├── network_collector.py     → active TCP/UDP connections
│   └── auth_log_collector.py    → SSH login tracking + brute force detection
├── Engine/alert_engine.py       → threshold + rule-based alert logic
├── Database/
│   ├── db_manager.py            → SQLite connection + CRUD operations
│   └── schema.sql               → table definitions + indexes
├── Api/routes.py                → Flask REST API (9 endpoints)
├── Dashboard/app.py             → Streamlit live dashboard
└── Utils/
    ├── logger.py                → structured logging to file + terminal
    └── config.py                → YAML config loader
```

---

## Data Flow

```
psutil + /proc filesystem + auth.log
              ↓
        Collectors (6 modules)
              ↓
     APScheduler (every 30s)
              ↓
    DatabaseManager → SQLite
              ↓
     AlertEngine (rule checks)
              ↓
     Flask REST API (9 endpoints)
              ↓
    Streamlit Dashboard (charts + tables)
```

---

## Tech Stack

| Component | Technology | Reason |
|---|---|---|
| Language | Python 3.10 | Rich ecosystem, psutil support |
| Monitoring | psutil | Industry-standard system library |
| Database | SQLite | Zero-config, full SQL support |
| Scheduler | APScheduler | Background thread scheduling |
| API | Flask | Lightweight REST API |
| Dashboard | Streamlit + Plotly | Fast Python-native UI |
| Config | PyYAML | Human-readable configuration |
| Logging | Python logging | Structured logs to file + terminal |

---

## Features

- [x] CPU, RAM, Disk monitoring every 30 seconds
- [x] Top 20 process tracking by memory usage
- [x] Active network connection monitoring (TCP/UDP)
- [x] Auth log parsing for SSH login events (/var/log/auth.log)
- [x] Brute force SSH detection via sliding-window SQL query
- [x] Port anomaly detection against configurable whitelist
- [x] Suspicious process name detection
- [x] Time-series data storage in SQLite with indexed tables
- [x] Threshold-based alert engine (CPU / RAM / Disk / Security)
- [x] Duplicate alert suppression (5-minute deduplication window)
- [x] REST API with 9 endpoints
- [x] Live Streamlit dashboard with Plotly area charts and gauges
- [x] Structured logging to terminal and log file
- [x] YAML-based configurable thresholds and port whitelist

---

## Installation

```bash
git clone https://github.com/Sushant-69x/SysLens.git
cd SysLens
python -m venv venv
```

Activate virtual environment:

Linux / Kali:
```bash
source venv/bin/activate
```

Windows PowerShell:
```bash
venv\Scripts\Activate.ps1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Running

Open 3 separate terminals. Activate venv in each terminal before running.

Linux / Kali activation:
```bash
source venv/bin/activate
```

Windows activation:
```bash
venv\Scripts\Activate.ps1
```

**Terminal 1 — Start Flask API:**
```bash
python -c "from Api.routes import app; app.run(port=5000)"
```

**Terminal 2 — Start collector engine:**
```bash
python main.py
```

**Terminal 3 — Start dashboard:**

Linux / Kali:
```bash
streamlit run Dashboard/app.py
```

Windows:
```bash
streamlit run Dashboard\app.py
```

Open browser: `http://localhost:8501`

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
| GET /api/auth/events | Recent auth log events |
| GET /api/auth/brute-force | Detected brute force IPs |
| GET /api/auth/summary | Auth events by type count |

---

## Database Schema

7 tables with structured indexing:

| Table | Purpose | Indexed On |
|---|---|---|
| cpu_metrics | CPU usage time-series | timestamp |
| memory_metrics | RAM + swap time-series | timestamp |
| disk_metrics | Disk usage per partition | timestamp |
| process_snapshots | Top 20 processes per cycle | timestamp, name |
| network_connections | Active TCP/UDP connections | timestamp, local_port |
| auth_events | SSH login events from auth.log | timestamp, source_ip, event_type |
| alerts | Generated alerts with severity | timestamp, severity |

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

-- Brute force detection — core security query
SELECT source_ip, COUNT(*) as attempts
FROM auth_events
WHERE event_type = 'FAILED_LOGIN'
AND timestamp >= datetime('now', '-10 minutes')
GROUP BY source_ip
HAVING COUNT(*) >= 5;

-- All unresolved critical alerts
SELECT * FROM alerts
WHERE severity = 'CRITICAL' AND resolved = 0
ORDER BY timestamp DESC;

-- Failed login attempts per IP today
SELECT source_ip, COUNT(*) as attempts
FROM auth_events
WHERE event_type = 'FAILED_LOGIN'
AND timestamp >= date('now')
GROUP BY source_ip
ORDER BY attempts DESC;
```

---

## Configuration

Edit `config.yaml` to customize thresholds and port whitelist:

```yaml
thresholds:
  cpu_percent: 90
  memory_percent: 85
  disk_percent: 85

alerts:
  brute_force_attempts: 5
  brute_force_window_minutes: 10

whitelist_ports:
  - 22    # SSH
  - 80    # HTTP
  - 443   # HTTPS
  - 3306  # MySQL
  - 5432  # PostgreSQL
```

---

## Key Design Decisions

- **SQLite over PostgreSQL** — portable, zero-config for development. Schema designed for easy PostgreSQL migration — only connection string needs changing.
- **APScheduler over cron** — runs in-process background thread, no OS-level setup required.
- **psutil over raw /proc parsing** — cross-platform, actively maintained, handles edge cases across distros.
- **Streamlit over React** — Python-native, eliminates JavaScript context-switching, 50 lines replaces 500.
- **Raw SQL over ORM** — keeps SQL logic visible, readable, and fully explainable in interviews.
- **Rule-based alerts over ML** — deterministic, explainable, zero training data required.

---

## Project Structure

```
SysLens/
├── Api/                  Flask REST API
├── Collectors/           System metric collectors
├── Dashboard/            Streamlit dashboard
├── Database/             SQLite schema + manager
├── Engine/               Scheduler + alert engine
├── Utils/                Logger + config loader
├── logs/                 Runtime log files
├── main.py               Entry point
├── config.yaml           Thresholds + whitelist config
├── requirements.txt      Python dependencies
└── README.md
```

---