all: hlls sets mag

hlls:
	for file in *.pcap; do uv run pcap2hlls --labels 1 --output `basename $$file .pcap`-hll.cbor $$file; done

sets:
	for file in *.pcap; do uv run pcap2sets --labels 1 --output `basename $$file .pcap`-set.json $$file; done
	for file in *.pcap; do uv run pcap2sets --labels 1 --output `basename $$file .pcap`-set.cbor $$file; done

mag: mag-hll mag-set

mag-hll:
	uv run hlls2magnitude *-hll.cbor

mag-set:
	uv run sets2magnitude *-set.cbor

lint:
	uv run ruff check

clean:
	rm -f *.cbor *.json
