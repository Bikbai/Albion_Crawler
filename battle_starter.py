import logging

from battle_processor import BattleProcessor
from constants import Realm
from utility import setup_logger

logging.basicConfig(level=logging.DEBUG)  # Optional: Minimal configuration for the root logger

# Create and configure a named logger
log = setup_logger()
log.info("Application started")

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-server", help="server to scrape", type=str, dest='server')

args = parser.parse_args()
snames = [el.name for el in Realm]
if not args.server in snames:
    log.error(f"Parameter -server value missing. Pass one of server value:  {snames}")
    exit(1)

processor = BattleProcessor(eval(f'Realm.{args.server}'))
processor.do_process()
