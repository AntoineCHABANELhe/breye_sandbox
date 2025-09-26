import sqlite3
from getmac import get_mac_address
from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class User(BaseModel):
    tableName = Table.USER.value

    primaryFields = [Field.USER_ID.value]
    
    fields = {
        "user_id": "INTEGER",
        "breye_user_id": "int",
        "default_user": "int",
        "progression": "int DEFAULT 0",
        "pseudo": "text DEFAULT NULL",
    }
    
    def onMigrated(self):
        mac = get_mac_address("eth0")
        
        if mac is None:
            mac = get_mac_address()
            
        mac = mac.lower().replace(':', '')

        breye_user_id_1 = f"{mac}0"

        data = {
            f'{Field.USER_ID.value}': 0,
            'breye_user_id': breye_user_id_1,
            'default_user': 1,
            'progression': None,
            "pseudo": "visiteur"
        }

        try:
            self.insert(data)
            # db.execute(f"INSERT INTO {Table.USER.value} VALUES (:{Field.USER_ID.value}, :breye_user_id, :default_user, :pseudo)", data)
        except sqlite3.Error as error:
            print(error)
