import sqlalchemy


from .engine import _wrap_create_engine
from ...utils.wrappers import unwrap as _u, wrap_function_wrapper as _w


def patch():
    if getattr(sqlalchemy.engine, '__datadog_patch', False):
        return
    setattr(sqlalchemy.engine, '__datadog_patch', True)

    # patch the engine creation function
    _w('sqlalchemy', 'create_engine', _wrap_create_engine)
    _w('sqlalchemy.engine', 'create_engine', _wrap_create_engine)


def unpatch():
    # unpatch sqlalchemy
    if getattr(sqlalchemy.engine, '__datadog_patch', False):
        setattr(sqlalchemy.engine, '__datadog_patch', False)
        _u(sqlalchemy, 'create_engine')
        _u(sqlalchemy.engine, 'create_engine')
