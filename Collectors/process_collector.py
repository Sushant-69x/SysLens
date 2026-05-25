import psutil
from Utils.logger import get_logger

logger = get_logger('ProcessCollector')

class ProcessCollector:
    def __init__(self, db_manager):
        self.db = db_manager

    def collect(self):
        results = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
            try:
                info = proc.info
                data = {
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu_percent': info['cpu_percent'],
                    'memory_percent': round(info['memory_percent'], 2) if info['memory_percent'] else 0.0,
                    'status': info['status'],
                    'username': info['username']
                }
                results.append(data)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory usage, top 20 only
        results = sorted(results, key=lambda x: x['memory_percent'], reverse=True)[:20]
        logger.info(f"Captured {len(results)} top processes")
        return results

    def collect_and_store(self):
        results = self.collect()
        for data in results:
            self.db.insert('process_snapshots', data)
        return results