from datetime import datetime
from sys import stdin
for line in stdin:
    timestamp, sample = line.split()
    timestamp = float(timestamp)
    when = datetime.utcfromtimestamp(timestamp)
    midnight = when.replace(hour=0, minute=0, second=0, microsecond=0)
    difference = when - midnight
    print difference.total_seconds(), sample

