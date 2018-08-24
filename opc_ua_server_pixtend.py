# Salzburg Research ForschungsgesmbH
# Armin Niedermueller

# OPC UA Server on PiXtend


import sys
sys.path.insert(0, "..")
import time

from ConveyorBeltX import ConveyorBeltX
from opcua import ua, uamethod, Server
from multiprocessing import Process
import datetime
import time

def move_belt_core(drive):
    print("own process")

    conbelt = ConveyorBeltX()

    if drive:
        conbelt.move_right_for(0.55) # 55cm
    else:
        conbelt.move_left_for(0.55)  # 55cm
    conbelt.halt()
    return True

@uamethod
def move_belt(parent, drive):
    print("move_belt function")
    process = Process(target=move_belt_core, args=(drive,))
    process.start()
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
    object_1 = object.add_object(idx, "Object1")
   
    # Parameters - Addresspsace, Name, Initial Value
    Time = myobj.add_variable(idx, "Time", 0)
    mover = myobj.add_method(idx, "MoveBelt", move_belt, [ua.VariantType.Boolean], [ua.VariantType.Boolean])
    ConBeltState = Param.add_variable(addspace, "Conveyor Belt - State", "init")
    ConBeltDistance = Param.add_variable(addspace, "Conveyor Belt - Distance", 0.0)

    # Set parameters writable by clients
    Time.set_writable()


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
        print(TIME, state, distance)
        Time.set_value(TIME)
        ConBeltState.set_value(state)
        ConBeltDistance.set_value(distance)
        
        # sleep 2 seconds
        time.sleep(2)
except KeyboardInterrupt:
        print("\nCtrl-C pressed. OPCUA - Pixtend - Server stopped at {}".format(url))
finally:
    #close connection, remove subcsriptions, etc
    server.stop()

