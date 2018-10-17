using UnityEngine;
using System.Collections;

public class WaterSplasherController : AbstractSocketioClient {
	private static readonly string SOCKETIO_SERVER = "ws://192.168.1.50:5000";
	private static readonly string SOCKETIO_NAMESPACE = "/events";

	public WaterSplasherController()
		: base(SOCKETIO_SERVER, SOCKETIO_NAMESPACE){}

	public void SetWatersplasher(bool state) {
        string stateStr = "0";

        if (state)
            stateStr = "1";

		Emit("unityWaterSplasherEvent", new JSONObject(stateStr));
	}
}
