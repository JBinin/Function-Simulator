from function import Functions, InstanceState
import unittest
from simulator import Simulator
from workload import Workload
import os


class FakeSimulator(Simulator):
    """
    implement a simulator class for test
    """

    def __init__(self, workload: Workload):
        super().__init__(workload)

    def run(self):
        """
        overwrite run() for test
        """
        pass


class TestInstanceState(unittest.TestCase):
    def setUp(self) -> None:
        self.test_instance = InstanceState()

    def test_check(self):
        self.assertTrue(self.test_instance.check(0))

    def test_update(self):
        self.assertTrue(self.test_instance.update(0, 10, 1))
        self.assertFalse(self.test_instance.update(1, 10, 1))
        self.assertTrue(self.test_instance.update(11, 10, 1))


class TestFunctions(unittest.TestCase):
    def setUp(self) -> None:
        test_workload = Workload()
        cur_dir = os.path.dirname(__file__)
        csv_file = os.path.join(cur_dir, "test_data/test_workload.csv")
        test_workload.add_workload(csv_file)
        self.test_simulator = FakeSimulator(test_workload)

    def test_update_instance(self):
        # create a new Functions for test
        self.test_simulator.function = Functions()
        self.test_simulator.function.update_instance(1, 0, "function1")
        self.test_simulator.function.update_instance(2, 0, "function2")
        test_function = self.test_simulator.function
        self.assertEqual(test_function.cold_start["function1"], 1)
        self.assertEqual(test_function.cold_start["function2"], 2)
        self.assertFalse(test_function.instances["function1"][0].idle)
        test_function.instances["function1"][0].idle = True
        self.test_simulator.function.update_instance(1, 0, "function1")
        self.assertEqual(test_function.warm_start["function1"], 1)


if __name__ == "__main__":
    unittest.main()
