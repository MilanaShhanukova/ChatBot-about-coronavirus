import unittest
import datetime
from unittest import mock
from unittest.mock import patch


class TestsDataParser(unittest.TestCase):

    def setUp(self) -> None:
        self.data_parser = classes.Calculator

    def test_ok_request(self):
        with patch('classes.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            info = self.data_parser.download_actual_file(7)
        self.assertEqual(info[0], "Информация о вирусе на сегодня:")

    def test_bad_request(self):
        date = (datetime.datetime.today() - datetime.timedelta(days=7)).strftime("%m/%d/%Y")
        with patch("classes.Calculator.download_actual_file", return_value=[f"Информация на сегодня пока нет. \
            Последние данные на {date} о вирусе:"]) as mock_get:
            info = mock_get(7)
        self.assertEqual(info[0], f"Информация на сегодня пока нет. Последние данные на {date} о вирусе:")


if __name__ == '__main__':
    unittest.main()
