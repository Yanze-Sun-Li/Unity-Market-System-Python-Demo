# item_details.py
import tkinter as tk
from tkinter import messagebox
from utils import get_data_by_id

def open_item_details_window(root, items_list, data_list):
    item_details_window = tk.Toplevel(root)
    item_details_window.title("Item Details")

    # Define item_id_entry and item_details_text within the function
    item_id_label = tk.Label(item_details_window, text="Enter Item ID:")
    item_id_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    item_id_entry = tk.Entry(item_details_window)
    item_id_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    show_item_details_button = tk.Button(item_details_window, text="Show Item Details", command=lambda: show_item_details(item_id_entry, item_details_text, items_list, data_list))
    show_item_details_button.grid(row=1, column=1, padx=10, pady=5, sticky="e")

    item_details_text = tk.Text(item_details_window, height=15, width=50)
    item_details_text.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    # Allow widgets to resize with the window
    item_details_window.grid_columnconfigure(0, weight=1)
    item_details_window.grid_rowconfigure(2, weight=1)

def show_item_details(item_id_entry, item_details_text, items_list, data_list):
    selected_item_id = item_id_entry.get()
    item = next((item for item in items_list if item["item_id"] == selected_item_id), None)
    if item:
        data_info = get_data_by_id(data_list, item["data_id"])
        item_info = (
            f"Item ID: {item['item_id']}\n"
            f"Name: {item['name']}\n"
            f"Average Price: {item['price']}\n"
            f"Average Amount: {item['amount']}\n"
            f"Common available for: {item['not_available_timer']} seconds\n"
            f"Data ID: {item['data_id']}\n"
        )
        if data_info:
            data_info_str = (
                f"\n--- Linked Data Information ---\n"
                f"Data ID: {data_info['id']}\n"
                f"Name: {data_info['name']}\n"
                f"Description: {data_info['description']}\n"
                f"Recommanded Price: {data_info['default_price']}\n"
                f"Item Type: {data_info['type']}\n"
                f"Stack Number: {data_info['stack_number']}\n"
            )
            item_info += data_info_str
        item_details_text.delete(1.0, tk.END)
        item_details_text.insert(tk.END, item_info)
    else:
        messagebox.showwarning("Warning", "Item ID not found.")
        
        
