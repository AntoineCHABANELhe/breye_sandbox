from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class Setting(BaseModel):
    tableName = Table.SETTING.value
    
    primaryFields = [Field.USER_ID.value, "key"]

    fields = {
        Field.USER_ID.value: "int",
        "key": "text",
        "value": "text",
    }

    fk = [
        {"table": Table.USER.value, "from": Field.USER_ID.value, "to": Field.USER_ID.value, "onDelete": "CASCADE"}
    ]
