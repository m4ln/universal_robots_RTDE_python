## This file describes somed examples of how to use the library to communicate with the robot controller.

################################################################################
# How to set start position of the robot
# You can move the robot via the control panel to your defined start postition and read the current joint positions.
# You will get six values, one for each joint. These values are the start position of the robot.
# Enter these values in the example below.

import math
import URBasic

ROBOT_IP = '192.168.178.120'
ACCELERATION = 0.5  # Robot acceleration value
VELOCITY = 0.5  # Robot speed value

# The Joint position the robot starts at
robot_startposition = (math.radians(-218),
                    math.radians(-63),
                    math.radians(-93),
                    math.radians(-20),
                    math.radians(88),
                    math.radians(0))

# initialise robot with URBasic
print("initialising robot")
robotModel = URBasic.robotModel.RobotModel()
robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_IP,robotModel=robotModel)

# Move Robot to the midpoint of the lookplane
robot.movej(q=robot_startposition, a= ACCELERATION, v= VELOCITY )