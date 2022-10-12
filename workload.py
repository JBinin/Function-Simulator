from __future__ import annotations

import os
from typing import TYPE_CHECKING

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
            row = row.astype("int64")
            if hash_function not in self.requests:
                if self.function_limit is not None and len(self.requests) >= self.function_limit:
                    continue
                self.requests[hash_function] = np.zeros(self.max_count, dtype=np.int64)

            self.requests[hash_function] = \
                np.concatenate((self.requests[hash_function], row.values), axis=None)
            max_count = max(max_count, self.requests[hash_function].size)

        self.max_count = max_count

        for key in self.requests.keys():
            if len(self.requests[key]) < self.max_count:
                self.requests[key] = np.concatenate(
                    (self.requests[key], np.zeros(self.max_count - len(self.requests[key]), dtype=np.int64)), axis=None)

    def add_workload_icebreaker_selected_traces(self, txt_file_dir):
        for lists in os.listdir(txt_file_dir):
            if self.function_limit is not None and len(self.requests) >= self.function_limit:
                break
            path = os.path.join(txt_file_dir, lists)
            if os.path.isfile(path):
                hash_function = lists[:-4]
                trace_data = read_from_txt(path)
                self.requests[hash_function] = trace_data

    def merge_workload(self, merge_count):
        assert merge_count > 1
        assert len(self.requests) % merge_count == 0
        keys = list(self.requests.keys())
        i = 0
        while i < len(keys):
            key_merge = keys[i]
            for key in keys[i + 1:i + merge_count]:
                self.requests[key_merge] = self.requests[key_merge] + self.requests[key]
                del self.requests[key]
            i += merge_count

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

    def split_n_workloads(self, n: int):
        assert n > 1
        sub_requests = []
        total_len = len(self.requests)
        single_len = total_len // n
        start = 0
        i = 0
        keys = list(self.requests.keys())
        while i < n:
            if i < n - 1:
                sub_requests.append(
                    {k: self.requests[k] for k in keys[start:start + single_len]}
                )
            else:
                sub_requests.append(
                    {k: self.requests[k] for k in keys[start:total_len]}
                )
            start += single_len
            i += 1
        traces = [Workload() for i in range(n)]
        for i in range(n):
            traces[i].requests = sub_requests[i]
            traces[i].max_count = self.max_count
        return traces
