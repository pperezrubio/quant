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

    def raw_data_gen(self):
        #CONTINUE: need to yield sids per index
        syms = ['PEP', 'KO']
        arr = map(self._sym_to_df, syms)
        df = pd.concat(arr, axis=1, keys=syms)
        for index, row in df.iterrows():
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
