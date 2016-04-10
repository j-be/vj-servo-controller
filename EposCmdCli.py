#!/usr/bin/python

from optparse import OptionParser
from epos_lib_wrapper import EposLibWrapper as Epos

def parse_cmd_args():
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="dev_name", default="EPOS2",
                      help="name of the Ctrl device")
    parser.add_option("-c", "--communication-protocol", dest="protocol", default="MAXON SERIAL V2",
                      help="communication protocol")
    parser.add_option("-i", "--interface", dest="interface", default="USB",
                      help="communication interface")
    parser.add_option("-p", "--port", dest="port", default="USB0",
                      help="port to use for communication")
    parser.add_option("-m", "--move", dest="move", type="int",
                      help="amount to move")
    parser.add_option("-v", "--velocity", dest="velocity", type="int",
                      help="the velocity to move with")
    parser.add_option("-a", "--acceleration", dest="acceleration", type="long", default=long(pow(2, 32) -1),
                      help="acceleration/deceleration")
    (options, _) = parser.parse_args()
    return options

args = parse_cmd_args()
print args

epos = Epos(args.dev_name, args.protocol, args.interface, args.port)
epos.openDevice()
epos.clearFaultState()
epos.moveToPositionWithVelocity(args.move, args.velocity, wait_for_target_reached=True)
epos.closeDevice()
