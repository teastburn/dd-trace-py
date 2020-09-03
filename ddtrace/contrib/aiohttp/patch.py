from ddtrace import config

from ...pin import Pin
from ...utils.wrappers import unwrap as _u, wrap_function_wrapper as _w


try:
    # instrument external packages only if they're available
    import aiohttp_jinja2
    from .template import _trace_render_template

    template_module = True
except ImportError:
    template_module = False


def patch():
    """
    Patch aiohttp third party modules:
        * aiohttp_jinja2
    """
    if template_module:
        if getattr(aiohttp_jinja2, '__datadog_patch', False):
            return
        setattr(aiohttp_jinja2, '__datadog_patch', True)

        _w('aiohttp_jinja2', 'render_template', _trace_render_template)
        Pin(app='aiohttp', service=config.service).onto(aiohttp_jinja2)


def unpatch():
    """
    Remove tracing from patched modules.
    """
    if template_module:
        if getattr(aiohttp_jinja2, '__datadog_patch', False):
            setattr(aiohttp_jinja2, '__datadog_patch', False)
            _u(aiohttp_jinja2, 'render_template')
