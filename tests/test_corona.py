import unittest
from unittest import mock
from unittest.mock import patch
from parser_corona_data import Parser_CoronaVirus, options
import mongomock


class TestAddActions(unittest.TestCase):

    def setUp(self) -> None:
        self.data_parser = Parser_CoronaVirus()
        self.data_parser.client = mongomock.MongoClient("localhost", 27017)
        self.test_countries = [{"Province": "a", "Confirmed": 1},
                               {"Province": "a", "Confirmed": 3},
                               {"Province": "d", "Confirmed": 4},
                               {"Province": "e", "Confirmed": 5}]
        
        self.test_one_country = [{"Country_Region": "Russia", "Confirmed": 25, "Deaths": 32, "Recovered": 12, "Active": 2},
                                 {"Country_Region": "US", "Confirmed": 25, "Deaths": 32, "Recovered": 12, "Active": 2},
                                 {"Country_Region": "Russia", "Confirmed": 25, "Deaths": 20, "Recovered": 10, "Active": 0},
                                 {"Country_Region": "Germany", "Confirmed": 25, "Deaths": 32, "Recovered": 12, "Active": 2}]

    def tearDown(self) -> None:
        self.data_parser.corona_collection.drop()

    # tests for find_suitable_date
    def test_find_existent_entry(self):
        self.data_parser.find_actual_data(10)
        result = self.data_parser.find_suitable_date(10)
        self.assertEqual(result, options.ENTRY_EXISTS_IN_DB)

    def test_find_nonexistent_entry(self):
        result = self.data_parser.find_suitable_date(-100)
        self.assertEqual(result, options.NOT_INFO)

    def test_find_reasonable_date_of_entry(self):
        result = self.data_parser.find_suitable_date()
        if result != options.ENTRY_EXISTS_IN_DB and result != options.NOT_INFO:
            result = 3
        self.assertEqual(result, 3)

    # test for write_data_corona
    def test_write_data_corona(self):
        result = self.data_parser.write_data_corona(self.data_parser.find_suitable_date())
        self.assertEqual(bool(result), True)

    # tests for find_top_five
    def test_find_value_by_date(self):
        result = self.data_parser.find_value_by_date('04-04-2020')
        self.assertIsNone(result)

    def test_find_target_countries_by_loc_and_asp(self):
        result = self.data_parser.find_target_countries_by_loc_and_asp(self.test_countries, "Province", "Confirmed")
        self.assertEqual(result, {"a": 4,
                                  "d": 4,
                                  "e": 5})

    def test_sort_countries_by_aspect(self):
        temp = self.data_parser.find_target_countries_by_loc_and_asp(self.test_countries, "Province", "Confirmed")
        result = self.data_parser.sort_countries_by_aspect(temp)
        self.assertEqual(result, [('e', 5), ('d', 4), ('a', 4)])

    # test for get_dynamics_info
    def test_get_info(self):
        result = self.data_parser.get_info(self.test_one_country, "Russia")
        self.assertEqual(result, {"Confirmed": 50,
                                  "Deaths": 52,
                                  "Recovered": 22,
                                  "Active": 2})


if __name__ == '__main__':
    unittest.main()
