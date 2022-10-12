import os

import numpy as np

from workload import Workload

cur_dir = os.path.dirname(__file__)
data_path = "Dataset/azure-functions-dataset2019/"
data_path = os.path.join(cur_dir, data_path)
csv_file_pre = "invocations_per_function_md.anon.d"

trace = Workload()
# trace.set_function_limit(1000)

for i in range(1, 15):
    csv_file = os.path.join(data_path, csv_file_pre + "{:02d}.csv".format(i))
    trace.add_workload(csv_file)

# trace.currency_cdf("currency_count.csv")

hash_function = "8203ff88388384a6f9ed28664e8e9484119ff340cb7dc0811a15194b3a507f0e"
np.savetxt(hash_function + ".txt", trace.requests[hash_function], fmt="%d")
