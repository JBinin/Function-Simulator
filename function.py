from __future__ import annotations
from typing import List, TYPE_CHECKING, Dict, Callable
from predictor import Histogram

if TYPE_CHECKING:
    from simulator import Simulator

from info import default_info
from simpy.util import start_delayed


class InstanceState(object):
    def __init__(self):
        self.idle = True
        self.warm = False
        self.last_request_start_time = 0
        self.execution_latency = 0
        self.cold_start_latency = 0
        self.memory = 0
        self.cpu = 0

    def check(self, now) -> bool:
        if self.idle:
            return True
        if now - self.last_request_start_time \
                >= self.execution_latency + self.cold_start_latency:
            self.idle = True
            self.warm = False
        return self.idle

    def update(self, now: int, execution_latency: int, cold_start_latency: int) -> bool:
        if not self.check(now):
            return False
        self.idle = False
        self.warm = False
        self.last_request_start_time = now
        self.execution_latency = execution_latency
        self.cold_start_latency = cold_start_latency
        return True


class Functions(object):
    def __init__(self):
        self.instances: Dict[str, List[InstanceState]] = {}
        self.simulator = None
        self.predictors: Dict[str, Histogram] = {}
        self.cold_start: Dict[str, int] = {}
        self.warm_start: Dict[str, int] = {}

        self.predict_trigger = None

    def attach(self, simulator: Simulator):
        self.simulator = simulator
        self.predict_trigger = self.simulator.env.event()

    def clear_idle_instances(self, now: int, hash_function: str):
        if hash_function not in self.instances:
            return
        self.instances[hash_function] = \
            [instance for instance in self.instances[hash_function]
             if not instance.check(now) or instance.warm]

    def update(self, request_count: int, now: int, hash_function: str):
        if request_count == 0:
            return
        self.update_instance(request_count, now, hash_function)
        self.update_predictor(request_count, now, hash_function)

    def update_instance(self, request_count: int, now: int, hash_function: str):
        if hash_function not in self.instances:
            self.instances[hash_function] = []
            self.cold_start[hash_function] = 0
            self.warm_start[hash_function] = 0
        for index in range(len(self.instances[hash_function])):
            if self.instances[hash_function][index].update(
                    now, default_info.get_exec_time_min(hash_function),
                    0):
                request_count -= 1
                self.warm_start[hash_function] += 1
                if request_count == 0:
                    return
        instance = InstanceState()
        instance.update(now, default_info.get_exec_time_min(hash_function),
                        default_info.get_cold_time_min(hash_function))
        self.instances[hash_function] += [instance] * request_count
        self.cold_start[hash_function] += request_count

    def clean(self, time: int, hash_function: str):
        if self.predictors[hash_function].last_predict_time == time:
            self.instances[hash_function] = []

    def create_instance(self, time: int, hash_function: str, currency: int, keep_alive_window: int):
        if self.predictors[hash_function].last_predict_time == time:
            instance = InstanceState()
            instance.warm = True
            self.instances[hash_function] = [instance] * currency
            self.duration_with_no_invocation(keep_alive_window, hash_function, self.clean)

    def duration_with_no_invocation(self, duration_time: int, hash_function: str, task: Callable, *args) -> bool:
        record_last_predict_time = self.predictors[hash_function].last_predict_time
        yield start_delayed(self.simulator.env, task(record_last_predict_time, hash_function, *args), duration_time)

    def update_predictor(self, request_count: int, now: int, hash_function: str):
        if hash_function not in self.predictors:
            self.predictors[hash_function] = Histogram(4 * 60)
        self.predictors[hash_function].predict(
            request_count, now, default_info.get_exec_time_min(hash_function))

        pre_warm_window = self.predictors[hash_function].pre_warm_window
        keep_alive_window = self.predictors[hash_function].keep_alive_window
        self.clear_idle_instances(now, hash_function)

        if pre_warm_window == 0:
            for instance in self.instances[hash_function]:
                instance.warm = True
            self.duration_with_no_invocation(
                keep_alive_window + default_info.get_exec_time_min(hash_function),
                hash_function, self.clean)
        else:
            currency = len(self.instances[hash_function])
            self.duration_with_no_invocation(default_info.get_exec_time_min(hash_function), hash_function, self.clean)
            self.duration_with_no_invocation(pre_warm_window, hash_function, self.create_instance, currency,
                                             keep_alive_window)

    def run(self):
        while True:
            # wait for next predict request
            yield self.predict_trigger
            real_workload = self.simulator.workload
            for hash_function, _ in real_workload.requests.items():
                self.update(
                    real_workload.requests[hash_function][real_workload.current_index],
                    self.simulator.env.now,
                    hash_function)
            self.predict_trigger = self.simulator.env.event()
