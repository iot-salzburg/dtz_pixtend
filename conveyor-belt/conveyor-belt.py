# Salzburg Research ForschungsgesmbH
# Christoph Schranz & Armin Niedermueller
# Conveyor Belt Control

from time import sleep
import pigpio

CYCLE = 128

DIR = 20    # Direction GPIO Pin
STEP = 21   # Step GPIO Pin
LEFT = 16   # GPIO pin of left
RIGHT = 19  # GPIO pin of right
RELAY = 12  # to control the relais


# Connect to pigpiod daemon
pi = pigpio.pi()

# Set up pins as an output
pi.set_mode(DIR, pigpio.OUTPUT)
pi.set_mode(STEP, pigpio.OUTPUT)
pi.set_mode(RELAY, pigpio.OUTPUT)
pi.write(RELAY, 1)

# Set up input switch
pi.set_mode(LEFT, pigpio.INPUT)
pi.set_mode(RIGHT, pigpio.INPUT)
pi.set_pull_up_down(LEFT, pigpio.PUD_UP)
pi.set_pull_up_down(RIGHT, pigpio.PUD_UP)

MODE = (14, 15, 18)   # Microstep Resolution GPIO Pins
RESOLUTION = {'Full': (0, 0, 0),
              'Half': (1, 0, 0),
              '1/4': (0, 1, 0),
              '1/8': (1, 1, 0),
              '1/16': (0, 0, 1),
              '1/32': (1, 0, 1)}
for i in range(3):
    pi.write(MODE[i], RESOLUTION['Full'][i])

# Set duty cycle and frequency
pi.set_PWM_dutycycle(STEP, CYCLE)  # PWM 1/2 On 1/2 Off
pi.set_PWM_frequency(STEP, 1000)   # 500 pulses per second


state = None
try:
    while True:
        oldstate = state
        if pi.read(LEFT) == 0:
            state = "left"
            pi.write(RELAY, 0)
            pi.set_PWM_dutycycle(STEP, CYCLE)  # PWM 1/2 On 1/2 Off
            pi.write(DIR, 1)
        elif pi.read(RIGHT) == 0:
            state = "right"
            pi.write(RELAY, 0)
            pi.set_PWM_dutycycle(STEP, CYCLE)  # PWM 1/2 On 1/2 Off
            pi.write(DIR, 0)
        else:
            state = "halt"
            pi.write(RELAY, 1)
            pi.set_PWM_dutycycle(STEP, 0)      # PWM off

        if state != oldstate:
            print(state)
        sleep(.1)

except KeyboardInterrupt:
    print ("\nCtrl-C pressed.  Stopping PIGPIO and exiting...")
finally:
    pi.set_PWM_dutycycle(STEP, 0)              # PWM off
    pi.write(RELAY, 1)
    pi.stop()
