# -*- coding: utf-8 -*-

"""Special tools for working with sequence types."""

from typing import TypeVar, Sequence, Callable, Dict, Iterator, List

T = TypeVar("T")
D = TypeVar("D")

def dedupe(seq: Sequence[T]) -> Sequence[T]:
    """Produces a copy  of a sequence with duplicates removed; order is preserved"""
    type_ = type(seq)
    if not isinstance(seq, Sequence):
        raise TypeError(f"{type_.__qualname__!r} object is not dedupe-able")
    seen = set()
    seenadd = seen.add  # optimization
    return type_([x for x in seq if not (x in seen or seenadd(x))])

def nn_mapping(seq: Sequence[T], distance_f: Callable[[T,T], D] = lambda a,b: b-a) -> Iterator[Dict[int,D]]:
    """Yields a mapping of the distance between some indexed item and all the other items in a given sequence for
    nearest neighbor calculation
    """
    for idx,item in enumerate(seq):
        d = dict()
        for neigh_idx,neigh in enumerate(seq):
            if idx == neigh_idx:
                continue
            d[neigh_idx] = distance_f(item, neigh)
        yield d
