import time
import logging
import threading


logger = logging.getLogger(__name__)


class ProcessorThread(threading.Thread):

    _running: bool = False

    def __init__(self, mailer, mailbox):
        super().__init__(name=__name__)
        self.mailer = mailer
        self.mailbox = mailbox
        self.setDaemon(True)

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

    def run(self, interval: float = 5.0, forever: bool = True):
        self._running = True
        while self._running:
            try:
                self.salvo()
                logger.debug(f'Sleeping for {interval}.')
                time.sleep(interval)
            except:
                self._running = False
                raise
