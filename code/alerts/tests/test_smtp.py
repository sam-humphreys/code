import unittest
import unittest.mock

import hypothesis

import code.alerts.smtp
import code.alerts.tests.hypothesis_strategies


@hypothesis.given(code.alerts.tests.hypothesis_strategies.smtp_email_strategy)
def test_email(email):
    """Test Email class is built successfully"""
    assert isinstance(email, code.alerts.smtp.Email), f'Email incorrectly built - {type(email)}'


@hypothesis.given(code.alerts.tests.hypothesis_strategies.smtp_email_strategy)
def test_email_build(email):
    """Test Email class is built successfully into a string"""
    def _check_string(build, prefix, string):
        expected = f'{prefix}: {string}' if string not in ['', ' '] else f'{prefix}:'
        assert expected in build, f'{expected} is not in built string:\n{build}'

    build = email.build()

    assert isinstance(build, str), f'Expected str got {type(build)}'

    _check_string(build, 'Subject', email.subject)
    _check_string(build, 'From', email.sender_email)
    _check_string(build, 'To', email.receiver_email)

    for i in email.text_and_type:
        assert i[0] in build, f'"{i[0]}" not found in build:\n{build}'


class TestSmtpClient(unittest.TestCase):
    """
    SMTP Client - created to pass around one client
    rather than create many and lose time

    Docs:
        - https://docs.python.org/3/library/unittest.html#unittest.TestCase
    """
    @unittest.mock.patch('smtplib.SMTP_SSL.login')
    def setUp(self, client):
        self.client = code.alerts.smtp.Client(
            username='test@client.com',
            password='password',
            testing=True,
        )

    def test_is_active(self):
        """Test client is active property method"""
        code, msg = self.client.server.noop()

        assert code == 250, f'Client is not active. Code - {code}. Message - {msg}'
        assert self.client.is_active, 'Client is not active'

    @hypothesis.given(
        receiver_email=code.alerts.tests.hypothesis_strategies.email_strategy,
        subject=code.alerts.tests.hypothesis_strategies.ascii_text_strategy,
        text_and_type=code.alerts.tests.hypothesis_strategies.text_and_type_list_strategy,
    )
    def test_send(self, receiver_email, subject, text_and_type):
        """Test the client send mail (cannot assert on exact message due to uniqueness of MIME type)"""
        # Mocking inside func to avoid Hypothesis Flaky errors (unittest recommended)
        with unittest.mock.patch('smtplib.SMTP_SSL.sendmail') as mock_sendmail:
            self.client.send(receiver_email, subject, text_and_type)

            mock_sendmail.assert_called_once()

            kall = mock_sendmail.call_args
            args, kwargs = kall

            assert kwargs['from_addr'] == self.client.username, f"Expected: {self.client.username}\nGot: {kwargs['from_addr']}"
            assert kwargs['to_addrs'] == receiver_email, f"Expected: {receiver_email}\nGot: {kwargs['to_addrs']}"

    def test_close_and_reconnect(self):
        """Test the client close function (quitting SMTP server) & reconnecting post close"""
        assert self.client.is_active, 'Client must be active to test quit'

        self.client.close()

        assert not self.client.is_active, 'Client must be inactive following close call'

        self.client.reconnect()

        assert self.client.is_active, 'Client must be active after reconnecting'
