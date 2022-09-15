"""
todo: this file need to be modify to match the real trace
"""


class FunctionInfo(object):
    def __init__(self):
        self.default_exec_time_min = 1
        self.default_cold_time_min = 0
        self.default_mem_mb = 100

    def get_exec_time_min(self, function: str):
        return self.default_exec_time_min

    def get_cold_time_min(self, function: str):
        return self.default_cold_time_min

    def get_mem_mb(self, function: str):
        return self.default_mem_mb


"""
singleton pattern
provide function related information
"""
default_info = FunctionInfo()
