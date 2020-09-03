# 3p
import pymysql

# project
from ddtrace import Pin
from ddtrace.contrib.dbapi import TracedConnection
from ...ext import net, db
from ...utils.wrappers import wrap_function_wrapper as _w, unwrap as _u

CONN_ATTR_BY_TAG = {
    net.TARGET_HOST: 'host',
    net.TARGET_PORT: 'port',
    db.USER: 'user',
    db.NAME: 'db',
}


def patch():
    _w('pymysql', 'connect', _connect)


def unpatch():
    _u(pymysql, "connect")


def _connect(func, instance, args, kwargs):
    conn = func(*args, **kwargs)
    return patch_conn(conn)


def patch_conn(conn):
    tags = {t: getattr(conn, a, '') for t, a in CONN_ATTR_BY_TAG.items()}
    pin = Pin(service='pymysql', app='pymysql', tags=tags)

    # grab the metadata from the conn
    wrapped = TracedConnection(conn, pin=pin)
    pin.onto(wrapped)
    return wrapped
