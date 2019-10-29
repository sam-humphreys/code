import typing
import contextlib
import logging

import sqlalchemy

LOG = logging.getLogger(__name__)


class Table(typing.NamedTuple):
    name: str
    cmd: typing.Callable


@contextlib.contextmanager
def create_engine(user: str, password: str, host: str, db: str) -> sqlalchemy.engine.Engine:
    """Context managed SQLAlchemy engine"""
    yield sqlalchemy.create_engine(f'postgresql://{user}:{password}@{host}/{db}')


def execute_sql(engine: sqlalchemy.engine.Engine, sql: str):
    """Logs and executes a raw SQL string"""
    LOG.info(f'Executing SQL:\n{sql}')
    engine.execute(sql)
