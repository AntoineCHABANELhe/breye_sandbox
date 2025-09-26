from time import sleep

import Source.Database.export_data as export
from colorama import Fore, init
from datetime import datetime, timezone

from Source.APIs.Hardware.wifi_wpa_cli import connect_to_wifi
from Source.BrailleTool.handle_logs import print_debug, DEBUG
from Source.FilesHandling.environment_data import isMarble
from Source.BrailleTool.convert import brailleToChar, guessStringInput, elementsToBraille
from Source.BrailleTool.error_enum import B_log
from Source.Database.db_enums import Table, Field, Action
from Source.Database.error_log import get_activity_id, errorLog
from Source.Database.analyse_data import calculateAgingTokenScore, calculateTokenGrade, \
    calculateTokenGradeFromWord
from Source.Database.handle_database import Data, HandleDB

init()


def log(status): errorLog("", status, mute=True, print_trace=False)


def addTokenOccurrence(token, new_value, current):  # TODO : handle multiplayer application
    today = datetime.now()
    user_id = export.get_user_id() if current else 0

    try:
        value, date = HandleDB().fetch(f"SELECT {Field.KNOWLEDGE_VALUE.value}, {Field.DATETIME.value} "
                                       f"FROM {Table.ANALYSE.value} "
                                       f"WHERE user_id=:user_id AND {Field.TOKEN.value}=:token",
                                       {
                                           'user_id': user_id,
                                           'token': token,
                                       })
        value = (calculateAgingTokenScore(value, date) + new_value) if value else new_value
    except:
        value = new_value

    try:
        HandleDB().execute(f"INSERT OR REPLACE INTO {Table.ANALYSE.value} VALUES (:user_id,:date,:token,:value);",
                           {
                               'user_id': user_id,
                               'date': today,
                               'token': token,
                               'value': value,
                           })
    except Exception as error:
        print_debug(error.__str__())
        errorLog(str(error), B_log.DATABASE_01)


def saveResultToken(tokens, err_suc_scale=0, current=True, add_grade=False):
    """
    Insert tokens and corresponding scores in the database

    Parameter(s):
    - tokens : list(braille) : each token tested with the same scale rating.
    - err_suc_scale : from -10 to 100, if the letter was correctly chosen and/or tested by the user.
    """
    braille_tokens = elementsToBraille(tokens)
    try:
        activity = HandleDB().getData(Data.ACTIVITY)
        activity_id = get_activity_id(activity)
        user_id = export.get_user_id() if current else 0
        for token in braille_tokens:
            if add_grade:
                calculateTokenGrade(token, err_suc_scale, current, addTokenOccurrence)
            letter = brailleToChar(token)
            time = HandleDB().getNow()
            data = {
                'user_id': user_id,
                'date_time': str(time),
                'token': letter,
                'err_suc_scale': err_suc_scale,
                'activity_id': activity_id
            }
            HandleDB().execute(f"INSERT INTO {Table.RESPONSE_TOKEN.value} VALUES (:user_id, :date_time, :token, :err_suc_scale, :activity_id)", data)

            print_debug(f"User ({user_id}) activity ({activity_id}) time ({str(time)}) letter ({letter})", DEBUG.SAVE)

            # Preparing data sent to the server
            data_dic = {'data': data,
                        'breye_user_id': export.get_user_breye_id(),
                        'activity': activity
                        }

            HandleDB().emitData(Table.RESPONSE_TOKEN.value, data_dic)

    except Exception as error:
        print_debug("LOG SAVE RESULT TOKEN ERROR")
        errorLog(str(error), B_log.DATABASE_02)


def saveResultWord(input_word, wanted_word, result, current=True, save_tokens=True):  # TODO : handle multiplayer application
    """Insert input_word and wanted_word in the database"""
    if input_word.isdigit() and wanted_word.isdigit():  # No braille mistake there
        result = 1
    user_id = export.get_user_id() if current else 0
    if save_tokens:
        for token in calculateTokenGradeFromWord(guessStringInput(input_word), guessStringInput(wanted_word), result, current, addTokenOccurrence):
            saveResultToken(token[0], token[1], current, add_grade=False)

    try:
        activity = HandleDB().getData(Data.ACTIVITY)
        activity_id = get_activity_id(activity)
        # Insert on row per letter
        time = HandleDB().getNow()
        data = {
            'user_id': user_id,
            'date_time': str(time),
            'input_word': input_word,
            'wanted_word': wanted_word,
            'activity_id': activity_id
        }
        HandleDB().execute(f"INSERT INTO {Table.RESPONSE_WORD.value} VALUES (:user_id, :date_time, :input_word, :wanted_word, :activity_id)", data)

        print_debug(f"User ({user_id}) activity ({activity_id}) time ({str(time)}) word ({input_word})", DEBUG.SAVE)

        # Preparing data sent to the server
        data_dic = {'data': data,
                    'breye_user_id': export.get_user_breye_id(),
                    'activity': activity
                    }

        HandleDB().emitData(Table.RESPONSE_WORD.value, data_dic)

    except Exception as error:
        errorLog(str(error), B_log.DATABASE_03)


def saveResultBlock(block_id, answer):  # Insert the answer to the question corresponding to block_id into the database
    try:
        user_id = export.get_user_id()
        time = HandleDB().getNow()
        data = {
            'user_id': user_id,
            'block_id': block_id,
            'answer': answer,
            'date_time': str(time)
        }
        HandleDB().execute(f"INSERT INTO {Table.RESPONSE_BLOCK.value} VALUES (:user_id, :block_id, :answer, :date_time)", data)

        # Preparing data sent to the server
        data_dic = {'data': data,
                    'breye_user_id': export.get_user_breye_id(),
                    }
        HandleDB().emitData(Table.RESPONSE_BLOCK.value, data_dic)

    except Exception as error:
        errorLog(str(error), B_log.DATABASE_04)


def initiateSession(activity):  # Initiate the session for an activity. The ending date of this session is updated later
    try:
        user_id = export.get_user_id()
        current_session = HandleDB().getData(Data.SESSION_ID)
        activity_id = get_activity_id(activity)
        time = HandleDB().getNow()

        if current_session is not None:
            stopSession(current_session, time)
        
        HandleDB().setData(Data.ACTIVITY, activity)

        cur = HandleDB().execute(f"INSERT INTO {Table.SESSION.value}(user_id, activity_id, date_time_start) VALUES (:user_id, :activity_id, :date_time_start)", {
            'user_id': user_id,
            'activity_id': activity_id,
            'date_time_start': time
        })

        HandleDB().setData(Data.SESSION_ID, cur.lastrowid)
        HandleDB().setData(Data.SCORE, 0)
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_05)


def stopSession(session_id, time):  # Record the ending of the session related to the last used activity to the database
    try:
        current_activity = HandleDB().getData(Data.ACTIVITY)
        breye_user_id = export.get_user_breye_id()
        score = HandleDB().getData(Data.SCORE)

        HandleDB().execute(f"UPDATE {Table.SESSION.value} "
                           f"SET date_time_end = :date_time_end, {Field.SCORE.value} = :score "
                           f"WHERE id = :id", {
                            "date_time_end": time,
                            "score": score,
                            "id": session_id
                            })

        # Prepare data to be sent to the server
        cur = HandleDB().execute(f"SELECT * FROM {Table.SESSION.value} WHERE id = ?", [session_id])
        row = cur.fetchone()
        data = dict(zip([key[0] for key in cur.description], row))
        data_dic = {'data': data, "breye_user_id": breye_user_id, "activity": current_activity}
        HandleDB().emitData(Table.SESSION.value, data_dic)
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_06)


def isFirstSession(activity):
    try:
        user_id = export.get_user_id()
        action_id = export.get_action_id(Action.GAME_ENDED)
        activity_id = get_activity_id(activity)

        complete_session = HandleDB().fetch(
            command=f"SELECT * FROM {Table.OCCURRENCE.value} "
                    f"WHERE user_id = ? AND action_id = ? AND activity_id = ?",
            params=[user_id, action_id, activity_id]
        )

        return complete_session is None or complete_session == []

    except Exception as error:
        errorLog(str(error), B_log.DATABASE_20)
        return True


def addOccurrence(action):
    try:
        user_id = export.get_user_id()
        activity = HandleDB().getData(Data.ACTIVITY)
        activity_id = get_activity_id(activity)
        action_id = export.get_action_id(action)
        HandleDB().execute(f"""INSERT OR REPLACE INTO {Table.OCCURRENCE.value}
            VALUES (:user_id,:action_id,:activity_id,
              COALESCE(
                (SELECT counter FROM {Table.OCCURRENCE.value}
                   WHERE user_id=:user_id AND action_id=:action_id AND activity_id=:activity_id),
                0) + 1);""",
                    {
                        'user_id': user_id,
                        'action_id': action_id,
                        'activity_id': activity_id
                    })

        HandleDB().execute(f"INSERT OR REPLACE INTO {Table.LAST_SENT.value} VALUES(?, '')", [Table.OCCURRENCE.value])
    except Exception as error:
        print_debug(error.__str__())
        errorLog(str(error), B_log.DATABASE_07)


def saveLast(table, value, db_con=None):
    """
    save the id of the last data of the table sent to the server

    Parameter(s):
    - table : Name of the table
    - value : id of the last data
    """

    if not HandleDB().table_exists(Table.LAST_SENT.value):
        HandleDB().execute(f'CREATE TABLE {Table.LAST_SENT.value} (table_id text PRIMARY KEY, last_id text)')
        errorLog(f'Table {Table.LAST_SENT.value} did not exist', B_log.DATABASE_08)
    try:
        HandleDB().execute(f"INSERT OR REPLACE INTO {Table.LAST_SENT.value} VALUES(?, ?)", [table, value])
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_09)


def saveUser(user_id, set_user=True):

    if not export.user_exists(user_id):
        try:
            data = {
                'user_id': user_id,
                'breye_user_id': f"{export.get_mac(False)}{user_id}",
                'default_user': 0,
                'progression': 101,
                "pseudo": f"utilisateur {user_id}"
            }
            HandleDB().execute(f"INSERT INTO {Table.USER.value} VALUES(:user_id, :breye_user_id, :default_user, :progression, :pseudo)", data)
            HandleDB().emitData(Table.USER.value, data)
        except Exception as error:
            errorLog(str(error), B_log.DATABASE_10)

    if set_user:
        HandleDB().setData(Data.USER_ID, user_id)
        HandleDB().setData(Data.BREYE_USER_ID, export.get_user_breye_id(user_id))


def getProgress():
    user_id = export.get_user_id()
    try:
        prog = HandleDB().fetch(f"SELECT progression FROM {Table.USER.value} WHERE user_id = {user_id}")
        return prog[0] if prog and prog[0] else 0
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_11)
        return 0


def saveProgress(progress):
    user_id = export.get_user_id()
    try:
        HandleDB().execute(f"UPDATE {Table.USER.value} SET progression = ? WHERE user_id = ?", [progress, user_id])
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_12)


# @export.timer_func
def saveUserPseudo(pseudo, id, field="user_id"):
    try:
        HandleDB().execute(f"UPDATE {Table.USER.value} SET pseudo = ? WHERE {field} = ?", [pseudo, id])
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} User pseudo saved", DEBUG.WEB)
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_13)


# @export.timer_func
def saveWifiNetworks(networks):
    if isMarble():
        print_debug("> No credentials saved in computer mode.", DEBUG.WEB)
        return

    if networks is None or len(networks) < 1:
        return

    connect_to_wifi(networks, from_web=True)


def saveParameter(param, val):
    user_id = export.get_user_id()

    try:
        parameter = HandleDB().fetch(f"SELECT * FROM {Table.SETTING.value} WHERE user_id = ? AND key = ? LIMIT 1", [user_id, param])

        if parameter is [] or parameter is None:
            HandleDB().execute(f"INSERT INTO {Table.SETTING.value} (user_id, key, value) VALUES (?, ?, ?)", [user_id, param, val])
        else:
            HandleDB().execute(f"UPDATE {Table.SETTING.value} SET value = ? WHERE user_id = ? AND key = ?", [val, user_id, param])
        
        return True
    except Exception as error:
        errorLog(str(error), B_log.DATABASE_14)
        return False


def tellUpdateQuizz(quizz_id: int):
    to_update = HandleDB().getData(Data.UPDATED_QUIZZ) or []
    to_update.append(f'{quizz_id}.json')
    HandleDB().setData(Data.UPDATED_QUIZZ, to_update)  # todo web: tell if quizz removed !


def getQuizzUpdated():
    updated = HandleDB().getData(Data.UPDATED_QUIZZ) or False
    HandleDB().setData(Data.UPDATED_QUIZZ, [])
    return updated
