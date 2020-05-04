import unittest
from classes import Calculator
from unittest import mock
from unittest.mock import patch

class TestsDataDynamics(unittest.TestCase):

    def setUp(self) -> None:
        self.data_parser = Calculator.download_actual_file()
        self.dynamics = Calculator.get_dynamics_info()

    def test_find_record_none(self):
        with patch('classes.open') as mock_open:
        mock_open.return_value = [{'Country_Region': 'test1_coutry', 'Province_State': 'test_state'},
                 {'Country_Region': 'test2_coutry', 'Province_State': 'test_state'}]
        test_province = {'Country_Region': 'test_coutry', 'Province_State': 'test_state'}
        record = self.dynamics.find_record("Russia", 7)
        self.assertEqual(record, None)
    self.assertEqual(info, ["Информация о вирусе на сегодня:"])




if __name__ == '__main__':
    unittest.main()
