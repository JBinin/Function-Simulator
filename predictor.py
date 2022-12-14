from typing import List
import numpy as np
from numpy import fft
import pmdarima as pm


def coefficient_of_variation(data):
    mean = np.mean(data)
    std = np.std(data, ddof=0)
    cv = std / mean
    return cv


class PredictAlgorithm(object):
    def __init__(self):
        self.pre_warm_window = 0
        self.keep_alive_window = 10
        self.last_predict_time = -1

    def predict(self, *args):
        pass


class DefaultKeepalive(PredictAlgorithm):
    def __init__(self, keep_alive_window):
        super().__init__()
        self.keep_alive_window = keep_alive_window
        self.last_predict_time = -1
        self.last_function_exec_time = 0

    def predict(self, state: int, now: int, function_exec_time: int):
        if state == 0:
            return
        self.last_predict_time = now
        self.last_function_exec_time = function_exec_time


class Histogram(PredictAlgorithm):
    def __init__(self, windows: int):
        super().__init__()
        self.last_function_exec_time = 0
        self.windows = windows
        self.it_distribution = np.zeros(windows)
        self.it_count = 0
        self.out_of_bounds = 0
        self.cv_threshold = 2
        self.pre_warm_window = 0
        self.keep_alive_window = self.windows

        # for arima algorithm
        self.model = None
        self.history = []
        self.using_arima = False

    def if_using_arima(self):
        if self.out_of_bounds > 4 and self.out_of_bounds / (self.out_of_bounds + self.it_count) > 0.5:
            self.using_arima = True
        else:
            self.using_arima = False
        return self.using_arima

    def predict(self, state: int, now: int, function_exec_time: int):
        """
        :param state: currency
        :param now: time stamp
        :param function_exec_time: the exec time for this invocation, used for next predict
        :return: None
        """
        if state == 0:
            return
        # first invocation
        if self.last_predict_time == -1:
            self.last_predict_time = now
            self.last_function_exec_time = function_exec_time
            return
        # for not first invocation
        if state != 0:
            it = now - self.last_predict_time - self.last_function_exec_time
            it = max(0, it)

            if it < self.windows:
                self.it_distribution[it] += state
                self.it_count += state
            else:
                self.out_of_bounds += 1
                self.history.append(it)

            if self.if_using_arima():
                self.arima()
            else:
                self.update_windows()

            self.last_predict_time = now
            self.last_function_exec_time = function_exec_time

    def arima(self):
        self.model = pm.auto_arima(self.history, error_action='ignore', trace=False,
                                   suppress_warnings=True)
        if self.model.with_intercept:
            predict_result = self.model.predict(n_periods=1)
            self.pre_warm_window = int(predict_result[0] * 0.75)
            self.keep_alive_window = int(predict_result[0] * 0.3)
        else:
            # if arima error
            self.pre_warm_window = 0
            self.keep_alive_window = self.windows

    def update_windows(self):
        # cv < 2:
        if self.it_count < 10 or coefficient_of_variation(self.it_distribution) < 2:
            self.keep_alive_window = self.windows
            self.pre_warm_window = 0
        else:
            low = self.it_count * 0.05
            high = self.it_count * 0.99
            total = 0
            low_get = False
            for i in range(self.windows):
                total += self.it_distribution[i]
                if not low_get and total >= low:
                    self.pre_warm_window = i - 1
                    low_get = True
                if low_get and total >= high:
                    self.keep_alive_window = i + 1 - self.pre_warm_window
                    break
            # to give the policy more room for error
            # use a 10% "margin"
            self.keep_alive_window = int(self.keep_alive_window * 1.1)
            self.pre_warm_window = int(self.pre_warm_window * 0.9)


class IceBreaker(PredictAlgorithm):
    def __init__(self, harmonics: int = 10, local_windows: int = 60):
        super().__init__()
        self.harmonics = harmonics
        self.local_windows = local_windows
        self.history = list()
        self.keep_alive_window = 1
        self.last_function_exec_time = 0

    def predict(self, state: int, now: int, function_exec_time: int):
        self.history.append(state)
        if len(self.history) > self.local_windows:
            self.history.pop(0)
        trace = np.arange(self.history)
        predict_result = self.fourier_extrapolation(trace, 1)[0]
        self.last_predict_time = now
        self.last_function_exec_time = function_exec_time

    def fourier_extrapolation(self, trace: np.ndarray, n_predict: int) -> List[int]:
        n = trace.size
        n_harm = self.harmonics
        t = np.arange(0, n)
        p = np.polyfit(t, trace, 2)
        trace_no_trend = trace - p[0] * t ** 2 - p[1] * t
        trace_freq = fft.fft(trace_no_trend)
        f = fft.fftfreq(n)
        index = list(range(n))
        index.sort(key=lambda j: np.absolute(f[j]))

        t_predict = np.arange(0, n + n_predict)
        resorted_sig = np.zeros(t_predict.size)
        for i in index[:1 + n_harm * 2]:
            amplitude = np.absolute(trace_freq[i]) / n
            phase = np.angle(trace_freq[i])
            resorted_sig += amplitude * np.cos(2 * np.pi * f[i] * t_predict + phase)
        return list(resorted_sig + p[0] * t_predict ** 2 + p[1] * t_predict)
