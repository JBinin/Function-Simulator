from __future__ import annotations
from typing import List, TYPE_CHECKING, Dict
from predictor import Histogram

if TYPE_CHECKING:
    from simulator import Simulator


class InstanceState(object):
    def __init__(self):
        self.idle = True
        self.last_request_start_time = 0
        self.execution_latency = 0
        self.cold_start_latency = 0

    def check(self, now) -> bool:
        if self.idle:
            return True
        if now - self.last_request_start_time \
                >= self.execution_latency + self.cold_start_latency:
            self.idle = True
        return self.idle

    def update(self, now: int, execution_latency: int, cold_start_latency: int):
        self.idle = False
        self.last_request_start_time = now
        self.execution_latency = execution_latency
        self.cold_start_latency = cold_start_latency


class Functions(object):
    def __init__(self):
        self.instances: Dict[str, List[InstanceState]] = {}
        self.simulator = None
        self.predictors: Dict[str, Histogram] = {}
        self.cold_start: Dict[str, int] = {}

    def attach(self, simulator: Simulator):
        self.simulator = simulator

    def clear_idle_instances(self, hash_function: str):
        if hash_function not in self.instances:
            return
        self.instances[hash_function] = \
            [instance for instance in self.instances[hash_function] if instance.idle]

    def update(self, request_count: int, now: int, hash_function: str):
        self.update_instance(request_count, now, hash_function)
        self.update_predictor(request_count, now, hash_function)

    def update_instance(self, request_count: int, now: int, hash_function: str):
        if hash_function not in self.instances:
            self.instances[hash_function] = []
            self.cold_start[hash_function] = 0
        function = self.instances[hash_function]
        index = 0
        while request_count > 0:
            if index < len(function):
                if function[index].check(now):
                    function[index].update(now, 0, 0)
                    index += 1
                    request_count -= 1
                    continue
                else:
                    index += 1
                    continue
            else:
                function.append(InstanceState())
                self.cold_start[hash_function] += 1
                continue

    def update_predictor(self, request_count: int, now: int, hash_function: str):
        if hash_function not in self.predictors:
            self.predictors[hash_function] = Histogram(4 * 60)
        self.predictors[hash_function].predict(request_count, now)

        pre_warm_window = self.predictors[hash_function].pre_warm_window
        keep_alive_window = self.predictors[hash_function].keep_alive_window
        self.clear_idle_instances(hash_function)
        currency = len(self.instances[hash_function])
        if pre_warm_window == 0:
            self.simulator.env.timeout(keep_alive_window)
            if self.simulator.env.now == self.predictors[hash_function].last_predict_time + keep_alive_window:
                self.instances[hash_function] = []
        else:
            self.instances[hash_function] = []
            self.simulator.env.timeout(pre_warm_window)
            if self.simulator.env.now == self.predictors[hash_function].last_predict_time + pre_warm_window:
                self.instances[hash_function] = [InstanceState()] * currency
                self.simulator.env.timeout(keep_alive_window)
                if self.simulator.env.now == \
                        self.predictors[hash_function].last_predict_time \
                        + keep_alive_window + keep_alive_window:
                    self.instances[hash_function] = []
