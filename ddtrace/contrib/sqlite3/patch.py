# 3p
import sqlite3
import sqlite3.dbapi2

# project
from ...contrib.dbapi import TracedConnection, TracedCursor, FetchTracedCursor
from ...pin import Pin
from ...settings import config
from ...utils.wrappers import wrap_function_wrapper as _w, unwrap as _u


def patch():
    _w(sqlite3, 'connect', traced_connect)
    _w(sqlite3.dbapi2, 'connect', traced_connect)


def unpatch():
    _u(sqlite3, "connect")
    _u(sqlite3.dbapi2, "connect")


def traced_connect(func, _, args, kwargs):
    conn = func(*args, **kwargs)
    return patch_conn(conn)


def patch_conn(conn):
    wrapped = TracedSQLite(conn)
    Pin(service='sqlite', app='sqlite').onto(wrapped)
    return wrapped


class TracedSQLiteCursor(TracedCursor):
    def executemany(self, *args, **kwargs):
        # DEV: SQLite3 Cursor.execute always returns back the cursor instance
        super(TracedSQLiteCursor, self).executemany(*args, **kwargs)
        return self

    def execute(self, *args, **kwargs):
        # DEV: SQLite3 Cursor.execute always returns back the cursor instance
        super(TracedSQLiteCursor, self).execute(*args, **kwargs)
        return self


class TracedSQLiteFetchCursor(TracedSQLiteCursor, FetchTracedCursor):
    pass


class TracedSQLite(TracedConnection):
    def __init__(self, conn, pin=None, cursor_cls=None):
        if not cursor_cls:
            # Do not trace `fetch*` methods by default
            cursor_cls = TracedSQLiteCursor
            if config.dbapi2.trace_fetch_methods:
                cursor_cls = TracedSQLiteFetchCursor

            super(TracedSQLite, self).__init__(conn, pin=pin, cursor_cls=cursor_cls)

    def execute(self, *args, **kwargs):
        # sqlite has a few extra sugar functions
        return self.cursor().execute(*args, **kwargs)
