import re
from datetime import datetime, timedelta
import time
import pytz
from StringIO import StringIO
# can be refactored using 'from pyswitch import Switch'
def trim_raw(file_path):
    buff = ''
    with open(file_path) as f:
        last_timestamp = None
        for line in f:
            r_header = re.match(r'^COLUMNS=(.+)', line)
            if bool(r_header):
                buff += r_header.group(1) + '\n'
                continue
            if re.compile('^[A-Z]').match(line):
                continue
            r_last_timestamp = re.match(r'^a(\d+),', line)
            if bool(r_last_timestamp):
                f_timestamp = int(r_last_timestamp.group(1))
                last_timestamp = datetime.fromtimestamp(f_timestamp, pytz.utc)
                arr = line.split(',')
                arr[0] = _dt_to_str_timestamp(last_timestamp)
                buff += (',').join(arr)
                continue

            arr = line.split(',')
            d_min = int(arr[0])
            arr[0] = _dt_to_str_timestamp(last_timestamp + timedelta(minutes=d_min))
            buff += (',').join(arr)
    return buff

def _dt_to_str_timestamp(dt):
    return str(int(time.mktime(dt.timetuple())))

def load_raw_dataframe(file_path):
    buff = trim_raw(file_path)
    import pandas as pd
    csv = StringIO(buff)
    df = pd.DataFrame.from_csv(csv)
    df.index = pd.to_datetime(df.index, utc=True, unit='s')
    return df

if __name__ == '__main__':
    example_file = '15-05-13-KO-1'
    test = load_raw_dataframe(example_file)
    print test
    from IPython import embed
    embed()
