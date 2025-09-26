import json

from time import time
from colorama import Fore
from getmac import get_mac_address

from Source.BrailleTool.handle_logs import print_debug, DEBUG
from Resources.unit_test import inUnittest
from Source.BrailleTool.error_enum import B_log
from Source.Database.db_enums import Table
from Source.Database.error_log import errorLog
from Source.Database.handle_database import HandleDB, Data


def getRecordsInTable(table_name, last_id='', raw=False):
    """last_id : id of the last data sent to the server. if not given, we retrieve all the data from the given table."""
    sql = ""

    if table_name == Table.SESSION.value or table_name == Table.RESPONSE_TOKEN.value or table_name == Table.RESPONSE_BLOCK.value or table_name == Table.RESPONSE_WORD.value or table_name == Table.OCCURRENCE.value:
        sql = f"LEFT JOIN {Table.USER.value} ON {table_name}.user_id = {Table.USER.value}.user_id "

    if table_name == Table.SESSION.value or table_name == Table.RESPONSE_TOKEN.value or table_name == Table.RESPONSE_WORD.value or table_name == Table.ERROR_LOG.value or table_name == Table.OCCURRENCE.value:
        sql += f"LEFT JOIN {Table.ACTIVITY.value} ON {table_name}.activity_id = {Table.ACTIVITY.value}.activity_id "

    if table_name == Table.OCCURRENCE.value:
        sql += f"LEFT JOIN {Table.ACTION.value} ON {table_name}.action_id = {Table.ACTION.value}.action_id "

    results = []
    cur = None

    if last_id == '':
        cur = HandleDB().execute(f"SELECT * FROM {table_name} {sql}")
    else:
        date = 'date_time_end' if table_name == Table.SESSION.value else 'date_time'
        cur = HandleDB().execute(f"SELECT * FROM {table_name} {sql} WHERE {date} > {last_id}")

    results = cur.fetchall()

    _json = [dict(zip([key[0] for key in cur.description], row)) for row in results]

    if raw:
        return _json

    return json.dumps(_json)


def get_all_data():
    print_debug(f'\t\t\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Send db : Generating jsons', DEBUG.WEB)

    dic = {}
    # last_data_sent = []

    for table in Table:
        table_name = table.value

        if table_name[0] != '_':
            dic[table_name] = []
            tabs = "\t\t" if len(table_name) < 10 else "\t" if len(table_name) < 20 else ""
            text = f'\t\t\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET}   > Generating json for {table_name}{tabs} '

            try:
                # last_id = HandleDB().fetch(f"SELECT last_id FROM {Table.LAST_SENT.value} WHERE table_id = ?", [table_name])

                # if not last_id:
                #     last_id = ''
                # else:
                #     last_id = last_id[0]

                # if str(last_id) != '1':  # last_id == '1' when 'Uses' table has not been modified, so we don't push it
                dic[table_name] = getRecordsInTable(table_name, "", raw=True)

                # if table_name == Table.OCCURRENCE.value:
                #     last_data_sent.append([table_name, '1'])

                # if dic[table_name] and 'date_time' in dic[table_name][-1]:  # dic[table_name][-1] is the latest data from the table
                #     last_data_sent.append([table_name, dic[table_name][-1]['date_time']])

                # if table_name == Table.SESSION.value and dic[table_name]:
                #     last_data_sent.append([table_name, dic[table_name][-1]['date_time_end']])
                
                print_debug(f'{text}> done !', DEBUG.WEB)
            except Exception as e:
                print_debug(f'{text}> Couldn\'t generate json for {table_name} : {e}')
                errorLog(f'Couldn\'t generate json for {table_name} : {e}', B_log.DATABASE_15, mute=True)

    return dic


def timer_func(func):
    # This function shows the execution time of the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        if not inUnittest():
            # print(f'Function {func.__name__!r}({args[0]}) executed in {(t2 - t1):.4f}s')
            print_debug(f'Function {func.__name__!r} executed in {(t2 - t1):.4f}s')
        return result

    return wrap_func


# @timer_func
def get_user_pseudo(user_id, field='user_id'):
    try:
        user = HandleDB().fetch(f"SELECT pseudo FROM {Table.USER.value} WHERE {field} = ? LIMIT 1", [user_id])
        return user[0] if user else ""
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_16)
        return ""


# @timer_func
def get_action_id(action_name):
    """
    Copies Activity but with actions.

    returns 404 if there are errors.

    Parameter(s):
    - db_con : SQLite connector
    - action : Name of the action
    """
    try:
        action = HandleDB().getBy(Table.ACTION.value, 'action', action_name)
        if action is None:
            HandleDB().execute(f"INSERT INTO {Table.ACTION.value}(action) VALUES (?)", [action_name])
            print_debug(f"#### Action '{action_name}' wasn't instantiated in the database, we're adding it.")
            action = HandleDB().getBy(Table.ACTION.value, 'action', action_name)
        return action[0]
    except Exception as error:
        print_debug(error)
        if not HandleDB().table_exists(Table.ACTION.value):
            HandleDB().execute(f'CREATE TABLE {Table.ACTION.value} (action_id INTEGER PRIMARY KEY, action text)')
            HandleDB().execute(f"INSERT INTO {Table.ACTION.value}(action) VALUES (?)", [action_name])
            errorLog(str(error), B_log.DATABASE_17)
            return HandleDB().getBy(Table.ACTION.value, 'action', action_name)[0]

    return 404


# @timer_func
def user_exists(id):
    """
    returns true if the user exists in the Users table

    Parameter(s):
    - id : User ID
    """
    if not HandleDB().table_exists(Table.USER.value):
        try:
            HandleDB().execute(f'''CREATE TABLE {Table.USER.value} (
                user_id INTEGER PRIMARY KEY,
                breye_user_id int,
                default_user int,
                progression int,
                pseudo text DEFAULT NULL
            )''')
        except Exception as error:
            errorLog(error, B_log.DATABASE_18)
        return False
    try:
        user = HandleDB().getBy(Table.USER.value, 'user_id', id)
        if user:
            return True
        return False

    except Exception as error:
        errorLog(error, B_log.DATABASE_19)
        return False


# @export.timer_func


# @export.timer_func
def get_parameter(user_id, param):
    try: 
        parameter = HandleDB().fetch(f"SELECT value FROM {Table.SETTING.value} WHERE user_id = ? AND key = ? LIMIT 1", [user_id, param])
        return parameter[0] if parameter else None
    except Exception as e:
        print_debug(e)
        return None


# @export.timer_func
def get_parameters(user_id):
    try:
        parameters = HandleDB().fetchAll(f"SELECT key, value FROM {Table.SETTING.value} WHERE user_id = ?", [user_id])
        return parameters
    except Exception as e:
        print_debug(e)
        return []


def get_user_breye_id(user_id=None):
    if user_id is None:
        breye_user_id = HandleDB().getData(Data.BREYE_USER_ID)
        
        if breye_user_id:
            return breye_user_id 

        user_id = 0
        
    try:
        breye_id = HandleDB().fetch(f"SELECT breye_user_id FROM {Table.USER.value} WHERE user_id = ? LIMIT 1", [user_id])
        return breye_id[0] if breye_id else None
    except Exception as e:
        print_debug(e)
        return ""


def get_mac(formatted=True):

    first_user = HandleDB().fetch(f"SELECT breye_user_id FROM {Table.USER.value} LIMIT 1")
    if first_user:
        mac = first_user[0][:-1]
    else:
        mac = get_mac_address("eth0") or get_mac_address() or "00000000"
        mac = mac.lower().replace(':', '')
    
    if formatted:
        return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2)).upper()

    return mac


def get_user_id():
    return HandleDB().getData(Data.USER_ID) or 0
