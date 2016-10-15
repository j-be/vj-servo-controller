import logging
import logging.config
import re
from multiprocessing import Process, Queue
from serial import Serial
from serial.serialutil import SerialException
from threading import Lock


# Serial communication with Arduino
SERIAL_NAME = '/dev/ttyUSB0'
SERIAL_BAUDRATE =115200
# Regex for a message
REGEX_MSG = '^#[0-9]+ [0-9]$'
MSG_TRUE = '1'


class FetchedPosition(object):
    def __init__(self, position, end):
        self.position = position
        self.end = end

    def get_position(self):
        return self.position

    def is_end(self):
        return self.end


class PositionFetcher(Process):
    def __init__(self, position_queue):
        super(PositionFetcher, self).__init__()
        self.log = logging.getLogger(PositionFetcher.__name__)
        self.current_position = None
        self.is_end = None
        self.serial_port = None
        self.msg_pattern = re.compile(REGEX_MSG)
        self.position_queue = position_queue
        self.serial_lock = Lock()

    def init_serial(self):
        try:
            self.serial_port = Serial(SERIAL_NAME, timeout=1, baudrate=SERIAL_BAUDRATE)
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
        except (OSError, SerialException) as error:
            self.stop()
            self.log.error("Cannot initialize. Reason: %s", error)

        self.log.debug("Serial: %s", self.serial_port)

    def fetch_data(self):
        self.serial_port.flushInput()
        while self.serial_port.read() != '#':
            pass
        msg = "#" + self.serial_port.readline().strip()
        if msg:
            self.log.debug("Received: %s", msg)
            self.store_data(msg)

    def store_data(self, msg):
        if self.msg_pattern.match(msg):
            data = msg.lstrip('#').split(" ")
            if data and len(data) == 2:
                self.current_position = int(data[0])
                self.is_end = data[1] == MSG_TRUE
                self.position_queue.put(FetchedPosition(int(data[0]), data[1] == MSG_TRUE))
        else:
            self.log.info("Cannot store data for message: %s! Not matching the pattern.", msg)

    def stop(self):
        # Close serial port
        self.log.info("Close serial port")
        if self.serial_port is not None and self.serial_port.isOpen():
            self.serial_port.close()
            self.serial_port = None
        else:
            self.log.warn("Already closed")

    def _get_current_position(self):
        if self.serial_port:
            return self.current_position, self.is_end

    def run(self):
        self.init_serial()

        try:
            while self.serial_port:
                self.fetch_data()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

        self.log.error("stopped")


if __name__ == "__main__":
    logging.config.fileConfig('log.ini')
    tester = PositionFetcher(Queue(10))
    tester.start()
    try:
        while True:
            pass
    finally:
        tester.stop()
