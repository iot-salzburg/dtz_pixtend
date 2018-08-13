# Salzburg Research ForschungsgesmbH
# Christoph Schranz & Armin Niedermueller

# Conveyor Belt Control - PiXtend
# The electronic layout is from the tutorial:
# https://www.rototron.info/raspberry-pi-stepper-motor-tutorial/

# Resource Package - so that the Class could only be used with the "with" statement
# if an exception occurs the __exit__ function is called and calls the close function of the Pixtend Object

from time import sleep
from multiprocessing import Process
from pixtendv2s import PiXtendV2S



class ConveyorBeltX:
    def __init__(self):
        self.shotstate = 0
        self.state = "init"
        self.distance = 0.0

        # PiXtend Control Object
        self.pixtend = PiXtendV2S()
        self.pixtend.gpio_pullups_enable = True
        self.pixtend.gpio0_ctrl = 0
        self.pixtend.gpio1_ctrl = 0
        self.pixtend.gpio2_ctrl = 0
        self.pixtend.gpio3_ctrl = 0
        self.pixtend.gpio1 = True
        self.pixtend.gpio0 = True

        self.velocity = 0.05428                 # Velocity of the belt im m/s (5.5cm/s)




        self.pixtend.pwm0_ctrl0 = 0b01111011    # Channel A & B deactivated, Frequency Mode activated, Prescaler at 64
                                                # Bit 0 - Mode0         1 <-
                                                # Bit 1 - Mode1         1 <-
                                                # Bit 2 - Dummy         0
                                                # Bit 3 - EnableA       0
                                                # Bit 4 - EnableB       0
                                                # Bit 5 - Prescaler0    1 <-
                                                # Bit 6 - Prescaler1    1 <-
                                                # Bit 7 - Prescaler2    0

        # set PWM registers
        self.pixtend.pwm0a = 120
        self.pixtend.pwm0b = 120                # Oscillator Frequency / 2 / Prescaler / PWM0A Register = Frequency
                                                #         16 Mhz       / 2 /    64     /      250       = 500Hz


    def write_state(self, state):
        with open("state.log", "w") as f:
            f.write(state)

    def write_distance(self, distance):
        with open("distance.log", "w") as f:
            f.write(str(distance))

    def move_left(self, distance = 0):
        self.state = "left"
        self.write_state(self.state)
        self.pixtend.digital_out3 = True             # RELAY ON
        self.pixtend.pwm0_ctrl0 = 0b01111011          # PWM Channel B - ON
        self.pixtend.digital_out0 = True             # Direction = Left

    def move_right(self, distance = 0):
        self.state = "right"
        self.write_state(self.state)
        self.pixtend.digital_out3 = True             # RELAY ON
        self.pixtend.pwm0_ctrl0 = 0b01111011          # PWM Channel B - ON
        self.pixtend.digital_out0 = False            # Direction = Right

    def halt(self):
        self.state = "halt"
        self.write_state(self.state)
        self.pixtend.digital_out3 = False            # RELAY OFF
        self.pixtend.pwm0_ctrl0 = 0b01100011          # PWM Channels A & B - OFF

    def stop(self):
        self.state = "stop"
        self.write_state(self.state)
        self.pixtend.pwm0_ctrl0 = 0b01100011          # PWM Channels A & B - OFF
        self.pixtend.digital_out3 = False            # RELAY OFF

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

        if not was_interrrupted:
            self.halt()

    def move_left_for(self, distance=0):
        self.move_left()
        time = distance/self.velocity
        waiting = Process(target=self.wait_for_it, args=(time,))
        waiting.start()

    def move_right_for(self, distance=0):
        self.move_right()
        time = distance/self.velocity
        waiting = Process(target=self.wait_for_it, args=(time,))
        waiting.start()

    def manual_control(self, showstate):
        self.showstate = showstate
        manual = Process(target=self.manual_control_core(), args=())
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
