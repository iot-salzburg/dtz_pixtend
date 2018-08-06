# Salzburg Research ForschungsgesmbH
# Christoph Schranz & Armin Niedermueller
# Conveyor Belt Control

from time import sleep
from multiprocessing import Process


class ConveyorBelt:
    def __init__(self):
        self.state = "init"
        self.distance = 0.0
        self.showstate = 0
        try:
            import pigpio
        except ModuleNotFoundError:
            raise "Module pigpio not found."

        self.CYCLE = 128
        self.velocity = 0.05428  # Velocity of the belt im m/s (5.5cm/s)

        self.DIR = 20  # Direction GPIO Pin
        self.STEP = 21  # Step GPIO Pin
        self.LEFT = 16  # GPIO pin of left
        self.RIGHT = 19  # GPIO pin of right
        self.RELAY = 12  # to control the relais

        # Connect to pigpiod daemon
        self.pi = pigpio.pi()

        # Set up pins as an output
        self.pi.set_mode(self.DIR, pigpio.OUTPUT)
        self.pi.set_mode(self.STEP, pigpio.OUTPUT)
        self.pi.set_mode(self.RELAY, pigpio.OUTPUT)
        self.pi.write(self.RELAY, 1)

        # Set up input switch
        self.pi.set_mode(self.LEFT, pigpio.INPUT)
        self.pi.set_mode(self.RIGHT, pigpio.INPUT)
        self.pi.set_pull_up_down(self.LEFT, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.RIGHT, pigpio.PUD_UP)

        MODE = (14, 15, 18)  # Microstep Resolution GPIO Pins
        RESOLUTION = {'Full': (0, 0, 0),
                      'Half': (1, 0, 0),
                      '1/4': (0, 1, 0),
                      '1/8': (1, 1, 0),
                      '1/16': (0, 0, 1),
                      '1/32': (1, 0, 1)}

        for i in range(3):
            self.pi.write(MODE[i], RESOLUTION['Full'][i])

        # Set duty cycle and frequency
        self.pi.set_PWM_dutycycle(self.STEP, self.CYCLE)  # PWM 1/2 On 1/2 Off
        self.pi.set_PWM_frequency(self.STEP, 1000)   # 500 pulses per second

    def btn_is_left(self):
        return not bool(self.pi.read(self.LEFT))

    def btn_is_right(self):
        return not bool(self.pi.read(self.RIGHT))

    def write_state(self, state):
        with open("state.log", "w") as f:
            f.write(state)

    def write_distance(self, distance):
        with open("distance.log", "w") as f:
            f.write(str(distance))

    def move_left(self, distance = 0):
        self.state = "left"
        self.write_state(self.state)
        self.pi.write(self.RELAY, 1)
        self.pi.set_PWM_dutycycle(self.STEP,self.CYCLE)  # PWM 1/2 On 1/2 Off
        self.pi.write(self.DIR, 1)

    def move_right(self, distance = 0):
        self.state = "right"
        self.write_state(self.state)
        self.pi.write(self.RELAY, 1)
        self.pi.set_PWM_dutycycle(self.STEP, self.CYCLE)  # PWM 1/2 On 1/2 Off
        self.pi.write(self.DIR, 0)

    def halt(self):
        self.state = "halt"
        self.write_state(self.state)
        self.pi.write(self.RELAY, 0)
        self.pi.set_PWM_dutycycle(self.STEP, 0)      # PWM off

    def stop(self):
        self.state = "stop"
        self.write_state(self.state)
        self.pi.set_PWM_dutycycle(self.STEP, 0)     # PWM off
        self.pi.write(self.RELAY, 0)
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

    def manual_control(self, showstate):
        self.showstate = showstate
        manual = Process(target=self.manual_control_core(), args=())
        manual.start()

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
                if oldstate != self.state and self.showstate == 1:
                   print(self.state)

                sleep(.1)

        except KeyboardInterrupt:
            print("\nCtrl-C pressed.  Stopping PIGPIO and exiting...")
        finally:
            self.stop()
