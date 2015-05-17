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

    def raw_data_gen(self):
        syms = ['KO', 'PEP']
        for sym in syms:
            file_name = filter(lambda x: re.match(re.compile(sym), x), os.listdir('.'))
            df = load_raw_dataframe(file_name[0])
            for index, row in df.iterrows():
                event = {
                    'dt': index,
                    'sid': sym,
                    'price': row['CLOSE'],
                    'volume': row['VOLUME'],
                    }
                yield event

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
