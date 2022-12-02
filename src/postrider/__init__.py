import dynaconf
import mailbox
import typing as t
from pathlib import Path
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mailer import SMTPConfiguration, Courrier
from queue import ProcessorThread


class Box:

    def __init__(self, path: t.Union[Path, str]):
        self.maildir = mailbox.Maildir(path)

    @staticmethod
    def create_message(origin, targets, subject, text, html=None):
        msg = MIMEMultipart("alternative")
        msg["From"] = origin
        msg["To"] = ','.join(targets)
        msg["Subject"] = subject
        msg.set_charset("utf-8")

        part1 = MIMEText(text, "plain")
        part1.set_charset("utf-8")
        msg.attach(part1)

        if html is not None:
            part2 = MIMEText(html, "html")
            part2.set_charset("utf-8")
            msg.attach(part2)

        return msg

    def post(self, message):
        self.maildir.add(message)


class PostRider:

   def __init__(self, mailer: Courrier, mailbox: Box):
       self.mailer = mailer
       self.mailbox = mailbox
       self.processor = ProcessorThread(
           mailer=mailer,
           mailbox=mailbox
       )



@cli
def run(config: Path, forever: bool = True, debug: bool = False):
    import dynaconf

    settings = dynaconf.Dynaconf(settings_files=[config])
    mailer = Courrier(SMTPConfiguration(**settings.smtp))
    mailbox = Box(settings.box.path)
    postrider = PostRider(smtpconf)
    postrider.processor.run(
        interval=settings.daemon.interval,
        forever=forever
    )

if __name__ == '__main__':
    run()
