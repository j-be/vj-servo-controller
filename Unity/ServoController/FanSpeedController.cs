using UnityEngine;
using System.Collections;

public class FanSpeedController : AbstractSocketioClient {
	private static readonly string SOCKETIO_SERVER = "http://192.168.1.50:5000";
	private static readonly string SOCKETIO_NAMESPACE = "/events";

	public FanSpeedController()
		: base(SOCKETIO_SERVER, SOCKETIO_NAMESPACE){}

	public void SetFanSpeed(int percentage) {
		Emit("unityFanSpeedEvent", percentage);
	}
}
