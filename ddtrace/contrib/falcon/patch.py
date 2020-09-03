import falcon

from ddtrace import config, tracer

from .middleware import TraceMiddleware
from ...utils.formats import asbool, get_env
from ...utils.wrappers import wrap_function_wrapper as _w


def patch():
    """
    Patch falcon.API to include contrib.falcon.TraceMiddleware
    by default
    """
    if getattr(falcon, '_datadog_patch', False):
        return

    setattr(falcon, '_datadog_patch', True)
    _w('falcon', 'API.__init__', traced_init)


def traced_init(wrapped, instance, args, kwargs):
    mw = kwargs.pop('middleware', [])
    service = config._get_service(default="falcon")
    distributed_tracing = asbool(get_env('falcon', 'distributed_tracing', default=True))

    mw.insert(0, TraceMiddleware(tracer, service, distributed_tracing))
    kwargs['middleware'] = mw

    wrapped(*args, **kwargs)
