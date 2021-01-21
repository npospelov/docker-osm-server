import logging
import logging.handlers
import configparser


def setup():
    config = configparser.ConfigParser()
    try:
        config.read('sync_db.ini')
        log_name = config['DEFAULT'].get('log_file')
    except:
        print("Error: cannot get 'log_file_name' from config")
        exit(1)

    log_handler = logging.handlers.RotatingFileHandler(log_name,maxBytes=1000000,backupCount=1)
    formatter = logging.Formatter('%(asctime)s : %(message)s', '%d.%m.%Y %H:%M:%S')
    log_handler.setFormatter(formatter)
    logger=logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)
    logging.info("")
