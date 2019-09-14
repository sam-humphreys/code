import unittest.mock

import hypothesis
import pytest
import kubernetes

import code.k8s.monitoring
import code.k8s.tests.hypothesis_strategies


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
    def test_watch_pods(self, events, namespace, mock_stream, mock_post_event):
        """Test watch pods function can handle mocked event instances"""
        mock_stream.return_value = events
        self.KubernetesClient.watch_pods(namespace)
