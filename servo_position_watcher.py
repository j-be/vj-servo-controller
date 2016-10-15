import logging
from enum import Enum
from Queue import Empty
from multiprocessing import Process, Queue

from epos_lib_wrapper import EposLibWrapper
from position_fetcher import PositionFetcher

MOVE_STOPPED = 0
MOVE_TO_HIGH = 1
MOVE_TO_LOW = 2

EPOS_RELATIVE_POSITION = 20000000
EPOS_SHORT_PULL_POSITION = 80000
EPOS_VELOCITY = 4840
EPOS_ACCELERATION = long(pow(2, 32) - 1)


class CommandType(Enum):
    enable = 0
    stop = 1
    move_to = 2
    reset_center = 3
    shutdown = -1


class Command(object):
    def __init__(self, command_type):
        self.commandType = command_type

    def get_type(self):
        return self.commandType


class EnableCommand(Command):
    def __init__(self):
        super(EnableCommand, self).__init__(CommandType.enable)


class StopCommand(Command):
    def __init__(self):
        super(StopCommand, self).__init__(CommandType.stop)


class MoveToCommand(Command):
    def __init__(self, position, velocity = None, acceleration = None):
        super(MoveToCommand, self).__init__(CommandType.move_to)
        self.position = position
        self.acceleration = acceleration
        self.velocity = velocity

    def get_position(self):
        if self.position:
            return self.position
        return EPOS_VELOCITY

    def get_velocity(self):
        if self.velocity:
            return self.velocity
        return EPOS_VELOCITY

    def get_acceleration(self):
        if self.acceleration:
            return self.acceleration
        return EPOS_ACCELERATION


class ResetCenterCommand(Command):
    def __init__(self):
        super(ResetCenterCommand, self).__init__(CommandType.reset_center)


class PositionWatcher(Process):
    def __init__(self, command_queue):
        super(PositionWatcher, self).__init__()
        self.log = logging.getLogger(PositionWatcher.__name__)
        # Queues for inbound and outbound
        self.command_queue = command_queue
        self.position_queue = None
        self.position_fetcher = None
        self.go_on = True
        # EPOS2 control library
        self.epos = EposLibWrapper()
        # Move direction
        self.move = MOVE_STOPPED
        # Command handlers
        self.handler = self._get_command_handler()
        # Position stuff
        self.target_position = 512
        self.offset = 0
        self.current_position = None

    def get_command_queue(self):
        return self.command_queue

    def _epos_enable(self, _ = None):
        self.epos.enableDevice()
        self.move = MOVE_STOPPED

    def _epos_move_to(self, command):
        self.target_position = command.get_position()
        # TODO: vel and accel

    def move_to_low(self):
        if self.move != MOVE_TO_LOW:
            self.log.debug("Moving to lower")
            self.epos.moveToPositionWithVelocity(-EPOS_RELATIVE_POSITION, EPOS_VELOCITY)
        self.move = MOVE_TO_LOW

    def move_to_high(self):
        if self.move != MOVE_TO_HIGH:
            self.log.debug("Moving to higher")
            self.epos.moveToPositionWithVelocity(EPOS_RELATIVE_POSITION, EPOS_VELOCITY)
        self.move = MOVE_TO_HIGH

    def dont_move(self):
        if self.epos.isEnabled() and self.move != MOVE_STOPPED:
            self.log.debug("Not moving")
            self.epos.moveToPositionWithVelocity(0, 0)
        self.move = MOVE_STOPPED

    def _position_reset_center(self, _):
        self.offset = 512 - self.current_position.get_position()

    def _epos_stop(self, _ = None):
        self.log.info("Stopping")
        self.epos.stop()
        self.move = MOVE_STOPPED

    def run(self):
        self.log.info("Starting position watcher process")
        self.position_queue = Queue(10)
        self.position_fetcher = PositionFetcher(self.position_queue)
        self.position_fetcher.start()

        try:
            while self.go_on:
                self._position_queue_handler()
                self.log.debug("Fetched position")
                self._command_queue_handler()
                self.log.debug("Handled command")
                self._watch_position()
                self.log.debug("Watched position")
        except KeyboardInterrupt:
            self.go_on = False
        except Exception, e:
            self.log.error("Exception in run: " + str(e))
        finally:
            self.position_fetcher.stop()
            self.position_fetcher.join()

        self.log.error("stopped")

    def stop(self):
        self.go_on = False

    def _command_queue_handler(self):
        try:
            command = self.command_queue.get(False)
            self.log.info("Got command: " + str(command.get_type()))
            if command:
                self.handler[command.get_type()](command)
        except Empty:
            pass

    def _watch_position(self):
        if not self.epos.isEnabled():
            return

        position = self.target_position - self.offset
        if position < self.current_position.get_position():
            self.move_to_low()
        elif position > self.current_position.get_position():
            self.move_to_high()
        else:
            self.dont_move()

    def _position_queue_handler(self):
        try:
            while True:
                self.current_position = self.position_queue.get(False)
        except Empty:
            pass

    def _get_command_handler(self):
        return {
            CommandType.enable: self._epos_enable,
            CommandType.move_to: self._epos_move_to,
            CommandType.reset_center: self._position_reset_center,
            CommandType.stop: self._epos_stop
        }
