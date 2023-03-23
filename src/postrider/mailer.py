import typing as t
import smtplib
import logging
from contextlib import contextmanager


class SMTPConfiguration(t.NamedTuple):
    port: int = 25
    host: str = "localhost"
    user: str = None
    password: str = None
    debug: bool = False


class Courrier:

    def __init__(self, config: SMTPConfiguration):
        self.config = config

    def connect(self):
        server = smtplib.SMTP(self.config.host, str(self.config.port))
        server.set_debuglevel(self.config.debug)
        code, response = server.ehlo()
        if code < 200 or code >= 300:
            raise RuntimeError(
                'Error sending EHLO to the SMTP server '
                f'(code={code}, response={response})'
            )
        # If we can encrypt this session, do it
        if server.has_extn("STARTTLS"):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection
        if self.config.user:
            server.login(self.config.user, self.config.password)
        return server

    @contextmanager
    def sender(self):
        server = self.connect()
        try:
            yield server.send_message
        finally:
            server.close()
