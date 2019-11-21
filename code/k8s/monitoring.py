import logging
import typing
import json

import kubernetes
import pandas

import code.alerts.slack

LOG = logging.getLogger(__name__)

KUBE_SYSTEM_NAMESPACES = [
    'kube-system',
    'kube-public',
]


class KubernetesClient:
    """
    Python Kubernetes client - central location for general methods

    param: local - Either use local or in-cluster kubernetes authentication config
    """
    def __init__(self, local: bool = None):
        self.local = local
        kubernetes.config.load_kube_config() if local else kubernetes.config.load_incluster_config()
        self.client: kubernetes.client.CoreV1Api = kubernetes.client.CoreV1Api()
        self.api_client: kubernetes.client.api_client.ApiClient = kubernetes.client.ApiClient()

    def watch_pods(self, namespace: str) -> None:
        """Watch pod events in the cluster for specified namespace. Send Slack alerts for each event"""
        watcher = kubernetes.watch.Watch()
        alerted = dict()

        LOG.info(f"Watching pod events in the '{namespace}' namespace")

        for event in watcher.stream(self.client.list_namespaced_pod, namespace=namespace):
            processed = _process_pod_event(alerted, event)

            if processed:
                name, status, colour = processed

                # Send Slack alert
                code.alerts.slack.post_event(code.alerts.slack.Event(
                    status=name,
                    colour=colour,
                    message=f"Status - {status}",
                ))

                alerted[name] = status

    def get_namespaces(self, exclude_kube_system: bool = None) -> typing.List[str]:
        """
        Return a list of string names for each namespace in cluster. Pass
        exclude_kube_system to remove the kubernetes system namespaces.
        """
        namespaces = self.client.list_namespace().items
        names = list()

        for n in namespaces:
            is_kube_system = n.metadata.name in KUBE_SYSTEM_NAMESPACES
            if (not exclude_kube_system) or (exclude_kube_system) and (not is_kube_system):
                names.append(n.metadata.name)

        return names

    def get_cluster_pod_metrics(self) -> pandas.DataFrame:
        """Construct a dataframe containing CPU & memory usage for all pods running on the cluster"""
        def _process(pod_metrics):
            for pod in pod_metrics:
                yield _process_api_metrics_pod(pod)

        request = self.api_client.call_api(
            resource_path='/apis/metrics.k8s.io/v1beta1/pods',
            method='GET',
            auth_settings=['BearerToken'],
            response_type='json',
            _preload_content=False,
        )

        response, code, headers = request
        pod_metrics = json.loads(response.data.decode())['items']

        return pandas.concat(_process(pod_metrics)).reset_index(drop=True)


def _process_pod_event(
    alerted: typing.Dict[str, str],
    event: typing.Dict[str, typing.Any],
) -> typing.Optional[typing.Tuple[str, str, code.alerts.slack.Colours]]:
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

    event_type = event['type'].upper()

    if event_type == 'ADDED' and status == 'PENDING':
        colour = code.alerts.slack.Colours.WARNING
    elif event_type in ['ADDED', 'MODIFIED'] and status != 'DELETED':
        colour = code.alerts.slack.Colours.SUCCESS
    else:
        colour = code.alerts.slack.Colours.ERROR

    return (name, status, colour)


def _process_api_metrics_pod(pod: typing.Dict[str, typing.Any]) -> pandas.DataFrame:
    """Extract CPU & memory metrics from a pod returned by the Kubernetes API"""
    data = {
        'ts': pandas.Timestamp('now'),
        'pod_name': pod['metadata']['name'],
        'namespace': pod['metadata']['namespace'],
    }

    df = pandas.DataFrame(data, index=[0])

    container_usage = [container['usage'] for container in pod['containers']]
    container_df = pandas.DataFrame(container_usage)

    # Sum containers usage & assign on pod level (data is formerly string type w/ unit)
    df = df.assign(
        # cpu_n=container_df['cpu'].str.strip('n').astype(int).sum(),
        # memory_ki=container_df['memory'].str.strip('Ki').astype(int).sum(),
        cpu=container_df['cpu'],
        memory=container_df['memory'],
    )

    return df

import time

import code.db.utils

table_name = code.db.monitoring.NAMESPACE_USAGE_TABLE_NAME

while True:
    with code.db.utils.create_engine('monitoring-rw', 'monitoringrules', 'localhost:9999', 'monitoring') as engine:
        client = KubernetesClient(True)
        df = client.get_cluster_pod_metrics()

        # Insert df into db table
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        LOG.info(f'Inserted {len(df)} records into {table_name} DB table')

    time.sleep(60)
