import logging

import click
import IPython

import code.k8s


@click.group()
def main():
    LOG = logging.getLogger(__name__)


# Register subcommands
main.add_command(code.k8s.k8s)


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
