import psutil
from Utils.logger import get_logger

logger = get_logger('DiskCollector')

class DiskCollector:
    def __init__(self, db_manager):
        self.db = db_manager

    def collect(self):
        results = []
        partitions = psutil.disk_partitions()

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                data = {
                    'mount_point': partition.mountpoint,
                    'total_gb': round(usage.total / 1024**3, 2),
                    'used_gb': round(usage.used / 1024**3, 2),
                    'free_gb': round(usage.free / 1024**3, 2),
                    'percent_used': usage.percent
                }
                results.append(data)
                logger.info(f"Disk {partition.mountpoint}: {usage.percent}% used")
            except PermissionError:
                continue

        return results

    def collect_and_store(self):
        results = self.collect()
        for data in results:
            self.db.insert('disk_metrics', data)
        return results