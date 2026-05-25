import time
from Engine.scheduler import MonitoringScheduler
from Utils.logger import get_logger

logger = get_logger('Main')

if __name__ == '__main__':
    logger.info("SysLens starting...")
    
    scheduler = MonitoringScheduler()
    
    # Run once immediately
    scheduler.run_all_collectors()
    
    # Start background scheduling
    scheduler.start()

    logger.info("SysLens running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.stop()