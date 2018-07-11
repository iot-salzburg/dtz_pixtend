from ConveyorBelt import ConveyorBelt
from time import sleep

conbelt = ConveyorBelt()

try:
    while True:
        oldstate = conbelt.state

        if conbelt.btn_is_left():
            conbelt.move_left()
        elif conbelt.btn_is_right():
            conbelt.move_right()
        else:
            conbelt.halt()

        if oldstate != conbelt.state:
            print(conbelt.state)

        sleep(.1)

except KeyboardInterrupt:
    print("\nCtrl-C pressed.  Stopping PIGPIO and exiting...")
finally:
    conbelt.stop()
