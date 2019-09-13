import logging

import click
import IPython


@click.group()
def main():
    LOG = logging.getLogger(__name__)


@main.command()
def ipython():
    """Run an IPython shell"""
    IPython.embed()


@main.command()
def test():
    LOG = logging.getLogger(__name__)
    LOG.info('SUCCESS')


if __name__ == '__main__':
    main()
