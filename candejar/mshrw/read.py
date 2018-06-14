# -*- coding: utf-8 -*-

"""Contains the procedure for reading a .msh file to an object."""

from typing import Iterable, Callable, Any, Dict, TypeVar, Sequence, Iterator
import itertools

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
    if isinstance(lines, str) or not isinstance(lines, Iterable):
        raise exc.MSHRWError(f"lines must be an iterable, not {type(lines).__qualname__}")
    iter_line_strs = iter(line.strip() for line in lines)
    nodes, elements, boundaries = get_all(iter_line_strs)
    # handle 2D elements
    e: dict
    for e in elements:
        for x in "kl":
            e[x] = e.get(x, 0)
    # check for leftover non-empty lines
    leftovers = [line.strip() for line in iter_line_strs]
    if any((leftover and not leftover.startswith("#")) for leftover in leftovers):
        raise exc.MSHLineProcessingError(
            f"There appear to be {len(leftovers)!s} extraneous data lines at the end of the file.")
    for attr, seq in zip("nodes elements boundaries".split(), (nodes, elements, boundaries)):
        setattr(msh, attr, list(seq))
    return msh


def get_all(ilines):
    nodes_elements_boundaries = []
    for parser in (parse_node, parse_element, parse_boundary):
        try:
            x = get_items(ilines, parser)
        except exc.MSHLineProcessingError as e:
            try:
                nitems = e.total
                line = e.line
            except AttributeError:
                raise e
            else:
                ilines = itertools.chain([str(nitems), line], ilines)
                x = []
        except StopIteration:
            x = []
        nodes_elements_boundaries.append(x)
    return nodes_elements_boundaries


def get_items(ilines, parser):
    while True:
        nitems = next(parse_lines(ilines, parse_total))["num"]
        if nitems:
            break
    item_tuples = []
    try:
        for n, i in zip(range(1, nitems + 1), parse_lines(ilines, parser)):
            item_tuples.append((n, i))
    except exc.MSHLineProcessingError as e:
        if len(item_tuples) == 0:
            e.total = nitems
        raise e
    _, items = zip(*item_tuples)
    return items


def parse_lines(ilines: Iterator[str], parser: Callable[[str], Dict[str, T]]) -> Iterator[Dict[str, T]]:
    if parser is parse_element:
        o_parser = parse_element_2d
    for line in ilines:
        if line and not line.startswith("#"):
            try:
                yield parser(line)
            except exc.MSHLineProcessingError as e:
                try:
                    parser, o_parser = o_parser, parser
                except NameError:
                    raise e from None
                else:
                    try:
                        yield parser(line)
                    except exc.MSHLineProcessingError:
                        raise e from None


def parse_line(line: str, field_names: Sequence[str],
               field_converters: Sequence[Callable[[str], T]]) -> Dict[str, T]:
    field_values = line.split()
    field_converters = tuple(field_converters)
    if not len(field_names) == len(field_values) == len(field_converters):
        e = exc.MSHLineProcessingError("line length mismatch occurred during parsing")
        e.line = line
        raise e
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


def parse_element_2d(element_line: str) -> Dict[str, Any]:
    field_names = "num i j".split()
    field_converters = (int,) * 3
    return parse_line(element_line, field_names, field_converters)


def parse_boundary(boundary_line: str) -> Dict[str, Any]:
    field_names = "num b".split()
    field_converters = (int, int)
    return parse_line(boundary_line, field_names, field_converters)
