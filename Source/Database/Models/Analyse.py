from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class Analyse(BaseModel):
    tableName = Table.ANALYSE.value

    primaryFields = [Field.USER_ID.value, Field.TOKEN.value]
    
    fields = {
        Field.USER_ID.value: "int",
        Field.DATETIME.value: "text",
        Field.TOKEN.value: "text",
        Field.KNOWLEDGE_VALUE.value: "int",
    }

    # relations = [
    #     f"FOREIGN KEY({Field.USER_ID.value}) REFERENCES {Table.USER.value}({Field.USER_ID.value})",
    #     f"PRIMARY KEY ({Field.USER_ID.value}, {Field.TOKEN.value})"
    # ]

    fk = [
        {"table": Table.USER.value, "from": Field.USER_ID.value, "to": Field.USER_ID.value, "onDelete": "CASCADE"},
    ]
