import json
import os
import sys
from tkinter import filedialog, messagebox

def get_data_by_id(data_list, data_id):
    for data in data_list:
        if data["id"] == data_id:
            return data
    return None

        
def get_data_folder():
    """Determine the correct path to the 'Data' folder, whether running from source or packaged."""
    # When PyInstaller bundles the app, it unpacks resources into a temporary _MEIPASS folder
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, "Data")

def load_data(data_list, file_name=None):
    """Load JSON data into the provided list, either from a user-selected file or from the Data folder."""
    file_path = None
    
    if file_name:
        # Look for the file in the 'Data' folder
        file_path = os.path.join(get_data_folder(), file_name)
    
    if not file_path or not os.path.exists(file_path):
        # If the file doesn't exist or was not provided, prompt the user to select a file
        file_path = filedialog.askopenfilename(
            title="Open Data File", 
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
        )

    if file_path:
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                data_list.clear()
                data_list.extend(data)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Failed to decode JSON file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")