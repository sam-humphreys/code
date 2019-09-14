import click

import code.k8s.monitoring


@click.group()
def k8s():
    """Subcommand for Kubernetes commands"""


@k8s.command()
@click.option('--local', is_flag=True,
    help='If specified will use local Kubernetes authentication rather than in-cluster')
@click.option('--namespace', type=str, default='default', help='The namespace within the cluster to watch pods')
def watch_pods(local, namespace):
    """
    Instantiates a Kubernetes client which watches pods in the specified namespace
    within desired cluster. Slack alerts are sent for any changes in pod status'.
    """
    local = True if local else False
    client = code.k8s.monitoring.KubernetesClient(local)
    client.watch_pods(namespace)
