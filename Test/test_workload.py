import unittest
from workload import Workload
from simulator import Simulator
from typing import Dict, List
import numpy as np
import os
from function import Functions


class FakeSimulator(Simulator):
    """
    implement a simulator class for test
    """

    def __init__(self, workload: Workload):
        super().__init__(workload)
        self.function = FakeFunctions()
        self.function.attach(self)

    def run(self):
        """
        overwrite run() for test
        """
        self.env.process(self.workload.run())
        self.env.process(self.function.run())
        self.env.run()


class FakeFunctions(Functions):
    """
    implement a function class for test
    """

    def __init__(self):
        super().__init__()
        self.simulator = None
        self.requests: Dict[str, List[int]] = {}
        self.timestamp: Dict[str, List[int]] = {}

    def attach(self, simulator: FakeSimulator):
        self.simulator = simulator
        self.predict_trigger = self.simulator.env.event()

    def update(self, request_count: int, now: int, hash_function: str):
        """
        implement update() for test
        just record the request_count every step
        """
        if hash_function not in self.requests:
            self.requests[hash_function] = []
        self.requests[hash_function].append(request_count)
        if hash_function not in self.timestamp:
            self.timestamp[hash_function] = []
        self.timestamp[hash_function].append(now)


class TestWorkload(unittest.TestCase):
    def test_add_workload(self):
        cur_dir = os.path.dirname(__file__)
        csv_file = os.path.join(cur_dir, "test_data/test_workload.csv")
        test_workload = Workload()
        test_workload.add_workload(csv_file)
        self.assertEqual(len(test_workload.requests), 9)
        self.assertEqual(test_workload.max_count, 1440)

        test_workload.add_workload(csv_file)
        self.assertEqual(len(test_workload.requests), 9)
        self.assertEqual(test_workload.max_count, 1440 * 2)

    def test_run(self):
        cur_dir = os.path.dirname(__file__)
        csv_file = os.path.join(cur_dir, "test_data/test_workload.csv")
        test_workload = Workload()
        test_workload.add_workload(csv_file)
        test_simulator = FakeSimulator(test_workload)
        test_simulator.run()
        hash_function_example = "520dbd6bd906840012aa0c4b778743efc7c0ac7b7caf96b3d7f85d46209b7872"
        self.assertEqual((np.array(test_simulator.function.requests[hash_function_example])
                          == test_workload.requests[hash_function_example]).all(), True)
        self.assertEqual(test_simulator.function.timestamp[hash_function_example],
                         list(range(0, test_simulator.workload.max_count)))


if __name__ == "__main__":
    unittest.main()
