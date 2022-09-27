import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from predictor import Histogram, DefaultKeepalive
import sys
import os
from typing import Dict, List
from workload import Workload

import statsmodels.api as sm


def get_policy_predictor(policy: str, *args):
    if policy == "DefaultKeepalive":
        return DefaultKeepalive(*args)
    if policy == "Histogram":
        return Histogram(*args)
    else:
        print("policy not supported: " + policy)
        sys.exit()


def split_dict(dicts: Dict[str, np.ndarray], sub_dicts: List[Dict[str, np.ndarray]], sub_dicts_len: int):
    if sub_dicts_len == 1:
        sub_dicts.append(dicts)
    else:
        total_len = len(dicts)
        single_dict_len = total_len // sub_dicts_len
        start = 0
        i = 0
        keys = list(dicts.keys())
        while i < sub_dicts_len:
            if i < sub_dicts_len - 1:
                sub_dicts.append(
                    {k: dicts[k] for k in keys[start:start + single_dict_len]}
                )
            else:
                sub_dicts.append(
                    {k: dicts[k] for k in keys[start:total_len]}
                )
            start += single_dict_len
            i += 1


def save_dict_list_to_csv(dict_list: List[Dict[str, int]], csv_file: str):
    length = len(dict_list)
    tmp_result = []
    for i in range(length):
        tmp_result.append(pd.DataFrame(dict_list[i], index=["mse"]).transpose())
    result = pd.concat(tmp_result)
    result.to_csv(csv_file)


def read_azure_datas(day: int, function_limits: int = None):
    cur_dir = os.path.dirname(__file__)
    data_path = "Dataset/azure-functions-dataset2019/"
    data_path = os.path.join(cur_dir, data_path)
    csv_file_pre = "invocations_per_function_md.anon.d"
    trace = Workload()
    if function_limits is not None:
        trace.set_function_limit(function_limits)

    for i in range(1, day + 1):
        csv_file = os.path.join(data_path, csv_file_pre + "{:02d}.csv".format(i))
        trace.add_workload(csv_file)
    return trace


def cdf_plot(data: np.ndarray, pic_file:str):
    ecdf = sm.distributions.ECDF(data)
    x = np.linspace(min(data), max(data))
    y = ecdf(x)
    plt.plot(x, y, "r--")
    plt.title("CDF")
    plt.savefig(pic_file)
