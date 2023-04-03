import time
import logging
import threading


logger = logging.getLogger(__name__)


class ProcessorThread(threading.Thread):

    _running: bool = False

    def __init__(self, mailer, mailbox, interval: float):
        super().__init__(name=__name__)
        self.mailer = mailer
        self.mailbox = mailbox
        self.interval = interval
        self.daemon = True

    def stop(self):
        if self._running:
            self._running = False

    def salvo(self):
        self.mailbox.lock()
        try:
            with self.mailer.sender() as sender:
                for key, message in self.mailbox.iteritems():
                    if not self._running:
                        logger.warning('Processor was stopped.')
                        raise StopIteration('Thread has stopped running')
                    logger.debug(f'Sending {key}.')
                    sender(message)
                    logger.debug(f'Discarding {key}.')
                    self.mailbox.discard(key)
        finally:
            self.mailbox.close()

    def run(self, forever: bool = True):
        self._running = True
        self.salvo()
        if forever:
            time.sleep(self.interval)
            while self._running:
                try:
                    self.salvo()
                    logger.debug(f'Sleeping for {self.interval}.')
                    time.sleep(self.interval)
                except:
                    self._running = False
                    raise
