from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class Activity(BaseModel):
    tableName = Table.ACTIVITY.value
    
    primaryFields = [Field.ACTIVITY_ID.value]

    fields = {
        Field.ACTIVITY_ID.value: "INTEGER",
        "activity": "text"
    }
