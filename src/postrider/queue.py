import time
import threading


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
                        raise StopIteration('Thread has stopped running')
                    sender(message)
                    self.mailbox.discard(key)
        finally:
            self.mailbox.close()

    def run(self, interval: float = 5.0, forever: bool = True):
        self._running = True
        while self._running:
            try:
                self.salvo()
                time.sleep(interval)
            except:
                self._running = False
                raise
