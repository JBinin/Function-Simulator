import numpy as np
from typing import Dict

from predictor import IceBreaker
from sklearn.metrics import mean_squared_error
from utility import split_dict, save_dict_list_to_csv, read_azure_datas
from multiprocessing import Process, Queue


def mse_cdf(multi_process: int, csv_file: str):
    """
    :param csv_file:
    :param multi_process: the num of process to process this problem
    :return: None
    """
    assert multi_process >= 1
    trace = read_azure_datas(14)
    sub_dicts = []
    split_dict(trace.requests, sub_dicts, multi_process)
    process_list = []

    que = Queue(multi_process)

    for i in range(multi_process):
        p = Process(target=single_process_mse, args=(sub_dicts[i], que))
        process_list.append(p)
        p.start()
    for p in process_list:
        p.join()

    mse_dict = [que.get() for i in range(multi_process)]
    save_dict_list_to_csv(mse_dict, csv_file)


def single_process_mse(sub_trace: Dict[str, np.ndarray], que: Queue):
    mse_dict = {}
    ice_predictor = IceBreaker(10)

    for hash_function in sub_trace.keys():
        one_function_trace = sub_trace[hash_function]
        n = one_function_trace.size
        local_window = 60
        predict_result = []
        for i in range(0, n - local_window):
            trace_window = one_function_trace[i:i + local_window]
            predict_list = ice_predictor.fourier_extrapolation(trace_window, 1)
            if predict_list[0] < 0:
                predict_list[0] = 0
            else:
                predict_list[0] = round(predict_list[0])
            predict_result.append(predict_list[0])
        one_function_trace = one_function_trace[local_window:]
        mse = mean_squared_error(one_function_trace, predict_result)
        mse_dict[hash_function] = mse
    que.put(mse_dict)
