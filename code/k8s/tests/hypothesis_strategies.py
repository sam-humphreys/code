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

pod_meta_strategy = st.builds(
    kubernetes.client.models.v1_object_meta.V1ObjectMeta,
    name=text_strategy,
    deletion_timestamp=pod_meta_deletion_ts_strategy,
)

pod_strategy = st.builds(
    kubernetes.client.models.v1_pod.V1Pod,
    metadata=pod_meta_strategy,
    status=pod_status_strategy,
)

event_strategy_type = st.sampled_from(['Added', 'Modified'])

event_strategy = st.fixed_dictionaries({
    'object': pod_strategy,
    'type': event_strategy_type,
})

multiple_event_strategy = st.lists(event_strategy, min_size=0, max_size=10)
