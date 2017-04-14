"""
Generic dbapi tracing code.
"""

# stdlib
import logging

# 3p
import wrapt

# project
from ddtrace import Pin
from ddtrace.ext import sql


log = logging.getLogger(__name__)


class TracedCursor(wrapt.ObjectProxy):
    """ TracedCursor wraps a psql cursor and traces it's queries. """

    _datadog_pin = None
    _datadog_name = None

    def __init__(self, cursor, pin):
        super(TracedCursor, self).__init__(cursor)
        self._datadog_pin = pin
        name = pin.app or 'sql'
        self._datadog_name = '%s.query' % name

    def _trace_method(self, method, resource, extra_tags, *args, **kwargs):
        pin = self._datadog_pin
        if not pin or not pin.enabled():
            return method(*args, **kwargs)
        service = pin.service

        with pin.tracer.trace(self._datadog_name, service=service, resource=resource) as s:
            s.span_type = sql.TYPE
            s.set_tag(sql.QUERY, resource)
            s.set_tags(pin.tags)

            for k, v in extra_tags.items():
                s.set_tag(k, v)

            try:
                return method(*args, **kwargs)
            finally:
                s.set_metric("db.rowcount", self.rowcount)

    def executemany(self, query, *args, **kwargs):
        # FIXME[matt] properly handle kwargs here. arg names can be different
        # with different libs.
        return self._trace_method(
            self.__wrapped__.executemany, query, {'sql.executemany': 'true'},
            query, *args, **kwargs)

    def execute(self, query, *args, **kwargs):
        return self._trace_method(
            self.__wrapped__.execute, query, {}, query, *args, **kwargs)

    def callproc(self, proc, args):
        self._trace_method(self.__wrapped__.callproc, proc, {}, proc, args)

    def __enter__(self):
        # previous versions of the dbapi didn't support context managers. let's
        # reference the func that would be called to ensure that errors
        # messages will be the same.
        self.__wrapped__.__enter__

        # and finally, yield the traced cursor.
        return self


class TracedConnection(wrapt.ObjectProxy):
    """ TracedConnection wraps a Connection with tracing code. """

    _datadog_pin = None

    def __init__(self, conn):
        super(TracedConnection, self).__init__(conn)
        name = _get_vendor(conn)
        Pin(service=name, app=name).onto(self)

    def cursor(self, *args, **kwargs):
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        pin = self._datadog_pin
        if not pin:
            return cursor
        return TracedCursor(cursor, pin)


def _get_vendor(conn):
    """ Return the vendor (e.g postgres, mysql) of the given
        database.
    """
    try:
        name = _get_module_name(conn)
    except Exception:
        log.debug("couldnt parse module name", exc_info=True)
        name = "sql"
    return sql.normalize_vendor(name)

def _get_module_name(conn):
    return conn.__class__.__module__.split('.')[0]
