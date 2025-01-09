import api_scraper as s
import logging
from logging.handlers import SysLogHandler
import os
from constants import LOGGER_NAME

# Configure the root logger minimally or not at all
logging.basicConfig(level=logging.WARNING)  # Optional: Minimal configuration for the root logger

# Create and configure a named logger
def setup_logger(level=logging.INFO):
    is_docker = os.environ.get('DOCKER_ENV', False)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    handlers = []
    # Create handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # консоль у всех
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    if is_docker:
        syslog_handler = SysLogHandler()
        syslog_handler.setFormatter(formatter)
        handlers.append(syslog_handler)
    else:
        file_handler = logging.FileHandler(f"./logs/{LOGGER_NAME}.log")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    # Create formatters and add them to handlers

    # Add handlers to the logger
    for h in handlers:
        logger.addHandler(h)
    return logger


log = setup_logger()

log.info("Application started")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-apitype", help="type of API", type=str, dest='apiType')
parser.add_argument("-server", help="server to scrape", type=str, dest='server')

args = parser.parse_args()
snames = [el.name for el in s.Realm]
if not args.server in snames:
    log.error(f"Parameter -server value missing. Pass one of server value:  {snames}")
    exit(1)

api_names = [el.name for el in s.ApiType]
if not args.apiType in api_names:
    log.error(f"Parameter -apitype value missing. Pass one of ApiType value: {api_names}")
    exit(1)

scraper = s.API_Scraper(
    api_type=eval(f's.ApiType.{args.apiType}'),
    server=eval(f's.Realm.{args.server}'))
scraper.do_crape()
