import unittest.mock

import hypothesis
import pytest
import kubernetes

import code.k8s.monitoring
import code.k8s.tests.hypothesis_strategies
import code.alerts.slack


@pytest.fixture(scope='class')
def client(request):
    with unittest.mock.patch('kubernetes.config.load_kube_config'):
        client = code.k8s.monitoring.KubernetesClient(local=True)
        request.cls.KubernetesClient = client


@pytest.mark.usefixtures('client')
class TestKubernetesClient(unittest.TestCase):

    def test_client(self):
        """Test client instance has been built accurately"""
        assert isinstance(self.KubernetesClient.client, kubernetes.client.apis.core_v1_api.CoreV1Api), \
            f'Client is not a CoreV1Api instance - {type(self.KubernetesClient.client)}'

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
