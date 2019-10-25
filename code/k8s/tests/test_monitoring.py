import unittest.mock

import hypothesis
import pytest
import kubernetes

import code.k8s.monitoring
import code.k8s.tests.hypothesis_strategies
import code.alerts.slack


class TestKubernetesClient(unittest.TestCase):
    @unittest.mock.patch('kubernetes.config.load_kube_config')
    def setUp(self, KubernetesClient):
        self.KubernetesClient = code.k8s.monitoring.KubernetesClient(local=True)

    def test_client(self):
        """Test client instance has been built accurately"""
        assert isinstance(self.KubernetesClient.client, kubernetes.client.apis.core_v1_api.CoreV1Api), \
            f'Client is not a CoreV1Api instance - {type(self.KubernetesClient.client)}'

    def test_api_client(self):
        """Test client instance has been built accurately"""
        assert isinstance(self.KubernetesClient.api_client, kubernetes.client.api_client.ApiClient), \
            f'Client is not a ApiClient instance - {type(self.KubernetesClient.api_client)}'

    @unittest.mock.patch.object(kubernetes.watch.Watch, 'stream')
    @unittest.mock.patch('code.alerts.slack.post_event')
    @hypothesis.given(
        events=code.k8s.tests.hypothesis_strategies.multiple_event_strategy,
        namespace=code.k8s.tests.hypothesis_strategies.text_strategy,
    )
    def test_watch_pods(self, events, namespace, mock_post_event, mock_stream):
        """Test watch pods function can handle mocked event instances"""
        def _build_expected_event(event):
            # Dummy to return same logic in order to assert
            name, status, colour = code.k8s.monitoring._process_pod_event(alerted={}, event=event)
            return code.alerts.slack.Event(
                status=name,
                colour=colour,
                message=f"Status - {status}",
            )

        mock_stream.return_value = events
        self.KubernetesClient.watch_pods(namespace)

        for event in events:
            built_event = _build_expected_event(event)
            mock_post_event.assert_any_call(built_event)

    @unittest.mock.patch.object(kubernetes.client.CoreV1Api, 'list_namespace')
    @hypothesis.given(namespace_list=code.k8s.tests.hypothesis_strategies.namespace_list_strategy)
    def test_get_namespaces(self, namespace_list, mock_list):
        """Test get namespaces for client"""
        mock_list.return_value = namespace_list
        expected = [n.metadata.name for n in namespace_list.items]
        actual = self.KubernetesClient.get_namespaces()

        assert len(namespace_list.items) == len(actual), 'Not all namespaces have been returned'
        assert all([n in expected for n in actual]), f'Different lists: {actual} - {expected}'

    @hypothesis.given(pod=code.k8s.tests.hypothesis_strategies.api_metrics_pod_strategy)
    def test_process_api_metrics_pod(self, pod):
        """Test the api metrics pod processor returns an expected dataframe"""
        print(pod)
        df = code.k8s.monitoring._process_api_metrics_pod(pod)

        assert len(df) == 1, 'More than one record returned, this should be impossible'

        # Calculate total CPU & memory usage for pod
        cpu = sum([int(i['usage']['cpu'].strip('n')) for i in pod['containers']])
        memory = sum([int(i['usage']['memory'].strip('Ki')) for i in pod['containers']])

        assert df.at[0, 'cpu_n'] == cpu, f'Expected {cpu}, got:\n{df}'
        assert df.at[0, 'memory_ki'] == memory, f'Expected {memory}, got:\n{df}'
        assert df.at[0, 'pod_name'] == pod['metadata']['name'], f"Expected {pod['metadata']['name']}, got:\n{df}"
        assert df.at[0, 'namespace'] == pod['metadata']['namespace'], f"Expected {pod['metadata']['namespace']}, got:\n{df}"
