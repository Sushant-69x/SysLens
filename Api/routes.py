from flask import Flask, jsonify
from Database.db_manager import DatabaseManager
from Utils.config import config
from Utils.logger import get_logger

logger = get_logger('API')
app = Flask(__name__)
db = DatabaseManager(config['database']['path'])

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'SysLens running'})

@app.route('/api/metrics/latest', methods=['GET'])
def latest_metrics():
    cpu = db.query('SELECT * FROM cpu_metrics ORDER BY timestamp DESC LIMIT 1')
    mem = db.query('SELECT * FROM memory_metrics ORDER BY timestamp DESC LIMIT 1')
    disk = db.query('SELECT * FROM disk_metrics ORDER BY timestamp DESC LIMIT 1')
    return jsonify({
        'cpu': cpu[0] if cpu else {},
        'memory': mem[0] if mem else {},
        'disk': disk[0] if disk else {}
    })

@app.route('/api/metrics/history', methods=['GET'])
def metrics_history():
    cpu = db.query('''
        SELECT * FROM cpu_metrics
        WHERE timestamp >= datetime("now", "-1 hour")
        ORDER BY timestamp ASC
    ''')
    mem = db.query('''
        SELECT * FROM memory_metrics
        WHERE timestamp >= datetime("now", "-1 hour")
        ORDER BY timestamp ASC
    ''')
    return jsonify({'cpu': cpu, 'memory': mem})

@app.route('/api/processes', methods=['GET'])
def processes():
    data = db.query('''
        SELECT * FROM process_snapshots
        WHERE timestamp = (SELECT MAX(timestamp) FROM process_snapshots)
        ORDER BY memory_percent DESC
    ''')
    return jsonify({'processes': data})

@app.route('/api/alerts', methods=['GET'])
def alerts():
    data = db.query('''
        SELECT * FROM alerts
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    return jsonify({'alerts': data})

@app.route('/api/network', methods=['GET'])
def network():
    data = db.query('''
        SELECT * FROM network_connections
        WHERE timestamp = (SELECT MAX(timestamp) FROM network_connections)
        ORDER BY local_port ASC
    ''')
    return jsonify({'connections': data})

@app.route('/api/auth/events', methods=['GET'])
def auth_events():
    data = db.query('''
        SELECT * FROM auth_events
        ORDER BY timestamp DESC
        LIMIT 100
    ''')
    return jsonify({'auth_events': data})

@app.route('/api/auth/brute-force', methods=['GET'])
def brute_force():
    data = db.query('''
        SELECT source_ip, COUNT(*) as attempts,
               MIN(timestamp) as first_attempt,
               MAX(timestamp) as last_attempt
        FROM auth_events
        WHERE event_type = "FAILED_LOGIN"
        AND timestamp >= datetime("now", "-1 hour")
        GROUP BY source_ip
        HAVING COUNT(*) >= 3
        ORDER BY attempts DESC
    ''')
    return jsonify({'brute_force_ips': data})

@app.route('/api/auth/summary', methods=['GET'])
def auth_summary():
    data = db.query('''
        SELECT event_type, COUNT(*) as count
        FROM auth_events
        GROUP BY event_type
        ORDER BY count DESC
    ''')
    return jsonify({'summary': data})

def start_api():
    logger.info("Flask API starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)