import sqlite3
import traceback
from colorama import Fore
from datetime import datetime, timezone
from Resources.unit_test import inUnittest
from Source.BrailleTool.error_enum import B_log
from Source.Database.db_enums import Table
from Source.Database.handle_database import HandleDB, Data


def simpleErrorLog(error_text: str = "", error_type: B_log = B_log.DEFAULT, activity_id=404):
    """
    Save error in the DB. If the table isn't created, create the ERROR_LOG table.

    Parameter(s):
    - error_text : The error to save. Will be converted to string
    - error_type : Which error it is. Will help with debugging
    """
    code = error_type.value[0]
    text = f"{error_text}{error_type.value[1]}"
    try:
        text = str(text).replace('\'', '\'\'')
        time = HandleDB().getNow()
        HandleDB().execute(f"INSERT INTO {Table.ERROR_LOG.value} VALUES ('{time}', ?, ?, ?)", [text, -code, activity_id])
    except sqlite3.Error as err:
        print(f"{err} > ################ --- {text}")


def errorLog(error_text: str = "", error_type: B_log = B_log.DEFAULT, mute=False, print_trace=True):
    """
    Save error in the DB. If the table isn't created, create the ERROR_LOG table.

    Parameter(s):
    - error_text : The error to save. Will be converted to string
    - error_type : Which error it is. Will help with debugging
    """
    code = error_type.value[0]
    text = f"{error_text}{error_type.value[1]}"
    if not mute:
        print(f"{Fore.RED}########## {Fore.MAGENTA}{code:-^8} {Fore.RESET}{text}")
        # if print_trace and not inUnittest():
        #     for line in traceback.format_stack():
        #         print(line.strip())
        #     print(f"{Fore.RED}####### ]]{Fore.RESET}")

    if print_trace:
        print(traceback.format_exc())

    try:
        activity = HandleDB().getData(Data.ACTIVITY)
        activity_id = get_activity_id(activity)

        try:
            text = str(text).replace('\'', '\'\'')
            time = HandleDB().getNow()
            HandleDB().execute(f"INSERT INTO {Table.ERROR_LOG.value} VALUES ('{time}', ?, ?, ?)", [text, -code, activity_id])
        except sqlite3.Error as err:
            print(f' > ################ --- log error {err}')
            if not HandleDB().table_exists(Table.ERROR_LOG.value):
                HandleDB().execute(f'CREATE TABLE {Table.ERROR_LOG.value} ( date_time  text ,log text,error_code int ,activity_id int)')
                time = HandleDB().getNow()
                HandleDB().execute(f"INSERT INTO {Table.ERROR_LOG.value} VALUES ('{time}','Table {Table.ERROR_LOG.value} did not exists',{B_log.TABLE_DOES_NOT_EXIST})")
    except Exception as e:
        print(e)


def get_activity_id(activity_name):
    """
    returns the activity Id of the requested activity.
    It will create the activity in the database if it wasn't yet created. This will log an error, as all br'eye might
    not have the same activity id if they are created this way.

    returns 404 if there are errors.

    Parameter(s):
    - activity_name : Name of the activity
    """

    if activity_name == '' or activity_name is None:
        return 0

    try:
        activity = HandleDB().getBy(Table.ACTIVITY.value, 'activity', activity_name)
        if not activity:
            HandleDB().execute(f"INSERT INTO {Table.ACTIVITY.value}(activity) VALUES (?)", [activity_name])
            if not inUnittest():
                print(f"#### Activity '{activity_name}' wasn't instantiated in the database, we're adding it.")
            activity = HandleDB().getBy(Table.ACTIVITY.value, 'activity', activity_name)
        return activity[0]
    except sqlite3.Error as err:
        if not HandleDB().table_exists(Table.ACTIVITY.value):
            simpleErrorLog(str(err), B_log.TABLE_DOES_NOT_EXIST)
            HandleDB().execute(f'CREATE TABLE {Table.ACTIVITY.value} (activity_id INTEGER PRIMARY KEY,activity text)')
            HandleDB().execute(f"INSERT INTO {Table.ACTIVITY.value}(activity) VALUES (?)", [activity_name])
            return HandleDB().getBy(Table.ACTIVITY.value, 'activity', activity_name)[0]
    except Exception as e:
        print(e)
    return 404
