from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters

from datetime import datetime
import pytz

import numpy as np

from csv_file_datasource import TempCSVDataSource

from engg.kalman_filter import KalmanFilterPair2

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

    context.kalman_filter = KalmanFilterPair2(A, B, H, x, P, Q, R)

    # storage
    context.price_a = []
    context.price_b = []
    context.err = []
    context.sqrt_q = []
    context.pair = []
    context.hedge_ratio = []
    context.intercept = []

def handle_data(context, data):
    price_a = data['KO'].price
    price_b = data['PEP'].price
    if np.isnan(price_b) or np.isnan(price_a):
        return
    rtn_val = context.kalman_filter.step(price_b, price_a)
    err = rtn_val.err
    sd = rtn_val.sd

    context.price_a.append(price_a)
    context.price_b.append(price_b)
    context.err.append(err)
    context.sqrt_q.append(sd)

    hedge_ratio = context.kalman_filter.get_hedge_ratio()
    context.hedge_ratio.append(hedge_ratio)
    context.intercept.append(context.kalman_filter.get_x1())
    context.pair.append(price_a + price_b * hedge_ratio)

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

    #from IPython import embed
    #embed()

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

    pylab.figure()
    pylab.plot(range(len(price_a)), price_a, 'r')
    pylab.xlabel('Time')
    pylab.ylabel('$')
    pylab.title('Price A')

    pylab.figure()
    pylab.plot(range(len(price_a)), price_b, 'g')
    pylab.xlabel('Time')
    pylab.ylabel('$')
    pylab.title('Price B')

    pylab.figure()
    pylab.plot(range(len(err)), algo.pair[i_start:], 'b')
    pylab.xlabel('Time')
    pylab.ylabel('$')
    pylab.title('Artificial Stationary Price')

    pylab.figure()
    pylab.plot(
            range(len(price_a)), algo.hedge_ratio, 'r',
            )
    pylab.xlabel('Time')
    pylab.ylabel('Hedge Ratio')
    pylab.title('Kalman Filter Test')

    pylab.figure()
    pylab.plot(
            range(len(price_a)), algo.intercept, 'g',
            )
    pylab.xlabel('Time')
    pylab.ylabel('Intercept')
    pylab.title('Kalman Filter Test')

    pylab.show()
