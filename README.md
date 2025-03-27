# DNS Magnitude Tools

This repository contains sample code for calculating DNS Magnitude from PCAPs.

Data is stored as CBOR encoded HLLs using the Apache Datasketches HLL implementation.


## Usage

### Convert PCAPs to HLLs

    uv run pcap2hlls --labels 1 --top 1000 --output hll1.cbor test1.pcap
    uv run pcap2hlls --labels 1 --top 1000 --output hll2.cbor test2.pcap

### Merge HLLs

    uv run merge_magnitude_hlls --output merged.cbor hll*.cbor

### Create report from HLLs

    uv run hlls2magnitude --output report.json merged.cbor
