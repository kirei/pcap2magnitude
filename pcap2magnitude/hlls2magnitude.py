"""Calculate DNS Magnitude data from HLLs"""

import argparse
import json
import logging
import math
from collections import defaultdict

import cbor2

from .hll import HyperLogLog, HyperLogLogUnion


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="HLLs to DNS Magnitude")

    parser.add_argument("--output", metavar="filename", help="DNS Magnitude report output")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging")
    parser.add_argument("hlls", metavar="filename", nargs="+", help="HLL files")

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

    magnitudes = {}
    total_unique_clients = all_clients.cardinality()

    for domain in all_domains:
        domain_unique_clients = all_domains[domain].cardinality()
        logging.debug("%d unique clients for %s", domain_unique_clients, domain)
        if m := round((math.log(domain_unique_clients) / math.log(total_unique_clients)) * 10, 3):
            magnitudes[domain] = {"magnitude": m, "clients": int(domain_unique_clients)}

    res = {
        "clients": int(total_unique_clients),
        "domains": magnitudes,
    }

    if args.output:
        with open(args.output, "w") as fp:
            json.dump(res, fp)
        logging.info("Wrote JSON report to %s", args.output)
    else:
        print(json.dumps(res, indent=4))


if __name__ == "__main__":
    main()
