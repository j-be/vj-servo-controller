import logging.config
import signal

from flask import Flask, send_from_directory, jsonify, request
from flask.ext.socketio import SocketIO, emit

from epos_lib_wrapper import EposLibWrapper
from position_fetcher import PositionFetcher, PositionMinReached, PositionMaxReached

EPOS_RELATIVE_POSITION_HIGH = 20000000
EPOS_RELATIVE_POSITION_LOW = -EPOS_RELATIVE_POSITION_HIGH
EPOS_VELOCITY = 3000

# Instanciate Flask (Static files and REST API)
app = Flask(__name__)
# Instanciate SocketIO (Websockets, used for events) on top of it
socketio = SocketIO(app)
# EPOS2 control library
epos = None
# Position fetcher
position_fetch = None


@app.route('/')
def index():
	return send_from_directory('static', 'index.html')


@app.route('/js/<path:path>')
def static_js_proxy(path):
	return send_from_directory('static/js/', path)


@socketio.on('moveTo', namespace='/servo')
def on_move_to(position):
	logging.error("Got move to %s", position)
	move_to(position)


def move_to(position):
	current_position, is_min, is_max = position_fetch.get_current_position()
	if position < current_position and not is_min:
		move_to_low()
	elif position > current_position and not is_max:
		move_to_high()
	else:
		logging.info("You asked me to move to %s, but position is %s, is_min: %s, is_max: %s",
					 position, current_position, is_min, is_max)


def move_to_low():
	logging.debug("Moving to lower")
	epos.moveToPositionWithVelocity(EPOS_RELATIVE_POSITION_LOW, EPOS_VELOCITY)


def move_to_high():
	logging.debug("Moving to higher")
	epos.moveToPositionWithVelocity(EPOS_RELATIVE_POSITION_HIGH, EPOS_VELOCITY)


def init_epos():
	global epos
	# Instanciate EPOS2 control library
	epos = EposLibWrapper()
	epos.enableDevice()


def init_position_fetcher():
	global position_fetch
	position_fetch = PositionFetcher()
	position_fetch.start()


def sig_term_handler(signum, frame):
	raise KeyboardInterrupt('Signal %i receivied!' % signum)


def main():
	# Initialize logger
	logging.config.fileConfig('log.ini')


	try:
		# Set signal handler for Shutdown
		signal.signal(signal.SIGTERM, sig_term_handler)

		init_position_fetcher()
		init_epos()

		try:
			# Blocking! - Start Flask server
			socketio.run(app, host='0.0.0.0')
		except PositionMinReached:
			logging.warn('Min reached')
		except PositionMaxReached:
			logging.warn('Max reached')
	except KeyboardInterrupt:
		pass
	finally:
		if position_fetch:
			position_fetch.stop()

if __name__ == '__main__':
	main()
