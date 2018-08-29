#      _____         __        __                               ____                                        __  
#     / ___/ ____ _ / /____   / /_   __  __ _____ ____ _       / __ \ ___   _____ ___   ____ _ _____ _____ / /_ 
#     \__ \ / __ `// //_  /  / __ \ / / / // ___// __ `/      / /_/ // _ \ / ___// _ \ / __ `// ___// ___// __ \
#    ___/ // /_/ // /  / /_ / /_/ // /_/ // /   / /_/ /      / _, _//  __/(__  )/  __// /_/ // /   / /__ / / / /
#   /____/ \__,_//_/  /___//_.___/ \__,_//_/    \__, /      /_/ |_| \___//____/ \___/ \__,_//_/    \___//_/ /_/ 
#                                              /____/                                                           
# Salzburg Research ForschungsgesmbH
# Armin Niedermueller & Christoph Schranz
#
# class to control a conveyor belt with an stepper motor via the PiXtend Hardware

from time import sleep
import sys
from pixtendv2s import PiXtendV2S
import threading


class ConveyorBeltX:
    def __init__(self):
        
        self.shotstate = 0
        self.state = "init"
        self.distance = 0.0

        # PiXtend Control Object
        self.pixtend = PiXtendV2S()
        
        # Enable Pull Up Resistors at GPIOs 
        self.pixtend.gpio_pullups_enable = True
        
        # Configure the GPIOs as Input
        self.pixtend.gpio0_ctrl = 0
        self.pixtend.gpio1_ctrl = 0
        self.pixtend.gpio2_ctrl = 0
        self.pixtend.gpio3_ctrl = 0
        
        # Switch the GPIOs 1 & 2 to HIGH (Pull Up)
        self.pixtend.gpio1 = True
        self.pixtend.gpio0 = True
        
        # Red light OFF & Green light ON
        self.pixtend.relay0 = False  
        
        self.velocity = 0.05428                 # Velocity of the belt im m/s (5.5cm/s)




        self.pixtend.pwm0_ctrl0 = 0b01100011    # Channel A & B deactivated, Frequency Mode activated, Prescaler at 64
                                                # Bit 0 - Mode0         1 <-
                                                # Bit 1 - Mode1         1 <-
                                                # Bit 2 - Dummy         0
                                                # Bit 3 - EnableA       0
                                                # Bit 4 - EnableB       0
                                                # Bit 5 - Prescaler0    1 <-
                                                # Bit 6 - Prescaler1    1 <-
                                                # Bit 7 - Prescaler2    0

        # set PWM registers
        self.pixtend.pwm0a = 125                # Oscillator Frequency / 2 / Prescaler / PWM0A Register = Frequency
        self.pixtend.pwm0b = 125                #         16 Mhz       / 2 /    64     /      125       = 1000Hz

        with open("state.log", "w") as f:
            f.write(self.state)


        with open("distance.log", "w") as f:
            f.write(str(self.distance))


    def write_state(self, state):
        with open("state.log", "w") as f:
            f.write(state)

    def write_distance(self, distance):
        with open("distance.log", "w") as f:
            f.write(str(distance))

    def move_left(self):
        self.state = "left"
        self.write_state(self.state)
        self.pixtend.digital_out3 = True             # RELAY ON
        self.pixtend.pwm0_ctrl0 = 0b01111011         # PWM Channel A & B - ON
        self.pixtend.digital_out0 = True             # Direction = Left
        self.pixtend.relay0 = True                   # Red light ON & Green light OFF

    def move_right(self):
        self.state = "right"
        self.write_state(self.state)
        self.pixtend.digital_out3 = True             # RELAY ON
        self.pixtend.pwm0_ctrl0 = 0b01111011         # PWM Channel B - ON
        self.pixtend.digital_out0 = False            # Direction = Right
        self.pixtend.relay0 = True                   # Red light ON & Green light OFF

    def halt(self):
        self.state = "halt"
        self.write_state(self.state)
        self.pixtend.digital_out3 = False            # RELAY OFF
        self.pixtend.pwm0_ctrl0 = 0b01100011         # PWM Channels A & B - OFF
        self.pixtend.relay0 = False                  # Red light OFF & Green light ON

    def stop(self):
        self.state = "stop"
        self.write_state(self.state)
        self.pixtend.digital_out3 = False            # RELAY OFF
        self.pixtend.pwm0_ctrl0 = 0b01100011         # PWM Channels A & B - OFF
        self.pixtend.relay0 = False                  # Red light OFF & Green light ON

    def wait_for_it(self, time):
        init_state = self.state
        was_interrrupted = False
        for _ in range(int(10*time)):
            if self.state != init_state:
                was_interrrupted = True
                break
            if init_state == "left":
                self.distance += 0.1*self.velocity
                self.write_distance(self.distance)
            elif init_state == "right":
                self.distance -= 0.1*self.velocity
                self.write_distance(self.distance)

            sleep(0.1)
        return True

    def move_left_for(self, distance=0):
        self.move_left()
        time = distance/self.velocity
        waiting = threading.Thread(name='waiter', target=self.wait_for_it, args=(time,))
        waiting.start()
        waiting.join()
        self.halt()

    def move_right_for(self, distance=0):
        self.move_right()
        time = distance/self.velocity
        waiting = threading.Thread(name='waiter', target=self.wait_for_it, args=(time,))
        waiting.start()
        waiting.join()
        self.halt()

    def manual_control(self, showstate):
        self.showstate = showstate
        manual.start()

    def manual_control_core(self):
        try:
            while True:
                oldstate = self.state
                if not self.pixtend.gpio0:
                    self.move_left()
                    self.distance += 0.1*self.velocity
                    self.write_distance(self.distance)
                elif not self.pixtend.gpio1:
                    self.move_right()
                    self.distance -= 0.1*self.velocity
                    self.write_distance(self.distance)
                else:
                    self.halt()
                if oldstate != self.state and self.showstate == 1:
                    print(self.state)

                sleep(.1)

        except KeyboardInterrupt:
            print("\nCtrl-C pressed.  Stopping PIGPIO and exiting...")
        finally:
            self.pixtend.close()   # cleanup function - closes all PiXtend's internal variables, objects, drivers, communication, etc
            self.pixtend = None
