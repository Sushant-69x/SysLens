import psutil
from Utils.logger import get_logger
from Utils.config import config

logger = get_logger('AlertEngine')

class AlertEngine:
    def __init__(self, db_manager):
        self.db = db_manager
        self.thresholds = config['thresholds']
        self.whitelist_ports = config['whitelist_ports']
        self.brute_force_attempts = config['alerts']['brute_force_attempts']
        self.brute_force_window = config['alerts']['brute_force_window_minutes']

    def check_cpu(self, cpu_data):
        if cpu_data['cpu_percent'] > self.thresholds['cpu_percent']:
            self._create_alert(
                alert_type='CPU_HIGH',
                severity='CRITICAL',
                description=f"CPU usage at {cpu_data['cpu_percent']}% — exceeds {self.thresholds['cpu_percent']}% threshold"
            )

    def check_memory(self, mem_data):
        if mem_data['percent_used'] > self.thresholds['memory_percent']:
            self._create_alert(
                alert_type='MEMORY_HIGH',
                severity='WARNING',
                description=f"RAM usage at {mem_data['percent_used']}% — exceeds {self.thresholds['memory_percent']}% threshold"
            )

    def check_disk(self, disk_data_list):
        for disk in disk_data_list:
            if disk['percent_used'] > self.thresholds['disk_percent']:
                self._create_alert(
                    alert_type='DISK_HIGH',
                    severity='WARNING',
                    description=f"Disk {disk['mount_point']} at {disk['percent_used']}% — exceeds {self.thresholds['disk_percent']}% threshold"
                )

    def check_ports(self):
        suspicious = []
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr:
                    port = conn.laddr.port
                    if port not in self.whitelist_ports:
                        suspicious.append(port)
                        self._create_alert(
                            alert_type='SUSPICIOUS_PORT',
                            severity='WARNING',
                            description=f"Unexpected listening port detected: {port} (PID: {conn.pid})"
                        )
        except Exception as e:
            logger.error(f"Port check failed: {e}")
        return suspicious

    def check_suspicious_processes(self):
        suspicious_names = [
            'netcat', 'nc.exe', 'ncat', 'nmap', 'mimikatz',
            'meterpreter', 'psexec', 'wce', 'fgdump'
        ]
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                name = proc.info['name'].lower() if proc.info['name'] else ''
                for sus in suspicious_names:
                    if sus in name:
                        self._create_alert(
                            alert_type='SUSPICIOUS_PROCESS',
                            severity='CRITICAL',
                            description=f"Suspicious process detected: {proc.info['name']} (PID: {proc.info['pid']})"
                        )
        except Exception as e:
            logger.error(f"Process check failed: {e}")

    def check_brute_force(self):
        query = '''
            SELECT source_ip, COUNT(*) as attempts
            FROM auth_events
            WHERE event_type = "FAILED_LOGIN"
            AND timestamp >= datetime("now", ? )
            GROUP BY source_ip
            HAVING COUNT(*) >= ?
        '''
        window = f"-{self.brute_force_window} minutes"
        results = self.db.query(query, (window, self.brute_force_attempts))

        for row in results:
            self._create_alert(
                alert_type='BRUTE_FORCE',
                severity='CRITICAL',
                description=f"Brute force detected from {row['source_ip']} — {row['attempts']} failed logins in {self.brute_force_window} minutes"
            )

        if results:
            logger.warning(f"Brute force detected from {len(results)} IPs")

        return results

    def _create_alert(self, alert_type, severity, description):
        existing = self.db.query('''
            SELECT id FROM alerts
            WHERE alert_type = ?
            AND description = ?
            AND timestamp >= datetime("now", "-5 minutes")
        ''', (alert_type, description))

        if existing:
            return

        alert = {
            'alert_type': alert_type,
            'severity': severity,
            'description': description,
            'resolved': 0
        }
        self.db.insert('alerts', alert)
        logger.warning(f"ALERT [{severity}] {alert_type}: {description}")

    def run_all_checks(self, cpu_data, mem_data, disk_data):
        self.check_cpu(cpu_data)
        self.check_memory(mem_data)
        self.check_disk(disk_data)
        self.check_ports()
        self.check_suspicious_processes()
        self.check_brute_force()