import logging
import logging.config
import typing

import click
import IPython

import code.k8s
import code.logging
import code.ui
import code.db

# Resolves issue with Docker container:
#   RuntimeError: Click will abort further execution because Python 3 was
#   configured to use ASCII as encoding for the environment. Consult
#   https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
click.core._verify_python3_env: typing.Callable = lambda: None


@click.group()
def main():
    logging.config.dictConfig(code.logging.CONFIG)
    IPython.InteractiveShell.colors = 'Linux'


# Register subcommands
main.add_command(code.k8s.k8s)
main.add_command(code.ui.ui)
main.add_command(code.db.db)


@main.command()
def ipython():
    """Run an IPython shell"""
    IPython.embed()


@main.command()
def test_cli():
    """Test whether or not the CLI is working"""
    LOG = logging.getLogger(__name__)
    LOG.info('CLI Working')


if __name__ == '__main__':
    main()
