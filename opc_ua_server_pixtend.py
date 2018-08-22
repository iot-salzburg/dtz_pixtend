# Salzburg Research ForschungsgesmbH
# Christoph Schranz & Armin Niedermueller

# OPC UA Server on PiXtend


from opcua import ua, uamethod, Server
from random import randint
import datetime
import time
from ConveyorBeltX import ConveyorBeltX


conbelt = ConveyorBeltX()

@uamethod
def move_belt(parent, direction, distance):
    if direction == "right":
        conbelt.move_right_for(distance)
        return true
    elif direction == "left":
        conbelt.move_left_for(distance)
        return true
    else:
       return false

# our server object
server = Server()

# server address
url = "opc.tcp://localhost:4840/freeopcua/server"
server.set_endpoint(url)

# Add name to the address space
name = "opc_ua_server_pixtend"   
addspace = server.register_namespace(name)

# get Objects node, this is where we should put our nodes
objects = server.get_objects_node()


# testing....
freeopcua_namespace = self.server.get_namespace_index("urn:freeopcua:python:server")
belt_mover = objects.get_child("0:belt_mover")


belt_mover.add_method(
   freeopcua_namespace, "belt_mover",  move_belt, [ua.VariantType.Double], [ua.VariantType.Boolean])



# Add a parameter object to the address space
Params = objects.add_object(addspace, "Parameters")

# Parameters - Addresspsace, Name, Initial Value
ConBeltState = Params.add_variable(addspace, "Conveyor Belt - State", "init")
ConBeltDistance = Params.add_variable(addspace, "Conveyor Belt - Distance", 0.0)
Time = Params.add_variable(addspace, "Time", 0)

# Set parameters writable by clients
Time.set_writable()
ConBeltState.set_writable()

# Start the server
server.start()
print("Server started ad {}".format(url))

try:
    # Assign random values to the parameters
    while True:
        # calculate random values
        Temperature = randint(10,50)  # Assign random value from 10 to 50
        Pressure = randint(200, 999)
        TIME = datetime.datetime.now()  # current time
        with open("state.log") as f:
            state = f.read()
        with open("distance.log") as f:
            distance = f.read()

        # set the random values inside the node
        print(Temperature, Pressure, TIME, state)
        Temp.set_value(Temperature)
        Press.set_value(Pressure)
        Time.set_value(TIME)
        ConBeltState.set_value(state)
        ConBeltDistance.set_value(distance)
        # sleep 2 seconds
        time.sleep(2)


finally:
    #close connection, remove subcsriptions, etc
    server.stop()

