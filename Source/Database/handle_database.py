import datetime
import sqlite3
from enum import auto, Enum
from datetime import timezone

from colorama import Fore

from Source.Database.db_enums import Table


class Data(Enum):
    SESSION_ID = auto()
    ACTIVITY = auto()
    SCORE = auto()
    ANALYSES = auto()
    USER_ID = auto()
    BREYE_USER_ID = auto()
    UPDATED_QUIZZ = auto()
    UPDATED_WIFI = auto()


class HandleDB:
    instance = None

    def __init__(self, name='BrEye.db', options={}):
        if not HandleDB.instance:
            HandleDB.instance = HandleDB.__HandleDB(name, options)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __HandleDB:
        def __init__(self, name='BrEye.db', options={}):
            self._sqlite_connection = sqlite3.connect(name, check_same_thread=False)
            self._sqlite_connection.execute('PRAGMA synchronous = OFF')
            sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())
            self.data = {}
            self._emit = None

            for data in Data:
                self.data[data.name] = None

        def getNow(self):
            return datetime.datetime.now(timezone.utc)

        def execute(self, command: str, params=[], print_error=True):
            try:
                cursor = self._sqlite_connection.execute(command, params)
                self._sqlite_connection.commit()
                return cursor
            except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                if print_error:
                    print(f'### error : {e} \n Could not complete command {command} params: {params}')
                return False

        def fetch(self, command: str, params=[]) -> list:
            try:
                return self.execute(command, params).fetchone()
            except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                print(f'### error : {e} \n Could not complete command {command}')
                return []

        def fetchAll(self, command: str, params=[]) -> list:
            try:
                return self.execute(command, params).fetchall()
            except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                print(f'### error : {e} \n Could not complete command {command}')
                return []

        def getBy(self, tableName, column, value):
            try:
                return self.fetch(f'SELECT * FROM {tableName} WHERE {column} = ? LIMIT 1', [value])
            except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                print(f'### error : {e} \n Could not get {tableName} with {column} = {value}')
                return []
        
        def getData(self, key):
            return self.data[key] if key in self.data else None

        def setData(self, key, value):
            self.data[key] = value

        def emitData(self, table, data):
            if self._emit:
                self._emit("data", {
                    "table": table,
                    "data": data
                })
            else:
                print(f"{Fore.RED}#########{Fore.MAGENTA}{'0000':-^8}{Fore.RESET} emit not set, nothing to send web socket")

        def setEmit(self, emit_method):
            self._emit = emit_method

        def table_exists(self, table) -> bool:
            """
            returns true if the table exist in the DataBase

            Parameter(s):
            - table : Name of the table
            """
            try:
                return self.execute("SELECT * FROM {}".format(table), print_error=False)
            except:
                return False

        def verify(self):
            """Check if the DB is operational. If not, repair it and returns False"""
            
            for tab in Table:
                if not self.table_exists(tab.value):
                    return False

            return True

    def close(self):
        if self._sqlite_connection:
            self._sqlite_connection.close()
        HandleDB.instance = None