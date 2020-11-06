from riot import Suite, Case

global_deps = [
    "mock",
    "pytest<4",
    "opentracing",
]

global_env = [("PYTEST_ADDOPTS", "--color=yes")]

suites = [
    Suite(
        name="black",
        command="black --check .",
        cases=[
            Case(
                pys=[3.8],
                pkgs=[
                    ("black", ["==20.8b1"]),
                ],
            ),
        ],
    ),
    Suite(
        name="flake8",
        command="flake8 ddtrace/ tests/",
        cases=[
            Case(
                pys=[3.8],
                pkgs=[
                    ("flake8", [">=3.8,<3.9"]),
                    ("flake8-blind-except", [""]),
                    ("flake8-builtins", [""]),
                    ("flake8-docstrings", [""]),
                    ("flake8-logging-format", [""]),
                    ("flake8-rst-docstrings", [""]),
                    ("pygments", [""]),
                ],
            ),
        ],
    ),
    Suite(
        name="tracer",
        command="pytest tests/tracer/",
        cases=[
            Case(
                pys=[
                    2.7,
                    3.5,
                    3.6,
                    3.7,
                    3.8,
                    3.9,
                ],
                pkgs=[("msgpack", [""])],
            ),
        ],
    ),
    Suite(
        name="pymongo",
        command="pytest tests/contrib/pymongo",
        cases=[
            Case(
                pys=[
                    2.7,
                    3.5,
                    3.6,
                    3.7,
                ],
                pkgs=[
                    (
                        "pymongo",
                        [
                            ">=3.0,<3.1",
                            ">=3.1,<3.2",
                            ">=3.2,<3.3",
                            ">=3.3,<3.4",
                            ">=3.4,<3.5",
                            ">=3.5,<3.6",
                            ">=3.6,<3.7",
                            ">=3.7,<3.8",
                            ">=3.8,<3.9",
                            ">=3.9,<3.10",
                            ">=3.10,<3.11",
                            "",
                        ],
                    ),
                    ("mongoengine", [""]),
                ],
            ),
            Case(
                pys=[
                    3.8,
                    3.9,
                ],
                pkgs=[
                    (
                        "pymongo",
                        [
                            ">=3.0,<3.1",
                            ">=3.1,<3.2",
                            ">=3.2,<3.3",
                            ">=3.3,<3.4",
                            ">=3.5,<3.6",
                            ">=3.6,<3.7",
                            ">=3.7,<3.8",
                            ">=3.8,<3.9",
                            ">=3.9,<3.10",
                            ">=3.10,<3.11",
                            "",
                        ],
                    ),
                    ("mongoengine", [""]),
                ],
            ),
        ],
    ),
    Suite(
        name="celery",
        command="pytest tests/contrib/celery",
        cases=[
            # Non-4.x celery should be able to use the older redis lib, since it locks to an older kombu
            Case(
                pys=[2.7, 3.5, 3.6],
                pkgs=[
                    ("celery", [">=3.1,<3.2"]),
                    ("redis", [">=2.10,<2.11"]),
                ],
            ),
            # 4.x celery bumps kombu to 4.4+, which requires redis 3.2 or later, this tests against
            # older redis with an older kombu, and newer kombu/newer redis.
            # https://github.com/celery/kombu/blob/3e60e6503a77b9b1a987cf7954659929abac9bac/Changelog#L35
            Case(
                pys=[2.7, 3.5, 3.6],
                pkgs=[
                    ("celery", [">=4.0,<4.1", ">=4.1,<4.2"]),
                    ("redis", [">=2.10,<2.11", ">=3.2,<3.3"]),
                    ("kombu", [">=4.3,<4.4", ">=4.4,<4.5"]),
                    ("pytest", [">=3,<4"]),
                ],
            ),
            # Celery 4.2 is now limited to Kombu 4.3
            # https://github.com/celery/celery/commit/1571d414461f01ae55be63a03e2adaa94dbcb15d
            Case(
                pys=[2.7, 3.5, 3.6],
                pkgs=[
                    ("celery", [">=4.2,<4.3"]),
                    ("redis", [">=2.10,<2.11"]),
                    ("kombu", [">=4.3,<4.4"]),
                    ("pytest", [">=3,<4"]),
                ],
            ),
            # Celery 4.3 wants Kombu >= 4.4 and Redis >= 3.2
            # Python 3.7 needs Celery 4.3
            Case(
                pys=[2.7, 3.5, 3.6, 3.7, 3.8, 3.9],
                pkgs=[("celery", [">=4.3,<4.4"]), ("redis", [">=3.2,<3.3"]), ("kombu", [">=4.4,<4.5"])],
            ),
        ],
    ),
]
