# -*- coding: utf-8 -*-

"""Module for useful decorators."""

from inspect import getfullargspec
from functools import wraps
from typing import Callable, Generator, Any, Optional, Union, Type, Iterable, Counter

_NO_CALLABLE_TYPE = type("_NO_CALLABLE_TYPE", (), {})
_NO_CALLABLE = _NO_CALLABLE_TYPE()

class CaseInsensitiveDecoratorError(Exception):
    pass

AnyCallable = Callable[...,Any]

def case_insensitive_arguments(callable: Union[_NO_CALLABLE_TYPE, AnyCallable] = _NO_CALLABLE,
                               *, insensitive_arg_names: Optional[Iterable[str]] = None):
    """Makes keyword arguments case-insensitive. The argument name list will be stringified.

    NOTE: The case_insensitive_arguments decorator must be called even if there are no arguments provided. If it is
    desired to use a stringified object of type `type` as a specified argument name, use ignore_error=True.
    """
    # check for accidental usage as @case_insensitive_arguments
    if insensitive_arg_names is None:
        insensitive_arg_names = []
    insensitive_arg_names_lower = [str(n).lower() for n in insensitive_arg_names]
    def wrapped_callable(callable):
        # get all names arguments in callable signature
        arg_names, _, _, _, kwonlyarg_names, _, _ = getfullargspec(callable)
        callable_arg_names = arg_names + kwonlyarg_names
        if isinstance(callable, type):
            # get rid of first bound argument
            callable_arg_names = callable_arg_names[1:]
        # associate lowercase versions with actual argument names
        callable_arg_names_dict = {n.lower():n for n in callable_arg_names}
        # handle insensitive_arg_names decorator argument
        if insensitive_arg_names_lower:
            # remove names not interested in
            insensitive_arg_names_dict = {k:v for k,v in callable_arg_names_dict.items() if k in insensitive_arg_names_lower}
        else:
            # assume ALL argument names are case insensitive
            insensitive_arg_names_dict = callable_arg_names_dict
        # check for names that aren't in the function signature
        if any(n not in insensitive_arg_names_dict for n in insensitive_arg_names_lower):
            invalid_names = [invalid_name for invalid_name,invalid_name_lower
                                            in zip(insensitive_arg_names, insensitive_arg_names_lower)
                                            if invalid_name_lower not in insensitive_arg_names_dict]
            raise CaseInsensitiveDecoratorError(f"Invalid argument name(s): {str(invalid_names)[1:-1]}")
        @wraps(callable)
        def wrapped(*args, **kwargs):
            # make sure no kwargs conflict with the case-insensitive args
            lower_arg_names_ctr = Counter([k.lower() for k in kwargs])
            if any(v!=1 and k in insensitive_arg_names_dict for k,v in lower_arg_names_ctr.items()):
                conflicting = [k for k,v in lower_arg_names_ctr.items() if k.lower() in insensitive_arg_names_dict and v!=1]
                raise CaseInsensitiveDecoratorError(f"received keyword arguments that conflict with the specified case-"
                                                    f"insensitive argument names: {str(conflicting)[1:-1]}")
            # lookup actual version of argument names based on lowercase version of provided name
            kwargs = {insensitive_arg_names_dict.get(n.lower(),n):v for n,v in kwargs.items()}
            return callable(*args, **kwargs)
        return wrapped
    if callable is _NO_CALLABLE:
        return wrapped_callable
    else:
        return wrapped_callable(callable)

# this thing below is stupid and broken. no idea if it's even worth doing. what a freaking waste of time.
'''
GeneratorFunction = Callable[..., Generator[Any, Any, Any]]
_NO_GEN_TYPE = type("_NO_GEN_TYPE", (), {})
_NO_GEN = _NO_GEN_TYPE()

_WRAPPED_GENERATOR_CODE="""
@wraps(generator_func)
def wrapped_generator_func(*args, *, {ended_signal_arg_name}=False, **kwargs) -> GeneratorFunction:
    yield from generator_func(*args, **kwargs)
    if {ended_signal_arg_name}:
        setattr(ended_ns, ended_attr, True)
    return return_value
"""[1:]

def generator_ended_signal(generator_func: Union[_NO_GEN_TYPE,GeneratorFunction]=_NO_GEN, *,
                           ended_ns: Any,
                           ended_attr: str = "complete",
                           return_value: Any = None):
    def generator_decorator(generator_func: GeneratorFunction):
        """Extend a generator so that it can be detected that it has ended. Set the keyword argument `ended_signal` to
        True to enable this behavior when first calling the generator.

        Detection is possible regardless of whether it was delegated to from another context. This is accomplished when
        desired by the generator optionally setting a previously specified object to a Truthy value. A value to be
        returned by the exhausted generator may also be optionally specified.
        """
        arg_names, varname_args, varname_kw, _, kwonlyarg_names, _, _ = getfullargspec(callable)
        generator_arg_names = arg_names + kwonlyarg_names + [varname_args] if varname_args else [] + [varname_kw] if varname_kw else []
        ended_signal_arg_name = "ended_signal"
        while ended_signal_arg_name in generator_arg_names:
            ended_signal_arg_name = "_" + ended_signal_arg_name
        ns = dict(generator_func=generator_func, wraps=wraps, return_value=return_value,
                  GeneratorFunction=GeneratorFunction, ended_ns=ended_ns, ended_attr=ended_attr)
        code = _WRAPPED_GENERATOR_CODE.format(ended_signal_arg_name=ended_signal_arg_name)
        try:
            exec(code, ns, ns)
        except SyntaxError as e:
            if e.args and "parameter and global" in e.args[0]:
                raise SignalGeneratorEndedError("check generator arguments for name conflicts with ended_ns or ended_attr") from e
            else:
                raise e
        wrapped_generator_func = ns["wrapped_generator_func"]
        return wrapped_generator_func

    # determine how decorator was called
    if generator_func is _NO_GEN:
        # outer decorator was called like @generator_ended_signal() or @generator_ended_signal(return_value="foo")
        return generator_decorator
    else:
        # outer decorator was called like @generator_ended_signal or generator_ended_signal(my_gen, return_value="foo")
        return generator_decorator(generator_func)
'''
