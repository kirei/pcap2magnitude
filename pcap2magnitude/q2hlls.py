"""Create HHLs from PCAPs"""

import argparse
import logging
import time
from collections import defaultdict

import cbor2

from .hll import HyperLogLog, get_top_n


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="Queries to HLLs")

    parser.add_argument("--output", metavar="filename", help="HLLs output")
    parser.add_argument("--top", type=int, help="Include only top-n domains")
    parser.add_argument("--debug", action="store_true", help="Enable debugging")
    parser.add_argument("input", metavar="filename", nargs="+", help="Input files")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    clients: HyperLogLog = HyperLogLog()
    domains: dict[str, HyperLogLog] = defaultdict(HyperLogLog)

    for filename in args.input:
        with open(filename) as fp:
            clients_count = 0
            t1 = time.perf_counter()
            for line in fp.readlines():
                domain, client, _ = line.split()
                clients.update(client)
                domains[domain].update(client)
                clients_count += 1
            t2 = time.perf_counter()
            logging.info(
                "Processed %d clients from %s in %.3f seconds",
                clients_count,
                filename,
                t2 - t1,
            )

    logging.info("Observed domains: %d", len(domains))
    logging.info("Observed clients: %d", clients.cardinality())

    if args.top:
        domains = get_top_n(domains, args.top)

    if args.output:
        res = {
            "clients": clients.serialize(),
            "domains": {
                domain: clients.serialize() for domain, clients in domains.items()
            },
        }
        with open(args.output, "wb") as fp:
            cbor2.dump(res, fp)
            logging.info("Wrote %d bytes as CBOR to %s", fp.tell(), args.output)


if __name__ == "__main__":
    main()
