from enum import Enum

# Crée l'énumération des différentes tables qui doivent exister
# Pour des raisons de simplicité d'envoi des données au serveur,
# la table Users doit être placée en 3eme


class Table(Enum):
    ACTIVITY = "Activity"
    ACTION = "Action"
    USER = "User"
    ERROR_LOG = "ErrorLog"
    OCCURRENCE = "Occurrence"
    SESSION = "Session"
    RESPONSE_TOKEN = "ResponseToken"
    RESPONSE_WORD = "ResponseWord"
    RESPONSE_BLOCK = "ResponseBlock"

    # DO NOT SEND (they start with _ )
    ANALYSE = "_Analyse"
    LAST_SENT = "_LastSent"
    SETTING = "_Setting"


class Field(Enum):
    USER_ID = "user_id"
    ACTION_ID = "action_id"
    ACTIVITY_ID = "activity_id"
    SCORE = "score"
    TOKEN = "token"
    DATETIME = "date_time"
    SCALE = "err_suc_scale"
    KNOWLEDGE_VALUE = "knowledge_value"
    ANSWER = "answer"


class Action(str, Enum):
    QUIT = 'quit'
    HELP = 'help'
    MULTI = 'multiplayer'
    GAME_LAUNCH = 'game_launch'
    GAME_ENDED = 'game_ended'
    CARROUSEL_VALIDATE = 'validate_carrousel'
    CARROUSEL_MOVE = 'move_carrousel'
    CAROUSEL = 'carousel'
    REPEAT = 'repeat'
    RULES = 'rules'
    REPLAY = 'replay'
    SCORE = 'score'
    TUTO = "game_tutorial"
    GAME_PARAM = "parameters_in_games"
