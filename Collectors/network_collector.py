import psutil
from Utils.logger import get_logger

logger = get_logger('NetworkCollector')

class NetworkCollector:
    def __init__(self, db_manager):
        self.db = db_manager

    def collect(self):
        results = []
        connections = psutil.net_connections(kind='inet')

        for conn in connections:
            try:
                data = {
                    'local_address': conn.laddr.ip if conn.laddr else None,
                    'local_port': conn.laddr.port if conn.laddr else None,
                    'remote_address': conn.raddr.ip if conn.raddr else None,
                    'remote_port': conn.raddr.port if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid,
                    'protocol': 'TCP' if conn.type.name == 'SOCK_STREAM' else 'UDP'
                }
                results.append(data)
            except Exception:
                continue

        logger.info(f"Captured {len(results)} network connections")
        return results

    def collect_and_store(self):
        results = self.collect()
        for data in results:
            self.db.insert('network_connections', data)
        return results