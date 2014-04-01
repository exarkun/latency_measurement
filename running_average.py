if __name__ == '__main__':
    import running_average
    raise SystemExit(running_average.main())

from sys import argv, stdin

from json import loads, dumps

from twisted.python.usage import UsageError, Options

class RunningAverageOptions(Options):
    optParameters = [
        ('window', 'w', 60, 'amount of time over which to average (seconds)', float),
        ]



class Averager(object):

    @property
    def _earliest(self):
        return self._timestamps[0]

    def __init__(self, window):
        self.window = window
        self._samples = []
        self._timestamps = []


    def add(self, when, sample):
        # Append first so there's always an earliest sample.
        self._timestamps.append(when)
        self._samples.append(sample)

        interval = when - self._earliest
        if interval > self.window:
            del self._samples[0]
            del self._timestamps[0]

        return sum(self._samples) / len(self._samples)



def main():
    options = RunningAverageOptions()
    try:
        options.parseOptions(argv[1:])
    except UsageError as e:
        raise SystemExit(str(e))

    averager = Averager(options["window"])

    for line in stdin:
        sample = loads(line)
        timestamp = sample["timestamp"]
        print dumps(dict(timestamp=timestamp, interval=averager.add(timestamp, sample["interval"])))
