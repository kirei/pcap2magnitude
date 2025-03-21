from ipaddress import IPv4Address, IPv6Address, ip_address
from pathlib import Path

from scapy.all import DNSQR, IP, IPv6
from scapy.utils import rdpcap


def minimize_address(ip: IPv4Address | IPv6Address) -> IPv4Address | IPv6Address:
    """Minimize address to /24 or /48"""
    if isinstance(ip, IPv4Address):
        return IPv4Address(ip.packed[0:3] + b"\0")
    else:
        return IPv6Address(ip.packed[0:6] + 10 * b"\0")


def truncate_domain(domain: str, labels: int) -> str:
    """Truncate domain (with trailing dot) to at most N labels"""
    return ".".join(domain.split(".")[-(labels + 1) :])


def pcap2queries(filename: Path, labels: int | None = None):
    """Read DNS packets from filename and yield minimize client address and domain"""

    for packet in rdpcap(filename):
        if packet.haslayer(DNSQR):
            sender = packet[IPv6].src if IPv6 in packet else packet[IP].src
            client = str(minimize_address(ip_address(sender.lower())))

            domain = packet[DNSQR].qname.decode().lower()
            if labels:
                domain = truncate_domain(domain, labels)

            yield client, domain.rstrip(".")
