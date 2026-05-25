import logging
import os

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )

    # Print to terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Save to file
    os.makedirs('logs', exist_ok=True)
    file_handler = logging.FileHandler('logs/syslens.log')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger