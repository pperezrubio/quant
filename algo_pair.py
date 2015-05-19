from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters

from datetime import datetime
import pytz

import numpy as np

from csv_file_datasource import TempCSVDataSource

from engg.kalman_filter import KalmanFilterPair

def initialize(context):
    Vw = 0.00001
    Ve = 0.001
    A = np.eye(2)
    B = 0 * np.eye(2)
    Q = Vw / (1-Vw) * np.eye(2)
    R = np.matrix([Ve])
    H = np.matrix([0,0])
    x = np.matrix([[0],[0]])
    P = 0 * np.eye(2)

    context.kalman_filter = KalmanFilterPair(A, B, H, x, P, Q, R)

    # storage
    context.price_a = []
    context.price_b = []
    context.err = []
    context.sqrt_q = []

def handle_data(context, data):
    price_a = data['KO'].price
    price_b = data['PEP'].price
    if np.isnan(price_b) or np.isnan(price_a):
        return
    err, q = context.kalman_filter.step(
            np.matrix([price_b]), np.matrix([price_a, 1.0]))

    context.price_a.append(price_a)
    context.price_b.append(price_b)
    context.err.append(err[0,0])
    context.sqrt_q.append(np.sqrt(np.abs(q[0,0])))

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

    i_start = 20
    price_a = algo.price_a
    price_b = algo.price_b
    err = algo.err[i_start:]
    sqrt_q = algo.sqrt_q[i_start:]

    import pylab
    pylab.plot(
            range(len(err)), err, 'r',
            range(len(err)), sqrt_q, 'g',
            range(len(err)), -1 * np.asarray(sqrt_q), 'g',
            )
    pylab.xlabel('Time')
    pylab.ylabel('Spread')
    pylab.title('Kalman Filter Test')
    pylab.legend(('err', 'upper_q', 'lower_q'))
    pylab.show()
