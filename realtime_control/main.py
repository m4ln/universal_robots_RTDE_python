"""
real time control using osc data (copy and modify from Face_tracking01.py)

Python program for realtime face tracking of a Universal Robot (tested with UR5cb)
Demonstration Video: https://youtu.be/HHb-5dZoPFQ
Explanation Video: https://www.youtube.com/watch?v=9XCNE0BmtUg

Created by Robin Godwyll
License: GPL v3 https://www.gnu.org/licenses/gpl-3.0.en.html

"""
import os

import URBasic
import math
import time
import math3d as m3d
from pythonosc import dispatcher
from pythonosc import osc_server
from typing import List, Any
import threading

from config_ur import ROBOT_HOST, ACCELERATION, VELOCITY, ROBOT_START_POS
from config_osc import OSC_HOST, OSC_PORT

"""SETTINGS AND VARIABLES ___________________________________________________"""

# Size of the robot view-window
# The robot will at most move this distance in each direction
min_x = -0.2
max_x = 0.2
min_y = -0.39
max_y = -0.27
min_z = 0.18
max_z = 0.4

# Maximum Rotation of the robot at the edge of the view window
hor_rot_max = math.radians(50)
vert_rot_max = math.radians(25)

debug = False
log_folder = 'ur_log'
prev_osc_arguments = [0, 0, 0, 0, 0, 0]

"""FUNCTIONS ________________________________________________________________"""


def stop_server():
    global keep_running
    keep_running = False


def close_all(server, logfile, robot):
    server.shutdown()
    server.server_close()
    logfile.close()
    robot.close()


def remove_folder(folder_name):
    import shutil
    # get current path
    root = os.getcwd()
    path = os.path.join(root, folder_name)

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def print_osc(address: str, *osc_arguments: List[Any]) -> None:
    print(f"{address}: {osc_arguments}")


def move_cartesian(address: str, *osc_arguments: List[Any]) -> None:
    """
    Function to move the robot to a new cartesian position
    :param address:
    :param osc_arguments: x, y, z, [optional] roll, pitch, yaw values of the new position

    :return: None
    """
    global speed, acceleration, robot, logfile, prev_osc_arguments

    # make sure the osc_arguments are in float format
    # store osc_arguments in float variables
    target_x = float(osc_arguments[0])
    target_y = float(osc_arguments[1])
    target_z = float(osc_arguments[2])

    # convert from mm to m
    target_x /= 1000
    target_y /= 1000
    target_z /= 1000

    # check if target_x, target_y, target_z are in the range between min and max
    # if target_x < min_x or target_x > max_x:
    #     print("x is out of range", target_x, min_x, max_x)
    #     return
    # if target_y < min_y or target_y > max_y:
    #     print("y is out of range", target_y, min_y, max_y)
    #     return
    # if target_z < min_z or target_z > max_z:
    #     print("z is out of range", target_z, min_z, max_z)
    #     return

    if len(osc_arguments) == 6:
        target_roll = osc_arguments[3]
        target_pitch = osc_arguments[4]
        target_yaw = osc_arguments[5]
    else:
        target_roll = 3.14
        target_pitch = 0
        target_yaw = 0.04

    if debug:
        print('OSC message:', osc_arguments)

    new_setp = [target_x, target_y, target_z, target_roll, target_pitch,
                target_yaw]

    robot.set_realtime_pose(new_setp)

    # if in the file './ur_log/UrEvent.log' there is a line with the text 'URBasic_realTimeClientEvent - ERROR - SendProgram: Program Stopped but not finished!!!', the program will stop
    root = os.getcwd()
    path = os.path.join(root, log_folder, 'UrEvent.log')
    with open(path, "r") as file:
        for line in file:
            if 'URBasic_realTimeClientEvent - ERROR - SendProgram: Program Stopped but not finiched!!!' in line:
                print("Program Stopped but not finished!!!")
                # write the actual tcp position to the logfile
                tcp_pos = robot.get_actual_tcp_pose()
                logfile.write(
                    f"{'previous:'}{prev_osc_arguments[0]}, {prev_osc_arguments[1]}, {prev_osc_arguments[2]}, {prev_osc_arguments[3]}, {prev_osc_arguments[4]}, {prev_osc_arguments[5]}\n")
                logfile.write(
                    f"{'actual:'}{tcp_pos[0]}, {tcp_pos[1]}, {tcp_pos[2]}, {tcp_pos[3]}, {tcp_pos[4]}, {tcp_pos[5]}\n")
                logfile.write(
                    f"{'target:'}{target_x}, {target_y}, {target_z}, {target_roll}, {target_pitch}, {target_yaw}\n")
                stop_server()
                exit()
                # sys.exit()

    print("New pose = " + str(new_setp))
    prev_osc_arguments = [target_x, target_y, target_z, target_roll,
                          target_pitch, target_yaw]


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
    # print("xy before conversion: ", xy_coord)

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
    # print("xy after conversion: ", x_y)

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


"""LOOP _____________________________________________________________________"""

# remove the folder 'ur_log' and its content
remove_folder(log_folder)

# initialise robot with URBasic
print("initialising robot")
robotModel = URBasic.robotModel.RobotModel()
robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_HOST, robotModel=robotModel)

robot.reset_error()
print("robot initialised")
time.sleep(1)

# Move Robot to the midpoint of the lookplane
# robot.movej(q=ROBOT_START_POS, a= ACCELERATION, v= VELOCITY )

robot_position = [0, 0]
origin = set_lookorigin()

robot.init_realtime_control()  # starts the realtime control loop on the Universal-Robot Controller
time.sleep(1)  # just a short wait to make sure everything is initialised

# set up a logfile to log the robot position
logfile = open("./ur_log/tcp_pos.txt", "w")
# if the file is not empty, overwrite it
logfile.truncate(0)
logfile.write("x, y, z, rx, ry, rz\n")

# Create a flag for running the server
server_running = threading.Event()
server_running.set()

# Set up the OSC server
dispatcher = dispatcher.Dispatcher()
# dispatcher.map("/position", print_osc)
dispatcher.map("/position", move_cartesian)
server = osc_server.BlockingOSCUDPServer(
    (OSC_HOST, OSC_PORT), dispatcher)
print("Serving on {}".format(server.server_address))

keep_running = True

try:
    # Create a new thread for the OSC server
    server_thread = threading.Thread(target=server.serve_forever)
    # Start the thread
    server_thread.start()

    while keep_running:
        time.sleep(1)  # Sleep for a while to reduce CPU usage

    close_all(server, logfile, robot)

except KeyboardInterrupt:
    print("closing robot connection")
    close_all(server, logfile, robot)
    exit()
except:
    close_all(server, logfile, robot)
    exit()
