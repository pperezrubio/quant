import os
import re

import numpy as np
import pandas as pd

from zipline.gens.utils import hash_args
from zipline.sources.data_source import DataSource

from google_minute import load_raw_dataframe

class TempCSVDataSource(DataSource):
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

    def _sym_to_df(self, sym):
        file_name = filter(lambda x: re.match(re.compile(sym), x), os.listdir('.'))
        df = load_raw_dataframe(file_name[0])
        return df

    def _df_within_start_end(self, df):
        # may need pytz here
        df['dt_dt'] = map(lambda x: x.to_datetime(), df.index)
        idx = (df['dt_dt'] > self.start) & (df['dt_dt'] < self.end)
        return df[idx]

    def raw_data_gen(self):
        syms = ['PEP', 'KO']
        arr = map(self._sym_to_df, syms)
        df = pd.concat(arr, axis=1, keys=syms)

        df_filtered = self._df_within_start_end(df)

        for index, row in df_filtered.iterrows():
            for sym in syms:
                event = {
                    'dt': index,
                    'sid': sym,
                    'price': row[sym]['CLOSE'],
                    'volume': 1e9,
                    #'volume': row[sym]['VOLUME'],
                    }
                yield event

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
