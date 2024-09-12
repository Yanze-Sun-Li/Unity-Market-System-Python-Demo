import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json
import os
import shutil

# Default file path for demand JSON
default_file_path = "demands.json"

# Define field names for demand properties (available_time_at removed)
fields = {
    "demand_id": "Demand ID",
    "item_id": "Item ID",
    "buy_price": "Buy Price",
    "max_amount": "Max Amount",
    "not_available_timer": "Not Available Timer"
}

# Load existing JSON file
def load_json_file():
    global demand_list, file_path
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:  # Use default file if no file is selected
        file_path = default_file_path
    
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                demand_list = json.load(file)
                messagebox.showinfo("Success", "File loaded successfully!")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to load JSON file.")
                demand_list = []
    else:
        demand_list = []
        messagebox.showinfo("Info", "File not found. A new file will be created.")

# Check if demand_id is duplicated
def check_duplicate_demand_id(new_id):
    for demand in demand_list:
        if demand["demand_id"] == new_id:
            return True
    return False

# Add new demand to the existing file
def add_demand_to_json():
    new_demand = {
        "demand_id": demand_id_entry.get(),
        "item_id": item_id_entry.get(),
        "buy_price": int(buy_price_entry.get()),
        "max_amount": int(max_amount_entry.get()),
        "not_available_timer": float(not_available_timer_entry.get())
    }
    
    if check_duplicate_demand_id(new_demand["demand_id"]):
        messagebox.showerror("Error", "Demand ID already exists! Please use a unique Demand ID.")
    else:
        demand_list.append(new_demand)
        sort_demands_by_id()  # Sort demand_list by demand_id before saving
        save_json_file()
        messagebox.showinfo("Success", "Demand added successfully!")

# Sort demand_list by demand_id as integer
def sort_demands_by_id():
    global demand_list
    demand_list.sort(key=lambda x: int(x["demand_id"]))

# Save the updated demand_list to the JSON file
def save_json_file():
    with open(file_path, "w") as file:
        json.dump(demand_list, file, indent=4)

# Copy the demand JSON file
def copy_json_file():
    original_file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    
    if not original_file_path:
        messagebox.showerror("Error", "No file selected!")
        return

    new_file_name = simpledialog.askstring("Input", "Enter the new file name (without extension):")
    
    if not new_file_name:
        messagebox.showerror("Error", "No name provided for the new file!")
        return
    
    directory = os.path.dirname(original_file_path)
    new_file_path = os.path.join(directory, new_file_name + ".json")
    
    try:
        shutil.copyfile(original_file_path, new_file_path)
        messagebox.showinfo("Success", f"File copied successfully as {new_file_name}.json!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy the file: {e}")

# Create main window for the generator
root = tk.Tk()
root.title("Demand Data Generator")

# Create and layout labels and entry fields
entries = {}
for i, (key, value) in enumerate(fields.items()):
    label = tk.Label(root, text=value)
    label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[key] = entry

# Map entries to specific variables
demand_id_entry = entries["demand_id"]
item_id_entry = entries["item_id"]
buy_price_entry = entries["buy_price"]
max_amount_entry = entries["max_amount"]
not_available_timer_entry = entries["not_available_timer"]

# Create buttons for actions
load_button = tk.Button(root, text="Load JSON File", command=load_json_file)
load_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

add_button = tk.Button(root, text="Add Demand", command=add_demand_to_json)
add_button.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

copy_button = tk.Button(root, text="Copy JSON File", command=copy_json_file)
copy_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=10)

# Initialize demand list and file path
demand_list = []
file_path = default_file_path

# Run the main loop
root.mainloop()
