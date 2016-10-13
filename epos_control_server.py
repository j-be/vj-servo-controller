#!/usr/bin/python

import logging.config
import signal
from multiprocessing import Process, Value

from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO

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

POTI_OFFSET = 0

# Initialize logger
logging.config.fileConfig('log.ini')

# Instanciate Flask (Static files and REST API)
app = Flask(__name__)
# Instanciate SocketIO (Websockets, used for events) on top of it
socketio = SocketIO(app)
# EPOS2 control library
epos = EposLibWrapper()
# Position fetcher
position_fetch = PositionFetcher()
# Is servo enabled
is_enabled = None
# Move direction
move = MOVE_STOPPED

# Run condition for watcher process
watch_position = Value('b', True)
# Target position
target_position = Value('i', 512)


def truncate_position(input_position):
	try:
		ret = int(input_position)
		ret = min(ret, 723)
		ret = max(ret, 300)
		return ret - POTI_OFFSET
	except Exception:
		return 512 - POTI_OFFSET


def set_target_position(position):
	with target_position.get_lock():
		target_position.value = truncate_position(position)


def change_target_position(position_delta):
	with target_position.get_lock():
		target_position.value = truncate_position(int(target_position.value) + position_delta)


@app.route('/')
def index():
	return send_from_directory('static', 'index.html')


@app.route('/js/<path:path>')
def static_js_proxy(path):
	return send_from_directory('static/js/', path)


@socketio.on('enable', namespace='/servo')
def on_enable(dummy=None):
	global move

	epos.enableDevice()
	move = MOVE_STOPPED


@socketio.on('moveTo', namespace='/servo')
def on_move_to(position):
	logging.debug("Got move to %s", position)
	set_target_position(position)


@socketio.on('stop', namespace='/servo')
def on_stop():
	stop()


@socketio.on('pullToLeft', namespace='/servo')
def on_pull_to_left():
	epos.moveToPositionWithVelocity(-EPOS_SHORT_PULL_POSITION, EPOS_VELOCITY)
	change_target_position(-MOVE_DELTA_SHORT_PULL)


@socketio.on('pullToRight', namespace='/servo')
def on_pull_to_right():
	epos.moveToPositionWithVelocity(EPOS_SHORT_PULL_POSITION, EPOS_VELOCITY)
	change_target_position(MOVE_DELTA_SHORT_PULL)


@socketio.on('resetCenter', namespace='/servo')
def reset_center():
	global POTI_OFFSET
	POTI_OFFSET = 512 - position_fetch.get_current_position()[0]


@app.route('/enable/', methods=['POST'])
def enable_post():
	on_enable()
	return jsonify({'error': 0}), 200


@app.route('/moveto/', methods=['POST'])
def move_to_post():
	on_move_to(request.json['position'])
	return jsonify({'error': 0}), 200


@app.route('/stop/', methods=['POST'])
def stop_post():
	on_stop()
	return jsonify({'error': 0}), 200


def move_to(position):
	if not epos.isEnabled():
		return
	current_position, is_end = position_fetch.get_current_position()
	logging.debug("Move to position %s, current is %s", position, current_position)
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

	logging.info("Stopping")
	epos.stop()
	move = MOVE_STOPPED


def position_watcher(target_position, watch_position):
	while watch_position.value:
		move_to(target_position.value)
	logging.error("Position watcher stopped")


def sig_term_handler(signum, frame):
	raise KeyboardInterrupt('Signal %i receivied!' % signum)


def main():
	global watch_position
	watcher = None

	try:
		# Set signal handler for Shutdown
		signal.signal(signal.SIGTERM, sig_term_handler)

		position_fetch.start()
		epos.openDevice()

		watcher = Process(target=position_watcher, args=(target_position, watch_position,))
		watcher.start()

		stop()

		# Blocking! - Start Flask server
		socketio.run(app, host='0.0.0.0')
	except KeyboardInterrupt:
		pass
	finally:
		if position_fetch:
			position_fetch.stop()
		watch_position.value = False
		if watcher:
			watcher.join()
		logging.error("Cleanup done, exiting")
		stop()

if __name__ == '__main__':
	main()
