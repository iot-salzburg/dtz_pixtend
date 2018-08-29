#      _____         __        __                               ____                                        __  
#     / ___/ ____ _ / /____   / /_   __  __ _____ ____ _       / __ \ ___   _____ ___   ____ _ _____ _____ / /_ 
#     \__ \ / __ `// //_  /  / __ \ / / / // ___// __ `/      / /_/ // _ \ / ___// _ \ / __ `// ___// ___// __ \
#    ___/ // /_/ // /  / /_ / /_/ // /_/ // /   / /_/ /      / _, _//  __/(__  )/  __// /_/ // /   / /__ / / / /
#   /____/ \__,_//_/  /___//_.___/ \__,_//_/    \__, /      /_/ |_| \___//____/ \___/ \__,_//_/    \___//_/ /_/ 
#                                              /____/                                                           
#   Salzburg Research ForschungsgesmbH
#   Armin Niedermueller

#   OPC UA Server on PiXtend
#   The purpose of this OPCUA client is to call the provided methods of the opc_ua_server_pixtend.py and read
#   its state variables

import time
import sys
sys.path.insert(0, "..")

from multiprocessing import Process
from opcua import Client

desired_distance = 0.55 # distance in meters to drive the belt
belt_velocity = 0.05428 # velocity of the belt in m/s (5.5cm/s)
timebuffer = 3          # time buffer for the wait loops after method call. wifi istn that fast

if __name__ == "__main__":

    client = Client("opc.tcp://192.168.48.42:4840/freeopcua/server/")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #print(var)
        #var.get_data_value() # get value of node as a DataValue object
        #var.get_value() # get value of node as a python builtin
        #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
        server_time = root.get_child(["0:Objects", "2:Object1", "2:ServerTime"])
        object1 = root.get_child(["0:Objects", "2:Object1"])
        mover = root.get_child(["0:Objects", "2:Object1", "2:MoveBelt"])
        conbelt_state =  root.get_child(["0:Objects", "2:Object1", "2:ConBeltState"])
        conbelt_dist = root.get_child(["0:Objects", "2:Object1", "2:ConBeltDist"]) 

        def move_belt(direction, distance):
            object1.call_method("2:MoveBelt", direction, desired_distance)  # drive 55cm right
            print("called move_belt to " + str(direction) + " for " + str(desired_distance) + "m")
            print("sleeping...")
            for i in range(0, (int(desired_distance/belt_velocity)*10)+timebuffer):
                time.sleep(0.1)


        while True:
            move_belt("right", 0.55)
            move_belt("left", 0.55)

    except KeyboardInterrupt:
        print("\nClient stopped")
    finally:
        client.disconnect()
