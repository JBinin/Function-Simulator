from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from typing import Dict

if TYPE_CHECKING:
    from simulator import Simulator


class Workload(object):
    def __init__(self):
        self.simulator = None
        self.requests: Dict[str, np.ndarray] = {}
        self.current_index = -1
        self.max_count = 0

    def attach(self, simulator: Simulator):
        self.simulator = simulator

    def add_workload(self, csv_file: str):
        requests = pd.read_csv(csv_file)
        for _, row in requests.iterrows():
            hash_function = row[2]
            row = row.iloc[4:]
            if hash_function not in self.requests:
                self.requests[hash_function] = row.values
            else:
                self.requests[hash_function] = \
                    np.concatenate((self.requests[hash_function], row.values), axis=None)
            self.max_count = max(self.max_count, self.requests[hash_function].size)

    def run(self):
        while self.current_index + 1 < self.max_count and not self.simulator.finished():
            self.current_index += 1
            self.simulator.function.predict_trigger.succeed()
            yield self.simulator.env.timeout(1)
        self.simulator.is_finished = True
