#!/usr/bin/python

import logging.config
import signal
from multiprocessing import Queue

from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO

from servo_position_watcher import EnableCommand, MoveToCommand, StopCommand, ResetCenterCommand, PositionWatcher, GetStatusCommand


# Initialize logger
logging.config.fileConfig('log.ini')
# Instanciate Flask (Static files and REST API)
app = Flask(__name__)
# Instanciate SocketIO (Websockets, used for events) on top of it
socketio = SocketIO(app)
# Position command queue
watcher_command_queue = None
# Staus queue
status_readout_queue = None


@app.route('/')
def index():
	return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
	return send_from_directory('static/', path)


@app.route('/status', methods=['GET'])
def get_status():
	watcher_command_queue.put(GetStatusCommand())
	status = status_readout_queue.get()
	logging.info("Got status=" + str(status))
	return jsonify(status)

@socketio.on('enable', namespace='/servo')
def on_enable(_ = None):
	logging.info("Got enable")
	watcher_command_queue.put(EnableCommand())


@socketio.on('moveTo', namespace='/servo')
def on_move_to(position):
	logging.debug("Got move to %s", position)
	watcher_command_queue.put(MoveToCommand(int(position)))


@socketio.on('stop', namespace='/servo')
def on_stop(_ = None):
	watcher_command_queue.put(StopCommand())


@socketio.on('resetCenter', namespace='/config')
def reset_center():
	logging.error("Resetting center")
	watcher_command_queue.put(ResetCenterCommand())


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


def sig_term_handler(signum, _):
	raise KeyboardInterrupt('Signal %i receivied!' % signum)


def main():
	global watcher_command_queue
	global status_readout_queue
	watcher = None

	try:
		# Set signal handler for Shutdown
		signal.signal(signal.SIGTERM, sig_term_handler)

		watcher = PositionWatcher(Queue(10))
		watcher_command_queue = watcher.get_command_queue()
		status_readout_queue = watcher.get_status_queue()
		watcher.start()

		watcher_command_queue.put(StopCommand())

		# Blocking! - Start Flask server
		socketio.run(app, host='0.0.0.0')
	except KeyboardInterrupt:
		pass
	finally:
		if watcher:
			watcher.stop()
			watcher.join()
		logging.error("Cleanup done, exiting")

if __name__ == '__main__':
	main()
