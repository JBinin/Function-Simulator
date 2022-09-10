from workload import Workload
import simpy
from function import Functions
from monitor import Monitor


class Simulator(object):
    def __init__(self, workload: Workload):
        self.env = simpy.Environment()
        self.workload = workload
        self.workload.attach(self)
        self.function = Functions()
        self.function.attach(self)
        self.monitor = Monitor()
        self.monitor.attach(self)
        self.is_finished = False

    def run(self):
        self.env.process(self.monitor.run())
        self.env.process(self.workload.run())
        self.env.run()

    def finished(self) -> bool:
        return self.is_finished
