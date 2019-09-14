import logging
import typing

import kubernetes

import code.alerts.slack

LOG = logging.getLogger(__name__)


class KubernetesClient:
    """
    Python Kubernetes client - central location for general methods

    param: local - Either use local or in-cluster kubernetes authentication config
    """
    def __init__(self, local: bool):
        kubernetes.config.load_kube_config() if local else kubernetes.config.load_incluster_config()
        self.client: kubernetes.client.CoreV1Api = kubernetes.client.CoreV1Api()

    def watch_pods(self, namespace: str) -> None:
        """Watch pod events in the cluster for specified namespace. Send Slack alerts for each event"""
        watcher = kubernetes.watch.Watch()
        alerted = dict()

        LOG.info(f"Watching pod events in the '{namespace}' namespace")

        for event in watcher.stream(self.client.list_namespaced_pod, namespace=namespace):
            processed = _process_pod_event(alerted, event)

            if processed:
                name, status = processed
                alerted[name] = status


def _process_pod_event(
    alerted: typing.Dict[str, str],
    event: typing.Dict[str, typing.Any],
) -> typing.Optional[typing.Tuple[str, str]]:
    """
    Process a Kubernetes pod event. If the pod name
    is in the alerted dict & status is the same do
    nothing. Otherwise send a Slack alert
    """
    name = event['object'].metadata.name
    status = event['object'].status.phase.upper()

    if status == 'RUNNING' and event['object'].metadata.deletion_timestamp:
        status = 'DELETED'

    alerted_status = alerted.get(name, None)

    if alerted_status and alerted_status == status:
        LOG.info(f'Event has already been alerted on - ({name}, {alerted_status})')
        return None

    _alert_pod_event(name, status, event['type'])

    return (name, status)


def _alert_pod_event(name: str, status: str, event_type: str) -> None:
    """Send Slack alert based upon pod event details"""
    if event_type == 'ADDED' and status == 'PENDING':
        colour = code.alerts.slack.Colours.WARNING
    elif event_type in ['ADDED', 'MODIFIED'] and status != 'DELETED':
        colour = code.alerts.slack.Colours.SUCCESS
    else:
        colour = code.alerts.slack.Colours.ERROR

    code.alerts.slack.post_event(code.alerts.slack.Event(
        status=name,
        colour=colour,
        message=f"Status - {status}",
    ))
