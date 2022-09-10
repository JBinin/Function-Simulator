from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from simulator import Simulator


class Monitor(object):
    def __init__(self):
        self.simulator = None
        self.states = []

    def attach(self, simulator: Simulator):
        self.simulator = simulator

    def run(self):
        while not self.simulator.finished():
            state = {
                "time_stamp": self.simulator.env.now,
            }
            self.states.append(state)
            yield self.simulator.env.timeout(1)
        state = {
            "time_stamp": self.simulator.env.now,
        }
        self.states.append(state)
        pd.DataFrame(self.states).to_csv("monitor_data.csv")
        pd.DataFrame.from_dict(
            self.simulator.function.cold_start, orient="index"
        ).to_csv("cold_start.csv")
