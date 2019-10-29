import logging

import click

import code.db.utils
import code.db.monitoring

LOG = logging.getLogger(__name__)


@click.group()
def db():
    """Subcommand for database commands"""


@db.command()
@click.option('--db-user', type=str, default='monitoring-rw')
@click.option('--db-password', type=str, default='monitoringrules')
@click.option('--db-host', type=str, default='localhost:9999')
@click.option('--db-name', type=str, default='monitoring')
def create_monitoring_tables(db_user: str, db_password: str, db_host: str, db_name: str):
    """
    Create all of the monitoring SQL tables.
    Requires an active connection to a SQL proxy, for example:
        ./cloud_sql_proxy -instances project:region:instance_name=tcp:9999
    """
    with code.db.utils.create_engine(db_user, db_password, db_host, db_name) as engine:
        for name, cmd in code.db.monitoring.TABLES:
            LOG.info(f'Creating table - {name}')
            cmd(engine)

    LOG.info(f'Successfully created - {len(code.db.monitoring.TABLES)} DB table(s)')
