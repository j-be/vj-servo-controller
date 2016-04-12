import logging
import re
import serial
import threading

# Serial communication with Arduino
SERIAL_NAME = '/dev/ttyACM0'
# Regex for a message
REGEX_MSG = '^#[0-9]+ [0-9] [0-9]$'
MSG_TRUE = '1'

class PositionMinReached(Exception):
    pass

class PositionMaxReached(Exception):
    pass

class PositionFetcher(object):
    def __init__(self):
        self.serial_port = None
        self.fetcher_thread = None
        self.current_position = None
        self.is_min = None
        self.is_max = None
        self.msg_pattern = re.compile(REGEX_MSG)

        try:
            # Start logger thread
            self.fetcher_thread = threading.Thread(target=self.fetch_data)

            # Init Serial port
            self.serial_port = serial.Serial(SERIAL_NAME, timeout=1)
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            self.serial_lock = threading.Lock()
        except OSError, error:
            self.serial_port = None
            logging.error("Cannot initialize. Reason: %s", error)
        except serial.serialutil.SerialException, error:
            self.serial_port = None
            logging.error("Cannot initialize. Reason: %s", error)

        logging.debug("Serial: %s", self.serial_port)

    def fetch_data(self):
        while self.serial_port:
            msg = self.serial_port.read()
            if msg:
                logging.debug("Received: %s", msg)
                self.store_data(msg)

    def store_data(self, msg):
        if self.msg_pattern.match(msg):
            data = msg.lstrip('#').split(" ")
            self.current_position = int(data[0])
            cur_is_min = data[1] == MSG_TRUE
            cur_is_max = data[2] == MSG_TRUE

            if not self.is_min and cur_is_min:
                raise PositionMinReached()
            if not self.is_max and cur_is_max:
                raise PositionMaxReached()
        else:
            logging.error("Cannot store data for message: %s! Not matching the pattern.", msg)

    def start(self):
        self.fetcher_thread.start()

    def stop(self):
        # Close serial port
        logging.info("Close serial port")
        if self.serial_port is not None and self.serial_port.isOpen():
            self.serial_port.close()
            self.serial_port = None

    def get_current_position(self):
        return self.current_position, self.is_min, self.is_max
