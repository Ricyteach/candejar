# -*- coding: utf-8 -*-

"""Special tools for working with sequence types."""

from typing import TypeVar, Sequence, Callable, Dict, Iterator, Generator, Tuple, Iterable

import itertools

T = TypeVar("T")
S = TypeVar("S")
D = TypeVar("D")


def orient_seq(seq: Sequence[T], idx_order: Iterable[int]) -> Sequence[T]:
    pass


# default distance function
DISTANCE_F = lambda a,b: b-a


def dedupe(seq: Sequence[S]) -> Sequence[S]:
    """Produces a copy  of a sequence with duplicates removed; order is preserved"""
    type_ = type(seq)
    if not isinstance(seq, Sequence):
        raise TypeError(f"{type_.__qualname__!r} object is not dedupe-able")
    seen = set()
    seenadd = seen.add  # optimization
    return type_([x for x in seq if not (x in seen or seenadd(x))])


def iter_distances(item: T, seq: Sequence[S], distance_f: Callable[[T,S], D] = DISTANCE_F) -> Iterator[D]:
    """Yields the distances between some item and sequence members for nearest neighbor calculation"""
    yield from map(distance_f, itertools.repeat(item), seq)


def nn_mapping(seq: Sequence[T],
               distance_f: Callable[[T,T], D] = DISTANCE_F,
               *, sort = False) -> Generator[Dict[int,D], None, Dict[int,Dict[int,D]]]:
    """Yields a mapping of the (optionally sorted) distances between the items in a given sequence for nearest
    neighbor calculation
    """
    dcts = {}
    for idx,item in enumerate(seq):
        dct = dict()
        for neigh_idx,neigh in enumerate(seq):
            if idx == neigh_idx:
                # don't perform distance function for same item
                continue
            if neigh_idx > idx:
                # new distance
                d = distance_f(item, neigh)
            else:
                # already seen
                d = dcts[neigh_idx][idx]
            dct[neigh_idx] = d
        if sort:
            sorted_dct = {k:dct[k] for k in sorted(dct.keys(),key=dct.__getitem__)}
            dcts[idx] = sorted_dct
            yield sorted_dct
        else:
            yield dct
    return dcts

def iter_nn(item: T, seq: Sequence[S], distance_f: Callable[[T,S], D] = DISTANCE_F) -> Iterator[Tuple[S,D]]:
    """Yields tuples in the form of (member,distance) in order of increasing distance

     The member is the sequence member and distance is the distance from the member to item
     """
    dct = dict(enumerate(iter_distances(item, seq, distance_f)))
    sorted_dct = {idx: dct[idx] for idx in sorted(dct.keys(), key=dct.__getitem__)}
    yield from ((seq[idx],d) for idx,d in sorted_dct.items())
