"""
todo: this file need to be modify to match the real trace
"""

import pandas as pd
from typing import Dict
import os


class FunctionInfo(object):
    def __init__(self):
        self.default_exec_time_min = 1
        self.default_cold_time_min = 0
        self.default_mem_mb = 100
        self.mem_mb: Dict[str, int] = {}
        self.exec_time_min: Dict[str, int] = {}

    def add_exec_time(self, csvfile: str):
        exec_time = pd.read_csv(csvfile)
        for _, row in exec_time.iterrows():
            hash_function = row[0]
            if hash_function not in self.exec_time_min:
                self.exec_time_min[hash_function] = row[1]

    def get_exec_time_min(self, hash_function: str):
        if hash_function in self.exec_time_min:
            return self.exec_time_min[hash_function]
        return self.default_exec_time_min

    def get_cold_time_min(self, hash_function: str):
        return self.default_cold_time_min

    def get_mem_mb(self, hash_function: str):
        return self.default_mem_mb


"""
singleton pattern
provide function related information
"""

cur_dir = os.path.dirname(__file__)
data_path = "Dataset/processed-azure-functions-dataset2019/function_duration_min.csv"
data_path = os.path.join(cur_dir, data_path)

default_info = FunctionInfo()
default_info.add_exec_time(data_path)
