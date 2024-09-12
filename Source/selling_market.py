import tkinter as tk
from tkinter import ttk, messagebox
import tkinter

class SellingMarketManager:
    def __init__(self, root, global_data_manager):
        self.root = root
        self.global_data_manager = global_data_manager
        self.demands_control_manager = None
        self.selling_window = None
        self.selling_window_open = False
        self.demands_tree = None
        self.refresh_task = None
        self.backpack_manager = None
        self.table_frame = None
        self.demands_frame = None
        self.search_var = None
        self.if_set_up = False
        self.current_sort_column = None
        self.sort_direction = True


        
    def set_backpack_manager(self,backpack_manager):
        self.backpack_manager = backpack_manager
        
        
    def set_demands_control(self, demands_control_manager):
        self.demands_control_manager = demands_control_manager    

        if self.demands_frame:
            # Search box for filtering demands by name
            tk.Label(self.demands_frame, text="Search Demand:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.demands_control_manager.search_var = tk.StringVar()
            self.demands_control_manager.search_entry = tk.Entry(self.demands_frame, textvariable=self.demands_control_manager.search_var)
            self.demands_control_manager.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  # Use grid for entry box
            # Make ure the entry box expands horizontally
            self.demands_frame.grid_columnconfigure(1, weight=1)
            # Bind the search box to update the demands table based on search input
            self.demands_control_manager.search_entry.bind("<KeyRelease>", lambda event: self.demands_control_manager.filter_demands(self.demands_control_manager.search_var.get()))

    def create_selling_table(self, parent):
        """Create the selling demands table with a vertical scrollbar and sorting functionality."""
        self.table_frame = tk.Frame(parent)
        self.table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")  # Use grid instead of pack

        # Create the scrollbar
        scrollbar = tk.Scrollbar(self.table_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")  # Grid for scrollbar

        # Create the table
        columns = ("Demand ID", "Name", "Reward", "Max Amount", "Not Available Timer")
        self.demands_tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)

        # Set table headers and column properties, and bind headers for sorting
        for col in columns:
            self.demands_tree.heading(col, text=col, anchor=tk.CENTER, command=lambda c=col: self.sort_by_column(c, False))
            self.demands_tree.column(col, anchor=tk.CENTER, width=100)

        self.demands_tree.grid(row=0, column=0, sticky="nsew")  # Grid for treeview
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Configure scrollbar
        scrollbar.config(command=self.demands_tree.yview)

        # Track the current sort state (column and direction)
        self.current_sort_column = None
        self.sort_direction = False

        return self.demands_tree

    def sort_by_column(self, col, reverse):
        """Sort the demands table based on the selected column."""
        # Get all the items in the table
        items = [(self.demands_tree.set(k, col), k) for k in self.demands_tree.get_children('')]

        # Sort the items based on the selected column
        try:
            items.sort(key=lambda t: int(t[0]) if t[0].isdigit() else t[0], reverse=reverse)
        except ValueError:
            # Fallback for sorting non-numeric values
            items.sort(key=lambda t: t[0], reverse=reverse)

        # Reorder the items in the table based on the sorted list
        for index, (_, k) in enumerate(items):
            self.demands_tree.move(k, '', index)

        # Toggle the sort direction for the next click
        self.sort_direction = not reverse

        # Store the current sort column
        self.current_sort_column = col

    def sort_by_column(self, col, reverse):
        """Sort the demands based on the selected column."""
        # Get the current items from the table
        items = [(self.demands_tree.set(k, col), k) for k in self.demands_tree.get_children('')]

        # Sort items based on the column value
        items.sort(reverse=reverse, key=lambda x: float(x[0]) if x[0].replace('.', '', 1).isdigit() else x[0].lower())

        # Rearrange the table items based on the sorted order
        for index, (val, k) in enumerate(items):
            self.demands_tree.move(k, '', index)

        # Update the sorting indicators
        self.demands_tree.heading(col, text=col, command=lambda: self.sort_by_column(col, not reverse))

        # Track the current sorted column and direction
        self.current_sort_column = col
        self.sort_direction = reverse


    def open_selling_market(self):
        """Open a new window displaying user demand, allowing users to sell items."""
        if self.selling_window_open:
            return

        # Create the selling market window
        self.selling_window = tk.Toplevel(self.root)
        self.selling_window.title("Selling Market")
        self.selling_window_open = True
        self.selling_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create the demands table and search box frame
        self.demands_tree = self.create_selling_table(self.selling_window)

        # Create a frame for the buttons to center them
        button_frame = tk.Frame(self.selling_window)
        button_frame.grid(row=2, column=0, pady=10, sticky="ew", columnspan=2)

        # Add buttons for selling items and finding new demands inside the button_frame
        tk.Button(button_frame, text="Sell Selected Item", command=lambda: self.sell_selected_item()).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Finding New Demands", command=lambda: self.demands_control_manager.clear_demands()).pack(side=tk.LEFT, padx=10)

        # Create a frame for the search box
        self.demands_frame = tk.Frame(self.selling_window)
        self.demands_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # Use grid for alignment

        # Set up demands control with the search box
        self.set_demands_control(self.demands_control_manager)

        # Ensure the buttons are centered by configuring the grid
        self.selling_window.grid_columnconfigure(0, weight=1)
        self.if_set_up = True


    def sell_selected_item(self):
        """Handle selling the currently selected item from the demands table."""
        selected_item = self.demands_tree.focus()
        if selected_item:
            item_values = self.demands_tree.item(selected_item, 'values')
            demand_id = item_values[0]
            asked_name = item_values[1]
            max_amount = int(item_values[3])

            user_item = self.global_data_manager.find_target_items_in_user_item(asked_name)
            if user_item:
                self.show_sell_confirmation_popup(user_item, item_values, max_amount)
            else:
                messagebox.showerror("Error", "You don't have this item in your inventory.")
        else:
            messagebox.showerror("Error", "Please select an item to sell.")

    def on_close(self):
        """Close the selling window and cancel any scheduled tasks."""
        if self.refresh_task:
            self.selling_window.after_cancel(self.refresh_task)
        self.selling_window_open = False
        self.demands_tree = None
        self.selling_window.destroy()
        
    def refresh_table(self):
        """Populate the table with all demands or filtered demands based on the search term and maintain sorting."""
        if self.demands_control_manager and self.demands_tree and self.if_set_up:
            # Get the search term from the search box
            search_term = self.demands_control_manager.search_var.get().lower().strip() if self.demands_control_manager.search_var else ""
            
            # Save the currently selected item's demand_id (if any)
            selected = self.demands_tree.focus()
            selected_demand_id = None
            if selected:
                selected_demand_id = self.demands_tree.item(selected, 'values')[0]  # Get the demand_id of the selected item

            # Clear the demands table
            self.demands_tree.delete(*self.demands_tree.get_children())

            # Decide whether to filter demands or show all
            if search_term:
                filtered_demands = self.demands_control_manager.get_filtered_demands(search_term)
            else:
                filtered_demands = self.demands_control_manager.global_data_manager.demands_list

            # Populate the table with filtered demands or all demands
            for demand in filtered_demands:
                item_name = self.demands_control_manager.find_item_name(demand["item_id"])
                item_name = item_name if item_name else "Unknown Item"  # Fallback to "Unknown Item" if item name is missing

                # Insert the demand into the table
                iid = self.demands_tree.insert("", tk.END, values=(
                    demand["demand_id"],
                    item_name,
                    demand["buy_price"],
                    demand["max_amount"],
                    int(demand["not_available_timer"])
                ))

                # Restore the selection if the previously selected item matches
                if selected_demand_id and str(demand["demand_id"]) == str(selected_demand_id):
                    self.demands_tree.selection_set(iid)
                    self.demands_tree.focus(iid)

            # Reapply the last used sorting after populating the table
            if self.current_sort_column:
                self.sort_by_column(self.current_sort_column, self.sort_direction)



    
    def show_sell_confirmation_popup(self, user_item, item_values, max_amount):
        """Display a popup window asking how much to sell and handle the confirmation."""
        
        def update_amount_from_entry(event=None):
            """Update the slider when the user types in the entry."""
            try:
                amount = int(amount_entry.get())
                if 0 <= amount <= min(user_item['amount'], max_amount):
                    amount_slider.set(amount)  # Update the slider to match the entry
                    update_total_price_label(amount)
                else:
                    amount_entry.delete(0, tk.END)  # Clear invalid input
            except ValueError:
                pass  # Ignore invalid input

        def update_amount_from_slider(event=None):
            """Update the entry when the user moves the slider."""
            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, str(int(amount_slider.get())))
            update_total_price_label(int(amount_slider.get()))

        def update_total_price_label(sell_amount):
            """Update the total price display in gold, silver, and copper."""
            total_copper_earned = sell_amount * int(item_values[2])
            total_gold = total_copper_earned // 10000
            remaining_copper = total_copper_earned % 10000
            total_silver = remaining_copper // 100
            total_copper = remaining_copper % 100

            total_price_label.config(
                text=f"Total Price: {total_gold} gold, {total_silver} silver, {total_copper} copper"
            )

        def confirm_sale():
            """Confirm the sale and process it."""
            try:
                sell_amount = int(amount_entry.get())
                if sell_amount > user_item['amount']:
                    messagebox.showerror("Error", "You don't have enough of this item to sell.")
                elif sell_amount > max_amount:
                    messagebox.showerror("Error", f"Demand only allows a maximum of {max_amount} units.")
                else:
                    total_copper_earned = sell_amount * int(item_values[2])
                    self.backpack_manager.receive_currency(total_copper_earned)
                    
                    try:
                        self.backpack_manager.refresh_backpack_inventory()
                    except tkinter.TclError as e:
                        # Handle the specific TclError when trying to access destroyed widgets
                        print("Backpack not open, skip refresh.")
                        
                    self.backpack_manager.auto_convert_money()

                    # Update the demand
                    demand = next((d for d in self.global_data_manager.demands_list if int(d['demand_id']) == int(item_values[0])), None)
                    if demand:
                        demand['max_amount'] -= sell_amount

                    # If the demand is fully met, remove it
                    if demand and demand['max_amount'] <= 0:
                        self.global_data_manager.demands_list.remove(demand)
                        self.global_data_manager.removed_demands_ids.append(demand['demand_id'])

                    # Remove the user item if the quantity is 0
                    user_item['amount'] -= sell_amount
                    if user_item['amount'] <= 0:
                        self.global_data_manager.user_items.remove(user_item)
                    self.backpack_manager.refresh_backpack_inventory()

                    # Inform the user about the sale
                    total_gold = total_copper_earned // 10000
                    remaining_copper = total_copper_earned % 10000
                    total_silver = remaining_copper // 100
                    total_copper = remaining_copper % 100

                    messagebox.showinfo(
                        "Sell Successful",
                        f"You sold {sell_amount}x {user_item['name']} for {total_gold} gold, {total_silver} silver, {total_copper} copper!"
                    )
                    
                    # Close the popup window after the sale is successful
                    popup_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.")

        # Create a popup window to ask for the amount to sell
        popup_window = tk.Toplevel(self.root)
        popup_window.title("Confirm Sale")

        # Display the item name and ask for the quantity to sell
        item_label = tk.Label(popup_window, text=f"Item: {user_item['name']}\nPrice: {item_values[2]} copper per unit")
        item_label.pack(pady=10)

        # Slider for selecting the amount to sell
        amount_slider = tk.Scale(popup_window, from_=1, to=min(user_item['amount'], max_amount), orient=tk.HORIZONTAL, label="Select Amount")
        amount_slider.pack(pady=5)

        # Entry to input the amount to sell
        amount_label = tk.Label(popup_window, text="Or enter amount:")
        amount_label.pack(pady=5)
        amount_entry = tk.Entry(popup_window)
        amount_entry.pack(pady=5)

        # Sync the slider and entry
        amount_slider.bind("<Motion>", update_amount_from_slider)  # Update entry when slider moves
        amount_entry.bind("<KeyRelease>", update_amount_from_entry)  # Update slider when entry changes

        # Total price display
        total_price_label = tk.Label(popup_window, text="Total Price: 0 copper")
        total_price_label.pack(pady=5)

        # Confirm and Cancel buttons
        confirm_button = tk.Button(popup_window, text="Confirm", command=confirm_sale)
        confirm_button.pack(pady=5)

        cancel_button = tk.Button(popup_window, text="Cancel", command=popup_window.destroy)
        cancel_button.pack(pady=5)

        # Set initial values for slider and entry
        amount_slider.set(1)
        amount_entry.insert(0, "1")
        update_total_price_label(1)
