import datetime
import logging
import typing
import time

import google.cloud.logging

LOG = logging.getLogger(__name__)


def extract_logs(
    projects: typing.List[str],
    filter_: str = None,
    sleep_between_requests: int = None,
) -> typing.List[typing.Tuple[datetime.datetime, typing.Dict[str, str], typing.Any]]:
    """
    Simple log extraction for entries matching given project(s) & a filter (if applicable)

    Returns a list, containing tuples storing:
        - Log timestamp
        - Log Resource labels
        - Log payload

    Note - Envvar GOOGLE_APPLICATION_CREDENTIALS="[PATH](.json)" must be set if deployed. This
    could be a custom service account limited to purely accessing logs.
    """
    client = google.cloud.logging.Client()

    iterator = client.list_entries(projects=projects, filter_=filter_)
    results = list()

    for page in iterator.pages:
        if page.num_items > 0:
            results.append([(entry.timestamp, entry.resource.labels, entry.payload) for entry in list(page)])

        if sleep_between_requests:
            LOG.info(f'Sleeping {sleep_between_requests} seconds before processing next page')
            time.sleep(sleep_between_requests)

    return results
