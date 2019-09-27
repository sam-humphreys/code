import string

import hypothesis.strategies as st

import code.alerts.slack
import code.alerts.smtp

text_strategy = st.text(max_size=50)

ascii_text_strategy = st.text(string.ascii_letters, max_size=50)

none_strategy = st.none()

colour_strategy = st.sampled_from(code.alerts.slack.Colours)

email_strategy = st.emails()

slack_event = st.builds(
    code.alerts.slack.Event,
    status=text_strategy,
    colour=colour_strategy,
    message=text_strategy,
)

type_strategy = st.sampled_from(code.alerts.smtp.EMAIL_TYPE_CHOICES)

text_and_type_strategy = st.tuples(ascii_text_strategy, type_strategy)

text_and_type_list_strategy = st.lists(text_and_type_strategy, min_size=1, max_size=3)

smtp_email_strategy = st.builds(
    code.alerts.smtp.Email,
    sender_email=email_strategy,
    receiver_email=email_strategy,
    subject=ascii_text_strategy,
    text_and_type=text_and_type_list_strategy,
)
