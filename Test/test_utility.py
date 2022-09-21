import os
import unittest
import utility
import numpy as np


class TestUtility(unittest.TestCase):
    def setUp(self) -> None:
        self.txt_file = "test.txt"
        with open(self.txt_file, "w") as f:
            for i in range(10):
                f.write(str(i) + "\n")

    def tearDown(self) -> None:
        os.remove(self.txt_file)

    def test_read_from_txt(self):
        result = utility.read_from_txt(self.txt_file)
        expect = np.array(list(range(10)))
        self.assertTrue(all(result == expect))


if __name__ == "__main__":
    unittest.main()
