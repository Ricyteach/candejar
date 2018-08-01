from typing import Dict, Callable, Any
import pytest

from candejar.utilities.decorators import case_insensitive_arguments, CaseInsensitiveDecoratorError, init_kwargs

CallableAny = Callable[...,Any]

@pytest.fixture
def f():
    def f(A, B, C=1, *args, D, E, F=2):
        return A,B,C,D,E,F
    return f

@pytest.fixture
def kwargs_lower():
    return dict(zip("abcdef",(1,2,3,4,5,6)))

@pytest.fixture
def kwargs_upper():
    return dict(zip("ABCDEF",(1,2,3,4,5,6)))

def test_decorator_called(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments()(f)
    assert f(**kwargs_lower) == tuple(kwargs_lower.values())

def test_decorator_called_args(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments(insensitive_arg_names=kwargs_lower.keys())(f)
    assert f(**kwargs_lower) == tuple(kwargs_lower.values())

def test_decorator_error_conflicting_args(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments(insensitive_arg_names=kwargs_lower.keys())(f)
    with pytest.raises(CaseInsensitiveDecoratorError):
        f(**kwargs_lower, D=0, E=0)

def test_decorator_error_unused_args(f: CallableAny, kwargs_upper: Dict):
    f=case_insensitive_arguments(insensitive_arg_names="ABC")(f)
    with pytest.raises(TypeError):
        f(**kwargs_upper, D=0, E=0)

def test_decorator_error_invalid_insensitive_args(f: CallableAny):
    with pytest.raises(CaseInsensitiveDecoratorError):
        case_insensitive_arguments(insensitive_arg_names="X")(f)

def test_decorator(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments(f)
    assert f(**kwargs_lower) == tuple(kwargs_lower.values())

def test_init_kwargs():
    class P:
        def __init__(self, **kwargs):
            print(f"UNUSED KWARGS: {kwargs}")


    @init_kwargs
    class C1(P):
        def __init__(self, a, **kwargs):
            print(f"C1 object!!! a = {a!r}")


    C1(1, b=2)

    @init_kwargs
    class C2(P):
        def __init__(self, a):
            print(f"C2 object!!! a = {a!r}")


    C2(1, b=2)


    from dataclasses import dataclass

    @init_kwargs
    @dataclass
    class C3(P):
        a: int = 1


    print(C3(1, b=2))
