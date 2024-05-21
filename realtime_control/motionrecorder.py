"""
real time control using osc data (copy and modify from Face_tracking01.py)

Python program for realtime face tracking of a Universal Robot (tested with UR5cb)
Demonstration Video: https://youtu.be/HHb-5dZoPFQ
Explanation Video: https://www.youtube.com/watch?v=9XCNE0BmtUg

Created by Robin Godwyll
License: GPL v3 https://www.gnu.org/licenses/gpl-3.0.en.html

"""
import os
import sys
sys.path.append("..")
import URBasic
import math
import time
import math3d as m3d
from pythonosc import dispatcher
from pythonosc import osc_server
from typing import List, Any
import threading
import _thread
import json
import tkinter as tk
from tkinter import ttk, filedialog

from config_ur import ROBOT_HOST, ACCELERATION, VELOCITY, ROBOT_START_POS
from config_osc import OSC_HOST, OSC_PORT

from pynput.keyboard import Key, Listener

moves = []
pose_counter = 1

waypoint_file = "moves_waypoints.json"


def save_waypoints(moves, filename):
    with open(filename, 'w') as file:
        json.dump(moves, file)

def load_waypoints(filename):
    with open(filename, 'r') as file:
        moves = json.load(file)
    return moves

# def input_thread(a_list):
#     input()             # use input() in Python3
#     a_list.append(True)

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

#def on_keypress(event):
  #  if event.name == 'l':
   #     print(get_current_position())

#


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




def get_current_position():
    #position = robot.get_actual_tcp_pose()
    
    # switched to joint positions to avoid ambiguous moves 
    position = robot.get_actual_joint_positions()
    return position

# a_list = []
# _thread.start_new_thread(input_thread, (a_list,))



# close connection to robot and osc server on keypress
# if(a_list):
#     print("key")

def on_press(key):
    global moves
    # adding new waypoint

    '''
    Movel along multiple waypoints. By configuring a blend radius continuous movements can be enabled.

    Parameters:
    waypoints: List waypoint dictionaries {pose: [6d], a, v, t, r}
    def movel(self, pose=None, a=1.2, v =0.25, t =0, r =0, wait=True, q=None):

    '''

    try:
        if key.char is not None:
            # Continue with your logic using key.char here
            pass

        if key.char == "a":
            print("getting pos")
            pos = get_current_position()
            print(pos)
            print(type(pos))
            #moves.append(pos.tolist())

            pose_key = "pose" #_" + str(pose_counter)
            pose_values = {}
            pose_values["pose"] = pos.tolist()
            a = 1.1
            v = 1.1
            t = 0.3
            r = 0.015

            #pose_values.append(a)
            #pose_values.append(v)
            #pose_values.append(t)
            #pose_values.append(r)

            pose_values["v"] = v
            pose_values["a"] = a
            pose_values["t"] = t
            pose_values["r"] = r

            print(pose_values)


            ++pose_counter
            #new_move = {}
            #new_move[pose_counter] = pose_values
            moves.append(pose_values) #[pose_key] = pos_values

        # moving through all points    
        elif key.char == "p":
            
            print("replay")
            robot.end_freedrive_mode()
            time.sleep(1)
            robot.init_realtime_control()  # starts the realtime control loop on the Universal-Robot Controller
            time.sleep(1)  # just a short wait to make sure everything is initialised
        
            # go throug a list of dictionaries
            #for smove in moves:
                #robot.stopl()
            #    robot.movel(pose=smove["pose"][:6], r=0.05)#,a=smove["pose"][6],v=smove["pose"][7],r=smove["pose"][9])
                #time.sleep(0.2)

            #doesnt seem to work:
            robot.movel_waypoints(moves)

            # old version
            # for smove in moves:
            #      print(smove)
            #      print(type(smove))
            #      robot.set_realtime_pose(smove)
            #      time.sleep(2)
        
        # clearing points
        elif key.char == "c":
            moves.clear()

        # load waypoints 
        elif key.char == "l":
            moves.clear()
            moves = load_waypoints(waypoint_file)

        # save waypoints
        elif key.char == "s":
            save_waypoints(moves, waypoint_file)


    
    except AttributeError:
        # Handle the case when key.char is not available
        pass

    #print(get_current_position())
    
def on_release(key):
    #print('{0} release'.format(
     #   key))
    if key == Key.esc:
        # Stop listener
        return False

listener = Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()



"""LOOP _____________________________________________________________________"""

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

robot.init_realtime_control()  # starts the realtime control loop on the Universal-Robot Controller
time.sleep(1)  # just a short wait to make sure everything is initialised

robot.freedrive_mode()
# set up a logfile to log the robot position




