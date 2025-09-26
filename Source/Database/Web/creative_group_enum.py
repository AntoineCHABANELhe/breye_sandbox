from enum import Enum
from Source.FilesHandling.environment_data import EnvironmentData


class Url(Enum):
    WS = EnvironmentData.API_URL.value


class Path(Enum):
    API = "AudioRessources/Sounds/API/"
    QUIZZES = "Games/Dependent/CustomQuestions/files/"
    GROUP_JSON = "Source/FilesHandling/CreativeGroup/group.json"


class GroupField(Enum):
    GROUP_ID = "id"
    NAME = "name"
    DISPLAY = "name_display"
    TEXT = "text"
    PATH = "path"
    CHILD = "children"
    QUIZZ = "quizzes"
    TYPE = "type"


class GroupTypes(Enum):
    CREATIVE = "creative", "Games/Dependent/CustomQuestions/Creative"  # pathing = this + lang once complete
    CREATIVE_LESSON = "creative_lesson", "Games/Dependent/CustomQuestions/Lessons"
    BREYE_LESSON = "breye_lesson", "Games/Dependent/CustomQuestions/LessonsBreye"
    ENIGMA = "enigma", "Games/Dependent/CustomQuestions/Enigma"
