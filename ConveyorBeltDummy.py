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

import threading
import logging
import time

class ConveyorBeltDummy:
    def __init__(self):

        self.logger = logging.getLogger(__name__)

        self.shotstate = 0
        self.state = "init" # possible states: "left", "right", "halt", "stop", "fail"
        self.distance = 0.0
        self.total_distance = 0.0
        self.service_interval = 2 # maintenance is required, if the total distance exceeds this number
        self.sim_breakdown = 10    # we simulate a breakdown, if the total distance exceeds this number
        self.maintenance_required = False


        self.velocity = 0.05428                 # Velocity of the belt im m/s (5.5cm/s)

        try:
            with open("state.log") as f:
                self.state = f.read()
            with open("distance.log") as f:
                self.distance = float(f.read())
            with open("total_distance.log") as f:
                self.total_distance = float(f.read())
                if self.total_distance > self.service_interval:
                    self.maintenance_required = True

            self.logger.info("restored conveyor belt (state, distance, total_distance) ({}, {}, {})".format(self.state, self.distance, self.total_distance))
        except:
            self.logger.info("could not restore state, creating new")

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

    def write_total_distance(self, total_distance):
        with open("total_distance.log", "w") as f:
            f.write(str(total_distance))

    def busy_light(self, busy):
        if busy is True:
            True                   # Red light ON & Green light OFF
        else:
            False                  # Red light OF & Green light ON
        return True

    def move_left(self):
        self.state = "left"
        self.write_state(self.state)

    def move_right(self):
        self.state = "right"
        self.write_state(self.state)

    def halt(self):
        self.state = "halt"
        self.write_state(self.state)

    def init(self):
        self.state = "init"
        self.write_state(self.state)

    def fail(self):
        self.state = "fail"
        self.write_state(self.state)

    def stop(self):
        self.state = "stop"
        self.write_state(self.state)

    def wait_for_it(self, distance):
        with open("total_distance.log") as f:
            self.total_distance = float(f.read())
        init_state = self.state
        traveltime = distance/self.velocity
        was_interrrupted = False
        self.logger.info("start moving %sm to %s for %ss", distance, init_state, traveltime)
        starttime = prevtime = time.time()
        while prevtime < (starttime + traveltime):
            time.sleep(0.1)
            currenttime = time.time()
            looptime = currenttime-prevtime
            currentdistance = looptime*self.velocity
            self.logger.debug("moved %sm to %s in %ss", currentdistance, init_state, looptime)
            if self.state != init_state:
                was_interrrupted = True
                break

            if init_state == "fail":
                self.logger.info("can't move in fail state, reset total dist!")
                return False

            if init_state == "left":
                self.distance += currentdistance
                self.write_distance(self.distance)
                self.total_distance += currentdistance
                self.write_total_distance(self.total_distance)
            elif init_state == "right":
                self.distance -= currentdistance
                self.write_distance(self.distance)
                self.total_distance += currentdistance
                self.write_total_distance(self.total_distance)

            if self.total_distance > self.service_interval:
                self.maintenance_required = True
            else:
                self.maintenance_required =  False

            if self.total_distance > self.sim_breakdown:
                self.fail()
                self.logger.info("stopped move due to failure at distance %sm", self.total_distance)
                return False

            prevtime = currenttime

        self.logger.info("finished move of %sm to %s in %ss", distance, init_state, traveltime)
        self.halt()
        return True

    def move_left_for(self, distance=0):
        if self.state == "halt" or self.state == "init":
            self.logger.debug("spawning thread for move_left")
            self.move_left()
            waiting = threading.Thread(name='waiter', target=self.wait_for_it, args=(distance,))
            waiting.start()
            waiting.join()

    def move_right_for(self, distance=0):
        if self.state == "halt" or self.state == "init":
            self.logger.debug("spawning thread for move_right")
            self.move_right()
            waiting = threading.Thread(name='waiter', target=self.wait_for_it, args=(distance,))
            waiting.start()
            waiting.join()

    def reset_totaldistance(self, totaldist=0):
        if totaldist < self.service_interval:
            self.maintenance_required = False

        self.init()
        self.write_total_distance(totaldist)
        self.write_distance(totaldist)
