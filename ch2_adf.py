from zipline.utils.factory import load_from_yahoo

from datetime import datetime
import pytz

import numpy as np
import statsmodels.tsa.stattools as st

def genhurst(ts, lags=20):
    len_s = len(ts)
    if len_s < lags:
        i_lags = range(2, len_s)
    else:
        i_lags = range(2, lags)
    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in i_lags]
    p = np.polyfit(np.log(i_lags), np.log(tau), 1)
    return p[0]*2.0

if __name__ == '__main__':
    start = datetime(2007, 7, 22, 0, 0, 0, 0, pytz.utc)
    end = datetime(2012, 3, 28, 0, 0, 0, 0, pytz.utc)

    data = load_from_yahoo(stocks=['cad=x'], start=start, end=end)

    #import pylab
    #pylab.plot(range(len(data)), data.values)
    #pylab.xlabel('Time')
    #pylab.ylabel('USD.CAD')
    #pylab.title('Price')
    #pylab.show()

    s = data.values.transpose()

    res = st.adfuller(s[0], 1)
    print res
    h = genhurst(s[0])
    print h
