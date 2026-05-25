from apscheduler.schedulers.background import BackgroundScheduler
from Database.db_manager import DatabaseManager
from Collectors.cpu_collector import CPUCollector
from Collectors.memory_collector import MemoryCollector
from Collectors.disk_collector import DiskCollector
from Collectors.process_collector import ProcessCollector
from Collectors.network_collector import NetworkCollector
from Collectors.auth_log_collector import AuthLogCollector
from Engine.alert_engine import AlertEngine
from Utils.logger import get_logger
from Utils.config import config

logger = get_logger('Scheduler')

class MonitoringScheduler:
    def __init__(self):
        self.db = DatabaseManager(config['database']['path'])
        self.interval = config['collection']['interval_seconds']

        self.collectors = {
            'cpu': CPUCollector(self.db),
            'memory': MemoryCollector(self.db),
            'disk': DiskCollector(self.db),
            'process': ProcessCollector(self.db),
            'network': NetworkCollector(self.db),
            'auth': AuthLogCollector(self.db)
        }

        self.alert_engine = AlertEngine(self.db)
        self.scheduler = BackgroundScheduler()

    def run_all_collectors(self):
        logger.info("--- Collection cycle started ---")
        cpu_data = self.collectors['cpu'].collect_and_store()
        mem_data = self.collectors['memory'].collect_and_store()
        disk_data = self.collectors['disk'].collect_and_store()
        self.collectors['process'].collect_and_store()
        self.collectors['network'].collect_and_store()
        self.collectors['auth'].collect_and_store()
        self.alert_engine.run_all_checks(cpu_data, mem_data, disk_data)
        logger.info("--- Collection cycle complete ---")

    def start(self):
        self.scheduler.add_job(
            self.run_all_collectors,
            'interval',
            seconds=self.interval,
            id='main_collection'
        )
        self.scheduler.start()
        logger.info(f"Scheduler started. Collecting every {self.interval} seconds")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")