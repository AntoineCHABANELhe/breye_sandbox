from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class ResponseWord(BaseModel):
    tableName = Table.RESPONSE_WORD.value

    primaryFields = [Field.DATETIME.value]

    fields = {
        Field.USER_ID.value: "int",
        Field.DATETIME.value: "text",
        Field.ANSWER.value: "text",
        "wanted_answer": "text",
        Field.ACTIVITY_ID.value: "int",
    }

    # relations = [
    #     f"FOREIGN KEY(activity_id) REFERENCES {Table.ACTIVITY.value}(activity_id)",
    #     f"FOREIGN KEY({Field.USER_ID.value}) REFERENCES {Table.USER.value}({Field.USER_ID.value})",
    #     "PRIMARY KEY (date_time)"
    # ]

    fk = [
        { "table": Table.ACTIVITY.value, "from": Field.ACTIVITY_ID.value, "to": Field.ACTIVITY_ID.value, "onDelete": "CASCADE" },
        { "table": Table.USER.value, "from": Field.USER_ID.value, "to": Field.USER_ID.value, "onDelete": "CASCADE" },
    ]
