''' This file is for the configuration of the robot and the control loop.'''

################################################################################
# CHANGE THESE VALUES TO MATCH YOUR ROBOT

# Define the robot's host IP and port
ROBOT_HOST = "169.254.15.222"
ROBOT_PORT = 30004

################################################################################
# Robot real-time control
import math

ACCELERATION = 0.3  # Robot acceleration value
VELOCITY = 0.3  # Robot speed value

# The Joint position the robot starts at
ROBOT_START_POS = (math.radians(39),
                   math.radians(-72),
                   math.radians(92),
                   math.radians(-105),
                   math.radians(-91),
                   math.radians(-275))

################################################################################
# TCP positions

# enter the configuration of the tcp points you want to use
# tcp_pos_config = [0,1,0,2,3,4,3,2]
# tcp_pos_config = [7,8,9,10,9,8]
# tcp_pos_config = [0, 1, 0, 2, 3, 4, 3, 4, 3, 5, 6, 7, 8, 9, 10, 9, 10, 8, 7, 6]
tcp_pos_config = [0]
# RX,RY,RZ for planar on x-y axis = 2.951, 1.077, ...

# single string (move in y direction)
tcp_pos_0 = [-0.036, -0.192, 0.176, 2.961, 1.165, 0.097]
tcp_pos_1 = [-0.198, -0.319, 0.176, 2.969, 1.172, 0.117]
# tcp_pos_0 = [-0.24, 0.015, 0.147, 2.255, 2.221, 0] # moving back
# tcp_pos_1 = [-0.24, -0.266, 0.147, 2.255, 2.221, 0] # playing

# lower string
tcp_pos_2 = [-0.09, -0.212, 0.209, 0.49, 3.118, 0.035] # moving back
tcp_pos_3 = [-0.09, -0.212, 0.199, 0.49, 3.118, 0.035] # position on string
tcp_pos_4 = [0.288, -0.266, 0.219, 0.680, 3.144, 0.069] # moving front

# upper string
tcp_pos_5 = [-0.258, -0.212, 0.209, 0.49, 3.118, 0.035] # moving more back (from pos 3)
tcp_pos_6 = [-0.258, -0.212, 0.209, 1.212, 2.908, 0.035] # rotating bow out of frame
tcp_pos_7 = [-0.098, -0.136, 0.522, 1.431, 2.755, -0.091] # moving up
tcp_pos_8 = [-0.011, -0.167, 0.522, 0.617, 3.028, -0.072] # moving to new position (string)
tcp_pos_9 = [0.0393, -0.171, 0.406, 0.655, 2.799, -0.257] # position on string
tcp_pos_10 = [0.23, -0.237, 0.475, 0.655, 2.799, -0.257] # moving front

# servoj
tcp_pos_servoj_0 = tcp_pos_0.copy()
tcp_pos_servoj_1 = tcp_pos_1.copy()


### test for interpolation
# tcp_pos_0 = [-0.15, -0.160, 0.178, 2.147, 2.387, 0.076]
# tcp_pos_1 = [-0.15, -0.400, 0.148, 2.147, 2.387, 0.076]
# tcp_pos_2 = [-0.15, -0.160, 0.178, 0.395, 3.16, 0.108]

####
# TCP positions (x,y,z,rx,ry,rz in base view) between which the robot moves
# be careful that unit is in meters and radians (on the panel it is mm and radians)
####
# playing the string with the bridge
# the bow starts from behind and moves a little downwards while going a bit up (-4mm in z direction)
# tcp_pos_0 = [-0.15, -0.160, 0.152, 2.147, 2.387, 0.076]
# tcp_pos_1 = [-0.15, -0.400, 0.148, 2.147, 2.387, 0.076]

# tcp_pos_0 = [-0.15, -0.251, 0.130, 2.147, 2.387, 0.076]
# tcp_pos_1 = [-0.15, -0.166, 0.130, 2.147, 2.387, 0.076]

# tcp_pos_0 = [-0.119, -0.528, 0.388, 0.03, -2.8, 1.5]
# tcp_pos_1 = [-0.119, -0.528, 0.388, 0.13, -2.8, 1.5]

# daniel
# tcp_pos_0 = [-0.12, -0.51, 0.21, 0, 3.11, 0.04]
# tcp_pos_1 = [-0.12, -0.51, 0.21, 0.6, 3.11, 0.04]
# tcp_pos_2 = [-0.12, -0.51, 0.21, 0, 3.11, 0.14]

# enter the configuration of the tcp points you want to use
tcp_poses_sel = []
# make a list of the tcp points you want to use
for pos in tcp_pos_config:
    tcp_poses_sel.append(globals()["tcp_pos_%i" % pos])

################################################################################
# joint (q) positions

import math

# convert degree to radians
def deg_to_rad(deg):
    return math.radians(deg)

q_pos_config = [0]

# single string (move in y direction)
q_pos_deg_0 = [39, -72, 92, -105, -91, -275]
q_pos_deg_1 = [90, -72, 92, -105, -91, -275]
q_pos_deg_2 = [90, -72, 70, -105, -91, -275]

q_pos_0 = [deg_to_rad(q) for q in q_pos_deg_0]
q_pos_1 = [deg_to_rad(q) for q in q_pos_deg_1]
q_pos_2 = [deg_to_rad(q) for q in q_pos_deg_2]

# enter the configuration of the tcp points you want to use
q_poses_sel = []
# make a list of the q points you want to use
for pos in q_pos_config:
    q_poses_sel.append(globals()["q_pos_%i" % pos])