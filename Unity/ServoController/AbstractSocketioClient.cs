using UnityEngine;
using System.Collections;
using SocketIOClient;

public abstract class AbstractSocketioClient {
	private IEndPointClient socket;
	private Client client;

	public AbstractSocketioClient(string url, string socketNamespace) {
		this.InitSocket(url, socketNamespace);
	}

	// Use this for initialization
	private void InitSocket (string url, string socketNamespace, bool debugEnabled = false) {
		client = new Client(url);

		client.Error += SocketError;
		if (debugEnabled)
			client.Message += SocketMessage;

		socket = client.Connect (socketNamespace);
	}

	protected void Emit(string eventName, object payload = null, System.Action<object> callBack = null) {
		socket.Emit(eventName, payload, callBack);
	}

	protected void On(string eventName, System.Action<SocketIOClient.Messages.IMessage> handler) {
		socket.On(eventName, handler);
	}

	public void Close() {
		client.Close();
	}

	/* ------------------------- */
	/* - Generic event handler - */
	/* ------------------------- */
	private void SocketError(object sender, SocketIOClient.ErrorEventArgs e) {
		Debug.LogError(e.Message);
	}

	private void SocketMessage(object sender, SocketIOClient.MessageEventArgs e) {
		Debug.Log ("[SocketIO] Got event: " + e.Message.Event + "-" + e.Message.MessageText);
	}
}
