if __name__ == '__main__':
    import latency_measurement
    raise SystemExit(latency_measurement.main())

from time import time
from socket import AF_PACKET, SOCK_RAW, socket, htons

ETH_P_ALL = 0x0003

from scapy.all import TCP

from zope.interface import implementer

from twisted.python.log import msg
from twisted.internet.protocol import AbstractDatagramProtocol
from twisted.pair.raw import IRawDatagramProtocol
from twisted.pair.ethernet import EthernetProtocol
from twisted.pair.ip import IPProtocol

@implementer(IRawDatagramProtocol)
class RawTCPProtocol(AbstractDatagramProtocol):
    def __init__(self):
        self._connections = {}
        self._times = []
        self._log = open("connection-setup-times.txt", "at")


    def datagramReceived(self, data, partial, source, dest, *args, **kwargs):
        now = time()

        tcp = TCP(data)
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
        self._log.write("%s %s %d %s %s %s\n" % (now, src_ip, src_port, dst_ip, dst_port, interval))
        if len(self._times) % 100 == 0:
            msg(format="Mean connection setup time %(mean)s seconds", mean=sum(self._times) / len(self._times))


def main():
    tcp = RawTCPProtocol()

    ipv4 = IPProtocol()
    ipv4.addProto(6, tcp)

    protocol = EthernetProtocol()
    protocol.addProto(0x800, ipv4)

    s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
    while True:
        data = s.recv(2 ** 16)
        protocol.datagramReceived(data)
