import unittest
import classes
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

        self.assertEqual(info[0], ["Информация о вирусе на сегодня:"])

    def test_bad_request(self):
        with patch("classes.requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            #mock_data.return_value = [20, 4, 2020]
            info = self.data_parser.download_actual_file(7)


        self.assertEqual(info[0], [f"Информация на сегодня пока нет. Последние данные на {datetime.datetime.today() - datetime.timedelta(days=7)} о вирусе:"])













if __name__ == '__main__':
    unittest.main()
