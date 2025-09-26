import random
from datetime import datetime, timezone

import numpy as np

from Source.BrailleTool.convert import elementToBraille
from Source.BrailleTool.handle_logs import print_debug, DEBUG
from Source.Database.db_enums import Field, Table
from Source.Database.error_log import get_activity_id
import Source.Database.export_data as export
from Source.Database.handle_database import HandleDB, Data


def getWorstBrailleToken(from_string: str = "", all_chars=False):
    return getWorstBrailleTokens(from_string, all_chars, nb_chars=1)[0]


def getWorstBrailleTokens(from_string: str = "", all_chars=False, nb_chars=1):
    """ from_string must be a braille string or a list of braille. """
    char_dic = _getAnalyses(from_string)
    if all_chars:
        return [key for (key, value) in sorted(char_dic.items(),  key=lambda x: x[1])]
    return _randomWorstToken(char_dic, nb_chars=nb_chars)

def _randomWorstToken(char_dic, nb_chars = 1):
    if nb_chars == 1:
        return random.choices(list(char_dic.keys()), weights=char_dic.values())[0]

    weights = np.array(list(char_dic.values()), dtype=float)
    probabilities = weights / weights.sum()

    # Use numpy's random choice to sample without replacement
    return list(np.random.choice(list(char_dic.keys()), size=min(nb_chars, len(weights)), replace=False, p=probabilities))

def _getAnalyses(from_string: str = ""):
    """ from_string must be a braille string or a list of braille. """
    last_analyses = HandleDB().getData(Data.ANALYSES)
    if last_analyses is None:
        char_dic = _updateAnalyses()
        HandleDB().setData(Data.ANALYSES, char_dic)
        return {k: char_dic[k] for k in char_dic.keys() & from_string}
    return {k: last_analyses[k] for k in last_analyses.keys() & from_string}

from Source.BrailleTool.definitions import UNICODE_START, UNICODE_END

def _updateAnalyses():
    char_dic = dict.fromkeys([chr(x) for x in range(UNICODE_START, UNICODE_END)], 0)
    for key in char_dic:
        value = HandleDB().fetch(f"SELECT {Field.KNOWLEDGE_VALUE.value} FROM {Table.ANALYSE.value} WHERE {Field.USER_ID.value} = ? AND {Field.TOKEN.value} = '{key}' LIMIT 1", [0])
        char_dic[key] = int(value[0]) if value else 0
    print_debug(str(char_dic), DEBUG.FULL)
    max_value = max(char_dic.values()) + 10
    return {key: max_value - v for key, v in char_dic.items()}


def calculateTokenGradeFromWord(word, wanted_word, result, current, update_database):
    token_err_suc_scale = []
    if result == 1:
        for c in word:
            token_err_suc_scale.append((c,100))
            update_database(elementToBraille(c), 205, current)
    else:
        lst = list(wanted_word)
        intersection = []
        remain = []
        for c in word:
            try:
                lst.remove(c)
                intersection.append(c)
            except:
                remain.append(c)
        remain.extend(lst)

        if result == -1:
            remain.extend(intersection)
        else:
            for c in intersection:
                token_err_suc_scale.append((c,100))
                update_database(elementToBraille(c), 205, current)
        for c in remain:
            token_err_suc_scale.append((c,-80))
            update_database(elementToBraille(c), 25, current)
    return token_err_suc_scale


def calculateTokenGrade(token, err_suc_scale, current, update_database):
    update_database(token, 105 + err_suc_scale, current)


def calculateAgingTokenScore(score, date):
    days_since = (HandleDB().getNow() - datetime.fromisoformat(date)).days - 1
    return int(score * 1/(1+0.001*days_since))


def setScore(score):
    HandleDB().setData(Data.SCORE, score)


def bestScoreForUser(activity=None, user_id=None):
    if activity is None:
        activity = HandleDB().getData(Data.ACTIVITY)

    if user_id is None:
        user_id = export.get_user_id()

    activity_id = get_activity_id(activity)
    score = HandleDB().fetch(f"SELECT {Field.SCORE.value} FROM {Table.SESSION.value} WHERE activity_id = :activity_id AND {Field.USER_ID.value} = :user_id ORDER BY {Field.SCORE.value} DESC LIMIT 1", {
        Field.ACTIVITY_ID.value: activity_id,
        "user_id": user_id
    })

    return score[0] if score else 0


def bestScore(activity=None):
    if activity is None:
        activity = HandleDB().getData(Data.ACTIVITY)

    activity_id = get_activity_id(activity)
    score = HandleDB().fetch(f"SELECT {Field.SCORE.value} FROM {Table.SESSION.value} WHERE activity_id = :activity_id ORDER BY {Field.SCORE.value} DESC LIMIT 1", {
        Field.ACTIVITY_ID.value: activity_id,
    })

    return score[0] if score else 0
