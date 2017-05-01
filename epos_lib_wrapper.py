import logging
import logging.config
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
		self.log = logging.getLogger("eposLib")
		self.lib = cdll.LoadLibrary(self._getLibraryName())
		self.dev_name = dev_name
		self.protocol = protocol
		self.interface = interface
		self.port = port
		self.node_id = 1
		self.enabled = False
		self.mode = None
		self.dev_handle = None

	def isEnabled(self):
		return self.enabled

	def _getLibraryName(self):
		current_platform = platform.system()
		self.log.debug("Running on platform: %s", current_platform)
		for lib, platforms in LIBS.iteritems():
			if current_platform in platforms:
				self.log.info("Found lib: %s for platform: %s", lib, current_platform)
				return lib
		self.log.error("No library found for platform: %s", current_platform)

	def openDevice(self):
		err = c_uint()
		self.dev_handle = self.lib.VCS_OpenDevice(self.dev_name, self.protocol, self.interface, self.port, byref(err))
		self.log.info("Open handle: %s error: %s", self.dev_handle, err.value)

	def closeDevice(self):
		self.disableDevice()
		err = c_uint()
		self.lib.VCS_CloseDevice(self.dev_handle, byref(err))
		self.log.info("Close handle: %s error: %s", self.dev_handle, err.value)

	def enableDevice(self):
		err = c_uint()
		self.lib.VCS_SetEnableState(self.dev_handle, self.node_id, byref(err))
		self.log.debug("Enabling node: %s error: %s", self.node_id, err.value)
		self.enabled = err.value == 0

	def disableDevice(self):
		err = c_uint()
		self.lib.VCS_SetDisableState(self.dev_handle, self.node_id, byref(err))
		self.log.info("Disabling node: %s error: %s", self.node_id, err.value)
		self.enabled = err.value != 0

	def activateProfilePositionMode(self):
		if self.isFaultState():
			self.clearFaultState()

		err = c_uint()
		self.lib.VCS_ActivateProfileVelocityMode(self.dev_handle, self.node_id, byref(err))
		self.log.debug("Activate ProfilePositionMode on node: %s error: %s", self.node_id, err.value)
		if err.value == 0:
			self.mode = MODE_PROFILE_POSITION

	def setProfilePositionVelocity(self, velocity, acceleration):
		err = c_uint()
		if not self.mode == MODE_PROFILE_POSITION:
			self.activateProfilePositionMode()
		self.lib.VCS_SetPositionProfile(self.dev_handle, self.node_id, velocity, acceleration, acceleration, byref(err))
		self.log.debug("Set velocity on node: %s to v=%s a=%s error: %s",
					  self.node_id, velocity, acceleration, err.value)

	def activatePositionMode(self):
		if self.isFaultState():
			self.clearFaultState()

		err = c_uint()
		self.lib.VCS_ActivateProfilePositionMode(self.dev_handle, self.node_id, byref(err))
		self.log.debug("Activate PositionMode on node: %s error: %s", self.node_id, err.value)
		if err.value == 0:
			self.mode = MODE_POSITION

	def moveToPosition(self, position, wait_for_target_reached=False):
		err = c_uint()
		if self.mode != MODE_POSITION:
			self.activatePositionMode()
		self.lib.VCS_MoveToPosition(self.dev_handle, self.node_id, position, 0, 1, byref(err))
		self.log.debug("Move node: %s to p=%s error: %s", self.node_id, position, err.value)

		if wait_for_target_reached:
			self.waitForTargetReached()

	def moveToPositionWithVelocity(self, position, velocity, acceleration=EPOS2_MAX_ACCEL, wait_for_target_reached=False):
		self.log.info("Move to p=%s v=%s a=%s wait=%s", position, velocity, acceleration, wait_for_target_reached)
		self.setProfilePositionVelocity(velocity, acceleration)
		self.moveToPosition(position, wait_for_target_reached)

	def waitForTargetReached(self, timeout=-1):
		err = c_uint()
		self.log.info("Waiting for target reached on node: %s", self.node_id)
		self.lib.VCS_WaitForTargetReached(self.dev_handle, self.node_id, timeout, byref(err))
		self.log.info("Target reached on node: %s", self.node_id)

	def stop(self):
		self.moveToPositionWithVelocity(0, 0)
		self.disableDevice()

	def isFaultState(self):
		err = c_uint()
		is_fault_state = c_int()
		self.lib.VCS_GetFaultState(self.dev_handle, self.node_id, byref(is_fault_state), byref(err))
		return is_fault_state.value == 1

	def clearFaultState(self):
		err = c_uint()
		if self.isFaultState():
			self.lib.VCS_ClearFault(self.dev_handle, self.node_id, byref(err))
			self.enableDevice()
			self.log.info("Cleared fault state on node: %s error: %s", self.node_id, err.value)
		else:
			self.log.debug("Node: %s is not in fault state!", self.node_id)

if __name__ == "__main__":
	from time import sleep

	logging.config.fileConfig('log.ini')

	wrapper = EposLibWrapper()

	try:
		wrapper.openDevice()
		wrapper.setProfilePositionVelocity(3000, 1000)
		wrapper.moveToPosition(0, True)
		#sleep(MOVEMENT_TIME)
	finally:
		wrapper.closeDevice()
