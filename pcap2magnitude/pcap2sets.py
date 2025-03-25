"""Create SETs from PCAPs"""

import argparse
import json
import logging
import time
from collections import defaultdict

import cbor2

from .pcap import pcap2queries


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="PCAP to SETs")

    parser.add_argument("--output", metavar="filename", help="SETs output")
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
        queries_count = 0
        t1 = time.perf_counter()

        for client, domain in pcap2queries(filename, labels=args.labels):
            logging.debug("%s %s", domain, client)
            clients.add(client)
            domains[domain].add(client)
            queries_count += 1

        t2 = time.perf_counter()
        logging.info(
            "Processed %d queries from %s in %.3f seconds",
            queries_count,
            filename,
            t2 - t1,
        )

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
