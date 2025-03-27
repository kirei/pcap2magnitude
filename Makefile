all: hlls mag

hlls:
	for file in *.pcap; do uv run pcap2hlls --labels 1 --output `basename $$file .pcap`-hll.cbor $$file; done

mag:
	uv run merge_magnitude_hlls --output merged.cbor *-hll.cbor
	uv run hlls2magnitude merged.cbor

reformat:
	uv run ruff check --select I --fix
	uv run ruff format

lint:
	uv run ruff check

clean:
	rm -f *.cbor
