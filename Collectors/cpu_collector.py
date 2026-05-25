import psutil
import os
from Utils.logger import get_logger

logger = get_logger('CPUCollector')

class CPUCollector:
    def __init__(self, db_manager):
        self.db = db_manager

    def collect(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        core_count = psutil.cpu_count()
        
        # Windows doesn't have getloadavg, handle both
        try:
            load_avg = os.getloadavg()
            load_1m, load_5m, load_15m = load_avg
        except AttributeError:
            load_1m = load_5m = load_15m = None

        data = {
            'cpu_percent': cpu_percent,
            'core_count': core_count,
            'load_avg_1m': load_1m,
            'load_avg_5m': load_5m,
            'load_avg_15m': load_15m
        }

        logger.info(f"CPU: {cpu_percent}% | Cores: {core_count}")
        return data

    def collect_and_store(self):
        data = self.collect()
        self.db.insert('cpu_metrics', data)
        return data