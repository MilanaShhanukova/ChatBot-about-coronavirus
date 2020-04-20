import unittest
from unittest import mock
from unittest.mock import patch
from bot import update_log, check_weather, get_money, fact, history, date, LOG_HISTORY


@update_log
def default_action(update):
    return None


class TestAddActions(unittest.TestCase):
    def setUp(self) -> None:
        self.update = mock.MagicMock()

    def tearDown(self) -> None:
        global LOG_HISTORY
        LOG_HISTORY = []

    def test_log_action(self):
        self.update.message.text = "i write a sms"
        self.update.effective_user.first_name = "Person"
        self.update.message.date = 0

        default_action(self.update)
        self.assertEqual(LOG_HISTORY, [{"user": "Person", "function": "default_action", "message": "i write a sms",
        								"date": 0}])

    def test_no_message_attr(self):
        self.update = mock.MagicMock(spec=["effective_user"])

        default_action(self.update)
        self.assertEqual(LOG_HISTORY, [])

    def test_no_user_attr(self):
        self.update = mock.MagicMock(spec=["message"])

        default_action(self.update)
        self.assertEqual(LOG_HISTORY, [])

    def test_none_update(self):
        self.update = None

        default_action(self.update)
        self.assertEqual(LOG_HISTORY, [])

    def test_no_update(self):
        with self.assertRaises(IndexError):
            default_action()

    def test_no_date(self):
        self.update = mock.MagicMock(spec=["date"])

        default_action(self.update)
        self.assertEqual(LOG_HISTORY, [])


if __name__ == '__main__':
    unittest.main()
