import logging
import typing as t
from mailbox import Mailbox, Maildir
from pathlib import Path
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from minicli import cli, run
from .mailer import SMTPConfiguration, Courrier
from .queue import ProcessorThread


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


def configure_logging(settings, debug: bool = False):
    import sys
    import logging

    log_level = logging.DEBUG if debug else settings.logging.level
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(log_level)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(module)s %(message)s',
        handlers=[stream_handler]
    )


@cli
def sender(config: Path, forever: bool = True, debug: bool = False):
    from dynaconf import Dynaconf

    settings = Dynaconf(settings_files=[config])
    configure_logging(settings, debug=debug)
    mailer = Courrier(SMTPConfiguration(**settings.smtp))

    workers = {}
    for name, conf in settings.box.items():
        path = Path(conf.path).resolve()
        assert path not in workers
        mailbox = Maildir(path)
        interval = settings.worker[name].get('interval', 5.0)
        workers[path] = ProcessorThread(mailer, mailbox, interval)

    for name, worker in workers.items():
        worker.start()

    for name, worker in workers.items():
        worker.join()


@cli
def testmail(config: Path, boxname: str):
    from dynaconf import Dynaconf

    settings = Dynaconf(settings_files=[config])
    mailbox = Maildir(settings.box[boxname].path)
    msg = create_message(
        'test@test.org',
        ['trollfot@gmail.com'],
        'This is a subject',
        'This is my email'
    )
    mailbox.add(msg)


def clirunner():
    run()

if __name__ == '__main__':
    run()
