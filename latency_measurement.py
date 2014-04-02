if __name__ == '__main__':
    import latency_measurement
    raise SystemExit(latency_measurement.main())

from os import fdopen
from time import time
from json import dumps
from socket import AF_PACKET, SOCK_RAW, socket, htons

ETH_P_ALL = 0x0003

from scapy.all import TCP

from zope.interface import implementer

from twisted.python.log import msg, err
from twisted.internet.protocol import AbstractDatagramProtocol
from twisted.pair.raw import IRawDatagramProtocol
from twisted.pair.ethernet import EthernetProtocol
from twisted.pair.ip import IPProtocol

@implementer(IRawDatagramProtocol)
class RawTCPProtocol(AbstractDatagramProtocol):
    def __init__(self, log):
        self._connections = {}
        self._times = []
        self._log = log


    def datagramReceived(self, data, partial, source, dest, *args, **kwargs):
        now = time()

        try:
            tcp = TCP(data)
        except:
            err(None, "scapy failed to parse TCP datagram")
            return

        src = (source, tcp.sport)
        dst = (dest, tcp.dport)
        syn = tcp.flags & 2
        ack = tcp.flags & 16

        if syn and not ack:
            self._connections[src, dst] = now
        elif syn and ack:
            started = self._connections.pop((dst, src), None)
            if started is not None:
                interval = now - started
                self._recordConnection(now, (dst, src), interval)


    def _recordConnection(self, now, ((src_ip, src_port), (dst_ip, dst_port)), interval):
        msg(format="Connection established in %(interval)s seconds", interval=interval)
        self._times.append(interval)
        self._log.write(dumps(dict(
                    timestamp=now, interval=interval,
                    source_ip=src_ip, source_port=src_port,
                    destination_ip=dst_ip, destination_port=dst_port)) + b"\n")
        if len(self._times) % 100 == 0:
            msg(format="Mean connection setup time %(mean)s seconds", mean=sum(self._times) / len(self._times))


def main():
    # Unbuffered mode makes it possible to do things like tail the log and
    # get semi-realtime results.  It should also prevent any lines from
    # being written non-atomically (if partial lines get written there will
    # be some mild corruption in the file).  This depends on the code using
    # self._log writing complete lines, of course.
    log = fdopen(1, "at", 0)
    tcp = RawTCPProtocol(log)

    ipv4 = IPProtocol()
    ipv4.addProto(6, tcp)

    protocol = EthernetProtocol()
    protocol.addProto(0x800, ipv4)

    s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
    while True:
        data = s.recv(2 ** 16)
        protocol.datagramReceived(data)
