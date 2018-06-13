# -*- coding: utf-8 -*-

"""Contains the procedure for reading a .msh file to an object."""

from typing import Iterable, Callable, Any, Dict, TypeVar, Sequence, Iterator

from . import MshObj, exc

T = TypeVar("T")


def line_strings(msh: MshObj, lines: Iterable[str]) -> MshObj:
    """Reads a .msh formatted file (example below) into a msh object.

    Example .msh format (commented and empty lines are optional/skipped):

        # nodes
        2
        1    0.0    0.0
        2    1.0    1.0
        # elements
        1    1    2    0    0
        # boundaries
        1    1

    """
    iter_line_strs = iter(line.strip() for line in lines)
    nnodes = next(parse_lines(iter_line_strs, parse_total))["num"]
    nodes = [node for _, node in zip(range(nnodes), parse_lines(iter_line_strs, parse_node))]
    nelements = next(parse_lines(iter_line_strs, parse_total))["num"]
    elements = [element for _, element in zip(range(nelements), parse_lines(iter_line_strs, parse_element))]
    nboundaries = next(parse_lines(iter_line_strs, parse_total))["num"]
    boundaries = [boundary for _, boundary in zip(range(nboundaries), parse_lines(iter_line_strs, parse_boundary))]
    # check for leftover non-empty lines
    leftovers = [line.strip() for line in iter_line_strs]
    if any((leftover and not leftover.startswith("#")) for leftover in leftovers):
        raise exc.MSHLineProcessingError(
            f"There appear to be {len(leftovers)!s} extraneous data lines at the end of the file.")
    for attr, seq in zip("nodes elements boundaries".split(), (nodes, elements, boundaries)):
        setattr(msh, attr, seq)
    return msh


def parse_lines(ilines: Iterator[str], parser: Callable[[str], Dict[str, T]]) -> Iterator[Dict[str, T]]:
    for line in ilines:
        if line and not line.startswith("#"):
            yield parser(line)


def parse_line(line: str, field_names: Sequence[str],
               field_converters: Sequence[Callable[[str], T]]) -> Dict[str, T]:
    field_values = line.split()
    field_converters = tuple(field_converters)
    if not len(field_names) == len(field_values) == len(field_converters):
        raise exc.MSHLineProcessingError("line length mismatch occurred during parsing")
    d = dict((name, converter(value)) for name, value, converter in zip(field_names, field_values, field_converters))
    return d


def parse_total(total_line: str) -> Dict[str, Any]:
    field_names = "num".split()
    field_converters = (int,)
    return parse_line(total_line, field_names, field_converters)


def parse_node(node_line: str) -> Dict[str, Any]:
    field_names = "num x y".split()
    field_converters = (int, float, float)
    return parse_line(node_line, field_names, field_converters)


def parse_element(element_line: str) -> Dict[str, Any]:
    field_names = "num i j k l".split()
    field_converters = (int,) * 5
    return parse_line(element_line, field_names, field_converters)


def parse_boundary(boundary_line: str) -> Dict[str, Any]:
    field_names = "b".split()
    field_converters = (int,)
    return parse_line(boundary_line, field_names, field_converters)
