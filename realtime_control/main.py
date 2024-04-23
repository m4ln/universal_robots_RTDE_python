"""
Face_tracking01
Python program for realtime face tracking of a Universal Robot (tested with UR5cb)
Demonstration Video: https://youtu.be/HHb-5dZoPFQ
Explanation Video: https://www.youtube.com/watch?v=9XCNE0BmtUg

Created by Robin Godwyll
License: GPL v3 https://www.gnu.org/licenses/gpl-3.0.en.html

"""
import random

import URBasic
import math
import time
import math3d as m3d
from pythonosc import dispatcher
from pythonosc import osc_server
from typing import List, Any
import threading

from config import ROBOT_HOST, tcp_pos_servoj_0, tcp_pos_servoj_1

osc_ip = "127.0.0.1"
osc_port = 12345

timestamp = 0
min_interval = 0.02
debug = True

def print_osc(address: str, *osc_arguments: List[Any]) -> None:
    print(f"{address}: {osc_arguments}")

# moves with predefined y/p/y values when receiving only 3 arguments
def move_cartesian(address: str, *osc_arguments: List[Any]) -> None:
    global timestamp, min_interval, speed, acceleration, cnt, setp, debug, robot

    # con.send_start()
    # state = con.receive()
    # if state is None:
    #     return

    if osc_arguments[2] != 50.0:
        return

    current_time = time.time()
    # tcp_pose = state.actual_TCP_pose
    target_x = (osc_arguments[0] - 500) * 0.001
    target_y = (osc_arguments[1] - 400) / 1000
    target_z = (osc_arguments[2] + 140) / 1000

    if len(osc_arguments) == 6:
        target_roll = osc_arguments[3]
        target_pitch = osc_arguments[4]
        target_yaw = osc_arguments[5]
    else:
        target_roll = 3.14
        target_pitch = 0
        target_yaw = 0.04

    # if (current_time - timestamp) > min_interval:
        # print('current time - timestamp = ' + str(current_time - timestamp))
        # print('min_interval = ' + str(min_interval))

    if debug:
        print(osc_arguments)

    new_setp = [target_x, target_y, target_z, target_roll, target_pitch,
                target_yaw]

    print("New pose = " + str(new_setp))

    robot.set_realtime_pose(new_setp)

    timestamp = current_time

    # elif debug:
        # print("message overflow, discarding request")
        # print("lower min_interval if you want to send with shorter intervals")


"""SETTINGS AND VARIABLES ________________________________________________________________"""

ROBOT_IP = ROBOT_HOST
ACCELERATION = 0.3  # Robot acceleration value
VELOCITY = 0.3  # Robot speed value

# The Joint position the robot starts at
robot_startposition = (math.radians(39),
                    math.radians(-72),
                    math.radians(92),
                    math.radians(-105),
                    math.radians(-91),
                    math.radians(-275))

# Size of the robot view-window
# The robot will at most move this distance in each direction
max_x = 0.2
max_y = 0.2

# Maximum Rotation of the robot at the edge of the view window
hor_rot_max = math.radians(50)
vert_rot_max = math.radians(25)

time.sleep(0.2)



"""FUNCTIONS _____________________________________________________________________________"""

"""def convert_rpy(angles):

    # This is very stupid:
    # For some reason this doesnt work if exactly  one value = 0
    # the following simply make it a very small value if that happens
    # I do not understand the math behind this well enough to create a better solution
    zeros = 0
    zero_pos = None
    for i,ang in enumerate(angles):
        if ang == 0 :
            zeros += 1
            zero_pos = i
    if zeros == 1:
        #logging.debug("rotation value" + str(zero_pos+1) +"is 0 a small value is added")
        angles[zero_pos] = 1e-6

    roll = angles[0]
    pitch = angles[1]
    yaw = angles[2]

    # print ("roll = ", roll)
    # print ("pitch = ", pitch)
    # print ("yaw = ", yaw)
    # print ("")

    for ang in angles:
        # print(ang % np.pi)
        pass

    if roll == pitch == yaw:

        if roll % np.pi == 0:
            rotation_vec = [0, 0, 0]
            return rotation_vec

    yawMatrix = np.matrix([
    [math.cos(yaw), -math.sin(yaw), 0],
    [math.sin(yaw), math.cos(yaw), 0],
    [0, 0, 1]
    ])
    # print("yawmatrix")
    # print(yawMatrix)

    pitchMatrix = np.matrix([
    [math.cos(pitch), 0, math.sin(pitch)],
    [0, 1, 0],
    [-math.sin(pitch), 0, math.cos(pitch)]
    ])
    # print("pitchmatrix")
    # print(pitchMatrix)

    rollMatrix = np.matrix([
    [1, 0, 0],
    [0, math.cos(roll), -math.sin(roll)],
    [0, math.sin(roll), math.cos(roll)]
    ])
    # print("rollmatrix")
    # print(rollMatrix)

    R = yawMatrix * pitchMatrix * rollMatrix
    # print("R")
    # print(R)

    theta = math.acos(((R[0, 0] + R[1, 1] + R[2, 2]) - 1) / 2)
    # print("theta = ",theta)
    multi = 1 / (2 * math.sin(theta))
    # print("multi = ", multi)


    rx = multi * (R[2, 1] - R[1, 2]) * theta
    ry = multi * (R[0, 2] - R[2, 0]) * theta
    rz = multi * (R[1, 0] - R[0, 1]) * theta

    rotation_vec = [rx,ry,rz]
    # print(rx, ry, rz)
    return rotation_vec
"""

def check_max_xy(xy_coord):
    """
    Checks if the face is outside of the predefined maximum values on the lookaraound plane

    Inputs:
        xy_coord: list of 2 values: x and y value of the face in the lookaround plane.
            These values will be evaluated against max_x and max_y

    Return Value:
        x_y: new x and y values
            if the values were within the maximum values (max_x and max_y) these are the same as the input.
            if one or both of the input values were over the maximum, the maximum will be returned instead
    """

    x_y = [0, 0]
    #print("xy before conversion: ", xy_coord)

    if -max_x <= xy_coord[0] <= max_x:
        # checks if the resulting position would be outside of max_x
        x_y[0] = xy_coord[0]
    elif -max_x > xy_coord[0]:
        x_y[0] = -max_x
    elif max_x < xy_coord[0]:
        x_y[0] = max_x
    else:
        raise Exception(" x is wrong somehow:", xy_coord[0], -max_x, max_x)

    if -max_y <= xy_coord[1] <= max_y:
        # checks if the resulting position would be outside of max_y
        x_y[1] = xy_coord[1]
    elif -max_y > xy_coord[1]:
        x_y[1] = -max_y
    elif max_y < xy_coord[1]:
        x_y[1] = max_y
    else:
        raise Exception(" y is wrong somehow", xy_coord[1], max_y)
    #print("xy after conversion: ", x_y)

    return x_y

def set_lookorigin():
    """
    Creates a new coordinate system at the current robot tcp position.
    This coordinate system is the basis of the face following.
    It describes the midpoint of the plane in which the robot follows faces.

    Return Value:
        orig: math3D Transform Object
            characterises location and rotation of the new coordinate system in reference to the base coordinate system

    """
    position = robot.get_actual_tcp_pose()
    orig = m3d.Transform(position)
    return orig

def move_to_face(robot_pos):
    """
    Function that moves the robot to the position of the face

    Inputs:
        list_of_facepos: a list of face positions captured by the camera, only the first face will be used
        robot_pos: position of the robot in 2D - coordinates

    Return Value:
        prev_robot_pos: 2D robot position the robot will move to. The basis for the next call to this funtion as robot_pos
    """

    # print("..", robot_target_xy)

    prev_robot_pos = robot_pos

    x = prev_robot_pos[0] + random.uniform(0, 0.01)
    y = prev_robot_pos[1] + random.uniform(0, 0.01)
    z = 0
    xyz_coords = m3d.Vector(x, y, z)

    x_pos_perc = x / max_x
    y_pos_perc = y / max_y

    x_rot = x_pos_perc * hor_rot_max
    y_rot = y_pos_perc * vert_rot_max * -1

    tcp_rotation_rpy = [y_rot, x_rot, 0]
    # tcp_rotation_rvec = convert_rpy(tcp_rotation_rpy)
    tcp_orient = m3d.Orientation.new_euler(tcp_rotation_rpy, encoding='xyz')
    position_vec_coords = m3d.Transform(tcp_orient, xyz_coords)

    oriented_xyz = origin * position_vec_coords
    oriented_xyz_coord = oriented_xyz.get_pose_vector()

    coordinates = oriented_xyz_coord

    qnear = robot.get_actual_joint_positions()
    next_pose = coordinates
    # robot.set_realtime_pose(next_pose)

    return prev_robot_pos

"""LOOP ____________________________________________________________________"""

# initialise robot with URBasic
print("initialising robot")
robotModel = URBasic.robotModel.RobotModel()
robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_IP,robotModel=robotModel)

robot.reset_error()
print("robot initialised")
time.sleep(1)

# Move Robot to the midpoint of the lookplane
# robot.movej(q=robot_startposition, a= ACCELERATION, v= VELOCITY )

robot_position = [0,0]
origin = set_lookorigin()

robot.init_realtime_control()  # starts the realtime control loop on the Universal-Robot Controller
time.sleep(1) # just a short wait to make sure everything is initialised

cnt= 0

try:
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/position", move_cartesian)
    # dispatcher.map("/position", print_osc)


    server = osc_server.ThreadingOSCUDPServer(
              (osc_ip, osc_port), dispatcher)
    print("Serving on {}".format(server.server_address))
    # Create a new thread for the OSC server
    server_thread = threading.Thread(target=server.serve_forever)

    # Start the thread
    server_thread.start()

except KeyboardInterrupt:
    print("closing robot connection")
    # Remember to always close the robot connection, otherwise it is not possible to reconnect
    robot.close()

except:
    robot.close()