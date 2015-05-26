import os
import re
from datetime import datetime
import pytz

import numpy as np
import pandas as pd
from scipy.io import loadmat

from zipline.gens.utils import hash_args
from zipline.sources.data_source import DataSource

from google_minute import load_raw_dataframe

def _filter_sym(str_sym, syms):
    item = filter(lambda x: x == [str_sym], syms[0])
    a, b = np.where(syms[0] == item)
    return b[0]

def _get_data(index,cell):
    return cell[:, index]

def _parse_datetime(fvalue):
    str_date = str(fvalue)[:8]
    dt_unaware = datetime.strptime(str_date, '%Y%m%d')
    return pytz.utc.localize(dt_unaware)

class TempDataSource(DataSource):
    def __init__(self, **kwargs):

        self.arg_string = hash_args('TempCSVDataSource', **kwargs)

        self.sids = kwargs.get('stocks')
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')

        self.started_sids = set()
        self._raw_data = None


    @property
    def instance_hash(self):
        return self.arg_string

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    def _df_within_start_end(self, df):
        # may need pytz here
        df['dt_dt'] = map(lambda x: x.to_datetime(), df.index)
        idx = (df['dt_dt'] > self.start) & (df['dt_dt'] < self.end)
        return df[idx]

    def raw_data_gen(self):
        mat_file = loadmat('test.mat')
        sym = 'TU'
        index = _filter_sym('TU', mat_file['syms'])
        cl = _get_data(index, mat_file['cl'])
        tday = _get_data(index, mat_file['tday'])

        for ftime, p in zip(tday, cl):
            event = {
                'dt': _parse_datetime(ftime),
                'sid': sym,
                'price': p,
                'volume': 1e9,
                }
            yield event

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
