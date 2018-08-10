# Salzburg Research ForschungsgesmbH
# Christoph Schranz & Armin Niedermueller

# Conveyor Belt Control - PiXtend
# The electronic layout is from the tutorial:
# https://www.rototron.info/raspberry-pi-stepper-motor-tutorial/

from time import sleep
from multiprocessing import Process


# Resource Package - so that the Class could only be used with the "with" statement 
# if an exception occurs the __exit__ function is called and calls the close function of the Pixtend Object
class ConveyorBeltXResource:
    def __enter__(self):
        class ConveyorBeltX:
            def __init__(self):
                self.state = "init"
                elf.distance = 0.0
                try:
                    import time
                    from multiprocessing import Process
                    from pixtendv2s import PiXtendV2S
                except ModuleNotFoundError:
                    raise "Module not found."
            
        
                # PiXtend Control Object
                pixtend = PiXtendV2S()

                self.velocity = 0.05428                 # Velocity of the belt im m/s (5.5cm/s)

                def dir_pin(state):                     # OUTPUT Pin for the motor controller - movement direction
                    pixtend.digitalout0(state)     
                def left_pin():                         # INPUT pin for left direction button
                    pixtend.digitalin0()            
                def right_pin():                        # INPUT pin for right direction button
                    pixtend.digitalin1()
                def relay_pin(state):                   # OUTPUT pin for the RELAY
                    pixtend.digitalout3(state)      
              
                relay_pin(OFF)                              # switch off POWER-RELAY



                # set PWM registers
                pixtend.pwm0a(250)                      # Oscillator Frequency / 2 / Prescaler / PWM0A Register = Frequency
                                                        #         16 Mhz       / 2 /    64     /      250       = 500Hz
                
                pixtend.pwm0_ctrl(0b00011011)           # Channel A & B deactivated, Frequency Mode activated, Prescaler at 64
                                                        # Bit 0 - Mode0         0
                                                        # Bit 1 - Mode1         1 <-
                                                        # Bit 3 - EnableA       0 
                                                        # Bit 4 - EnableB       0 
                                                        # Bit 5 - Prescaler0    0
                                                        # Bit 6 - Prescaler1    1 <- 
                                                        # Bit 7 - Prescaler2    1 <-
                                                        
            def btn_is_left(self):
                return not left_pin()

            def btn_is_right(self):
                return not right_pin()

            def write_state(self, state):
                with open("state.log", "w") as f:
                    f.write(state)

            def write_distance(self, distance):
                with open("distance.log", "w") as f:
                    f.write(str(distance))

            def move_left(self, distance=0):
                self.state = "left"
                self.write_state(self.state)
                relay_pin(ON)
                pixtend.pwm0_ctrl(0b01111011)           # PWM Channels A & B - ON
                dir_pin(ON)

            def move_right(self, distance = 0):
                self.state = "right"
                self.write_state(self.state)
                relay_pin(ON)
                pixtend.pwm0_ctrl(0b01111011)           # PWM Channels A & B - ON
                dir_pin(OFF)

            def halt(self):
                self.state = "halt"
                self.write_state(self.state)
                relay_pin(OFF)
                pixtend.pwm0_ctrl(0b00011011)           # PWM Channels A & B - OFF

            def stop(self):
                self.state = "stop"
                self.write_state(self.state)
                pixtend.pwm0_ctrl(0b00011011)           # PWM Channels A & B - OFF
                relay_pin(OFF)
                self.pi.stop()

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


                def manual_control_core(self):
                    try:
                        while True:
                            oldstate = self.state
                            if self.btn_is_left():
                                self.move_left()
                                self.distance += 0.1*self.velocity
                                self.write_distance(self.distance)
                            elif self.btn_is_right():
                                self.move_right()
                                self.distance -= 0.1*self.velocity
                                self.write_distance(self.distance)
                            else:
                                self.halt()
                            if oldstate != self.state:
                                print(self.state)

                            sleep(.1)

                    except KeyboardInterrupt:
                        print("\nCtrl-C pressed.  Stopping PIGPIO and exiting...")
                    finally:
                        self.stop()

                # cleanup function - closes all PiXtend's internal variables, objects, drivers, communication, etc
            def cleanup(self):
                pixtend.close()
                pxitend = None

        self.package_obj = ConveyorBeltX()
        return self.package_obj

    def __exit__(self, exc_type, exc_value, traceback):
        self.package_obj.cleanup()
