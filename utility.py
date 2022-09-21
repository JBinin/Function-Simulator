import numpy as np
from predictor import Histogram, DefaultKeepalive
import sys


def read_from_txt(txt_file: str) -> np.ndarray:
    result = []
    with open(txt_file) as f:
        for line in f:
            result.append(int(line))
    return np.array(result)


def get_policy_predictor(policy: str, *args):
    if policy == "DefaultKeepalive":
        return DefaultKeepalive(*args)
    if policy == "Histogram":
        return Histogram(*args)
    else:
        print("policy not supported: " + policy)
        sys.exit()
