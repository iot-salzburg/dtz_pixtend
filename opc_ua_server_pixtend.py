#      _____         __        __                               ____                                        __
#     / ___/ ____ _ / /____   / /_   __  __ _____ ____ _       / __ \ ___   _____ ___   ____ _ _____ _____ / /_
#     \__ \ / __ `// //_  /  / __ \ / / / // ___// __ `/      / /_/ // _ \ / ___// _ \ / __ `// ___// ___// __ \
#    ___/ // /_/ // /  / /_ / /_/ // /_/ // /   / /_/ /      / _, _//  __/(__  )/  __// /_/ // /   / /__ / / / /
#   /____/ \__,_//_/  /___//_.___/ \__,_//_/    \__, /      /_/ |_| \___//____/ \___/ \__,_//_/    \___//_/ /_/
#                                              /____/
# Salzburg Research ForschungsgesmbH
# Armin Niedermueller

# OPC UA Server on PiXtend
# The purpose of this OPCUA server is to provide methods to control the conveyorbelt (stepper motor) and read the state
# of the conveyor belt
# the hardware is PiXtend - Raspberry Pi SPS

import sys
sys.path.insert(0, "..")
import time
import logging
import socket

from ConveyorBeltDummy import ConveyorBeltDummy as ConveyorBeltX
#from ConveyorBeltX import ConveyorBeltX
from opcua import ua, uamethod, Server
import datetime
import time
import threading
import traceback

conbelt = ConveyorBeltX()

def move_belt_core(direction, distance):
    if direction == "right":
        conbelt.move_right_for(distance)
    elif direction == "left":
        conbelt.move_left_for(distance)
    return True

# Method to control the conveyor belt - direction is "right" or "left", distance is float in meters.
@uamethod
def move_belt(parent, direction, distance):
    move_thread = threading.Thread(name='move_belt_thread', target = move_belt_core, args = (direction, distance,))
    move_thread.daemon = True
    move_thread.start()
    return True

# method for alarm light control - Value busy True means the light should show red, e.g when the robot is running
@uamethod
def switch_light(parent, busy):
    conbelt.busy_light(busy)
    return True

@uamethod
def reset_totaldist(parent):
    conbelt.reset_totaldistance(0)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s %(name)s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger("opcua.server").setLevel(logging.ERROR)
    logger.info("Starting OPC-UA Server on host: {}"
                .format(socket.gethostname()))
    # setup our server
    server = Server()
    url = "opc.tcp://0.0.0.0:4840/freeopcua/server"
    server.set_endpoint(url)

    # setup our own namespace
    server.register_namespace("ns=2")


    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # Add a parameter object to the address space
    conveyorbelt_object = objects.add_object("ns=2; i=1", "ConveyorBelt")

    # Parameters - Addresspsace, Name, Initial Value
    server_time = conveyorbelt_object.add_variable("ns=2; i=2", "ServerTime", 0)
    mover = conveyorbelt_object.add_method("ns=2; i=3", "MoveBelt", move_belt, [ua.VariantType.String, ua.VariantType.Float], [ua.VariantType.Boolean])
    resetTotalDistance = conveyorbelt_object.add_method("ns=2; i=14", "ResetTotalDistance", reset_totaldist)
    busy_light = conveyorbelt_object.add_method("ns=2; i=7", "SwitchBusyLight", switch_light, [ua.VariantType.Boolean] , [ua.VariantType.Boolean])
    conbelt_state = conveyorbelt_object.add_variable("ns=2; i=10", "ConBeltState", "init")
    conbelt_dist = conveyorbelt_object.add_variable("ns=2; i=11", "ConBeltDist", 0.0)
    conbelt_moving = conveyorbelt_object.add_variable("ns=2; i=12", "ConBeltMoving", False)
    conbelt_totaldist = conveyorbelt_object.add_variable("ns=2; i=13", "ConBeltTotalDist", 0.0)

    # Set parameters writable by clients
    server_time.set_writable()


    # Start the server
    server.start()

    logger.info("OPCUA - Pixtend - Server started at {}".format(url))

    try:
        # Assign random values to the parameters
        while True:
            TIME = datetime.datetime.now()  # current time
            with open("state.log") as f:
                state = f.read()
            with open("distance.log") as f:
                distance = f.read()
            with open("total_distance.log") as f:
                total_distance = f.read()

            if state != "init" and state != "stop" and state != "halt":
                conbelt_moving.set_value(True)
            else:
                conbelt_moving.set_value(False)

            # set the random values inside the node
            logger.debug("Belt-State: " + str(state) + "   Belt-Distance: " + str(distance)+ "   Belt-Total Distance: " + str(total_distance) + "   Server-Time: " + str(server_time.get_value()))
            server_time.set_value(TIME)
            conbelt_state.set_value(state)
            conbelt_dist.set_value(distance)
            conbelt_totaldist.set_value(total_distance)

            # sleep 2 seconds
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("\nCtrl-C pressed. OPCUA - Pixtend - Server stopped at {}".format(url))
    except Exception as ex:
        traceback.print_exc()
        logger.error(ex)
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
        conbelt = None
        sys.exit(0)
