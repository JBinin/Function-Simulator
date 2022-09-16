from typing import List
import numpy as np
from numpy import fft


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
                self.update_windows()
            else:
                self.out_of_bounds += 1
            self.last_predict_time = now
            self.last_function_exec_time = function_exec_time

    def update_windows(self):
        cv = coefficient_of_variation(self.it_distribution)
        # cv < 2:
        if cv <= 2 or self.it_count < 10:
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
    def __init__(self, harmonics: int = 10):
        super().__init__()
        self.harmonics = harmonics

    def fourier_extrapolation(self, trace: List[int], n_predict: int) -> List[int]:
        trace = np.array(trace)
        n = trace.size
        n_harm = self.harmonics
        t = np.arange(0, n)
        p = np.polyfit(t, trace, 1)
        trace_no_trend = trace - p[0] * t
        trace_freq = fft.fft(trace_no_trend)
        print(trace_freq)
        f = fft.fftfreq(n)
        index = list(range(n))
        index.sort(key=lambda j: np.absolute(f[j]))

        t_predict = np.arange(0, n + n_predict)
        resorted_sig = np.zeros(t_predict.size)
        for i in index[:1 + n_harm * 2]:
            amplitude = np.absolute(trace_freq[i])
            phase = np.angle(trace_freq[i])
            resorted_sig += amplitude * np.cos(2 * np.pi * f[i] * t_predict + phase)
        return list(resorted_sig + p[0] * t_predict)
