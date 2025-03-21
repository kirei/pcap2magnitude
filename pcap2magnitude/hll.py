"""
HLL implemented using Apache Datasketches

https://apache.github.io/datasketches-python
"""

from typing import Self

import datasketches


class HyperLogLog:
    def __init__(self, sketch=None) -> None:
        lgk = 12  # 2^k = 4096 rows in the table
        self.sketch = sketch or datasketches.hll_sketch(lg_k=lgk, tgt_type=datasketches.tgt_hll_type.HLL_8)

    def update(self, datum: str) -> None:
        self.sketch.update(datum)

    def cardinality(self) -> int:
        return self.sketch.get_estimate()

    def serialize(self) -> bytes:
        return self.sketch.serialize_compact()

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        return cls(sketch=datasketches.hll_sketch.deserialize(data))


class HyperLogLogUnion:
    def __init__(self) -> None:
        lg_max_k = 12
        self.sketch = datasketches.hll_union(lg_max_k=lg_max_k)

    def merge(self, hll: HyperLogLog) -> None:
        self.sketch.update(hll.sketch)

    def cardinality(self) -> int:
        return self.sketch.get_estimate()
