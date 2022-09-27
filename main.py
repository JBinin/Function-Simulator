from simulator import Simulator
from utility import read_azure_datas, cdf_plot
from mse import mse_cdf
import pandas as pd


def run_simulate():
    trace = read_azure_datas(2)
    simulator = Simulator(trace)
    simulator.set_policy("DefaultKeepalive", 10)
    simulator.run()


def run_mse_cdf():
    mse_cdf(6, "mse_cdf.csv")
    mse_cdf_data = pd.read_csv("mse_cdf.csv")
    mse = mse_cdf_data["mse"].values
    cdf_plot(mse, "mse_cdf.pdf")


if __name__ == "__main__":
    run_mse_cdf()
