from ddtrace.utils.wrappers import wrap_function_wrapper


def test_wrap_function_idempotence():
    class A:
        def add(self, x, y):
            return x + y

    def square(wrapped, instance, args, kwargs):
        result = wrapped(*args, **kwargs)
        return result ** 2

    assert A().add(1,2) == 3
    wrap_function_wrapper(A, "add", square)
    assert A().add(1,2) == 9
    wrap_function_wrapper(A, "add", square)
    assert A().add(1,2) == 9
