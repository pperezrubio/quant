from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import create_simulation_parameters

from datetime import datetime
import pytz

import numpy as np

from csv_file_datasource import TempCSVDataSource

def initialize(context):
    pass

def handle_data(context, data):
    context.order_target('KO', 1)
    context.order_target('PEP', 1)

    context.record(
        ko=data['KO'].price,
        pep=data['PEP'].price
        )

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
    print results # only daily_stats is supported by default Algo class
