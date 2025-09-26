from Source.Database.db_enums import Table, Field
from Source.Database.Models.model import BaseModel


class Session(BaseModel):
    tableName = Table.SESSION.value

    primaryFields = ["id"]

    fields = {
        "id": "INTEGER",
        Field.USER_ID.value: "int",
        Field.SCORE.value: "int",
        Field.ACTIVITY_ID.value: "int",
        "date_time_start": "text",
        "date_time_end": "text DEFAULT NULL",
    }

    oldFieldsNames = {
        Field.SCORE.value: ["scr"]
    }

    fk = [
        {"table": Table.USER.value, "from": Field.USER_ID.value, "to": Field.USER_ID.value, "onDelete": "CASCADE"},
    ]
