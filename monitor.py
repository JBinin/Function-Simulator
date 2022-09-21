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
            # state = {
            #     "time_stamp": self.simulator.env.now,
            # }
            # self.states.append(state)
            yield self.simulator.env.timeout(1)
        # state = {
        #     "time_stamp": self.simulator.env.now,
        # }
        # self.states.append(state)
        # pd.DataFrame(self.states).to_csv("monitor_data.csv")
        result = [self.simulator.function.cold_start, self.simulator.function.warm_start,
                  self.simulator.function.wasted_time]
        pd.DataFrame(result, index=["cold", "warm", "wasted_time"]).transpose().to_csv("result.csv")
