import sqlalchemy

from code.db.utils import Table, execute_sql

NAMESPACE_USAGE_TABLE_NAME = 'namespace_usage'


def _create_namespace_usage_table(engine: sqlalchemy.engine.Engine) -> None:
    """
    Creates a DB table for K8s namespace monitoring.
    Schema is in raw postgreSQL for ease of understanding.
    """
    sql = f"""
        CREATE TABLE IF NOT EXISTS
        {NAMESPACE_USAGE_TABLE_NAME} (
            pk BIGINT NOT NULL PRIMARY KEY,
            ts timestamp NOT NULL,
            pod_name text NOT NULL,
            namespace text NOT NULL,
            cpu_n BIGINT NOT NULL,
            memory_ki BIGINT NOT NULL
        );
    """

    execute_sql(engine, sql)


TABLES = [
    Table(NAMESPACE_USAGE_TABLE_NAME, _create_namespace_usage_table),
]
