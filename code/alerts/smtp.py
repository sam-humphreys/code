import typing
import smtplib
import ssl
import email.mime.multipart
import email.mime.text
import logging

LOG = logging.getLogger(__name__)

# Default SSL port
SSL_PORT = 465

SMTP_HOST = 'smtp.gmail.com'

EMAIL_TYPE_CHOICES = ['plain', 'html']


class Email(typing.NamedTuple):
    sender_email: str
    receiver_email: str
    subject: str
    text_and_type: typing.List[typing.Tuple[str, str]]

    def build(self) -> str:
        """Build a MIMEMultipart message using self, then convert to string"""
        msg = email.mime.multipart.MIMEMultipart("alternative")
        msg["Subject"] = self.subject
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email

        for i in self.text_and_type:
            text, type_ = i
            assert type_ in EMAIL_TYPE_CHOICES, f'Type {type_} is not in valid choices - {EMAIL_TYPE_CHOICES}'

            part = email.mime.text.MIMEText(text, type_)
            msg.attach(part)

        return msg.as_string()


class Client:
    """Generic Gmail SMTP client for sending emails"""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self.server: smtplib.SMTP_SSL = smtplib.SMTP_SSL(
            host=SMTP_HOST,
            port=SSL_PORT,
            context=ssl.create_default_context(),
        )

        self.server.login(user=self.username, password=self.password)  # Authenticate

    @property
    def is_active(self) -> bool:
        """Check the state of the SMTP server, return simple bool"""
        try:
            code, msg = self.server.noop()
            msg = msg.decode()
        except smtplib.SMTPServerDisconnected as err:
            # SMTP codes - https://serversmtp.com/smtp-error/
            code = 421
            msg = err

        if code != 250:
            LOG.warning(f'Server status is not OK: {code} - {msg}')
            return False

        LOG.info(f'Server status is OK: {code} - {msg}')
        return True

    def send(self, receiver_email: str, subject: str, text_and_type: typing.List[typing.Tuple[str, str]]) -> None:
        """Send an email"""
        email = Email(
            sender_email=self.username,
            receiver_email=receiver_email,
            subject=subject,
            text_and_type=text_and_type,
        )

        email_str = email.build()
        self.server.sendmail(from_addr=self.username, to_addrs=receiver_email, msg=email_str)
        LOG.info(f'Sent email from {self.username}. To {receiver_email}')

    def reconnect(self) -> None:
        """Reconnect SMTP server"""
        if not self.is_active:
            LOG.info('Server already connected')
            pass

        self.server.connect(SMTP_HOST)

    def close(self):
        """Close SMTP server connection if active state"""
        if self.is_active:
            LOG.info('Quitting active server')
            self.server.quit()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
