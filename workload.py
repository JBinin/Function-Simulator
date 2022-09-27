from __future__ import annotations

import os
from typing import TYPE_CHECKING

import numpy
import numpy as np
import pandas as pd
from typing import Dict

if TYPE_CHECKING:
    from simulator import Simulator


def read_from_txt(txt_file: str) -> np.ndarray:
    result = []
    with open(txt_file) as f:
        for line in f:
            result.append(int(line))
    return np.array(result)


class Workload(object):
    def __init__(self):
        self.simulator = None
        self.requests: Dict[str, np.ndarray] = {}
        self.current_index = -1
        self.max_count = 0
        self.function_limit = None

    def attach(self, simulator: Simulator):
        self.simulator = simulator

    def set_function_limit(self, limit):
        self.function_limit = limit

    def add_workload(self, csv_file: str):
        requests = pd.read_csv(csv_file)
        max_count = 0
        for _, row in requests.iterrows():
            hash_function = row[2]
            row = row.iloc[4:]
            row = row.astype("int")
            if hash_function not in self.requests:
                if self.function_limit is not None and len(self.requests) >= self.function_limit:
                    continue
                self.requests[hash_function] = np.zeros(self.max_count, dtype=numpy.int64)

            self.requests[hash_function] = \
                np.concatenate((self.requests[hash_function], row.values), axis=None)
            max_count = max(max_count, self.requests[hash_function].size)

        self.max_count = max_count

        for key in self.requests.keys():
            if len(self.requests[key]) < self.max_count:
                self.requests[key] = np.concatenate(
                    (self.requests[key], np.zeros(self.max_count - len(self.requests[key]))), axis=None)

    def add_workload_icebreaker_selected_traces(self, txt_file_dir):
        for lists in os.listdir(txt_file_dir):
            if self.function_limit is not None and len(self.requests) >= self.function_limit:
                break
            path = os.path.join(txt_file_dir, lists)
            if os.path.isfile(path):
                hash_function = lists[:-4]
                trace_data = read_from_txt(path)
                self.requests[hash_function] = trace_data

    def currency_cdf(self, save_csv_file: str):
        currency_count: Dict[str, int] = {}
        for hash_function in self.requests.keys():
            currency_count[hash_function] = len(set(self.requests[hash_function]))
        pd.DataFrame([currency_count], index=["currency"]).transpose().to_csv(save_csv_file)

    def run(self):
        while self.current_index + 1 < self.max_count and not self.simulator.finished():
            self.current_index += 1
            self.simulator.function.predict_trigger.succeed()
            yield self.simulator.env.timeout(1)
        self.simulator.is_finished = True
