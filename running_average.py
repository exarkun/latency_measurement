if __name__ == '__main__':
    import running_average
    raise SystemExit(running_average.main())

from sys import argv, stdin, stderr

from ipaddr import IPNetwork, IPAddress

from twisted.python.usage import UsageError, Options

class RunningAverageOptions(Options):
    optParameters = [
        ('window', 'w', 60, 'amount of time over which to average (seconds)', float),
        ]

    def __init__(self):
        Options.__init__(self)
        self["source-networks"] = []
        self["destination-networks"] = []

    def opt_include_source(self, network):
        self["source-networks"].append((True, IPNetwork(network)))

    def opt_exclude_source(self, network):
        self["source-networks"].append((False, IPNetwork(network)))

    def opt_include_destination(self, network):
        self["destination-networks"].append((True, IPNetwork(network)))

    def opt_exclude_destination(self, network):
        self["destination-networks"].append((False, IPNetwork(network)))


def match(address, networks):
    address = IPAddress(address)
    for (include, network) in networks:
        if address in network:
            return include
    return None


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
        try:
            when, sourceIP, _, destinationIP, _, duration, = line.split()
        except ValueError:
            stderr.write("Bad line: %r\n" % (line,))
        sourceMatch = match(sourceIP, options["source-networks"])
        if sourceMatch is None:
            destinationMatch = match(destinationIP, options["destination-networks"])
            if destinationMatch is None:
                matched = True
            else:
                matched = destinationMatch
        else:
            matched = sourceMatch

        if matched:
            when = float(when)
            duration = float(duration)
            print when, averager.add(when, duration)
