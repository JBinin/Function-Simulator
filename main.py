import os

from workload import Workload
from simulator import Simulator

cur_dir = os.path.dirname(__file__)
data_path = "Dataset/azure-functions-dataset2019/"
data_path = os.path.join(cur_dir, data_path)
csv_file_pre = "invocations_per_function_md.anon.d"

trace = Workload()

for i in range(1, 2):
    csv_file = os.path.join(data_path, "{:02d}.csv".format(i))
    csv_file = data_path + csv_file
    trace.add_workload(csv_file)

simulator = Simulator(trace)
simulator.run()
