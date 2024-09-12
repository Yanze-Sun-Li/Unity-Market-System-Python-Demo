import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json
import os
import shutil

# Default file path
default_file_path = "items.json"

# Define field names, including the new "weight" field
fields = {
    "item_id": "Item ID",
    "name": "Name",
    "price": "Price",
    "amount": "Amount",
    "not_available_timer": "Not Available Timer",  # Modify existing field
    "data_id": "Data ID",  # New field
    "weight": "Weight"  # Add new weight field
}

# Load an existing JSON file
def load_json_file():
    global item_list, file_path
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:  # If the user doesn't select a file, use the default path
        file_path = default_file_path
    
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                item_list = json.load(file)
                messagebox.showinfo("Success", "File loaded successfully!")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to load JSON file.")
                item_list = []
    else:
        item_list = []
        messagebox.showinfo("Info", "File not found. A new file will be created.")

# Check if item_id is duplicated
def check_duplicate_item_id(new_id):
    for item in item_list:
        if item["item_id"] == new_id:
            return True
    return False

# Add a new item to the existing file
def add_item_to_json():
    new_item = {
        "item_id": item_id_entry.get(),
        "name": name_entry.get(),
        "price": price_entry.get(),
        "amount": amount_entry.get(),
        "not_available_timer": not_available_timer_entry.get(),  # Use modified field
        "data_id": data_id_entry.get(),  # New field
        "weight": weight_entry.get()  # Include the weight field
    }
    
    if check_duplicate_item_id(new_item["item_id"]):
        messagebox.showerror("Error", "Item ID already exists! Please use a unique Item ID.")
    else:
        item_list.append(new_item)
        sort_items_by_id()  # Sort item_list by item_id before saving
        save_json_file()
        messagebox.showinfo("Success", "Item added successfully!")

# Sort item_list by item_id as an integer
def sort_items_by_id():
    global item_list
    item_list.sort(key=lambda x: int(x["item_id"]))

# Save data to the existing JSON file
def save_json_file():
    with open(file_path, "w") as file:
        json.dump(item_list, file, indent=4)

# Copy JSON file
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

# Create the main window
root = tk.Tk()
root.title("Item Data Generator")

# Create and layout labels and input fields
entries = {}
for i, (key, value) in enumerate(fields.items()):
    label = tk.Label(root, text=value)
    label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[key] = entry

# Assign entry variables
item_id_entry = entries["item_id"]
name_entry = entries["name"]
price_entry = entries["price"]
amount_entry = entries["amount"]
not_available_timer_entry = entries["not_available_timer"]  # Use modified field
data_id_entry = entries["data_id"]  # New field
weight_entry = entries["weight"]  # New weight field

# Create buttons
load_button = tk.Button(root, text="Load JSON File", command=load_json_file)
load_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

add_button = tk.Button(root, text="Add Item", command=add_item_to_json)
add_button.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

# Button to copy the JSON file
copy_button = tk.Button(root, text="Copy JSON File", command=copy_json_file)
copy_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=10)

# Initialize data list and file path
item_list = []
file_path = default_file_path

# Start the main loop
root.mainloop()
