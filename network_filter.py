if __name__ == '__main__':
    import network_filter
    raise SystemExit(network_filter.main())

from json import loads

from sys import argv, stdin, stderr

from ipaddr import IPNetwork, IPAddress

from twisted.python.usage import UsageError, Options

class NetworkFilterOptions(Options):
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



def main():
    options = NetworkFilterOptions()
    try:
        options.parseOptions(argv[1:])
    except UsageError as e:
        raise SystemExit(str(e))

    for line in stdin:
        try:
            sample = loads(line)
        except ValueError:
            stderr.write("Bad line: %r\n" % (line,))

        sourceMatch = match(sample["source_ip"], options["source-networks"])
        if sourceMatch is None:
            destinationMatch = match(sample["destination_ip"], options["destination-networks"])
            if destinationMatch is None:
                matched = True
            else:
                matched = destinationMatch
        else:
            matched = sourceMatch

        if matched:
            print line,
