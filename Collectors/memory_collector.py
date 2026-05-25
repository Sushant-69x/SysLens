import psutil
from Utils.logger import get_logger

logger = get_logger('MemoryCollector')

class MemoryCollector:
    def __init__(self, db_manager):
        self.db = db_manager

    def collect(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        data = {
            'total_mb': round(mem.total / 1024**2, 2),
            'used_mb': round(mem.used / 1024**2, 2),
            'available_mb': round(mem.available / 1024**2, 2),
            'percent_used': mem.percent,
            'swap_used_mb': round(swap.used / 1024**2, 2),
            'swap_percent': swap.percent
        }

        logger.info(f"RAM: {mem.percent}% used | Swap: {swap.percent}%")
        return data

    def collect_and_store(self):
        data = self.collect()
        self.db.insert('memory_metrics', data)
        return data