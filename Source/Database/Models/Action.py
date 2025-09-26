from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class Action(BaseModel):
    tableName = Table.ACTION.value

    primaryFields = [Field.ACTION_ID.value]
    
    fields = {
        Field.ACTION_ID.value: "INTEGER",
        "action": "text"
    }
