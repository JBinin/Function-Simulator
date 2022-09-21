from __future__ import annotations

import utility
from predictor import PredictAlgorithm
from typing import List, TYPE_CHECKING, Dict, Callable

if TYPE_CHECKING:
    from simulator import Simulator

from info import default_info


class InstanceState(object):
    def __init__(self):
        self.idle = True
        self.warm = False
        self.last_request_start_time = 0
        self.execution_latency = 0
        self.cold_start_latency = 0
        self.memory = 1
        self.cpu = 1
        # time stamp of pre warm
        # to calculate the wasted time
        self.pre_warm_load_time = None

    def set_pre_warm_load_time(self, time: int):
        self.pre_warm_load_time = time

    # get wasted time and reset the pre warm load time to -1
    def wasted_time_and_reset(self, now: int) -> int:
        if self.pre_warm_load_time is None:
            return 0
        wasted_time = now - self.pre_warm_load_time
        self.pre_warm_load_time = None
        return wasted_time

    def check(self, now) -> bool:
        if self.idle:
            return True
        if now - self.last_request_start_time \
                >= self.execution_latency + self.cold_start_latency:
            self.idle = True
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
        self.predictors: Dict[str, PredictAlgorithm] = {}
        self.cold_start: Dict[str, int] = {}
        self.warm_start: Dict[str, int] = {}
        self.wasted_time: Dict[str, int] = {}
        self.event_list: Dict[int, List[Callable]] = {}
        self.last_currency: Dict[str, int] = {}

        self.predict_trigger = None

    def attach(self, simulator: Simulator):
        self.simulator = simulator
        self.predict_trigger = self.simulator.env.event()

    def update(self, request_count: int, now: int, hash_function: str):
        if request_count == 0:
            self.process_event()
            return
        self.update_instance(request_count, now, hash_function)
        self.update_currency(hash_function)
        self.process_event()
        self.update_predictor(request_count, now, hash_function)

    def update_currency(self, hash_function: str):
        if hash_function in self.instances.keys():
            currency = len(self.instances[hash_function])
            if currency != 0:
                self.last_currency[hash_function] = currency

    def update_instance(self, request_count: int, now: int, hash_function: str):
        if hash_function not in self.instances:
            self.instances[hash_function] = []
            self.cold_start[hash_function] = 0
            self.warm_start[hash_function] = 0
            self.wasted_time[hash_function] = 0

        for index in range(len(self.instances[hash_function])):
            instance = self.instances[hash_function][index]
            if instance.update(
                    now, default_info.get_exec_time_min(hash_function),
                    0):
                request_count -= 1
                self.wasted_time[hash_function] += instance.wasted_time_and_reset(now)
                self.warm_start[hash_function] += 1
                if request_count == 0:
                    return
        instance = InstanceState()
        instance.update(now, default_info.get_exec_time_min(hash_function),
                        default_info.get_cold_time_min(hash_function))
        self.instances[hash_function] += [instance] * request_count
        self.cold_start[hash_function] += request_count

    def clean(self, time: int, hash_function: str):
        def real_function():
            if self.predictors[hash_function].last_predict_time == time:
                for instance in self.instances[hash_function]:
                    self.wasted_time[hash_function] += instance.wasted_time_and_reset(self.simulator.env.now)
                self.instances[hash_function] = []

        return real_function

    def tag_pre_warm_time(self, time: int, hash_function: str):
        def real_function():
            if self.predictors[hash_function].last_predict_time == time:
                for instance in self.instances[hash_function]:
                    instance.set_pre_warm_load_time(self.simulator.env.now)
                    instance.warm = True
                    instance.idle = True

        return real_function

    def create_instance(self, time: int, hash_function: str, currency: int):
        def real_function():
            if self.predictors[hash_function].last_predict_time == time:
                instance = InstanceState()
                instance.warm = True
                self.instances[hash_function] = [instance] * currency

        return real_function

    def duration_with_no_invocation(self, duration_time: int, hash_function: str, task: Callable, *args):
        record_last_predict_time = self.predictors[hash_function].last_predict_time
        key = self.simulator.env.now + duration_time
        if key not in self.event_list.keys():
            self.event_list[key] = []

        self.event_list[key].append(task(record_last_predict_time, hash_function, *args))

    def update_predictor(self, request_count: int, now: int, hash_function: str):
        if hash_function not in self.predictors:
            self.predictors[hash_function] = utility.get_policy_predictor(self.simulator.policy,
                                                                          *self.simulator.policy_args)
        self.predictors[hash_function].predict(
            request_count, now, default_info.get_exec_time_min(hash_function))

        pre_warm_window = self.predictors[hash_function].pre_warm_window
        keep_alive_window = self.predictors[hash_function].keep_alive_window

        if pre_warm_window == 0:
            self.duration_with_no_invocation(default_info.get_exec_time_min(hash_function), hash_function,
                                             self.tag_pre_warm_time)
            self.duration_with_no_invocation(
                keep_alive_window + default_info.get_exec_time_min(hash_function),
                hash_function, self.clean)
        else:
            currency = self.last_currency[hash_function]
            self.duration_with_no_invocation(default_info.get_exec_time_min(hash_function), hash_function, self.clean)
            self.duration_with_no_invocation(default_info.get_exec_time_min(hash_function) + pre_warm_window,
                                             hash_function, self.create_instance, currency)
            self.duration_with_no_invocation(default_info.get_exec_time_min(hash_function) + pre_warm_window,
                                             hash_function, self.tag_pre_warm_time)
            self.duration_with_no_invocation(default_info.get_exec_time_min(hash_function) + pre_warm_window +
                                             keep_alive_window, hash_function, self.clean)

    def process_event(self):
        key = self.simulator.env.now
        if key not in self.event_list.keys():
            return
        for event in self.event_list[key]:
            event()
        del self.event_list[key]

    def run(self):
        while True:
            # wait for next predict request
            yield self.predict_trigger
            real_workload = self.simulator.workload
            for hash_function in real_workload.requests.keys():
                self.update(
                    real_workload.requests[hash_function][real_workload.current_index],
                    self.simulator.env.now,
                    hash_function)
            self.predict_trigger = self.simulator.env.event()
