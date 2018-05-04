from typing import Dict, Callable, Any
import pytest

from candejar.utilities.decorators import case_insensitive_arguments, CaseInsensitiveDecoratorError

CallableAny = Callable[...,Any]

@pytest.fixture
def f():
    def f(A, B, C=1, *args, D, E, F=2, **kwargs):
        return A,B,C,D,E,F
    return f

@pytest.fixture
def kwargs_lower():
    return dict(zip("abcdef",(1,2,3,4,5,6)))

def test_decorator_called(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments()(f)
    assert f(**kwargs_lower) == tuple(kwargs_lower.values())

def test_decorator_called_args(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments(insensitive_arg_names=kwargs_lower.keys())(f)
    assert f(**kwargs_lower) == tuple(kwargs_lower.values())

def test_decorator_errors(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments(insensitive_arg_names=kwargs_lower.keys())(f)
    with pytest.raises(CaseInsensitiveDecoratorError):
        f(**kwargs_lower, D=0, E=0)
    g=case_insensitive_arguments(insensitive_arg_names="ABC")(f)
    with pytest.raises(CaseInsensitiveDecoratorError):
        f(**{k:v for k,v in kwargs_lower.items() if k in "abc"}, D=0, E=0, F=0)

def test_decorator(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments(f)
    assert f(**kwargs_lower) == tuple(kwargs_lower.values())
