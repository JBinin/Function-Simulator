import unittest

from predictor import Histogram


class TestHistogram(unittest.TestCase):
    def test_predict(self):
        test_predictor = Histogram(10)
        states = [1, 0, 0, 9, 0]
        for index, s in enumerate(states):
            test_predictor.predict(s, index)
        self.assertEqual(test_predictor.pre_warm_window, 0)
        self.assertEqual(test_predictor.keep_alive_window, 2)

    def test_cv(self):
        test_cv = Histogram(20)
        states = [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]
        for index, s in enumerate(states):
            test_cv.predict(s, index)
        self.assertEqual(test_cv.keep_alive_window, 20)
        self.assertEqual(test_cv.pre_warm_window, 0)


if __name__ == "__main__":
    unittest.main()
