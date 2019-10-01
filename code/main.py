import logging
import logging.config

import click
import IPython

import code.k8s
import code.logging
import code.ui


@click.group()
def main():
    logging.config.dictConfig(code.logging.CONFIG)
    IPython.InteractiveShell.colors = 'Linux'


# Register subcommands
main.add_command(code.k8s.k8s)
main.add_command(code.ui.ui)


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
