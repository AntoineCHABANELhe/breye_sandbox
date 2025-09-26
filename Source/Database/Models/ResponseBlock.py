from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class ResponseBlock(BaseModel):
    tableName = Table.RESPONSE_BLOCK.value
    
    primaryFields = [Field.DATETIME.value]

    fields = {
        Field.USER_ID.value: "int",
        "block_id": "int",
        Field.ANSWER.value: "text",
        Field.DATETIME.value: "text",
    }

    # relations = [
    #     f"FOREIGN KEY({Field.USER_ID.value}) REFERENCES {Table.USER.value}({Field.USER_ID.value})",
    #     "PRIMARY KEY (date_time)"
    # ]

    fk = [
        {"table": Table.USER.value, "from": "user_id", "to": "user_id", "onDelete": "CASCADE"},
    ]
