"""Merge DNS Magnitude HLLs"""

import argparse
import logging
from collections import defaultdict

import cbor2

from .hll import HyperLogLog, HyperLogLogUnion


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="Merge DNS Magnitude HLLs")

    parser.add_argument("--output", metavar="filename", required=True, help="HLL output file")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging")
    parser.add_argument("hlls", metavar="filename", nargs="+", help="HLL input files")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    all_clients: HyperLogLogUnion = HyperLogLogUnion()
    all_domains: dict[str, HyperLogLogUnion] = defaultdict(HyperLogLogUnion)

    for filename in args.hlls:
        with open(filename, "rb") as fp:
            dataset = cbor2.load(fp)
            logging.info("Read %d bytes from %s", fp.tell(), filename)

        dataset_clients = HyperLogLog.deserialize(dataset["clients"])
        all_clients.merge(dataset_clients)

        for domain, hll_bytes in dataset["domains"].items():
            hll = HyperLogLog.deserialize(hll_bytes)
            all_domains[domain].merge(hll)

    res = {
        "clients": all_clients.serialize(),
        "domains": {domain: clients.serialize() for domain, clients in all_domains.items()},
    }

    with open(args.output, "wb") as fp:
        cbor2.dump(res, fp)
        logging.info("Wrote %d bytes as CBOR to %s", fp.tell(), args.output)


if __name__ == "__main__":
    main()
