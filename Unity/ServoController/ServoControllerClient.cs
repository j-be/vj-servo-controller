using UnityEngine;

public class ServoControllerClient : AbstractSocketioClient {
	private static readonly string SOCKETIO_SERVER = "ws://192.168.1.51:5000";
	private static readonly string SOCKETIO_NAMESPACE = "/servo";

	public ServoControllerClient()
		: base(SOCKETIO_SERVER, SOCKETIO_NAMESPACE){}

	/* -------------------- */
	/* - Eventemitter     - */
	/* -------------------- */
	public void EventSetServoPosition(long position) {
		Debug.LogWarning("Set servo to: " + position);
		this.Emit("moveTo", new JSONObject(position));
	}

	public void EventStop() {
		this.Emit("stop");
	}

	public void EventEnable() {
		this.Emit("enable");
	}

	public void PullToLeft() {
	    this.Emit("pullToLeft");
	}

	public void PullToRight() {
	    this.Emit("pullToRight");
	}
}
