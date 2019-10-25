import datetime

import hypothesis.strategies as st
import kubernetes

text_strategy = st.text()

pod_status_phase = st.sampled_from(['Pending', 'Running'])

pod_status_strategy = st.builds(
    kubernetes.client.models.V1PodStatus,
    phase=pod_status_phase,
)

# Deletion timestamp can trigger different behaviour, so try with & without
pod_meta_deletion_ts_strategy = st.sampled_from([None, datetime.datetime(2019, 9, 14)])

kube_meta_strategy = st.builds(
    kubernetes.client.models.v1_object_meta.V1ObjectMeta,
    name=text_strategy,
    deletion_timestamp=pod_meta_deletion_ts_strategy,
)

pod_strategy = st.builds(
    kubernetes.client.models.v1_pod.V1Pod,
    metadata=kube_meta_strategy,
    status=pod_status_strategy,
)

event_strategy_type = st.sampled_from(['Added', 'Modified'])

event_strategy = st.fixed_dictionaries({
    'object': pod_strategy,
    'type': event_strategy_type,
})

multiple_event_strategy = st.lists(event_strategy, min_size=3, max_size=10, unique_by=(lambda x: x['object'].metadata.name))

namespace_strategy = st.builds(
    kubernetes.client.models.v1_namespace.V1Namespace,
    metadata=kube_meta_strategy,
)

namespace_list_strategy = st.builds(
    kubernetes.client.models.v1_namespace_list.V1NamespaceList,
    items=st.lists(namespace_strategy, min_size=0, max_size=3),
)

api_metrics_cpu_memory_strategy = st.fixed_dictionaries({
    'cpu': st.from_regex('([0-9]{1,5})n', fullmatch=True),
    'memory': st.from_regex('([0-9]{1,5})Ki', fullmatch=True),
})

api_metrics_containers_usage_strategy = st.fixed_dictionaries({'usage': api_metrics_cpu_memory_strategy})

api_metrics_containers_list_strategy = st.lists(api_metrics_containers_usage_strategy, min_size=1, max_size=3)

api_metrics_metadata_strategy = st.fixed_dictionaries({
    'name': text_strategy,
    'namespace': text_strategy,
})

api_metrics_pod_strategy = st.fixed_dictionaries({
    'metadata': api_metrics_metadata_strategy,
    'containers': api_metrics_containers_list_strategy,
})
