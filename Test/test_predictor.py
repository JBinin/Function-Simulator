import unittest

from predictor import Histogram


class TestHistogram(unittest.TestCase):
    def test_predict(self):
        test_predictor = Histogram(10)
        states = [1, 0, 0, 10, 0]
        for index, s in enumerate(states):
            test_predictor.predict(s, index, 1)
        self.assertEqual(test_predictor.pre_warm_window, 0)
        self.assertEqual(test_predictor.keep_alive_window, 2)

    def test_cv(self):
        test_cv = Histogram(20)
        states = [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
        for index, s in enumerate(states):
            test_cv.predict(s, index, 1)
        self.assertEqual(test_cv.keep_alive_window, 20)
        self.assertEqual(test_cv.pre_warm_window, 0)


class TestARIMA(unittest.TestCase):
    def test_auto_arima(self):
        predictor = Histogram(10)
        states = [10, 301, 423, 710, 801, 820, 916]
        for i in range(len(states)):
            predictor.predict(1, states[i], 1)
        self.assertEqual(predictor.pre_warm_window, 112)
        self.assertEqual(predictor.keep_alive_window, 45)


if __name__ == "__main__":
    unittest.main()
