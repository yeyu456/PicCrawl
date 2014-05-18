import logging
import logging.config

def log():
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('Crawl')
    return logger

    

