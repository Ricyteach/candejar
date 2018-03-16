# -*- coding: utf-8 -*-

"""CID line module for working with individual lines of a .cid file."""

import re
from dataclasses import make_dataclass, dataclass, field
from .cidfield import make_field_obj


PREFIX_TEMPLATE = '{: >25s}!!'


@dataclass
class CidLine:
    def __init_subclass__(cls, line_def, **kwargs):
        """Use information provided by the line_def object to create the class mamber variables."""
        # defin cid line prefix, e.g.:                      A-1!!
        cls.prefix = PREFIX_TEMPLATE.format(line_def.prefix)
        # all linedef members assumed to be fields, other than name, prefix and _cid_class
        cls.fields = {k:v for k,v in vars(line_def).items() if k not in ('name', 'prefix','_cid_class')}
        cls.parser = re.compile(''.join(f.regex(n) for n,f in cls.fields.items()))
        if line_def.name in 'C3 C4 C5 D1'.split():
            cls.last = '{}'
            prefix_ignore = 28
        else:
            cls.last = ''
            prefix_ignore = 27
        cls.line_slice = slice(prefix_ignore, None)
        super().__init_subclass__(**kwargs)
    def __format__(self, format_spec):
        return NotImplemented
    def parse(self, s):
        return NotImplemented


def make_cid_line_cls(name, **definitions):
    prefix = definitions.pop("prefix")
    fields = [(f_name, type(default), field(default=default)) for f_name,(_, default, *_) in definitions.items()]
    fieldobjs = {n:make_field_obj(dfntn_seq) for n,dfntn_seq in definitions.items()}
    parser = re.compile(''.join(f.regex(n) for n, f in fieldobjs.items()))
    if name in 'C3 C4 C5 D1'.split():
        last = '{}'
        prefix_ignore = 28
    else:
        last = ''
        prefix_ignore = 27
    line_slice = slice(prefix_ignore, None)
    return make_dataclass(name, fields, bases=(CidLine,), namespace=dict(prefix=PREFIX_TEMPLATE.format(prefix),
                                                                         _parser=parser, last = last,
                                                                         line_slice = line_slice))
