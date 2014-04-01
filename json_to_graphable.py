from datetime import datetime
from json import loads
from sys import stdin

from pytz import utc

for line in stdin:
    event = loads(line)
    when = datetime.fromtimestamp(event["timestamp"], utc)
    print when.isoformat(), event["interval"]

