import os
import unittest

from utility import split_dict, save_dict_list_to_csv
import numpy as np


class TestUtility(unittest.TestCase):
    def test_split_dict(self):
        test_dicts = {
            "a": np.array([0, 0]),
            "b": np.array([1, 1]),
            "c": np.array([2, 2]),
            "d": np.array([3, 3])
        }
        test_dict_list = []
        split_dict(test_dicts, test_dict_list, 3)
        self.assertEqual(len(test_dict_list), 3)
        self.assertEqual(len(test_dict_list[0]), 1)
        self.assertEqual(len(test_dict_list[2]), 2)
        self.assertEqual(test_dict_list[2]["d"][0], 3)

    def test_save_dict_list_to_csv(self):
        csv_file = "test_utility.csv"
        test_dict_list = [
            {"a": 1, "b": 2},
            {"c": 3}
        ]
        save_dict_list_to_csv(test_dict_list, csv_file)
        with open(csv_file) as f:
            lines = f.readlines()
            self.assertEqual(lines[0], ",mse\n")
            self.assertEqual(lines[1], "a,1\n")
            self.assertEqual(lines[2], "b,2\n")
            self.assertEqual(lines[3], "c,3\n")
        os.remove(csv_file)


if __name__ == "__main__":
    unittest.main()
