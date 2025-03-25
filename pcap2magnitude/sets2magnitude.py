"""Calculate DNS Magnitude data from SETs"""

import argparse
import json
import logging
import math
from collections import defaultdict

import cbor2


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="HLLs to DNS Magnitude")

    parser.add_argument("--output", metavar="filename", help="DNS Magnitude output")
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Enable debugging"
    )
    parser.add_argument("hlls", metavar="filename", nargs="+", help="HLL files")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    all_clients: set[str] = set()
    all_domains: dict[str, set[str]] = defaultdict(set)

    for filename in args.hlls:
        if filename.endswith(".json"):
            with open(filename) as fp:
                dataset = json.load(fp)
        else:
            with open(filename, "rb") as fp:
                dataset = cbor2.load(fp)

        dataset_clients = set(dataset["clients"])
        all_clients.update(dataset_clients)

        dataset_domains: dict[str, set[str]] = {}
        dataset_domains = set(dataset["domains"])
        for domain, domain_clients in dataset["domains"].items():
            all_domains[domain].update(set(domain_clients))

        logging.info("%s unique clients: %d", filename, len(dataset_clients))
        logging.info("%s unique domains: %d", filename, len(dataset_domains))

    logging.info("Total unique clients: %d", len(all_clients))
    logging.info("Total unique domains: %d", len(all_domains))

    magnitudes = {}
    total_unique_clients = len(all_clients)

    for domain in all_domains:
        domain_unique_clients = len(all_domains[domain])
        logging.debug("%d unique clients for %s", domain_unique_clients, domain)
        if m := round(
            (math.log(domain_unique_clients) / math.log(total_unique_clients)) * 10, 3
        ):
            magnitudes[domain] = {"magnitude": m, "clients": int(domain_unique_clients)}
    res = {"clients": int(total_unique_clients), "domains": magnitudes}

    if args.output:
        with open(args.output) as fp:
            json.dump(res, fp)
    else:
        print(json.dumps(res, indent=4))


if __name__ == "__main__":
    main()
