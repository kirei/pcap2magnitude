"""Create SETs from PCAPs"""

import argparse
import json
import logging
import time
from collections import defaultdict
from ipaddress import IPv4Address, IPv6Address, ip_address

import cbor2
from scapy.all import DNSQR, IP, IPv6
from scapy.utils import rdpcap


def minimize_address(ip: IPv4Address | IPv6Address) -> IPv4Address | IPv6Address:
    if isinstance(ip, IPv4Address):
        return IPv4Address(ip.packed[0:3] + b"\0")
    else:
        return IPv6Address(ip.packed[0:6] + 10 * b"\0")


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="PCAP to SETs")

    parser.add_argument(
        "--output",
        metavar="filename",
        help="SETs collection output",
    )
    parser.add_argument("--labels", type=int, help="Number of labels to count")
    parser.add_argument("--debug", action="store_true", help="Enable debugging")
    parser.add_argument("pcaps", metavar="filename", nargs="+", help="PCAP files")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    clients: set[str] = set()
    domains: dict[str, set[str]] = defaultdict(set)

    for filename in args.pcaps:
        t1 = time.perf_counter()
        packets = rdpcap(filename)

        logging.info("Read %d packets from %s", len(packets), filename)

        queries_count = 0
        for packet in packets:
            if packet.haslayer(DNSQR):
                queries_count += 1

                sender = packet[IPv6].src if IPv6 in packet else packet[IP].src
                client = str(minimize_address(ip_address(sender.lower())))

                domain = packet[DNSQR].qname.decode().lower().rstrip(".")
                if args.labels:
                    domain = domain.split(".")[-args.labels]

                logging.debug("%s %s", domain, client)

                clients.add(client)
                domains[domain].add(client)

        t2 = time.perf_counter()
        logging.info("Processed %d queries from %s in %.3f seconds", queries_count, filename, t2 - t1)

    logging.info("Observed domains: %d", len(domains))
    logging.info("Observed clients: %d", len(clients))

    if args.output:
        res = {
            "clients": list(clients),
            "domains": {domain: list(clients) for domain, clients in domains.items()},
        }
        if args.output.endswith(".json"):
            with open(args.output, "w") as fp:
                json.dump(res, fp, separators=(",", ":"))
                logging.info("Wrote %d bytes as JSON to %s ", fp.tell(), args.output)
        else:
            with open(args.output, "wb") as fp:
                cbor2.dump(res, fp)
                logging.info("Wrote %d bytes as CBOR to %s", fp.tell(), args.output)


if __name__ == "__main__":
    main()
