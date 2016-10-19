import inspect
import logging

class MockLib(object):
    def __init__(self, *args):
        self.log = logging.getLogger("eposLib")
        self.log.error("MockLib running!")
        self.enabled = False
        for arg in args:
            self.log.error("\t" + str(arg))

    def isEnabled(self):
        return self.enabled

    def VCS_OpenDevice(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args:
            self.log.error("\t" + str(arg))

    def VCS_CloseDevice(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args:
            self.log.error("\t" + str(arg))

    def VCS_SetEnableState(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))
        self.enabled = True

    def VCS_SetDisableState(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))
        self.enabled = False

    def VCS_ActivateProfileVelocityMode(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))

    def VCS_SetPositionProfile(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))

    def VCS_ActivateProfilePositionMode(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))

    def VCS_MoveToPosition(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))

    def VCS_WaitForTargetReached(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))

    def VCS_GetFaultState(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))

    def VCS_ClearFault(self, *args):
        self.log.error(inspect.stack()[1][3] + ":")
        for arg in args: self.log.error("\t" + str(arg))
