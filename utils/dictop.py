from typing import Dict, Hashable

__all__ = [
    "join_map",
]


def join_map(d: Dict[Hashable, float], d2: Dict[Hashable, float]) -> None:
    for k, v in d2.items():
        if k in d.keys():
            d[k] += v
        else:
            d[k] = v
