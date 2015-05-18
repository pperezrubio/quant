from zipline.api import order_target, record, symbol, history, add_history
from zipline.algorithm import TradingAlgorithm
from zipline.sources.simulated import RandomWalkSource

from datetime import datetime
import pytz

import matplotlib.pyplot as plt
import numpy as np

from csv_file_datasource import TempCSVDataSource


def initialize(context):
    pass

def handle_data(context, data):
    order_target('KO', 100)
    order_target('PEP', 100)

    record(
        ko=data[symbol('KO')].price,
        pep=data['PEP'].price
        )

if __name__ == '__main__':
    start = datetime(2015,5,7,0,0,0,0, pytz.utc)
    end = datetime(2015,5,16,0,0,0,0, pytz.utc)
    data = TempCSVDataSource(stocks=['KO', 'PEP'], start=start, end=end)
    algo = TradingAlgorithm(handle_data=handle_data, initialize=initialize)
    results = algo.run(data)
    from IPython import embed
    embed()
