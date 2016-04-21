#!/usr/bin/python

import logging.config
import signal
import threading

from flask import Flask, send_from_directory
from flask.ext.socketio import SocketIO

from epos_lib_wrapper import EposLibWrapper
from position_fetcher import PositionFetcher

POSITION_MAX_DELTA_TO_END = 0

EPOS_RELATIVE_POSITION = 20000000
EPOS_SHORT_PULL_POSITION = 80000
EPOS_VELOCITY = 4840

MOVE_STOPPED = 0
MOVE_TO_HIGH = 1
MOVE_TO_LOW = 2

MOVE_DELTA_SHORT_PULL = 100

# Instanciate Flask (Static files and REST API)
app = Flask(__name__)
# Instanciate SocketIO (Websockets, used for events) on top of it
socketio = SocketIO(app)
# EPOS2 control library
epos = None
# Position fetcher
position_fetch = None
# Watch position
watch_position = True
# Is servo enabled
is_enabled = None
# Target position
target_position = 512
# Move direction
move = MOVE_STOPPED


@app.route('/')
def index():
	return send_from_directory('static', 'index.html')


@app.route('/js/<path:path>')
def static_js_proxy(path):
	return send_from_directory('static/js/', path)


@socketio.on('enable', namespace='/servo')
def on_enable(dummy=None):
	global is_enabled
	global move

	is_enabled = True
	epos.enableDevice()
	move = MOVE_STOPPED


@socketio.on('moveTo', namespace='/servo')
def on_move_to(position):
	global target_position
	logging.debug("Got move to %s", position)
	target_position = position


@socketio.on('stop', namespace='/servo')
def on_stop():
	stop()


@socketio.on('pullToLeft', namespace='/servo')
def on_pull_to_left():
	#epos.moveToPositionWithVelocity(-EPOS_SHORT_PULL_POSITION, EPOS_VELOCITY)
	global target_position
	target_position -= MOVE_DELTA_SHORT_PULL


@socketio.on('pullToRight', namespace='/servo')
def on_pull_to_right():
	epos.moveToPositionWithVelocity(EPOS_SHORT_PULL_POSITION, EPOS_VELOCITY)
	global target_position
	target_position += MOVE_DELTA_SHORT_PULL

def truncate_position(input_position):
	try:
		ret = int(input_position)
		ret = min(ret, 923)
		ret = max(ret, 100)
		return ret
	except Exception:
		return 512


def move_to(target_position):
	if not is_enabled:
		return
	position = truncate_position(target_position)
	current_position, is_end = position_fetch.get_current_position()
	logging.info("Move to position %s, current is %s", position, current_position)
	if position < current_position:
		move_to_low()
	elif position > current_position:
		move_to_high()
	else:
		logging.info("You asked me to move to %s, but position is %s, is_end: %s",
					 position, current_position, is_end)
		epos.moveToPositionWithVelocity(0, 0)


def move_to_low():
	global move
	if move != MOVE_TO_LOW:
		logging.debug("Moving to lower")
		epos.moveToPositionWithVelocity(-EPOS_RELATIVE_POSITION, EPOS_VELOCITY)
	move = MOVE_TO_LOW


def move_to_high():
	global move
	if move != MOVE_TO_HIGH:
		logging.debug("Moving to higher")
		epos.moveToPositionWithVelocity(EPOS_RELATIVE_POSITION, EPOS_VELOCITY)
	move = MOVE_TO_HIGH


def stop():
	global move
	global is_enabled

	logging.info("Stopping")
	epos.stop()
	move = MOVE_STOPPED
	is_enabled = False


def init_epos():
	global epos
	# Instanciate EPOS2 control library
	epos = EposLibWrapper()
	epos.openDevice()


def init_position_fetcher():
	global position_fetch
	position_fetch = PositionFetcher()
	position_fetch.start()


def position_watcher():
	while watch_position:
		move_to(target_position)
	logging.error("Position watcher stopped")


def sig_term_handler(signum, frame):
	raise KeyboardInterrupt('Signal %i receivied!' % signum)


def main():
	global watch_position
	# Initialize logger
	logging.config.fileConfig('log.ini')


	try:
		# Set signal handler for Shutdown
		signal.signal(signal.SIGTERM, sig_term_handler)

		init_position_fetcher()
		init_epos()

		watcher_thread = threading.Thread(target=position_watcher)
		watcher_thread.start()

		stop()

		# Blocking! - Start Flask server
		socketio.run(app, host='0.0.0.0')
	except KeyboardInterrupt:
		pass
	finally:
		if position_fetch:
			position_fetch.stop()
		watch_position = False
		logging.error("Cleanup done, exiting")
		stop()

if __name__ == '__main__':
	main()
