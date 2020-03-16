import configparser
from mysql.connector import connect

class Database:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.properties')

        self._conn = connect(host=config['Database']['database.host'],
                     database=config['Database']['database.dbname'],
                     user=config['Database']['database.user'],
                     password=config['Database']['database.pass'],
                     auth_plugin='mysql_native_password')
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()