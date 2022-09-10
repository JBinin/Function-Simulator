from workload import Workload
from simulator import Simulator


data_path = "~/Downloads/azurefunctions-dataset2019/"
csv_file_pre = "invocations_per_function_md.anon.d"

trace = Workload()

for i in range(1, 2):
    csv_file = csv_file_pre + "{:02d}.csv".format(i)
    csv_file = data_path + csv_file
    trace.add_workload(csv_file)

simulator = Simulator(trace)
simulator.run()
