import unittest.mock
import json

import hypothesis
import pytest

import code.alerts.slack
import code.alerts.tests.hypothesis_strategies


@hypothesis.given(event=code.alerts.tests.hypothesis_strategies.slack_event)
def test_build_event(event: code.alerts.slack.Event):
    """Test the building of a slack message is accurate given the inputs"""
    build = event.build()
    build = build['attachments'].pop()  # Only one item in this list
    fields = build['fields'].pop()

    assert build['title'] == event.status.title(), \
        f"Title is incorrect:\nGot - {build['title']}\nShould be - {event.status.title()}"

    assert fields['value'] == event.message, \
        f"Message does not match provided:\nGot - {fields['value']}. Provided - {event.message}"


@unittest.mock.patch('requests.post')
@unittest.mock.patch('time.time', unittest.mock.MagicMock(return_value=12345))
@hypothesis.given(event=code.alerts.tests.hypothesis_strategies.slack_event)
def test_post_slack_event(event: code.alerts.slack.Event, mock_post):
    """Test posting to Slack using the inputs provided. Mock the actual post"""
    code.alerts.slack.post_event(event)

    mock_post.assert_called_with(
        code.alerts.slack.ALERTS_CHANNEL,
        data=json.dumps(event.build()),
    )
