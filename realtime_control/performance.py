import sys
sys.path.append("..")
import threading
import time
from pythonosc import dispatcher
from pythonosc import osc_server
from typing import List, Any
import threading
import URBasic
import math
import json
import os

from config_ur import ROBOT_HOST, ACCELERATION, VELOCITY, ROBOT_START_POS
from config_osc import OSC_HOST, OSC_PORT

import tkinter as tk
from tkinter import ttk, filedialog

moves = []
json_data = {}

debug = True

# Define a variable to keep track of the current mode
current_mode = "idle"

#x_offset = tk.StringVar()
#y_offset = tk.StringVar()
#z_offset = tk.StringVar()

def init_robot():
    global robot
    # initialise robot with URBasic
    print("initialising robot")

    robot.reset_error()
    print("robot initialised")
    time.sleep(.1)

    robot.init_realtime_control()  # starts the realtime control loop on the Universal-Robot Controller
    time.sleep(.1)  # just a short wait to make sure everything is initialised

def set_freedrive():
    global robot

    init_robot()
    robot.freedrive_mode()

def replay_robot_positions(robot_positions):
    """
    Replays the robot positions stored in the `robot_positions` list.

    Args:
        robot_positions (list): A list of dictionaries, where each dictionary contains the
            timestamp and the corresponding joint positions.
    """

    global x_offset, y_offset, z_offset

    if not robot_positions:
        print("No robot positions to replay.")
        return

    init_robot()
    last_time = time.time() #robot_positions[0]['timestamp']

    for position_data in robot_positions:
        timestamp = position_data['timestamp']
        position = position_data['position']

        position[0] += x_offset / 1000
        position[1] += y_offset / 1000
        position[2] += z_offset / 1000

        # Set the robot's pose using the stored joint positions
        robot.set_realtime_pose(position)
        print("sending {} at time {}".format(position, timestamp))

        # Wait for the appropriate delay based on the timestamp
        delay = timestamp # - (time.time() - start_time)
        if delay > 0:
            time.sleep(delay)

def replay_folder(directory_path="performance"):
    global moves
    moves = []
    print("replay the whole performance folder")
    init_robot()
        # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the "performance" directory
    performance_dir = os.path.join(script_dir, 'performance')
    
    # Sort the filenames in the directory
    filenames = sorted(os.listdir(directory_path))
    
    for filename in filenames:
        if filename.endswith('.json'):
            file_path = os.path.join(performance_dir, filename)
            with open(file_path) as file:
                data = json.load(file)
                moves.extend(data)
    
    #return moves
    
    replay_robot_positions(moves)

def sum_timestamps_in_directory(directory_path="performance"):
    total_timestamps = 0

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a JSON file
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            
            # Load the JSON data from the file
            with open(file_path, "r") as file:
                data = json.load(file)

                for position_data in data:
                # Add the "timestamp" value to the total
                    total_timestamps += float(position_data["timestamp"])
    
    return total_timestamps

def stop_server():
    global keep_running
    keep_running = False


def close_all(server, logfile, robot):
    server.shutdown()
    server.server_close()
    logfile.close()
    robot.close()


def move_cartesian(address: str, *osc_arguments: List[Any]) -> None:
    """
    Function to move the robot to a new cartesian position
    :param address:
    :param osc_arguments: x, y, z, [optional] roll, pitch, yaw values of the new position

    :return: None
    """

    global speed, acceleration, robot, logfile, prev_osc_arguments, x_offset, z_offset, z_offset, current_mode

    if(current_mode != "osc"):
        return

    # make sure the osc_arguments are in float format
    # store osc_arguments in float variables
    target_x = float(osc_arguments[0])
    target_y = float(osc_arguments[1])
    target_z = float(osc_arguments[2])

    # consider offsets

    target_x += x_offset
    target_y += y_offset
    target_z += z_offset


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

    print("New pose = " + str(new_setp))
    prev_osc_arguments = [target_x, target_y, target_z, target_roll,
                          target_pitch, target_yaw]


def switch_mode(mode):
    global current_mode, headers_label, idle_button, playback_button, touchdesigner_button
    if mode == "idle":
        current_mode = "idle"
        root.configure(background="#f07c7c")
        headers_label.configure(text="IDLE MODE", background="#f07c7c", foreground="black", font=("Arial", 20))
       # idle_button.configure(background="#f07c7c", foreground="white", activebackground="#e86464", activeforeground="white")
       # playback_button.configure(background="#fcd0a1", foreground="black", activebackground="#fbba7c", activeforeground="black")
       # touchdesigner_button.configure(background="#a8d8b9", foreground="black", activebackground="#91c8a2", activeforeground="black")

    #    set_freedrive()
    
    elif mode == "playback":
        current_mode = "playback"
        root.configure(background="#fcd0a1")
        headers_label.configure(text="PLAYBACK", background="#fcd0a1", foreground="black", font=("Arial", 20))

        replay_folder()
        #idle_button.configure()
       # idle_button.configure(background="#f07c7c", foreground="white", activebackground="#e86464", activeforeground="white")
       # playback_button.configure(background="#fcd0a1", foreground="black", activebackground="#fbba7c", activeforeground="black")
       # touchdesigner_button.configure(background="#a8d8b9", foreground="black", activebackground="#91c8a2", activeforeground="black")
    elif mode == "osc":
        current_mode = "osc"
        root.configure(background="#a8d8b9")
        headers_label.configure(text="OSC", background="#a8d8b9", foreground="black", font=("Arial", 20))

        #start osc server



       # idle_button.configure(background="#f07c7c", foreground="white", activebackground="#e86464", activeforeground="white")
       # playback_button.configure(background="#fcd0a1", foreground="black", activebackground="#fbba7c", activeforeground="black")
       # touchdesigner_button.configure(background="#a8d8b9", foreground="black", activebackground="#91c8a2", activeforeground="black")


total_duration = sum_timestamps_in_directory()
print(total_duration)


# GUI

# Create root window
root = tk.Tk()
root.title("Robot Motion Planner")

# Set the window size and make it fixed
root.geometry("200x380")
root.resizable(False, False)

# Make the window always on top
root.wm_attributes("-topmost", 1)

# Create headers frame
headers_frame = ttk.Frame(root)
headers_frame.pack()

# Create header label
headers_label = ttk.Label(headers_frame, text="IDLE MODE", font=("Arial", 20))
headers_label.pack(side=tk.TOP, padx=10, pady=10)

status_text = "performance of {:.2f}s duration loaded".format(total_duration)
status_label = ttk.Label(headers_frame, text=status_text, font=("Arial", 10))
status_label.pack(side=tk.TOP, padx=10, pady=10)

# Create mode buttons
idle_button = ttk.Button(root, text="Idle", command=lambda: switch_mode("idle"))
idle_button.pack(side=tk.TOP, pady=5, padx=2)

playback_button = ttk.Button(root, text="Playback", command=lambda: switch_mode("playback"))
playback_button.pack(side=tk.TOP, pady=5, padx=2)

touchdesigner_button = ttk.Button(root, text="OSC", command=lambda: switch_mode("osc"))
touchdesigner_button.pack(side=tk.TOP, pady=5, padx=2)

# Create input fields frame
input_frame = ttk.Frame(root)
input_frame.pack()

x_offset = tk.DoubleVar()
y_offset = tk.DoubleVar()
z_offset = tk.DoubleVar()

# Create input fields
x_label = ttk.Label(input_frame, text="X-Offset:", background=root.cget("background"), foreground="white")
x_label.pack(side=tk.TOP, padx=(10, 5))
x_entry = ttk.Entry(input_frame, textvariable=x_offset, width=3)
x_entry.pack(padx=5)

y_label = ttk.Label(input_frame, text="Y-Offset:", background=root.cget("background"), foreground="white")
y_label.pack(side=tk.TOP, padx=5)
y_entry = ttk.Entry(input_frame, textvariable=y_offset, width=3)
y_entry.pack(side=tk.TOP, padx=5)

z_label = ttk.Label(input_frame, text="Z-Offset:", background=root.cget("background"), foreground="white")
z_label.pack(side=tk.TOP, padx=5)
z_entry = ttk.Entry(input_frame, textvariable=z_offset, width=3)
z_entry.pack(side=tk.TOP, padx=(5, 10))

# Set the button style
style = ttk.Style()
style.configure("TButton", relief="flat", padding=5)
style.map("TButton", background=[("active", "#e86464"), ("pressed", "#e86464")], foreground=[("active", "white"), ("pressed", "white")])


robotModel = URBasic.robotModel.RobotModel()
robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_HOST, robotModel=robotModel)


switch_mode("idle")

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


root.mainloop()
