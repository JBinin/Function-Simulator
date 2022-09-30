from simulator import Simulator
from workload import Workload
from utility import read_azure_datas, cdf_plot
from cdf import mse_cdf
import pandas as pd
import multiprocessing


def run_simulate():
    trace = read_azure_datas(2)
    simulator = Simulator(trace)
    simulator.set_policy("DefaultKeepalive", 10)
    simulator.run()


def single_process_task(workload: Workload, index: int, policy: str, *args):
    simulator = Simulator(workload)
    simulator.set_policy(policy, *args)
    simulator.monitor.set_filename(str(index))
    simulator.run()


def run_multi_simulate(multi_process_num: int):
    trace = read_azure_datas(1, 12)
    traces = trace.split_n_workloads(multi_process_num)
    policy = "Histogram"

    process_list = []
    for i in range(multi_process_num):
        p = multiprocessing.Process(target=single_process_task, args=(traces[i], i, policy, 4 * 60))
        process_list.append(p)
        p.start()
    for p in process_list:
        p.join()

    merge_csv(policy, 0, multi_process_num)


def merge_csv(prefix: str, low: int, high: int):
    datas = []
    for i in range(low, high):
        file_name = prefix + "_" + str(i) + ".csv"
        datas.append(pd.read_csv(file_name))
    result = pd.concat(datas, ignore_index=True)
    result.to_csv(prefix + "_merge.csv")


def run_mse_cdf():
    mse_cdf(6, "mse_cdf.csv")
    mse_cdf_data = pd.read_csv("mse_cdf.csv")
    mse = mse_cdf_data["mse"].values
    cdf_plot(mse, "mse_cdf.pdf")


if __name__ == "__main__":
    # run_mse_cdf()

    run_multi_simulate(4)
