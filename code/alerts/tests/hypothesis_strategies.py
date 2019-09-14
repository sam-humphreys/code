import hypothesis.strategies as st

import code.alerts.slack

text_strategy = st.text(max_size=50)

none_strategy = st.none()

colour_strategy = st.sampled_from(code.alerts.slack.Colours)

slack_event = st.builds(
    code.alerts.slack.Event,
    status=text_strategy,
    colour=colour_strategy,
    message=text_strategy,
)
