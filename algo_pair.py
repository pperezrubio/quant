from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters

from datetime import datetime
import pytz

import numpy as np

from csv_file_datasource import TempCSVDataSource

from engg.kalman_filter import KalmanFilterPair

def initialize(context):
    Vw = 0.1
    Ve = 0.001
    A = np.eye(2)
    B = 0 * np.eye(2)
    Q = Vw / (1-Vw) * np.eye(2)
    R = Ve
    H = np.matrix([0,0])
    x = np.matrix([[0],[0]])
    P = 0 * np.eye(2)

    context.kalman_filter = KalmanFilterPair(A, B, H, x, P, Q, R)

def handle_data(context, data):
    price_a = data['KO'].price
    price_b = data['PEP'].price
    err, q = context.kalman_filter.step(price_b, np.matrix([price_a, 1.0]))

    context.record(
        ko=data['KO'].price,
        pep=data['PEP'].price
        )

if __name__ == '__main__':
    start = datetime(2015, 5, 14, 3, 31, 0, 0, pytz.utc)
    end = datetime(2015, 5, 15, 9, 59, 0, 0, pytz.utc)

    data = TempCSVDataSource(stocks=['KO', 'PEP'], start=start, end=end)

    sim_params = create_simulation_parameters(
        start=start, end=end, capital_base=5000, data_frequency='minute')

    algo = TradingAlgorithm(
            handle_data=handle_data,
            initialize=initialize,
            sim_params=sim_params
            )
    results = algo.run(data)
    print results
    from IPython import embed
    embed()
