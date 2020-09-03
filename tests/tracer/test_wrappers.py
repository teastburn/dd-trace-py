import inspect
import pytest

from ddtrace.vendor import wrapt


@pytest.fixture
def diamond():
    class Diamond(object):
        class A(object):
            def run(self):
                return "A"

        class B(A):
            pass

        class C(A):
            def run(self):
                return ["C", super(Diamond.C, self).run()]

        class D(B, C):
            pass

    return Diamond


def double(wrapped, instance, args, kwargs):
    return wrapped(*args, **kwargs) * 2


def test_wrapping_module_diamond(diamond):
    assert inspect.getmro(diamond.D) == (diamond.D, diamond.B, diamond.C, diamond.A, object)

    assert "run" not in vars(diamond.D)
    assert diamond.D.run == diamond.C.run
    assert diamond.D().run() == ["C", "A"]

    wrapt.wrap_function_wrapper(diamond.D, "run", double)
    assert "run" in vars(diamond.D)
    assert isinstance(vars(diamond.D)["run"], wrapt.FunctionWrapper)
    assert diamond.D.run.__wrapped__ == diamond.C.run
    assert diamond.D().run() == ["C", "A", "C", "A"]


def test_wrapping_module_diamond_intermediate(diamond):
    assert "run" not in vars(diamond.D)
    assert diamond.D.run == diamond.C.run
    assert diamond.D().run() == ["C", "A"]

    wrapt.wrap_function_wrapper(diamond.B, "run", double)
    wrapt.wrap_function_wrapper(diamond.D, "run", double)
    assert "run" in vars(diamond.B)
    assert "run" in vars(diamond.D)
    assert isinstance(vars(diamond.D)["run"], wrapt.FunctionWrapper)
    assert diamond.B.run.__wrapped__ == diamond.A.run
    assert diamond.D.run.__wrapped__ == diamond.B.run
    assert diamond.B().run() == "AA"
    assert diamond.D().run() == "AAAA"


def test_wrapping_instance_diamond(diamond):
    d = diamond.D()

    assert "run" not in vars(d)
    assert d.run() == ["C", "A"]

    wrapt.wrap_function_wrapper(d, "run", double)
    assert "run" in vars(d)
    assert "run" not in vars(diamond.D)
    assert d.run() == ["C", "A", "C", "A"]
