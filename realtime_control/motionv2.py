import os
import sys
sys.path.append("..")
import URBasic
import time
import math3d as m3d
from pythonosc import dispatcher
from pythonosc import osc_server
from typing import List, Any
import json
import tkinter as tk
from tkinter import ttk, filedialog

from config_ur import ROBOT_HOST, ACCELERATION, VELOCITY, ROBOT_START_POS
from config_osc import OSC_HOST, OSC_PORT

from pynput.keyboard import Key, Listener

moves = []
pose_counter = 1

HEIGHT = 900
WIDTH = 600
json_data = {}
current_row = 0

#robotModel = URBasic.robotModel.RobotModel()
#robot = URBasic.urScriptExt.UrScriptExt(host=ROBOT_HOST, robotModel=robotModel)

def save_waypoints(moves, filename):
    with open(filename, 'w') as file:
        json.dump(moves, file)

def load_waypoints(filename):
    with open(filename, 'r') as file:
        moves = json.load(file)
    return moves

def init_robot():
    global robot
    # initialise robot with URBasic
    print("initialising robot")

    robot.reset_error()
    print("robot initialised")
    time.sleep(1)

    robot.init_realtime_control()  # starts the realtime control loop on the Universal-Robot Controller
    time.sleep(1)  # just a short wait to make sure everything is initialised

def set_freedrive():
    global robot

    init_robot()
    robot.freedrive_mode()

def replay():
    global moves, robot, json_data

    init_robot()

    robot.movel_waypoints(json_data)

def get_current_position():
    global robot
    
    position = robot.get_actual_tcp_pose()
    return position

def load_json(filename):
    global moves
    with open(filename) as file:
        data = json.load(file)
    
    moves = data
    return data

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def update_entry(row, column, value):
    global headers, json_data

    if column in [1, 2, 3, 4, 5]:
        json_data[row][headers[column - 1]] = value
    else:
        # Handle other columns here, if needed
        pass

def save_changes():
    global json_data

    save_json(json_filename, json_data)
    print("Changes saved.")

def populate_table():
    global json_data, headers

    # Clear existing table data
    table.delete(*table.get_children())

    # Populate table with data
    for i, item in enumerate(json_data):
        values = [str(item.get(header, "")) for header in headers]
        table.insert("", "end", values=values)

def open_file_dialog():
    global json_data

    filename = filedialog.askopenfilename(filetypes=[('JSON Files', '*.json')])
    if filename:
        global json_filename
        json_filename = filename
        json_data = load_json(json_filename)
        clear_table()
        populate_table()
        configure_canvas()

def clear_table():
    #for child in table_frame.winfo_children():
     #   child.destroy()x

     return

def configure_canvas():
    table_frame.update_idletasks()
    canvas.config(scrollregion=(0,0,800,800))#)canvas.bbox("all")),
    canvas.configure(scrollregion=(0,0,800,800))#canvas.bbox("all"))
    canvas.configure(yscrollcommand=scrollbar.set)

def on_canvas_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def create_new_file():
    global json_data, json_filename
    json_data = []
    json_filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[('JSON Files', '*.json')])
    if json_filename:
        save_json(json_filename, json_data)
        clear_table()
        configure_canvas()

def add_entry():
    pos = get_current_position()
    new_entry = {
        "pose": pos.tolist(),
        "t": 2.0,
        "r": 0.0015,
        "comments": ""
    }

    json_data.append(new_entry)
    populate_table()

def move_to_pose():
    global current_row
    init_robot()

    print(json_data)
    robot.movel(pose=json_data[current_row]["pose"],t=3)

def move_up():
    #still to implement
    pass

def move_down():
    #still to implement
    pass

def rewind():
    global moves, robot, json_data

    init_robot()

    reversed_movements = json_data[:current_row+1][::-1]
    robot.movel_waypoints(reversed_movements)

# Create root window
root = tk.Tk()
root.title("Robot Motion Planner")

# Create headers frame
headers_frame = ttk.Frame(root)
headers_frame.pack()

# Define table headers
headers = ["pose", "t", "r", "comments"]

# Create labels for headers
for j, header in enumerate(headers):
    label = ttk.Label(headers_frame, text=header, width=15, anchor="center")
    label.grid(row=0, column=j, padx=5, pady=5)

# Create table frame
table_frame = ttk.Frame(root)
table_frame.pack(pady=10)

# Create scrollable canvas
canvas = tk.Canvas(table_frame, height=HEIGHT, width=WIDTH, scrollregion=(0,0,500,500))
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure canvas
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create table
table = ttk.Frame(canvas)
canvas.create_window((0, 0), window=table, anchor='nw')

# Attach canvas to scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=canvas.yview)

# Create table
table = ttk.Treeview(canvas, columns=headers, show="headings")
table.pack()

# Create New File button
new_button = ttk.Button(root, text="New File", command=create_new_file)
new_button.pack(side=tk.LEFT,pady=5, padx=2)

# Create Freedrive button
freedrive_button = ttk.Button(root, text="Freedrive", command=set_freedrive)
freedrive_button.pack(side=tk.LEFT,pady=5, padx=2)

# Create Open File button
open_button = ttk.Button(root, text="Open File", command=open_file_dialog)
open_button.pack(side=tk.LEFT,pady=5, padx=2)

# Create Save button
save_button = ttk.Button(root, text="Save Changes", command=save_changes)
save_button.pack(side=tk.LEFT,pady=5, padx=2)

# Add waypoint button
add_button = ttk.Button(root, text="Add waypoint", command=add_entry)
add_button.pack(side=tk.LEFT,pady=5, padx=2)

# replay button
replay_button = ttk.Button(root, text="replay", command=replay)
replay_button.pack(side=tk.LEFT,pady=5, padx=2)

# move to selected pose
move_to_button = ttk.Button(root, text="move to selected pose", command=move_to_pose)
move_to_button.pack(side=tk.LEFT,pady=5, padx=2)

# rewind
rewind_button = ttk.Button(root, text="rewind from selected", command=rewind)
rewind_button.pack(side=tk.LEFT,pady=5, padx=2)

def delete_entry():
    global table

    #selected_rows = dt.get_rows(selected=True)
    selected_entry = current_row #table.get_rows(selected=True)
    if selected_entry:
        #index = int(selected_entry.lstrip("I00"))  # Extract the row index from the entry ID
        del json_data[current_row]
        clear_table()
        populate_table()
        configure_canvas()

# delete button
delete = ttk.Button(root, text="delete", command=delete_entry)
delete.pack(side=tk.LEFT,pady=5, padx=2)

# Start the main loop
root.mainloop()