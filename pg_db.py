import psycopg
from psycopg_pool import ConnectionPool

class PG_DB:
    def __init__(self):
        self.connection = psycopg.connect("dbname=test user=postgres")

