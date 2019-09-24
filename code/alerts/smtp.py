import typing
import smtplib
import ssl
import email.mime.multipart
import email.mime.text

# Default SSL port
SSL_PORT = 465

EMAIL_TYPE_CHOICES = ['plain', 'html']


class Email(typing.NamedTuple):
    sender_email: str
    receiver_email: str
    subject: str
    text_and_type: typing.List[typing.Tuple[str, str]]

    def build(self) -> email.mime.multipart.MIMEMultipart:
        msg = email.mime.multipart.MIMEMultipart("alternative")
        msg["Subject"] = self.subject
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email

        for i in self.text_and_type:
            text, type_ = i
            assert type_ in EMAIL_TYPE_CHOICES, f'Type {type_} is not in valid choices - {EMAIL_TYPE_CHOICES}'

            part = email.mime.text.MIMEText(text, type_)
            msg.attach(part)

        return msg


class Client:
    """Generic SMTP client for sending emails"""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self.server: smtplib.SMTP_SSL = smtplib.SMTP_SSL(
            host="smtp.gmail.com",
            port=SSL_PORT,
            context=ssl.create_default_context(),
        )

        self.server.login(user=self.username, password=self.password)  # Authenticate

    def _server_is_active(self) -> bool:
        """Check the state of the SMTP server, return simple bool"""
        code, msg = self.server.noop()
        if code != 250:
            return False

        return True

    @property
    def is_active(self) -> bool:
        return self._server_is_active()

    def send(self, receiver_email: str, subject: str, text_and_type: typing.List[typing.Tuple[str, str]]):
        email = Email(
            sender_email=self.username,
            receiver_email=receiver_email,
            subject=subject,
            text_and_type=text_and_type,
        )

        email_str = email.build().as_string()
        self.server.sendmail(from_addr=self.username, to_addrs=receiver_email, msg=email_str)

    def close(self):
        """Close SMTP server connection if active state"""
        if self._server_is_active():
            self.server.quit()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
