import api_scraper as s
import logging
import os.path

# Configure the root logger minimally or not at all
from utility import setup_logger

logging.basicConfig(level=logging.WARNING)  # Optional: Minimal configuration for the root logger

# Create and configure a named logger

log = setup_logger()

version = ""
fname = "version.txt"
if os.path.isfile(fname):
    with open(fname, 'r') as f:
        version = f.readline()

log.info(f"Application started. Version: {version}")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-apitype", help="type of API", type=str, dest='apiType')
parser.add_argument("-server", help="server to scrape", type=str, dest='server')

args = parser.parse_args()
log.info(f"args: {args}")

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
scraper.do_scrape()
