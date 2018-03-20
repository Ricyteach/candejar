# -*- coding: utf-8 -*-

"""CID line module for working with individual lines of a .cid file."""
import re
from dataclasses import make_dataclass, dataclass, field, asdict
from . import CIDError
from .cidfield import make_field_obj


class LineError(CIDError):
    pass


PREFIX_TEMPLATE = '{: >25s}!!'


@dataclass
class CidLine:
    def __format__(self, format_spec: str) -> str:
        if format_spec:
            if format_spec.startswith('cid'):
                # prefix
                result_list = ['' if 'np' in format_spec else self.prefix]
                # "L" or " " for line types C3 C4 C5 D1
                try:
                    result_list.append({
                                           self.start == 28 and "L" not in format_spec: "",
                                           self.start == 27: " ",
                                           self.start == 27 and "L" in format_spec: "L",
                                       }[True])
                except KeyError:
                    if self.start in (27,28):
                        raise LineError("unsupported format string passed to {type(self).__name__}.__format__") from None
                    else:
                        raise LineError("upsupported line start location provided; cid lines start at 27 or 28") from None
                # fields
                try:
                    result_list.append(''.join(self.cidfields[label].format(value) for label,value in asdict(self).items()))
                except CIDError as e:
                    msg = '\n'.join(f"{self.fields[label]!r}:\t{value!r}" for label,value in vars(self).items())
                    raise LineError('\n'+msg) from e
                return ''.join(result_list)
            else:
                raise LineError("unsupported format string passed to {type(self).__name__}.__format__")
        else:
            return super().__format__(format_spec)
    @classmethod
    def parse(cls, s: str) -> "CidLine":
        if s.startswith(cls.prefix):
            s = s[slice(cls._start, None)]
        try:
            return cls(**{k:cls.cidfields[k].parse(v) for k,v in cls._parser.fullmatch(s).groupdict().items()})
        except AttributeError:
            raise ValueError(f'{cls.__name__} failed to parse line:\n{s!r}')


def make_cid_line_cls(name, **definitions):
    """Uses information provided by the ciddefs.yml to create the CidLine child classes."""
    prefix = definitions.pop("prefix")
    # dataclass fields
    fields = [(f_name, type(default), field(default=default)) for f_name,(_, default, *_) in definitions.items()]
    # cid line fields
    cidfields = {f_name:make_field_obj(*dfntn_seq) for f_name,dfntn_seq in definitions.items()}
    parser = re.compile(''.join(f.regex(n) for n, f in cidfields.items()))
    if name in 'C3 C4 C5 D1'.split():
        start = 28
    else:
        start = 27
    return make_dataclass(name, fields, bases=(CidLine,), namespace=dict(prefix=PREFIX_TEMPLATE.format(prefix), _parser=parser,
                                                                         _start=start, cidfields=cidfields))
