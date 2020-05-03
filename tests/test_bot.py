import unittest
from unittest import mock
from unittest.mock import patch

from bot import update_log, get_money, fact,LOG_HISTORY, get_data_with_url


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


class TestsFact(unittest.TestCase):

    # тест получения данных по url, неверный url
    def test_bad_url(self):
        with patch('bot.requests.get') as mock_get:  # мокаем get
            mock_get.return_value.ok = False
            data = get_data_with_url('http://qqq.com')
        self.assertEqual(data, None)

    # тест получения данных по url, верный url
    def test_good_url(self):
        with patch('bot.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {'cat': 240}
            data = get_data_with_url('http://qqq.com')
        self.assertEqual(data, {'cat': 240})

    def test_get_facts_no_data(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = None
            most_upvoted = fact()
        self.assertEqual(most_upvoted, "We don't see cats, so cannot find the cutest(")

    def test_get_facts_no_most_upvoted(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = {'all': [{'upvotes': 0, 'text': 'text message'}]}
            most_upvoted = fact()
        self.assertEqual(most_upvoted, "It's impossible to find the most upvoted post, all are cute!")

    def test_get_facts_most_upvoted(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = {'all': [{'upvotes': 1, 'text': 'text message'}]}
            most_upvoted = fact()
        self.assertEqual(most_upvoted, 'Самый залайканный пост - это: text message')

    def test_get_two_most_upvoted(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = {'all': [{'upvotes': 1, 'text': 'text message'}, {'upvotes': 1, 
                                      'text': 'text message_2'}]}
            most_upvoted = fact()
        self.assertEqual(most_upvoted, 'Самый залайканный пост - это: text message, text message_2')


class TestMoney(unittest.TestCase):
    def test_currency(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = {"Valute": {"EUR": {"Name": "Евро", "Value": 3}}}
            currency = get_money("Евро  ")
        self.assertEqual(currency, "Стоимость Евро сейчас 3 ₽")

    def test_bad_name(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = {"Valute": {"EUR": {"Name": "Евро"}}}
            currency = get_money("bad_name")
        self.assertEqual(currency, "Не было найдено информации по данной валюте")

    def test_empty_info_for_all(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = {"Valute": {}}
            currency = get_money("Евро  ")
        self.assertEqual(currency, "Не было найдено информации по данной валюте")

    def test_empty_info_for_currency(self):
        with patch('bot.get_data_with_url') as mock_data:
            mock_data.return_value = {"Valute": {"EUR": {"Name": "Евро", "Value": 0}}}
            currency = get_money("bad_name")
        self.assertEqual(currency, "Не было найдено информации по данной валюте")


if __name__ == '__main__':
    unittest.main()
