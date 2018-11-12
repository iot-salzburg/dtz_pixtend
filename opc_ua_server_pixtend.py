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

from ConveyorBeltX import ConveyorBeltX
from opcua import ua, uamethod, Server
import datetime
import time
import threading

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

if __name__ == "__main__":

    # setup our server
    server = Server()
    url = "opc.tcp://0.0.0.0:4840/freeopcua/server"
    server.set_endpoint(url)

    # setup our own namespace
    uri = "https://github.com/iot-salzburg/dtz_pixtend"
    idx = server.register_namespace(uri)


    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # Add a parameter object to the address space
    conveyorbelt_object = objects.add_object(idx, "ConveyorBelt")

    # Parameters - Addresspsace, Name, Initial Value
    server_time = conveyorbelt_object.add_variable(idx, "ServerTime", 0)
    mover = conveyorbelt_object.add_method(idx, "MoveBelt", move_belt, [ua.VariantType.String, ua.VariantType.Float], [ua.VariantType.Boolean])
    busy_light = conveyorbelt_object.add_method(idx, "SwitchBusyLight", switch_light, [ua.VariantType.Bool] , [ua.VariantType.Boolean])
    conbelt_state = conveyorbelt_object.add_variable(idx, "ConBeltState", "init")
    conbelt_dist = conveyorbelt_object.add_variable(idx, "ConBeltDist", 0.0)

    # Set parameters writable by clients
    server_time.set_writable()


    # Start the server
    server.start()

    print("OPCUA - Pixtend - Server started at {}".format(url))

    try:
        # Assign random values to the parameters
        while True:
            TIME = datetime.datetime.now()  # current time
            with open("state.log") as f:
                state = f.read()
            with open("distance.log") as f:
                distance = f.read()

            # set the random values inside the node
            print("Belt-State: " + str(state) + "   Belt-Distance: " + str(distance) + "   Server-Time: " + str(server_time.get_value()))
            server_time.set_value(TIME)
            conbelt_state.set_value(state)
            conbelt_dist.set_value(distance)

            # sleep 2 seconds
            time.sleep(2)
    except KeyboardInterrupt:
            print("\nCtrl-C pressed. OPCUA - Pixtend - Server stopped at {}".format(url))
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
        conbelt = None
        sys.exit(0)
