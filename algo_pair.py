from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters

from datetime import datetime
import pytz

import numpy as np

from csv_file_datasource import TempCSVDataSource

from engg.kalman_filter import KalmanFilterPair2

class Storage:
    pass

def initialize(context):
    context.sym_a = 'KO'
    context.sym_b = 'PEP'
    Vw = 0.000001
    Ve = 0.001
    A = np.eye(2)
    B = 0 * np.eye(2)
    Q = Vw / (1-Vw) * np.eye(2)
    R = np.matrix([Ve])
    H = np.matrix([0,0])
    x = np.matrix([[0],[0]])
    P = 0 * np.eye(2)

    context.kalman_filter = KalmanFilterPair2(A, B, H, x, P, Q, R)
    context.target_position = None
    context.current_position = None

    # storage
    context.storage = Storage()
    context.storage.price_a = []
    context.storage.price_b = []
    context.storage.err = []
    context.storage.sqrt_q = []
    context.storage.pair = []
    context.storage.hedge_ratio = []
    context.storage.intercept = []

def handle_data(context, data):
    price_a = data[context.sym_a].price
    price_b = data[context.sym_b].price
    if np.isnan(price_b) or np.isnan(price_a):
        return
    rtn_val = context.kalman_filter.step(price_b, price_a)
    err = rtn_val.err
    sd = rtn_val.sd

    context.storage.price_a.append(price_a)
    context.storage.price_b.append(price_b)
    context.storage.err.append(err)
    context.storage.sqrt_q.append(sd)

    hedge_ratio = context.kalman_filter.get_hedge_ratio()
    context.storage.hedge_ratio.append(hedge_ratio)
    context.storage.intercept.append(context.kalman_filter.get_x1())
    context.storage.pair.append(price_a + price_b * hedge_ratio)

    # Determine Position
    if err < -sd:
        context.target_position = 'long'
    elif err > sd:
        context.target_position = 'short'
    else:
        context.target_position = 'exit'

    num_shares = 1000
    # Order
    if context.current_position != context.target_position:
        if context.target_position == 'long':
            context.order(context.sym_a, num_shares)
            context.order(context.sym_b, hedge_ratio * num_shares)
            context.current_position = 'long'

        elif context.target_position == 'short':
            context.order(context.sym_a, -num_shares)
            context.order(context.sym_b, hedge_ratio * -num_shares)
            context.current_position = 'short'

        elif context.target_position == 'exit':
            context.order_target(context.sym_a, 0)
            context.order_target(context.sym_b, 0)
            context.current_position = 'exit'

if __name__ == '__main__':
    start = datetime(2015, 5, 14, 3, 31, 0, 0, pytz.utc)
    end = datetime(2015, 5, 14, 4, 31, 0, 0, pytz.utc)
    #end = datetime(2015, 5, 15, 9, 59, 0, 0, pytz.utc)

    data = TempCSVDataSource(stocks=['KO', 'PEP'], start=start, end=end)

    sim_params = create_simulation_parameters(
        start=start, end=end, capital_base=5000,
        data_frequency='minute',
        emission_rate='minute'
        )

    algo = TradingAlgorithm(
            handle_data=handle_data,
            initialize=initialize,
            sim_params=sim_params
            )
    results = algo.run(data)

    i_start = 20
    price_a = algo.storage.price_a
    price_b = algo.storage.price_b
    err = algo.storage.err[i_start:]
    sqrt_q = algo.storage.sqrt_q[i_start:]

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
    pylab.plot(range(len(err)), algo.storage.pair[i_start:], 'b')
    pylab.xlabel('Time')
    pylab.ylabel('$')
    pylab.title('Artificial Stationary Price')

    pylab.figure()
    pylab.plot(
            range(len(price_a)), algo.storage.hedge_ratio, 'r',
            )
    pylab.xlabel('Time')
    pylab.ylabel('Hedge Ratio')
    pylab.title('Kalman Filter Test')

    pylab.figure()
    pylab.plot(
            range(len(price_a)), algo.storage.intercept, 'g',
            )
    pylab.xlabel('Time')
    pylab.ylabel('Intercept')
    pylab.title('Kalman Filter Test')

    pylab.show()
