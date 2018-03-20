# -*- coding: utf-8 -*-

"""CID line field module for working with individual fields in lines of a .cid file."""
from . import CIDError
from dataclasses import InitVar, field, dataclass
from enum import Enum
from typing import TypeVar, Any, Optional, Union, ClassVar


PRECISION = 2  # for float field objects only


class FieldError(CIDError):
    pass

class Align(Enum):
    LEFT, Left, left = ('<',)*3
    RIGHT, Right, right = ('>',)*3
    #CENTER, Center, center = ('^',)*3
    #FILL, Fill, fill = ('=',)*3
    #BLANK, Blank, blank = ('',)*3

ALIGN_SPEC_DEFAULT = {str: Align.left, int: Align.right, float: Align.right}
TYPE_SPEC_DEFAULT = {str: 's', int: 'd', float: 'f'}

class PrecisionDesc:
    """Descriptor to manage precision attribute of Field objects."""
    def __get__(self, instance, owner):
        try:
            return instance._precision
        except AttributeError:
            if instance:
                return PRECISION if issubclass(type(instance.default), float) else None
            else:
                return None
    def __set__(self, instance, value):
        if not issubclass(type(instance.default), float) and value is not None:
            raise FieldError(f"A {type(instance).__name__} object containing data of type {type(instance.default).__name__} does not support precision.")
        if value is not None:
            instance._precision = value

FieldType = TypeVar("FieldType")

@dataclass
class Field:
    """Defines the fields that make up each line of a file."""
    width: int  # fixed number of characters for the field
    default: Any  # field value contained by default; ignored if field is flagged as optional
    optional: bool = False  # allows for blank fields
    align: Optional[Union[str,Align]] = None  # defaults to ALIGN_SPEC_DEFAULT[type(default)].value
    precision: Optional[int] = PrecisionDesc()  # used for float fields only; defaults to PRECISION
    type_: InitVar[Optional[str]] = field(default=None)  # "s", "f", or "d"; defaults to TYPE_SPEC_DEFAULT[type(default)]
    fill: ClassVar[str] = field(default=" ", init=False)  # character used to fill empty space in field
    def __post_init__(self, type_) -> None:
        try:
            if self.align is None:
                self.align = ALIGN_SPEC_DEFAULT[type(self.default)].value
            if isinstance(self.align,Align):
                self.align = self.align.value
            if type_ is None:
                self.type_ = TYPE_SPEC_DEFAULT[type(self.default)]
            else:
                self.type_ = type_
        except KeyError:
            raise FieldError(f"No default settings available for field of type {type(self.default).__name__}")
    def parse(self, s: Optional[str]) -> FieldType:
        try:
            return type(self.default)(s)
        except Exception as e:
            try:
                if self.optional and (s is None or s.strip() == ""):
                    return self.default
            except:
                raise e
    @property
    def spec(self) -> str:
        precision = f".{self.precision}" if self.precision is not None else ""
        return f"{self.fill}{self.align}{self.width}{precision}{self.type_}"
    @property
    def blank_spec(self) -> str:
        return f"{self.fill}{self.align}{self.width}"
    def regex(self, name: str) -> str:
        qmark = {True:"?", False:""}[self.optional]
        restr = f"(?P<{name}>.{{{self.width}}}){qmark}"
        return restr
    def format(self, value: Optional[FieldType] = None) -> str:
        if self.optional and (value == self.default or value is None):
            return format('', self.blank_spec)
        try:
            return format(value, self.spec)
        except TypeError as e:
            raise FieldError(f"FieldError occurred when formatting:\n\tOBJ: {self!r}\n\tSPEC: {self.spec!r}") from e

def make_field_obj(*defntn_seq):
    """Placeholder function for now."""
    return Field(*defntn_seq)
