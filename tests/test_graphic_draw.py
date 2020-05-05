import unittest
from unittest.mock import patch
from graphic_draw import Statistics


class TestGraphics(unittest.TestCase):

    def setUp(self) -> None:
        self.draw_graphic = Statistics()
        self.test_dates = ['5/1/2020', '5/2/2020']
        self.test_countries = [{"Country/Region": "France", '5/1/20': '3', '5/2/20': '1'},
                               {"Country/Region": "France", '5/1/20': '1', '5/2/20': '2'}]
        self.test_info = {'5/1/2020': [3, 1],
                          '5/2/2020': [1, 2]}

    def test_get_info(self):
        result_info = self.draw_graphic.get_current_info(self.test_countries, self.test_dates)
        self.assertEqual(result_info, self.test_info)

    def test_write_data(self):
        with patch("graphic_draw.Statistics.get_current_info") as mock_current_info:
            mock_current_info.return_value = self.test_info
            info = self.draw_graphic.write_data_in_data_set("France", self.test_dates)
            self.assertEqual([4, 3], info)

    def test_good_dates(self):
        test_bad_dates = ["4/20/2020", "1/10/2000", "11/12/2002"]
        good_dates = self.draw_graphic.correct_dates(test_bad_dates)
        self.assertEqual(good_dates, ['04/20', '01/10', '11/12'])


if __name__ == '__main__':
    unittest.main()
