import sys
sys.path.append("..")
import threading
import time
#from pythonosc import dispatcher
#from pythonosc import osc_server
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
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
from async_tkinter_loop import async_handler, async_mainloop

class DummyRobot:
    def reset_error(self):
        pass
    def init_realtime_control(self):
        pass
    def freedrive_mode(self):
        pass
    def set_realtime_pose(self, args):
        pass
    def get_actual_joint_positions(self):
        pass
    def movej(self, args):
        pass

moves = []
json_data = {}

debug = True
run_without_connection = False

headers_label = None
status_label = None

stop_flag = False
playback_active = False

if(run_without_connection):
    robot = DummyRobot()
else: 
    robotModel = URBasic.robotModel.RobotModel()
    robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_HOST, robotModel=robotModel)

# Define a variable to keep track of the current mode
current_mode = "idle"

x_offset = 0.0 #tk.StringVar()
y_offset = 0.0 #tk.StringVar()
z_offset = 0.0 #tk.StringVar()

def init_robot(robot):
    #global robot
    # initialise robot with URBasic
    print("initialising robot")

    robot.reset_error()
    print("robot initialised")
    time.sleep(.1)

    robot.init_realtime_control()  # starts the realtime control loop on the Universal-Robot Controller
    time.sleep(.1)  # just a short wait to make sure everything is initialised

def set_freedrive(robot):
    #global robot

    init_robot(robot)
    robot.freedrive_mode()

def replay_robot_positions(robot_positions, robot):
    """
    Replays the robot positions stored in the `robot_positions` list.

    Args:
        robot_positions (list): A list of dictionaries, where each dictionary contains the
            timestamp and the corresponding joint positions.
    """

    global x_offset, y_offset, z_offset, stop_flag, playback_active

    if not robot_positions:
        print("No robot positions to replay.")
        return

    init_robot(robot)
    last_time = time.time() #robot_positions[0]['timestamp']
    stop_flag = False

    for position_data in robot_positions:
        if stop_flag:
            print("ABORTING PLAYBACK")
            playback_active = False
            stop_flag = False
            return
        
        timestamp = position_data['timestamp']
        position = position_data['position']

        position[0] += x_offset
        position[1] += y_offset
        position[2] += z_offset

        # position[0] /= 1000
        # position[1] /= 1000
        # position[2] /= 1000

        # Set the robot's pose using the stored joint positions
        robot.set_realtime_pose(position)
        print("sending {} at time {}".format(position, timestamp))

        # Wait for the appropriate delay based on the timestamp
        delay = timestamp # - (time.time() - start_time)
        if delay > 0:
            time.sleep(delay)

def replay_folder(robot, directory_path="performance"):
    global moves, playback_active
    moves = []
    print("replay the whole performance folder")
    init_robot(robot)
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
    
    # Start the replay_robot_positions function in a separate thread
    playback_active = True
    replay_thread = threading.Thread(target=replay_robot_positions, args=(moves, robot))
    replay_thread.start()

   # replay_robot_positions(moves, robot)

def move_to_home(robot):
    print(robot.get_actual_joint_positions())
    #joints = [-1.49995485e-03, -1.84361376e+00, -4.27633047e-01, -9.55459194e-01, 1.55824673e+00,  1.41437389e+01]
    joints = [-1.85186068e-03, -8.55259435e-01, -1.33400774e+00, -1.02435590e+00,
  1.60649371e+00,  1.41792606e+01]
    print("homing to joint positions: ")
    print(joints)
    robot.movej(q=joints, t=5)
    switch_mode("idle")

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


def close_all(server, robot):
    server.shutdown()
    server.server_close()
    robot.close()


def move_cartesian(address: str, *osc_arguments: List[Any]) -> None:
    """
    Function to move the robot to a new cartesian position
    :param address:
    :param osc_arguments: x, y, z, [optional] roll, pitch, yaw values of the new position

    :return: None
    """

    global robot, speed, acceleration, prev_osc_arguments, x_offset, z_offset, z_offset, current_mode

    if(current_mode != "osc"):
        return

    # make sure the osc_arguments are in float format
    # store osc_arguments in float variables
    target_x = float(osc_arguments[0])
    target_y = float(osc_arguments[1])
    target_z = float(osc_arguments[2])


    # convert from mm to m
    target_x /= 1000
    target_y /= 1000
    target_z /= 1000
    
    # consider offsets, they are already in m
    target_x += x_offset
    target_y += y_offset
    target_z += z_offset

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


def switch_mode(robot, mode):
    global current_mode, headers_label, idle_button, playback_button, touchdesigner_button, headers_label, status_label, playback_active, stop_flag
    if mode == "idle" and not playback_active:
        current_mode = "idle"
        root.configure(background="#f07c7c")
        
        headers_label.configure(text="IDLE MODE", background="#f07c7c", foreground="black", font=("Arial", 20))
        #idle_button.configure(background="#f07c7c", foreground="white", activebackground="#e86464", activeforeground="white")
       # playback_button.configure(background="#fcd0a1", foreground="black", activebackground="#fbba7c", activeforeground="black")
       # touchdesigner_button.configure(background="#a8d8b9", foreground="black", activebackground="#91c8a2", activeforeground="black")

        set_freedrive(robot)
    
    elif mode == "playback" and not playback_active:
        current_mode = "playback"
        root.configure(background="#fcd0a1")
        headers_label.configure(text="PLAYBACK", background="#fcd0a1", foreground="black", font=("Arial", 20))

        replay_folder(robot)
        #idle_button.configure()
       # idle_button.configure(background="#f07c7c", foreground="white", activebackground="#e86464", activeforeground="white")
       # playback_button.configure(background="#fcd0a1", foreground="black", activebackground="#fbba7c", activeforeground="black")
       # touchdesigner_button.configure(background="#a8d8b9", foreground="black", activebackground="#91c8a2", activeforeground="black")
    elif mode == "osc" and not playback_active:
        current_mode = "osc"
        root.configure(background="#a8d8b9")
        headers_label.configure(text="OSC", background="#a8d8b9", foreground="black", font=("Arial", 20))

        #start osc server
        init_robot(robot)

    elif mode == "home" and current_mode == "idle":
        move_to_home(robot)

    elif mode == "home" and current_mode != "idle":
        print("PLEASE SET TO IDLE BEFORE HOMING")

    elif mode == "stop":
        stop_flag = True
       # idle_button.configure(background="#f07c7c", foreground="white", activebackground="#e86464", activeforeground="white")
       # playback_button.configure(background="#fcd0a1", foreground="black", activebackground="#fbba7c", activeforeground="black")
       # touchdesigner_button.configure(background="#a8d8b9", foreground="black", activebackground="#91c8a2", activeforeground="black")

def on_x_offset_change(event):
    global x_offset
    try:
        x_offset = float(event.widget.get())
        x_offset /= 1000
        print(f"X-Offset value changed to: {x_offset}")
    except ValueError:
        print("Invalid value entered. X-Offset must be a float.")
        x_offset = 0.0  

def on_y_offset_change(event):
    global y_offset
    try:
        y_offset = float(event.widget.get())
        y_offset /= 1000
        print(f"Y-Offset value changed to: {y_offset}")
    except ValueError:
        print("Invalid value entered. Y-Offset must be a float.")
        y_offset = 0.0  

def on_z_offset_change(event):
    global z_offset
    try:
        z_offset = float(event.widget.get())
        z_offset /= 1000
        print(f"Z-Offset value changed to: {z_offset}")
    except ValueError:
        print("Invalid value entered. Z-Offset must be a float.")
        z_offset = 0.0  

total_duration = sum_timestamps_in_directory()
print(total_duration)

# GUI

# Create root window
root = tk.Tk()
root.title("Robot Motion Planner")

# Set the window size and make it fixed
root.geometry("200x420")
root.resizable(False, False)

# Make the window always on top
root.wm_attributes("-topmost", 1)

# Set up the OSC server
dispatcher = Dispatcher()
# dispatcher.map("/position", print_osc)
dispatcher.map("/position", move_cartesian)


async def async_mainloop(root):
    """Asynchronous Tkinter event loop"""
    while True:
        root.update()
        await asyncio.sleep(0.001)


async def init_main(robot):
    global headers_label, status_label

    """Initialize the asynchronous OSC server and Tkinter GUI"""
    server = AsyncIOOSCUDPServer((OSC_HOST, OSC_PORT), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

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
    idle_button = ttk.Button(root, text="Idle", command=lambda: switch_mode(robot,"idle"))
    idle_button.pack(side=tk.TOP, pady=5, padx=2)

    playback_button = ttk.Button(root, text="Playback", command=lambda: switch_mode(robot,"playback"))
    playback_button.pack(side=tk.TOP, pady=5, padx=2)

    touchdesigner_button = ttk.Button(root, text="OSC", command=lambda: switch_mode(robot,"osc"))
    touchdesigner_button.pack(side=tk.TOP, pady=5, padx=2)

    move_home_button = ttk.Button(root, text="Home", command=lambda: switch_mode(robot,"home"))
    move_home_button.pack(side=tk.TOP, pady=5, padx=2)

    stop_button = ttk.Button(root, text="Stop", command=lambda: switch_mode(robot,"stop"))
    stop_button.pack(side=tk.TOP, pady=5, padx=2)

    # Create input fields frame
    input_frame = ttk.Frame(root)
    input_frame.pack()

    x_off = tk.DoubleVar()
    y_off = tk.DoubleVar()
    z_off = tk.DoubleVar()

    # Create input fields
    x_label = ttk.Label(input_frame, text="X-Offset:", background=root.cget("background"), foreground="white")
    x_label.pack(side=tk.TOP, padx=(10, 5))
    x_entry = ttk.Entry(input_frame, textvariable=x_off, width=3)
    x_entry.pack(padx=5)
    x_entry.bind("<FocusOut>", on_x_offset_change)


    y_label = ttk.Label(input_frame, text="Y-Offset:", background=root.cget("background"), foreground="white")
    y_label.pack(side=tk.TOP, padx=5)
    y_entry = ttk.Entry(input_frame, textvariable=y_off, width=3)
    y_entry.pack(side=tk.TOP, padx=5)
    y_entry.bind("<FocusOut>", on_y_offset_change)


    z_label = ttk.Label(input_frame, text="Z-Offset:", background=root.cget("background"), foreground="white")
    z_label.pack(side=tk.TOP, padx=5)
    z_entry = ttk.Entry(input_frame, textvariable=z_off, width=3)
    z_entry.pack(side=tk.TOP, padx=(5, 10))
    z_entry.bind("<FocusOut>", on_z_offset_change)


    # Set the button style
    style = ttk.Style()
    style.configure("TButton", relief="flat", padding=0, borderwith=0)
    style.map("TButton", background=[("active", "#e86464"), ("pressed", "#e86464")], foreground=[("active", "grey"), ("pressed", "white")])

    switch_mode(robot, "idle")

    await async_mainloop(root)  # Enter main loop of program

    transport.close()  # Clean up serve endpoint

# Run the asynchronous OSC server and Tkinter GUI
asyncio.run(init_main(robot))














