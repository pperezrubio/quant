import os
import re
from datetime import datetime
import pytz

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.stats import pearsonr

from IPython import embed

from ch6_datasource import _get_data, _filter_sym, _parse_datetime


def load_timeseries():
    mat_file = loadmat('quant-data/inputDataOHLCDaily_20120511.mat')
    sym = 'TU'
    index = _filter_sym('TU', mat_file['syms'])
    cl = _get_data(index, mat_file['cl'])
    tday = map(_parse_datetime,_get_data(index, mat_file['tday']))
    return pd.Series(cl, tday)

def get_return(s1, s2):
    ret = (s1 - s2) / s2
    return ret

def exclude_nan(s1, s2):
    i_nan = np.isnan(s1) | np.isnan(s2)
    return s1[~i_nan], s2[~i_nan]

if __name__ == '__main__':
    s = load_timeseries()
    lookback = 40
    holddays = 20

    ret_lag = get_return(s, s.shift(-lookback))
    ret_fut = get_return(s.shift(holddays), s)

    s1, s2 = exclude_nan(ret_lag, ret_fut)
    if lookback >= holddays:
        ind = np.arange(0, len(s1) - 1, holddays)
    else:
        ind = np.arange(0, len(s1) - 1, lookback)

    corr, p_value = pearsonr(s1[ind], s2[ind])
    print "%d %d %f %f" % (lookback, holddays, corr, p_value)
