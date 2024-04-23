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

import rtde_client_library.rtde.rtde as rtde
import rtde_client_library.rtde.rtde_config as rtde_config
from config_ur import ROBOT_HOST, ROBOT_PORT, tcp_pos_1, tcp_pos_2, tcp_pos_3, tcp_pos_4

# logging.basicConfig(level=logging.INFO)

# Define the configuration file name
config_filename = "x_shape_control_loop_configuration.xml"

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


# start data synchronization
if not con.send_start():
    sys.exit()

# control loop
move_completed = True
while keep_running:
    # receive the current state
    state = con.receive()

    if state is None:
        break

    # If a move has been completed and the robot is ready for a new one
    if move_completed and state.output_int_register_0 == 1:
        move_completed = False
        # Determine the new setpoint
        if setp_to_list(setp) == tcp_pos_1:
            new_setp = tcp_pos_2
        elif setp_to_list(setp) == tcp_pos_2:
            new_setp = tcp_pos_3
        elif setp_to_list(setp) == tcp_pos_3:
            new_setp = tcp_pos_4
        else:
            new_setp = tcp_pos_1
        # Update the setpoint
        list_to_setp(setp, new_setp)
        print("New pose = " + str(new_setp))
        # send new setpoint
        con.send(setp)
        # set watchdog
        watchdog.input_int_register_0 = 1
    # If a move is in progress and the robot is not ready for a new one
    elif not move_completed and state.output_int_register_0 == 0:
        print("Moved to confirmed pose (TCP) = " + str(state.actual_TCP_pose))
        move_completed = True
        # reset watchdog
        watchdog.input_int_register_0 = 0

    # kick watchdog
    con.send(watchdog)

con.send_pause()

con.disconnect()
