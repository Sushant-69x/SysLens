CREATE TABLE IF NOT EXISTS cpu_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_percent REAL NOT NULL,
    load_avg_1m REAL,
    load_avg_5m REAL,
    load_avg_15m REAL,
    core_count INTEGER
);

CREATE TABLE IF NOT EXISTS memory_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_mb REAL NOT NULL,
    used_mb REAL NOT NULL,
    available_mb REAL NOT NULL,
    percent_used REAL NOT NULL,
    swap_used_mb REAL,
    swap_percent REAL
);

CREATE TABLE IF NOT EXISTS disk_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    mount_point TEXT NOT NULL,
    total_gb REAL NOT NULL,
    used_gb REAL NOT NULL,
    free_gb REAL NOT NULL,
    percent_used REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS process_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    pid INTEGER NOT NULL,
    name TEXT NOT NULL,
    cpu_percent REAL,
    memory_percent REAL,
    status TEXT,
    username TEXT
);

CREATE TABLE IF NOT EXISTS network_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    local_address TEXT,
    local_port INTEGER,
    remote_address TEXT,
    remote_port INTEGER,
    status TEXT,
    pid INTEGER,
    protocol TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    resolved INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS auth_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    event_type TEXT NOT NULL,
    username TEXT,
    source_ip TEXT,
    service TEXT,
    raw_line TEXT
);

CREATE INDEX IF NOT EXISTS idx_cpu_timestamp ON cpu_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_mem_timestamp ON memory_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_disk_timestamp ON disk_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_proc_timestamp ON process_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_auth_timestamp ON auth_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_auth_source_ip ON auth_events(source_ip);
CREATE INDEX IF NOT EXISTS idx_auth_event_type ON auth_events(event_type);