using UnityEngine;
using SocketIOClient;

public class ServoControllerClient : AbstractSocketioClient {
	private static readonly string SOCKETIO_SERVER = "http://192.168.1.51:5000";
	private static readonly string SOCKETIO_NAMESPACE = "/servo";

	public ServoControllerClient()
		: base(SOCKETIO_SERVER, SOCKETIO_NAMESPACE){}

	/* -------------------- */
	/* - Eventemitter     - */
	/* -------------------- */
	public void EventSetServoPosition(long position) {
		this.Emit("moveTo", position);
	}

	public void EventStop() {
		this.Emit("stop");
	}

	public void PullToLeft() {
	    this.Emit("pullToLeft");
	}

	public void PullToRight() {
	    this.Emit("pullToRight");
	}
}
