import typing
import json
import logging
import time
import enum

import requests

LOG = logging.getLogger(__name__)

ALERTS_CHANNEL = 'https://hooks.slack.com/services/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'


class Colours(enum.Enum):
    ERROR = 'danger'
    SUCCESS = 'good'
    WARNING = 'warning'
    NEUTRAL = '#439FE0'


class Event(typing.NamedTuple):
    status: str
    message: str
    colour: Colours

    def build(self) -> typing.Dict[str, typing.Union[str, int]]:
        """
        Event template message builder
        Docs - https://api.slack.com/docs/message-attachments
        """
        return {
            "attachments": [
                {
                    "fallback": self.status.title(),
                    "color": self.colour.value,
                    "title": f"{self.status.title()}",
                    "title_link": 'https://console.cloud.google.com/home/dashboard',
                    "fields": [
                        {
                            "title": "Event",
                            "value": self.message,
                            "short": "False"
                        },
                    ],
                    "ts": int(time.time()),
                },
            ],
        }


def post_event(event: Event) -> None:
    """
    Post event to Slack channel
    Docs: https://api.slack.com/incoming-webhooks
    """
    event = event.build()
    requests.post(ALERTS_CHANNEL, data=json.dumps(event))
    LOG.info(f'Posted {event} to {ALERTS_CHANNEL}')
