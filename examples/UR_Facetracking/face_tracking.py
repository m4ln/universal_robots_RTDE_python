#!/usr/bin/env python
# Copyright (c) 2016-2022, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys

sys.path.append("..")
import logging

import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

import time
import math
from imutils.video import VideoStream
import math3d as m3d
import cv2
import imutils
import numpy as np
from config import ROBOT_HOST, ROBOT_PORT, tcp_pos_1

"""SETTINGS AND VARIABLES ________________________________________________________________"""

RASPBERRY_BOOL = False

ACCELERATION = 0.4  # Robot acceleration value
VELOCITY = 0.4  # Robot speed value

# Path to the face-detection model:
pretrained_model = cv2.dnn.readNetFromCaffe("MODELS/deploy.prototxt.txt", "MODELS/res10_300x300_ssd_iter_140000.caffemodel")

video_resolution = (700, 400)  # resolution the video capture will be resized to, smaller sizes can speed up detection
video_midpoint = (int(video_resolution[0]/2),
                  int(video_resolution[1]/2))
video_asp_ratio  = video_resolution[0] / video_resolution[1]  # Aspect ration of each frame
video_viewangle_hor = math.radians(25)  # Camera FOV (field of fiew) angle in radians in horizontal direction

# Variable which scales the robot movement from pixels to meters.
m_per_pixel = 00.00009

# Size of the robot view-window
# The robot will at most move this distance in each direction
max_x = 0.2
max_y = 0.2

# Maximum Rotation of the robot at the edge of the view window
hor_rot_max = math.radians(50)
vert_rot_max = math.radians(25)


vs = VideoStream(src= 0 ,
                 usePiCamera= RASPBERRY_BOOL,
                 resolution=video_resolution,
                 framerate = 13,
                 meter_mode = "backlit",
                 exposure_mode ="auto",
                 shutter_speed = 8900,
                 exposure_compensation = 2,
                 rotation = 0).start()
time.sleep(0.2)

"""FUNCTIONS _____________________________________________________________________________"""

def find_faces_dnn(image):
    """
    Finds human faces in the frame captured by the camera and returns the positions
    uses the pretrained model located at pretrained_model

    Input:
        image: frame captured by the camera

    Return Values:
        face_centers: list of center positions of all detected faces
            list of lists with 2 values (x and y)
        frame: new frame resized with boxes and probabilities drawn around all faces

    """

    frame = image
    frame = imutils.resize(frame, width= video_resolution[0])

    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the detections and predictions
    pretrained_model.setInput(blob)

    # the following line handles the actual face detection
    # it is the most computationally intensive part of the entire program
    # TODO: find a quicker face detection model
    detections = pretrained_model.forward()
    face_centers = []
    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence < 0.4:
            continue

        # compute the (x, y)-coordinates of the bounding box for the object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")


        # draw the bounding box of the face along with the associated probability
        text = "{:.2f}%".format(confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10

        face_center = (int(startX + (endX - startX) / 2), int(startY + (endY - startY) / 2))
        position_from_center = (face_center[0] - video_midpoint[0], face_center[1] - video_midpoint[1])
        face_centers.append(position_from_center)

        cv2.rectangle(frame, (startX, startY), (endX, endY),
                      (0, 0, 255), 2)
        cv2.putText(frame, text, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        #cv2.putText(frame, str(position_from_center), face_center, 0, 1, (0, 200, 0))
        cv2.line(frame, video_midpoint, face_center, (0, 200, 0), 5)
        cv2.circle(frame, face_center, 4, (0, 200, 0), 3)

    return face_centers, frame

def show_frame(frame):
    cv2.imshow('RobotCamera', frame)
    k = cv2.waitKey(6) & 0xff

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

def set_lookorigin(state):
    """
    Creates a new coordinate system at the current robot tcp position.
    This coordinate system is the basis of the face following.
    It describes the midpoint of the plane in which the robot follows faces.

    Return Value:
        orig: math3D Transform Object
            characterises location and rotation of the new coordinate system in reference to the base coordinate system

    """
    position = state.actual_TCP_pose
    print("position: ", position)
    orig = m3d.Transform(position)
    return orig

def move_to_face(list_of_facepos,robot_pos, con):
    """
    Function that moves the robot to the position of the face

    Inputs:
        list_of_facepos: a list of face positions captured by the camera, only the first face will be used
        robot_pos: position of the robot in 2D - coordinates

    Return Value:
        prev_robot_pos: 2D robot position the robot will move to. The basis for the next call to this funtion as robot_pos
    """

    state = con.receive()

    face_from_center = list(list_of_facepos[0])  # TODO: find way of making the selected face persistent

    prev_robot_pos = robot_pos
    scaled_face_pos = [c * m_per_pixel for c in face_from_center]

    robot_target_xy = [a + b for a, b in zip(prev_robot_pos, scaled_face_pos)]
    # print("..", robot_target_xy)

    robot_target_xy = check_max_xy(robot_target_xy)
    prev_robot_pos = robot_target_xy

    x = robot_target_xy[0]
    y = robot_target_xy[1]
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
    qnear = state.actual_TCP_pose
    next_pose = coordinates
    print("next pose: ", next_pose)
    con.send(next_pose)

    return prev_robot_pos

def setp_to_list(sp):
    '''Convert the setpoint to a list.'''
    sp_list = []
    for i in range(0, 6):
        sp_list.append(sp.__dict__["input_double_register_%i" % i])
    return sp_list

def list_to_setp(sp, list):
    '''Convert the list to a setpoint.'''
    for i in range(0, 6):
        sp.__dict__["input_double_register_%i" % i] = list[i]
    return sp

"""LOOP _____________________________________________________________________________"""

# logging.basicConfig(level=logging.INFO)

# Define the configuration file name
config_filename = "face_tracing_configuration.xml"

# Flag to keep the control loop running
keep_running = True

logging.getLogger().setLevel(logging.INFO)

# Parse the configuration file
conf = rtde_config.ConfigFile(config_filename)
# Get the recipes for state, setpoint, and watchdog from the configuration file
state_names, state_types = conf.get_recipe("state")
setp_names, setp_types = conf.get_recipe("setp")
watchdog_names, watchdog_types = conf.get_recipe("watchdog")

# Create a connection to the robot
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
# Establish the connection
con.connect()

# get controller version
con.get_controller_version()

# setup recipes
con.send_output_setup(state_names, state_types)
setp = con.send_input_setup(setp_names, setp_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)

# Initialize the setpoint registers to 0
setp.input_double_register_0 = 0
setp.input_double_register_1 = 0
setp.input_double_register_2 = 0
setp.input_double_register_3 = 0
setp.input_double_register_4 = 0
setp.input_double_register_5 = 0

# The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
watchdog.input_int_register_0 = 0

# start data synchronization
if not con.send_start():
    sys.exit()

robot_position = [0,0]
origin = set_lookorigin(con.receive())

# move to startposition
tcp_start_pos = tcp_pos_1
list_to_setp(setp, tcp_start_pos)
print("moving to start position (TCP) = " + str(tcp_start_pos))
# send new setpoint
con.send(setp)
# reset watchdog
move_completed = False
watchdog.input_int_register_0 = 1

cnt = 0

try:
    print("starting loop")
    # control loop
    # move_completed = True
    while keep_running:
        # receive the current state
        state = con.receive()

        if state is None:
            break
        # If a move has been completed and the robot is ready for a new one
        if move_completed and state.output_int_register_0 == 1:
            frame = vs.read()
            face_positions, new_frame = find_faces_dnn(frame)
            show_frame(new_frame)
            print(face_positions)
            if face_positions != []:
                print("face found")
                tcp_pose = state.actual_TCP_pose
                print(tcp_pose)
                # rotate the tcp pose (rx, ry) relatively to 10%
                if cnt % 2 == 0:
                    tcp_pose[3] += 0.1
                    tcp_pose[4] += 0.1
                else:
                    tcp_pose[3] -= 0.1
                    tcp_pose[4] -= 0.1
                cnt += 1
                print(tcp_pose)
                list_to_setp(setp, tcp_pose)
                con.send(setp)
            # if len(face_positions) > 0:
            #     robot_position = move_to_face(face_positions, robot_position, con)
            move_completed = False
            # # Determine the new setpoint
            # new_setp = setp1 if setp_to_list(setp) == setp2 else setp2
            # # Update the setpoint
            # list_to_setp(setp, new_setp)
            # print("New pose = " + str(new_setp))
            # # send new setpoint
            # con.send(setp)
            # set watchdog
            watchdog.input_int_register_0 = 1
        # If a move is in progress and the robot is not ready for a new one
        elif not move_completed and state.output_int_register_0 == 0:
            print("Move to confirmed pose (TCP)= " + str(state.target_TCP_pose))
            move_completed = True
            # reset watchdog
            watchdog.input_int_register_0 = 0

        # kick watchdog
        con.send(watchdog)

    con.send_pause()
    con.disconnect()
except KeyboardInterrupt:
    print("closing robot connection")
    # Remember to always close the robot connection, otherwise it is not possible to reconnect
    con.disconnect()
except:
    con.disconnect()
