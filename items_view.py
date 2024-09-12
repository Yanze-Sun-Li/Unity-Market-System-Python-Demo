import tkinter as tk
from tkinter import ttk

def open_items_window(root, items_list):
    items_window = tk.Toplevel(root)
    items_window.title("Items")

    # Define the columns: ID, Name, Default Price
    columns = ("Item ID", "Name", "Default Price")
    items_tree = ttk.Treeview(items_window, columns=columns, show="headings")
    
    # Set up the column headers
    items_tree.heading("Item ID", text="Item ID")
    items_tree.heading("Name", text="Name")
    items_tree.heading("Default Price", text="Average Price")

    # Insert the items_list data into the Treeview
    for item in items_list:
        items_tree.insert(
            "", tk.END,
            values=(item["item_id"], item["name"], item["price"])  # Insert ID, Name, and Price
        )

    # Allow the Treeview to resize with the window
    items_tree.pack(fill=tk.BOTH, expand=True)

    # Add a scrollbar to the items_window
    scrollbar = tk.Scrollbar(items_window, orient="vertical", command=items_tree.yview)
    items_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Make the window resizable
    items_window.grid_columnconfigure(0, weight=1)
    items_window.grid_rowconfigure(0, weight=1)

