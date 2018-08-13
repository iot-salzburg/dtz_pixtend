#!/usr/bin/env python
# Salzburg Research ForschungsgesmbH
# Christoph Schranz & Armin Niedermueller

# Conveyor Belt Control - PiXtend
# The electronic layout is from the tutorial:
# https://www.rototron.info/raspberry-pi-stepper-motor-tutorial/

from ConveyorBeltX import ConveyorBeltXResource

with ConveyorBeltXResource() as conbelt:
    conbelt.manual_control()
