import logging
from time import sleep

MESSAGE = '600 1'

class MockSerial(object):
    def __init__(self):
        self.log = logging.getLogger(MockSerial.__name__)
        self.is_open = True
        self.log.error("Serial running on mock!")

    def read(self):
        sleep(0.02)
        return '#'

    def readline(self):
        if not self.is_open:
            self.log.critical("Call to readline when Serial is already closed!")
            raise Exception("Call to readline when Serial is already closed!")
        #self.log.error("Mock serial returns " + MESSAGE)
        return MESSAGE

    def close(self):
        self.log.error("Close mock serial")
        self.is_open = False

    def isOpen(self):
        return self.is_open

    def flushInput(self):
        pass
