"""Create HHLs from PCAPs"""

import argparse
import logging
import time
from collections import defaultdict

import cbor2

from .hll import HyperLogLog
from .pcap import pcap2queries


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="PCAP to HLLs")

    parser.add_argument("--output", metavar="filename", help="HLLs output")
    parser.add_argument("--labels", type=int, help="Number of labels to count")
    parser.add_argument("--debug", action="store_true", help="Enable debugging")
    parser.add_argument("pcaps", metavar="filename", nargs="+", help="PCAP files")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    clients: HyperLogLog = HyperLogLog()
    domains: dict[str, HyperLogLog] = defaultdict(HyperLogLog)

    for filename in args.pcaps:
        queries_count = 0
        t1 = time.perf_counter()

        for client, domain in pcap2queries(filename, labels=args.labels):
            logging.debug("%s %s", domain, client)
            clients.update(client)
            domains[domain].update(client)
            queries_count += 1

        t2 = time.perf_counter()
        logging.info("Processed %d queries from %s in %.3f seconds", queries_count, filename, t2 - t1)

    logging.info("Observed domains: %d", len(domains))
    logging.info("Observed clients: %d", clients.cardinality())

    if args.output:
        res = {
            "clients": clients.serialize(),
            "domains": {domain: clients.serialize() for domain, clients in domains.items()},
        }
        with open(args.output, "wb") as fp:
            cbor2.dump(res, fp)
            logging.info("Wrote %d bytes as CBOR to %s", fp.tell(), args.output)


if __name__ == "__main__":
    main()
