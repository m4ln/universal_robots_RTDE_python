import sys
sys.path.append("..")
import threading
import time
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

# Global flag to control the recording loop
recording_flag = False
recording_thread = None

robotModel = URBasic.robotModel.RobotModel()
robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_HOST, robotModel=robotModel)

def create_new_file():
    global json_data, json_filename
    json_data = []
    json_filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[('JSON Files', '*.json')])
    if json_filename:
        save_json(json_filename, json_data)

def open_file_dialog():
    global json_data

    filename = filedialog.askopenfilename(filetypes=[('JSON Files', '*.json')])
    if filename:
        global json_filename
        json_filename = filename
        json_data = load_json(json_filename)

def load_json(filename):
    global moves
    with open(filename) as file:
        data = json.load(file)
    
    moves = data
    return data

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def save_changes():
    global json_data, moves

    save_json(json_filename, list(moves))
    print("Changes saved.")

def get_robot_positions(interval=1.0):
    """
    Runs a loop that retrieves the robot's joint positions and stores the results with timestamps.

    Args:
        interval (float): Time interval (in seconds) between position updates.

    Returns:
        A list of dictionaries, where each dictionary contains the timestamp and
        the corresponding joint positions.
    """
    global recording_flag, moves, json_data
    robot_positions = []
    last_time = time.time()

    while recording_flag:
        #position = [1,1,1,1,1,1]#    robot.get_actual_joint_positions()
        # position = robot.get_actual_joint_positions()
        position = robot.get_actual_tcp_pose().tolist()

        
        timestamp = time.time() - last_time
        last_time = timestamp
        robot_positions.append({'timestamp': interval, 'position': position})
        print("recording {}".format(position))
        time.sleep(interval)

    moves = robot_positions
    json_data = moves
    return robot_positions

def replay_robot_positions(robot_positions):
    """
    Replays the robot positions stored in the `robot_positions` list.

    Args:
        robot_positions (list): A list of dictionaries, where each dictionary contains the
            timestamp and the corresponding joint positions.
    """
    if not robot_positions:
        print("No robot positions to replay.")
        return

    init_robot()
    last_time = time.time() #robot_positions[0]['timestamp']

    for position_data in robot_positions:
        timestamp = position_data['timestamp']
        position = position_data['position']

        # Set the robot's pose using the stored joint positions
        robot.set_realtime_pose(position)
        print("sending {} at time {}".format(position, timestamp))

        # Wait for the appropriate delay based on the timestamp
        delay = timestamp # - (time.time() - start_time)
        if delay > 0:
            time.sleep(delay)

def start_recording():
    """
    Starts the recording loop in the `get_robot_positions()` function.
    """
    global recording_flag, recording_thread
    recording_flag = True
    recording_thread = threading.Thread(target=get_robot_positions, args=(0.05,))
    recording_thread.start()

def stop_recording():
    """
    Stops the recording loop in the `get_robot_positions()` function.
    """
    global recording_flag, recording_thread, json_data
    recording_flag = False
    if recording_thread:
        recording_thread.join()

    print("Recording stopped.")

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

def clear():
    global moves
    moves = []

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

def home1():
    print(robot.get_actual_joint_positions())
    #joints = [-1.49995485e-03, -1.84361376e+00, -4.27633047e-01, -9.55459194e-01, 1.55824673e+00,  1.41437389e+01]
    joints = [-1.85186068e-03, -8.55259435e-01, -1.33400774e+00, -1.02435590e+00,
  1.60649371e+00,  1.41792606e+01]
    robot.movej(q=joints, t=5)

def home2():
    print(robot.get_actual_joint_positions())
    joints = [-0.52981788, -1.12756066, -1.77152109, -0.42770417,  1.608863,   14.59378231] #robot.movej(q=joints, t=5)
    robot.movej(q=joints, t=5)

def home3():
    print(robot.get_actual_joint_positions())
    joints = [ 0.73322874, -0.30509599, -1.83537686, -1.23113926,  1.64226055, 13.76494969]
    robot.movej(q=joints, t=5)

def change_speed(speed):
    if speed != 0:
        print("changing speed by a factor of {}".format(speed))
        for position_data in moves:
            position_data['timestamp'] /= speed

def change_speed_folder(speed, directory="performance"):
    if speed == 0:
        return

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the specified directory
    directory_path = os.path.join(script_dir, directory)

    # Sort the filenames in the directory
    filenames = sorted(os.listdir(directory_path))

    for filename in filenames:
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Modify the timestamps
            for entry in data:
                entry['timestamp'] /= speed

            # Write the modified data back to the file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

    print(f"Timestamps modified by a factor of {speed} in all JSON files in the '{directory}' directory.")

# Create root window
root = tk.Tk()
root.title("Robot Motion Planner")

# Create headers frame
headers_frame = ttk.Frame(root)
headers_frame.pack()

# Create New File button
new_button = ttk.Button(root, text="New File", command=create_new_file)
new_button.pack(side=tk.TOP,pady=5, padx=2)


# Create Open File button
open_button = ttk.Button(root, text="Open File", command=open_file_dialog)
open_button.pack(side=tk.TOP,pady=5, padx=2)

# Create Save button
save_button = ttk.Button(root, text="Save Changes", command=save_changes)
save_button.pack(side=tk.TOP,pady=5, padx=2)

# Create buttons
freedrive_button = ttk.Button(root, text="Freedrive Mode", command=set_freedrive)
freedrive_button.pack(side=tk.TOP,pady=5, padx=2)

start_recording_button = ttk.Button(root, text="Start Recording", command=start_recording)
start_recording_button.pack(side=tk.TOP, pady=5, padx=2)

stop_recording_button = ttk.Button(root, text="Stop Recording", command=stop_recording)
stop_recording_button.pack(side=tk.TOP, pady=5, padx=2)

#normalmode_button = ttk.Button(root, text="Normal Mode", command=init_robot)
#normalmode_button.pack(side=tk.TOP,pady=5, padx=2)

replay_positions_button = ttk.Button(root, text="Replay Single Movement", command=lambda: replay_robot_positions(moves))
replay_positions_button.pack(side=tk.TOP, pady=5, padx=2)

clear_positions = ttk.Button(root, text="Clear", command=clear)
clear_positions.pack(side=tk.TOP, pady=5, padx=2)


home_button1 = ttk.Button(root, text="Home 1", command=home1)
home_button1.pack(side=tk.TOP, pady=5, padx=2)

home_button2 = ttk.Button(root, text="Home 2", command=home2)
home_button2.pack(side=tk.TOP, pady=5, padx=2)

home_button3 = ttk.Button(root, text="Home 3", command=home3)
home_button3.pack(side=tk.TOP, pady=5, padx=2)

replay_performance = ttk.Button(root, text="Replay Performance Folder", command=replay_folder)
replay_performance.pack(side=tk.TOP, pady=5, padx=2)

speed_var = tk.DoubleVar()
speed_entry = tk.Entry(root, textvariable=speed_var)
speed_entry.pack(side=tk.TOP, pady=5, padx=2)

speedchange = ttk.Button(root, text="Change Speed of active recording", command=lambda: change_speed(speed_var.get()))
speedchange.pack(side=tk.TOP, pady=5, padx=2)

speedchange_folder = ttk.Button(root, text="Change Speed for performance folder", command=lambda: change_speed_folder(speed_var.get()))
speedchange_folder.pack(side=tk.TOP, pady=5, padx=2)


# Run the GUI main loop
root.mainloop()