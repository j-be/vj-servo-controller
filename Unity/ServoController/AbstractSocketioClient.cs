using UnityEngine;
using System.Collections;
using SocketIO;

public abstract class AbstractSocketioClient : SocketIOComponent {

	public AbstractSocketioClient(string url, string messageNamespace)
		:base(url, messageNamespace){}

	/* ------------------------- */
	/* - Generic event handler - */
	/* ------------------------- */
	private void SocketError(SocketIOEvent e) {
		Debug.LogError(e.data.Print());
	}

	private void SocketMessage(SocketIOEvent e) {
		Debug.Log ("[SocketIO] Got event: " + e.name + "-" + e.data);
	}
}
