from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class ErrorLog(BaseModel):
    tableName = Table.ERROR_LOG.value

    primaryFields = [Field.DATETIME.value]
    
    fields = {
        Field.DATETIME.value: "text",
        "log": "text",
        "error_code": "int",
        Field.ACTIVITY_ID.value: "int",
    }

    # relations = [
    #     f"FOREIGN KEY(activity_id) REFERENCES {Table.ACTIVITY.value}(activity_id)"
    # ]

    fk = [
        {"table": Table.ACTIVITY.value, "from": Field.ACTIVITY_ID.value, "to": Field.ACTIVITY_ID.value, "onDelete": "CASCADE"}
    ]
