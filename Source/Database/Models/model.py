from colorama import Fore
from Source.Database.handle_database import HandleDB


class BaseModel:
    tableName = None
    fk = []

    primaryFields = ["id"]

    oldFieldsNames = {}

    def __init__(self, primary_values: dict = None):
        if primary_values is None:
            self.primaryValue = {field: None for field in self.primaryFields}
        else:
            self.primaryValue = primary_values

    def onMigrated(self):
        """ Override this method to do something after migration """

    def insert(self, data):
        """ Insert data into table """

        columns = ", ".join([f"{key}" for key in self.fields.keys()])
        values = ", ".join([f":{key}" for key in self.fields.keys()])

        HandleDB().execute(f"INSERT INTO {self.tableName} ({columns}) VALUES ({values})", data)

    def update(self, data: dict):
        """ Update data in table """

        # data = {
        #     ,
        #     'breye_user_id': f"{export.get_mac(False)}{user_id}",
        #     'default_user': 0,
        #     'progression': 101,
        #     "pseudo": f"utilisateur {user_id}"
        # }
        #
        # User({'user_id': user_id}).update(data) """INSTEAD OF""" HandleDB().execute( ....,data)

        columns = ", ".join([f"{key} = :{key}" for key in data.keys()])

        data.update(self.primaryValues)

        HandleDB().execute(f"UPDATE {self.tableName} SET {columns} WHERE {self.primaryField} = :{self.primaryField}", data)

    def getSchemaField(self, field):
        """ Get schema of field """

        parts = self.fields[field].split()
        type = parts[0].upper()
        extra = []

        if len(parts) > 1:
            extra = parts[1:]

        return f"{field} {type} {' '.join(extra)}".strip() if field in self.fields else None

    def getSchema(self, pretty=False):
        """ Get schema of table """
        separator = ",\n  " if pretty else ", "
        columns = separator.join([
            self.getSchemaField(key)
            for key, value in self.fields.items()
        ])

        relations_lst = [
            f"FOREIGN KEY ({value['from']}) REFERENCES {value['table']}({value['to']}) {'ON DELETE ' + value['onDelete'] if 'onDelete' in value else ''}".strip()
            for value in self.fk
        ]
        relations_lst.append(f"PRIMARY KEY ({', '.join(self.primaryFields)})")

        relations = separator.join(relations_lst)

        if pretty:
            return f"""CREATE TABLE {self.tableName} (\n  {columns}\n)"""
        
        return f"""CREATE TABLE {self.tableName} ({(columns + ', ' + relations).strip().strip(',')})"""

    def getCurrentSchema(self):
        cursor = HandleDB().execute(f"PRAGMA table_info({self.tableName})")
        columns = [desc[0] for desc in cursor.description]
        columns = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor = HandleDB().execute(f"PRAGMA foreign_key_list({self.tableName})")
        relations = [desc[0] for desc in cursor.description]
        relations = [dict(zip(relations, row)) for row in cursor.fetchall()]

        return {
            "columns": columns,
            "relations": relations
        }
    
    def getCurrentSchemaColumnSQL(self, column):
        sql = [column['name'], column['type'].upper()]

        if column["notnull"] == 1:
            sql.append("NOT NULL")

        if column["pk"] == 1:
            sql.append("PRIMARY KEY")

        return " ".join(sql)

    def migrate(self):
        """
        Check if table exists and up to date
        """

        if not HandleDB().table_exists(self.tableName):
            print(f"  > Creating {self.tableName} :", end=" ")
            HandleDB().execute(self.getSchema())
            self.onMigrated()
            print(f" Created {self.tableName}")

            return

        current_schema = self.getCurrentSchema()

        # Check columns
        print(f"Checking columns for {self.tableName + '...':17}", end=" ")
        for key, value in self.fields.items():
            schema = self.getSchemaField(key)

            if not schema:
                continue

            # Check if current column has old name
            oldNames = self.oldFieldsNames[key] if key in self.oldFieldsNames else []
            try:
                oldColumn = [column for column in current_schema["columns"] if column["name"] in oldNames][0]
            except:
                oldColumn = None

            # Check if column exists
            if oldColumn:
                print(f"\n  >> Renaming column {Fore.BLUE}{oldColumn['name']}{Fore.RESET} to {key} in {self.tableName}", end=" ")
                HandleDB().execute(f"ALTER TABLE {self.tableName} RENAME COLUMN {oldColumn['name']} TO {key}")
                print(f"{Fore.GREEN}Renamed{Fore.RESET}")
                current_schema = self.getCurrentSchema()

            try:
                column = [column for column in current_schema["columns"] if column["name"] == key][0]
            except:
                column = None

            if not column:
                print(f"\n  >> Adding column {Fore.BLUE}{key}{Fore.RESET} to {self.tableName}", end=" ")
                HandleDB().execute(f"ALTER TABLE {self.tableName} ADD COLUMN {schema}")
                print(f"{Fore.GREEN}Added{Fore.RESET}")

        # Remove columns that are not in model
        for column in current_schema["columns"]:
            if column["name"] not in self.fields.keys():
                print(f"\n  >> Removing column {Fore.BLUE}{column['name']}{Fore.RESET} from {self.tableName}", end=" ")
                HandleDB().execute(f"ALTER TABLE {self.tableName} DROP COLUMN {column['name']}")
                print(f"{Fore.GREEN}Removed{Fore.RESET}")

        # Check relations
        print(f"Checking relations for {self.tableName}")
        for value in self.fk:
            if value["from"] not in [relation["from"] for relation in current_schema["relations"]]:
                print(f"\n  >> Adding relation {Fore.BLUE}{value['from']}{Fore.RESET} to {self.tableName}", end=" ")
                HandleDB().execute(f"ALTER TABLE {self.tableName} ADD FOREIGN KEY ({value['from']}) REFERENCES {value['table']}({value['to']})")
                print(f"{Fore.GREEN}Added{Fore.RESET}")
