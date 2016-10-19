using UnityEngine;
using System.Collections;

public class ServoTest : MonoBehaviour {
	private ServoControllerClient servoClient = null;

	public long position = 1;

	// Use this for initialization
	void Start () {
		servoClient = new ServoControllerClient();
		servoClient.EventSetServoPosition(position);
	}
}
