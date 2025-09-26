from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class Occurrence(BaseModel):
    tableName = Table.OCCURRENCE.value
    
    primaryFields = [Field.USER_ID.value, Field.ACTION_ID.value, Field.ACTIVITY_ID.value]

    fields = {
        Field.USER_ID.value: "int",
        Field.ACTION_ID.value: "int",
        Field.ACTIVITY_ID.value: "int",
        "counter": "int"
    }

    # relations = [
    #     f"FOREIGN KEY(activity_id) REFERENCES {Table.ACTIVITY.value}(activity_id)",
    #     f"FOREIGN KEY(action_id) REFERENCES {Table.ACTION.value}(action_id)",
    #     f"FOREIGN KEY({Field.USER_ID.value}) REFERENCES {Table.USER.value}({Field.USER_ID.value})",
    #     f"PRIMARY KEY ({Field.USER_ID.value}, action_id, activity_id)"
    # ]

    fk = [
        {"table": Table.ACTIVITY.value, "from": Field.ACTIVITY_ID.value, "to": Field.ACTIVITY_ID.value, "onDelete": "CASCADE"},
        {"table": Table.ACTION.value, "from": Field.ACTION_ID.value, "to": Field.ACTION_ID.value, "onDelete": "CASCADE"},
        {"table": Table.USER.value, "from": Field.USER_ID.value, "to": Field.USER_ID.value, "onDelete": "CASCADE"}
    ]
