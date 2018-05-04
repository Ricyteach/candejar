from typing import Dict, Callable, Any
import pytest

from candejar.utilities.decorators import case_insensitive_arguments, CaseInsensitiveDecoratorError

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
    f=case_insensitive_arguments(insensitive_arg_names="X")(f)
    with pytest.raises(CaseInsensitiveDecoratorError):
        f(**kwargs_lower, D=0, E=0)

def test_decorator(f: CallableAny, kwargs_lower: Dict):
    f=case_insensitive_arguments(f)
    assert f(**kwargs_lower) == tuple(kwargs_lower.values())
