from Source.BrailleTool.handle_logs import print_debug
from Source.SoundHandling.macro_enums import Macro


def get_activity_name(title_macro: Macro = Macro.NONE, quizz_id: int = -1, group: bool = False):
    if not activity_names.get(title_macro, False) and quizz_id < 0:
        print_debug(f" {title_macro.name} can't create an activity !")

    return (activity_names.get(title_macro, False) or
            ((f"menu_{quizz_id}" if group else f"crea_{quizz_id}") if quizz_id > 0 else ""))


activity_names = {
    Macro.TITLE_MAIN_MENU: "menu_000_main_manager",

    Macro.TITLE_TUTORIAL_MANAGER: "menu_001_tutorial_manager",
    Macro.TITLE_LESSON_MANAGER: "menu_002_lesson_manager",
    Macro.TITLE_BREYE_LESSON: "menu_003_breye_lesson",

    # Game menus
    Macro.TITLE_GAME_MANAGER: "menu_010_game_manager",

    Macro.TITLE_FIRST_GAME_MANAGER: "menu_011_first_game_manager",
    Macro.TITLE_BOARD_GAME_MANAGER: "menu_012_board_game_manager",
    Macro.TITLE_ADVENTURE_GAME_MANAGER: "menu_013_adventure_game_manager",
    Macro.TITLE_COMPETITIVE_GAME_MANAGER: "menu_014_competitive_game_manager",
    Macro.TITLE_MUSICAL_GAME: "menu_015_musical_game_manager",
    Macro.TITLE_DISPLAY_GAME_MANAGER: "menu_016_display_game_manager",
    Macro.TITLE_MATH_GAME_MANAGER: "menu_017_math_game_manager",

    # Selection
    Macro.TITLE_SELECT_TOKENS: "menu_020_select_tokens",

    Macro.TITLE_SELECT_TOKENS_DEFAULT: "menu_021_select_tokens_default",
    Macro.TITLE_SELECT_TOKENS_LAST: "menu_022_select_tokens_last",
    Macro.TITLE_SELECT_TOKENS_FREE: "menu_023_select_tokens_free",
    Macro.TITLE_SELECT_TOKENS_PACKAGE: "menu_024_select_tokens_package",

    # Creative
    Macro.TITLE_BREYE_LESSON_MANAGER: "menu_031_breye_lesson_manager",
    Macro.TITLE_MANAGER_C_QST: "menu_032_creative_manager",
    Macro.TITLE_ENIGMA: "menu_033_creative_enigma_manager",

    # Parameters
    Macro.TITLE_PARAMETER: "menu_040_parameter",
    Macro.TITLE_PARAMETER_GAMEPLAY: "menu_041_parameter_gameplay",
    Macro.TITLE_PARAMETER_ADMIN: "menu_042_parameter_admin",
    Macro.TITLE_WIFI_SELECTION: "menu_043_selection_wifi",

    # Games (and activities ?)
    Macro.TITLE_DISCOVER_TOKENS: "game_001_discover_tokens",
    Macro.TITLE_SPELLING: "game_002_alphabet",
    Macro.TITLE_SPELLING_POINT: "game_003_point_alphabet",
    Macro.TITLE_SMALL_WORDS: "game_004_small_words",
    Macro.TITLE_WRITE_WORDS: "game_005_write_words",
    Macro.TITLE_LEARN_MULTIPLICATION: "game_006_learn_multiplication",

    Macro.TITLE_SEQUENCE: "game_007_sequence",
    Macro.TITLE_MIND: "game_008_mind_domino",
    Macro.TITLE_GOGO: "game_009_gogo",
    Macro.TITLE_SIMPLE_CALCULUS: "game_010_simple_calculus",
    Macro.TITLE_GTN: "game_011_guess_the_number",
    Macro.TITLE_MOTLIMELO: "game_022_motus",
    Macro.TITLE_CRAZY_PYRAMIDS: "game_023_pyramids",

    Macro.TITLE_PIANIST_COMPOSER: "game_012_composer",
    Macro.TITLE_PIANIST_PLAY_MELODY: "game_013_play_melody",
    Macro.TITLE_PIANIST_FIND_MELODY: "game_014_find_melody",

    Macro.TITLE_ESCAPE_GAME: "game_015_escape_game",
    Macro.TITLE_CLOCK: "game_016_the_clock_game",

    Macro.TITLE_MEMORY: "game_017_memory",
    Macro.TITLE_SEA: "game_018_battleship",
    Macro.TITLE_CULTURE_CHALLENGE: "game_019_trivia",
    Macro.TITLE_CROSS_GAMES: "game_020_cross_games",

    Macro.TITLE_FIND_THE_DIFFERENCE: "game_021_find_the_difference",
    Macro.TITLE_FOLLOW_THE_CHAR: "game_024_braille_racing",

    # Lessons and Chapters
    Macro.TUTB_CHAP1: "game_101_tut_chap_1",
    Macro.TUTB_CHAP2: "game_102_tut_chap_2",
    Macro.TUTB_CHAP3: "game_103_tut_chap_3",
    Macro.TUTB_CHAP4: "game_104_tut_chap_4",
    Macro.TUTB_CHAP5: "game_105_tut_chap_5",
    Macro.TUTB_CHAP6: "game_106_tut_chap_6",

    Macro.TUTM_CHAP1: "game_111_tutm_chap_1",
    Macro.TUTM_CHAP2: "game_112_tutm_chap_2",
    Macro.TUTM_CHAP3: "game_113_tutm_chap_3",
    Macro.TUTM_CHAP4: "game_114_tutm_chap_4",

    Macro.LESSON_TUTORIAL: "game_120_lesson_tutorial",
    Macro.LESSON_CHAPTER1: "game_121_lesson_chapter1",
    Macro.LESSON_CHAPTER2: "game_122_lesson_chapter2",
    Macro.LESSON_CHAPTER3: "game_123_lesson_chapter3",
    Macro.LESSON_CHAPTER4: "game_124_lesson_chapter4",
    Macro.LESSON_CHAPTER5: "game_125_lesson_chapter5",
    Macro.LESSON_CHAPTER6: "game_126_lesson_chapter6",
    Macro.LESSON_CHAPTER7: "game_127_lesson_chapter7",
    Macro.LESSON_CHAPTER8: "game_128_lesson_chapter8",
    Macro.LESSON_CHAPTER9: "game_129_lesson_chapter9",
    Macro.LESSON_CHAPTER10: "game_130_lesson_chapter10"}
