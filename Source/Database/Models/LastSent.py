from Source.Database.db_enums import Table
from Source.Database.Models.model import BaseModel


class LastSent(BaseModel):
    tableName = Table.LAST_SENT.value
    
    primaryFields = ["table_id"]
    
    fields = {
        "table_id": "TEXT",
        "last_id": "letter"
    }
