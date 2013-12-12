import datetime
import time
from datetime import datetime
import logging
import functools


logger = logging.getLogger(__name__)

def time2secs(time):
    return time.hour*3600+time.minute*60+time.second

def secs2time(secs):
    return datetime.time(secs // 3600, (secs % 3600) // 60, secs % 60)

def datetime2ts(datetime_obj):
    return int(time.mktime(datetime_obj.timetuple())) if datetime_obj is not None else None

def ts2datetime(ts):
    return datetime.fromtimestamp(ts) if ts is not None else None

def floor(datetime):
    return datetime.replace(hour=0,minute=0,second=0,microsecond=0)

#timedelta.total_seconds() - new in version 2.7.
def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def timeit(method):
    @functools.wraps(method)
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        logging.debug('%r finished in %2.3f sec' % (method.__name__, te-ts))
        return result
    return timed
