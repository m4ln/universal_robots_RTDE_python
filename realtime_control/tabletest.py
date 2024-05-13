import tkinter as tk
from tkinter import ttk, filedialog
import json

HEIGHT = 500
WIDTH = 600

json_data = {}

def load_json(filename):
    with open(filename) as file:
        data = json.load(file)
    return data

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def update_entry(row, column, value):
    global headers, json_data

    pass

    if column in [1, 2, 3, 4, 5]:  # Check if the column is for "a", "v", "t", or "comment"
        json_data[row][headers[column]] = value
    else:
        # Handle other columns here, if needed
        pass

def save_changes():
    global json_data

    save_json(json_filename, json_data)
    print("Changes saved.")

def populate_table():
    global json_data, headers

    for i, item in enumerate(json_data):
        for j in range(len(headers)):
            entry = ttk.Entry(table_frame, width=15)
            entry.insert(0, str(item.get(headers[j], "")))
            entry.grid(row=i, column=j, padx=5, pady=5)
            entry.bind('<FocusOut>', lambda event, row=i, column=j: update_entry(row=row, column=column, value=entry.get()))

            # Use default argument in lambda function
            entry.bind('<FocusOut>', lambda event, row=i, column=j, entry=entry: update_entry(row, column, entry.get()))

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
    for child in table_frame.winfo_children():
        child.destroy()

def configure_canvas():
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.configure(scrollregion=canvas.bbox("all"))
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
    new_entry = {
        "pose": [0.1999289976126454, -0.20447875064210733, 0.14435776646531312, -0.6242898216143485, -2.960625905426241, 0.05204646139338261],
        "t": 0.2,
        "r": 0.0005,
        "comments" : ".."
    }
    json_data.append(new_entry)
    clear_table()
    populate_table()
    configure_canvas()

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
canvas = tk.Canvas(table_frame, height=HEIGHT, width=WIDTH)
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



# Create New File button
open_button = ttk.Button(root, text="New File", command=create_new_file)
open_button.pack(side=tk.LEFT,pady=5, padx=2)

# Create Open File button
open_button = ttk.Button(root, text="Open File", command=open_file_dialog)
open_button.pack(side=tk.LEFT,pady=5, padx=2)

# Create Save button
save_button = ttk.Button(root, text="Save Changes", command=save_changes)
save_button.pack(side=tk.LEFT,pady=5, padx=2)

# Add waypoint button
save_button = ttk.Button(root, text="Add waypoint", command=add_entry)
save_button.pack(side=tk.LEFT,pady=5, padx=2)

# replay button
save_button = ttk.Button(root, text="replay", command=save_changes)
save_button.pack(side=tk.LEFT,pady=5, padx=2)

# Start the main loop
root.mainloop()