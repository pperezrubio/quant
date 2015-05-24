from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters
from zipline.utils.factory import load_from_yahoo

from datetime import datetime
import pytz

import numpy as np
import statsmodels.api as sm

from IPython import embed

syma = 'GLD'
symb = 'USO'

class Storage:
    pass

def initialize(context):
    context.i = 0
    context.sym_a = syma
    context.sym_b = symb
    context.storage = Storage()
    context.storage.price_a = []
    context.storage.price_b = []
    context.storage.yport = []
    context.storage.beta0 = []
    context.storage.beta1 = []

def handle_data(context, data):
    lookback = 20

    context.i += 1
    price_a = data[context.sym_a].price
    price_b = data[context.sym_b].price

    context.storage.price_a.append(price_a)
    context.storage.price_b.append(price_b)

    if context.i >= lookback:
        arr_a = context.storage.price_a[-lookback:]
        arr_b = context.storage.price_b[-lookback:]
        v_a = np.asarray(arr_a).reshape(lookback, 1)
        v_b = np.asarray(arr_b).reshape(lookback, 1)
        v_ones = np.ones(v_a.shape)
        v_aa = np.hstack([v_a, v_ones])
        est = sm.OLS(v_b, v_aa).fit()
        beta0, beta1 = est.params

        hedge_ratio = beta0
        yport = -hedge_ratio * price_a + price_b

        context.storage.yport.append(yport)
        context.storage.beta0.append(beta0)
        context.storage.beta1.append(beta1)
    else:
        context.storage.yport.append(0)
        context.storage.beta0.append(0)
        context.storage.beta1.append(0)

if __name__ == '__main__':
    start = datetime(2006, 3, 24, 0, 0, 0, 0, pytz.utc)
    end   = datetime(2012, 4, 9, 0, 0, 0, 0, pytz.utc)

    data = load_from_yahoo(stocks=[syma, symb], start=start, end=end)

    sim_params = create_simulation_parameters(
        start=start, end=end, capital_base=5000,
        data_frequency='daily',
        emission_rate='daily'
        )

    algo = TradingAlgorithm(
            handle_data=handle_data,
            initialize=initialize,
            sim_params=sim_params
            )
    results = algo.run(data)
    normal_length = len(algo.storage.price_a)

    import pylab
    pylab.figure()
    pylab.plot(range(normal_length), algo.storage.price_a, 'r')
    pylab.xlabel('Time')
    pylab.ylabel('$')
    pylab.title('Price A')

    pylab.figure()
    pylab.plot(range(normal_length), algo.storage.price_b, 'g')
    pylab.xlabel('Time')
    pylab.ylabel('$')
    pylab.title('Price B')

    pylab.figure()
    pylab.plot(range(normal_length), algo.storage.yport, 'b')
    pylab.xlabel('Time')
    pylab.ylabel('$')
    pylab.title('Price Artifical Stationary')

    pylab.figure()
    pylab.plot(range(normal_length), algo.storage.beta0, 'g')
    pylab.xlabel('Time')
    pylab.ylabel('Value')
    pylab.title('Beta 0')

    pylab.figure()
    pylab.plot(range(normal_length), algo.storage.beta1, 'g')
    pylab.xlabel('Time')
    pylab.ylabel('Value')
    pylab.title('Beta 1')


    pylab.show()


