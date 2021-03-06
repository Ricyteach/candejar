# -*- coding: utf-8 -*-

"""CID line module for working with individual lines of a .cid file."""

from __future__ import annotations
import re
from dataclasses import make_dataclass, dataclass, field, asdict
from typing import Optional, Type, Pattern, TypeVar

from .exc import CIDError, LineError, LineParseError
from .cidfield import make_field_obj


PREFIX_TEMPLATE = "{: >25s}!!"
START_COLUMN = {n:28 for n in 'C3 C4 C5 D1'.split()}
START_COLUMN["Stop"] = 0


class Start:
    """The starting position for parsing a CID file line with a prefix."""
    def __get__(self, instance: Optional[CidLine], owner: Type[CidLine]) -> int:
        return START_COLUMN.get(owner.__name__, 27)


class Parser:
    """The compiled regex pattern parser created by combining `cidfield.Field` regex patterns."""
    def __get__(self, instance: Optional[CidLine], owner: Type[CidLine]) -> Pattern[str]:
        try:
            p = owner._parser
        except AttributeError:
            parser_str = "".join(f.regex(n) for n, f in owner.cidfields.items())
            if parser_str.endswith("?"):
                # optional ending parser; tweak so captures zero up to the field with of characters and ignores trailing spaces
                m = re.fullmatch(r"(.*?)(\d+)$", parser_str[:-3])
                first, second = m.groups()
                parser_str = first + "," + second + "}) *"
            else:
                # required ending parser; tweak so captures correct # of characters and ignores trailing spaces
                parser_str = parser_str + " *"
            p = owner._parser = re.compile(parser_str)
        return p


CidLineChild = TypeVar("CidLineChild", bound="CidLine")


@dataclass
class CidLine:
    """Parent class for all readable/writable CID file lines."""
    def __format__(self, format_spec: str) -> str:
        if format_spec:
            if format_spec.startswith("cid"):
                # prefix
                result_list = ["" if "np" in format_spec else self.prefix]
                # "L" or " " for line types C3 C4 C5 D1
                try:
                    result_list.append({
                                           self.start_ == 0 and "L" not in format_spec: "",
                                           self.start_ == 27 and "L" not in format_spec: "",
                                           self.start_ == 28: " ",
                                           self.start_ == 28 and "L" in format_spec: "L",
                                       }[True])
                except KeyError:
                    if self.start_ in (27,28):
                        raise LineError(f"unsupported format string passed to {type(self).__name__}.__format__") from None
                    else:
                        raise LineError(f"upsupported line start location provided for {type(self).__name__} object; "
                                        f"cid lines start at 27 or 28, not {self.start_!s}") from None
                # fields
                try:
                    result_list.append(''.join(self.cidfields[label].format(value) for label,value in asdict(self).items()))
                except CIDError as e:
                    msg = '\n'.join(f"{self.cidfields[label]!r}:\t{value!r}" for label,value in vars(self).items())
                    raise LineError('\n'+msg) from e
                return ''.join(result_list)
            else:
                raise LineError("unsupported format string passed to {type(self).__name__}.__format__")
        else:
            return super().__format__(format_spec)
    @classmethod
    def parse(cls: Type[CidLineChild], line: str) -> CidLineChild:
        if line.startswith(cls.prefix):
            line = line[slice(cls.start_, None)]
        try:
            return cls(**{k:cls.cidfields[k].parse(v) for k,v in cls.parser.fullmatch(line).groupdict().items()})
        except AttributeError as e:
            raise LineParseError(f"{cls.__name__} failed:\n{line!r}") from e


def make_cid_line_cls(name_, **definitions):
    """Uses information provided by the ciddefs.yml to create the CidLine child classes."""
    prefix = definitions.pop("prefix")
    # dataclass fields
    fields = [(f_name, type(default), field(default=default)) for f_name,(_, default, *_) in definitions.items()]
    # cid line fields
    cidfields = {f_name:make_field_obj(*dfntn_seq) for f_name,dfntn_seq in definitions.items()}

    return make_dataclass(name_, fields, bases=(CidLine,), namespace=dict(prefix=PREFIX_TEMPLATE.format(prefix)
                                                                            if prefix is not None else "",
                                                                          parser=Parser(), start_=Start(), cidfields=cidfields))
