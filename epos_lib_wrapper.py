import platform
from ctypes import cdll, c_int, c_uint, byref

MODE_POSITION = 1
MODE_PROFILE_POSITION = 2
MOVEMENT_TIME = 240
LIBS = {
	"libEposCmd.so": ["Linux"],
	"EposCmd.dll": ["Windows", "CYGWIN_NT-10.0"]
	}

EPOS2_MAX_ACCEL = long(pow(2, 32) - 1)

class EposLibWrapper(object):
	def __init__(self, dev_name="EPOS2", protocol="MAXON SERIAL V2", interface="USB", port="USB0"):
		self.lib = cdll.LoadLibrary(self._getLibraryName())
		self.dev_name = dev_name
		self.protocol = protocol
		self.interface = interface
		self.port = port
		self.node_id = 1
		self.enabled = False
		self.mode = None
		self.dev_handle = None

	@staticmethod
	def _getLibraryName():
		current_platform = platform.system()
		print current_platform
		for lib, platforms in LIBS.iteritems():
			if current_platform in platforms:
				return lib

	def openDevice(self):
		err = c_uint()
		self.dev_handle = self.lib.VCS_OpenDevice(self.dev_name, self.protocol, self.interface, self.port, byref(err));
		print "Open error:", err.value, "handle:", self.dev_handle

	def closeDevice(self):
		self.disableDevice()
		err = c_uint()
		self.lib.VCS_CloseDevice(self.dev_handle, byref(err))
		print "Close handle:", self.dev_handle, "error:", err.value

	def enableDevice(self):
		err = c_uint()
		self.lib.VCS_SetEnableState(self.dev_handle, self.node_id, byref(err))
		print "Enabling device handle", self.dev_handle, "node:", self.node_id, "error:", err.value
		self.enabled = err.value == 0

	def disableDevice(self):
		err = c_uint()
		self.lib.VCS_SetDisableState(self.dev_handle, self.node_id, byref(err))
		print "Disabling device handle", self.dev_handle, "node:", self.node_id, "error:", err.value
		self.enabled = err.value == 0

	def activateProfilePositionMode(self):
		err = c_uint()
		if not self.enabled:
			self.enableDevice()

		self.lib.VCS_ActivateProfileVelocityMode(self.dev_handle, self.node_id, byref(err))
		print "Profile position mode, handle:", self.dev_handle, "node:", self.node_id, "error:", err.value
		if err.value == 0:
			self.mode = MODE_PROFILE_POSITION

	def setProfilePositionVelocity(self, velocity, acceleration):
		err = c_uint()
		if not self.mode == MODE_PROFILE_POSITION:
			self.activateProfilePositionMode()
		self.lib.VCS_SetPositionProfile(self.dev_handle, self.node_id, velocity, acceleration, acceleration, byref(err))
		print "Set profile position velocity node:", self.node_id, "to velocity:", velocity, "acceleration:", acceleration, "error:", err.value

	def activatePositionMode(self):
		err = c_uint()		
		if not self.enabled:
			self.enableDevice()
		self.lib.VCS_ActivateProfilePositionMode(self.dev_handle, self.node_id, byref(err))
		print "Position mode, handle:", self.dev_handle, "node:", self.node_id, "error:", err.value
		if err.value == 0:
			self.mode = MODE_POSITION

	def moveToPosition(self, position, wait_for_target_reached=False):
		err = c_uint()
		if self.mode != MODE_POSITION:
			self.activatePositionMode()
		self.lib.VCS_MoveToPosition(self.dev_handle, self.node_id, position, 0, 1, byref(err))
		print "Move node:", self.node_id, "to position:", position, "error:", err.value

		if wait_for_target_reached:
			print "Waiting for target reached"
			self.waitForTargetReached()
			print "Target reached"

	def moveToPositionWithVelocity(self, position, velocity, acceleration=EPOS2_MAX_ACCEL, wait_for_target_reached=False):
		self.setProfilePositionVelocity(velocity, acceleration)
		self.moveToPosition(position, wait_for_target_reached)

	def waitForTargetReached(self, timeout=-1):
		err = c_uint()
		self.lib.VCS_WaitForTargetReached(self.dev_handle, self.node_id, timeout, byref(err))

	def isFaultState(self):
		err = c_uint()
		is_fault_state = c_int()
		self.lib.VCS_GetFaultState(self.dev_handle, self.node_id, byref(is_fault_state), byref(err))
		return is_fault_state.value == 1

	def clearFaultState(self):
		err = c_uint()
		if self.isFaultState():
			self.lib.VCS_ClearFault(self.dev_handle, self.node_id, byref(err))
			print "Handle:", self.dev_handle, "node:", self.node_id, "cleared fault state. error:", err.value
		else:
			print "Handle:", self.dev_handle, "node:", self.node_id, "is not in fault state!"

if __name__ == "__main__":
	from time import sleep
	wrapper = EposLibWrapper()

	try:
		wrapper.openDevice()
		wrapper.setProfilePositionVelocity(3000, 1000)
		wrapper.moveToPosition(0, True)
		#sleep(MOVEMENT_TIME)
	finally:
		wrapper.closeDevice()
