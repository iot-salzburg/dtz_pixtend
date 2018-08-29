# Salzburg Research ForschungsgesmbH
# Armin Niedermueller

# OPC UA Server on PiXtend


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

@uamethod
def move_belt(parent, direction, distance):
    print("move_belt function")
    move_thread = threading.Thread(name='move_belt_thread', target = move_belt_core, args = (direction, distance,)) 
    move_thread.daemon = True
    move_thread.start()
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
    object1 = objects.add_object(idx, "Object1")

    # Parameters - Addresspsace, Name, Initial Value
    server_time = object1.add_variable(idx, "ServerTime", 0)
    mover = object1.add_method(idx, "MoveBelt", move_belt, [ua.VariantType.String, ua.VariantType.Float], [ua.VariantType.Boolean])
    conbelt_state = object1.add_variable(idx, "ConBeltState", "init")
    conbelt_dist = object1.add_variable(idx, "ConBeltDist", 0.0)

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
