import os
import random
import unittest
import Source.Database.db_enums as enums
from Source.SoundHandling.fetch_data import Parameter
from Resources.unit_test import HiddenPrints
from Source.Database.handle_database import HandleDB
from Source.Database.migration import Migration
from Source.Database.save_data import *
from Source.Database.export_data import get_user_pseudo, get_parameters
from Source.Database.error_log import get_activity_id


class TestCreateDB(unittest.TestCase):
    db_name = f'test.db'

    @classmethod
    def setUpClass(cls) -> None:
        with HiddenPrints():
            def dummy(a, b):
                pass

            HandleDB().close()
            HandleDB(cls.db_name)
            HandleDB().setEmit(dummy)
            Migration().load()

    @classmethod
    def tearDownClass(cls) -> None:
        HandleDB().close()
        try:
            os.remove("test.db")
        except:
            pass

    def test_save_tokens(self):
        # Check save result token
        saveResultToken(["⠁"], 100, 'test')

        last_result = HandleDB().fetch(f"SELECT * FROM {enums.Table.RESPONSE_TOKEN.value} ORDER BY date_time DESC LIMIT 1", [])

        self.assertEqual(last_result[2], 'a')
        self.assertEqual(last_result[3], 100)

        # Check save result word
        saveResultWord("a", "aa", 'test')

        last_result = HandleDB().fetch(f"SELECT * FROM {enums.Table.RESPONSE_WORD.value} ORDER BY date_time DESC LIMIT 1", [])

        self.assertEqual(last_result[2], 'a')
        self.assertEqual(last_result[3], 'aa')

        # TODO : add tests for saveResultBlock

    def test_initiate_session(self):
        initiateSession("test")

        activity_id = get_activity_id("test")
        last_result = HandleDB().fetch(f"SELECT * FROM {enums.Table.SESSION.value} ORDER BY date_time_start DESC LIMIT 1", [])

        self.assertEqual(last_result[3], activity_id)

    def test_save_user(self):
        saveUser(99, False)

        last_result = HandleDB(self.db_name).fetch(f"SELECT * FROM {enums.Table.USER.value} ORDER BY user_id DESC LIMIT 1", [])

        self.assertEqual(last_result[0], 99)

    def test_save_param(self):
        saveUser(97, True)
        num_to_save = random.randint(0, 100)

        for param in Parameter:
            saveParameter(param.name, num_to_save)

        for param in get_parameters(97):
            self.assertEqual(num_to_save, int(param[1]))

        self.assertEqual(len(Parameter), len(get_parameters(97)))

    def test_save_user_pseudo(self):
        saveUser(98)

        with HiddenPrints():
            saveUserPseudo("abc.wav", 98)

        pseudo = get_user_pseudo(98)
        self.assertEqual(pseudo, "abc.wav")


if __name__ == '__main__':
    unittest.main()
