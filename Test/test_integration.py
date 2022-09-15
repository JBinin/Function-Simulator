import unittest
import os
from workload import Workload
from simulator import Simulator


class TestIntegrated(unittest.TestCase):
    def test(self):
        test_workload = Workload()
        cur_dir = os.path.dirname(__file__)
        csv_file = os.path.join(cur_dir, "test_data/integration_data.csv")
        test_workload.add_workload(csv_file)
        simulator = Simulator(test_workload)
        simulator.run()
        self.assertEqual(
            simulator.function.cold_start[
                "520dbd6bd906840012aa0c4b778743efc7c0ac7b7caf96b3d7f85d46209b7872"], 1)
        self.assertEqual(
            simulator.function.warm_start[
                "520dbd6bd906840012aa0c4b778743efc7c0ac7b7caf96b3d7f85d46209b7872"], 287)


if __name__ == "__main__":
    unittest.main()
