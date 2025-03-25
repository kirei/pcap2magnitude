# DNS Magnitude Tools

This repository contains sample code for calculating DNS Magnitude from PCAPs.


## Data formats

Two data formats are implemented:

- CBOR encoded HLL using the Apache Datasketches HLL implementation
- CBOR/JSON encoded plain text


## Usage

### Convert PCAPs to CBOR-encoded HLLs

    uv run pcap2hlls --labels 1 --top 1000 --output hll1.cbor test1.pcap
    uv run pcap2hlls --labels 1 --top 1000 --output hll2.cbor test2.pcap

### Merge CBOR-encoded HLLs

    uv run merge_magnitude_hlls --output merged.cbor hll*.cbor

### Create report from CBOR-encoded HLLs

    uv run hlls2magnitude --output report.json merged.cbor
