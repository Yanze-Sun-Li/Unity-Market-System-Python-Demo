import tkinter as tk
from tkinter import ttk, messagebox
import random

class FixedPriceMarketManager:
    def __init__(self, root, global_data_manager):
        self.root = root
        self.global_data_manager = global_data_manager
        self.selling_window = None
        self.selling_window_open = False
        self.demands_tree = None
        self.backpack_manager = None
        self.refresh_task = None  # Track the refresh task ID
        self.refresh_price_time = 10000
        self.search_var = tk.StringVar()


    def set_backpack_manager(self, backpack_manager):
        self.backpack_manager = backpack_manager

    def create_fixed_price_table(self, parent):
        """Create a table for displaying items with buy/sell prices, with sorting and search functionality."""
        self.table_frame = tk.Frame(parent)
        self.table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        scrollbar = tk.Scrollbar(self.table_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")

        columns = ("Item ID", "Name", "Sell Price", "Purchase Price")
        self.demands_tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)

        # Set table headers and column properties, and bind each header for sorting
        for col in columns:
            self.demands_tree.heading(col, text=col, anchor=tk.CENTER,
                                      command=lambda _col=col: self.sort_by_column(_col, False))
            self.demands_tree.column(col, anchor=tk.CENTER, width=150)

        self.demands_tree.grid(row=0, column=0, sticky="nsew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        scrollbar.config(command=self.demands_tree.yview)

        return self.demands_tree

    def create_search_box(self, parent):
        """Create a search box for filtering items in the table."""
        search_frame = tk.Frame(parent)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(search_frame, text="Search Item:").grid(row=0, column=0, padx=5, pady=5)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Bind the search box to trigger refresh when user types
        search_entry.bind("<KeyRelease>", lambda event: self.refresh_table())
        search_frame.grid_columnconfigure(1, weight=1)
    
    def sort_by_column(self, col, reverse):
        """Sort the table by the selected column."""
        data = [(self.demands_tree.set(k, col), k) for k in self.demands_tree.get_children('')]

        # Perform the sort, converting numeric columns to integers
        if col in ("Sell Price", "Purchase Price"):
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        else:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(data):
            self.demands_tree.move(k, '', index)

        self.demands_tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

        
        

    def open_fixed_price_market(self):
        """Open a new window displaying items with buy/sell prices."""
        if self.selling_window_open:
            return

        self.selling_window = tk.Toplevel(self.root)
        self.selling_window.title("Fixed Price Market (Buy/Sell Prices)")
        self.selling_window_open = True
        self.selling_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create the search box
        self.create_search_box(self.selling_window)

        # Create the table with buy/sell prices
        self.demands_tree = self.create_fixed_price_table(self.selling_window)

        # Start auto-refresh
        self.auto_refresh_table()

        # Create buttons for buying, selling, and exiting
        button_frame = tk.Frame(self.selling_window)
        button_frame.grid(row=3, column=0, pady=10, sticky="ew", columnspan=2)

        buy_button = tk.Button(button_frame, text="Purchase Selected Item", command=self.buy_selected_item)
        buy_button.grid(row=0, column=0, padx=10)

        sell_button = tk.Button(button_frame, text="Sell Selected Item", command=self.sell_selected_item)
        sell_button.grid(row=0, column=1, padx=10)

        close_button = tk.Button(button_frame, text="Close Market", command=self.on_close)
        close_button.grid(row=0, column=2, padx=10)

        self.selling_window.grid_rowconfigure(1, weight=1)
        self.selling_window.grid_columnconfigure(0, weight=1)


    def refresh_table(self):
        """Populate the table with items from items_list and calculate the buy/sell prices, while preserving the selection and applying search filters."""
        if not self.demands_tree:
            return

        search_term = self.search_var.get().lower().strip()  # Get search term

        selected_item = self.demands_tree.focus()
        selected_item_id = None
        if selected_item:
            selected_item_id = self.demands_tree.item(selected_item, 'values')[0]

        self.demands_tree.delete(*self.demands_tree.get_children())

        for item in self.global_data_manager.items_list:
            item_name = item['name'].lower()

            # Apply search filter
            if search_term and search_term not in item_name:
                continue

            lowest_market_price = self.get_lowest_market_price(item['data_id'])
            buy_price_from_user = int(lowest_market_price) if lowest_market_price > 0 else int(item['price'])
            highest_market_price = self.get_highest_market_price(item['data_id'])
            sell_price_to_user = int(max(item['price'], highest_market_price * 0.9))

            sell_price_to_user = self.apply_randomness(sell_price_to_user)
            if sell_price_to_user < buy_price_from_user:
                sell_price_to_user = buy_price_from_user + 1

            item_iid = self.demands_tree.insert("", tk.END, values=(
                item['item_id'],
                item['name'],
                buy_price_from_user,
                sell_price_to_user
            ))

            if selected_item_id and str(item['item_id']) == str(selected_item_id):
                self.demands_tree.selection_set(item_iid)
                self.demands_tree.focus(item_iid)

    def apply_randomness(self, price):
        randomness_factor = random.uniform(1, 1.15)
        return int(price * randomness_factor)

    def get_lowest_market_price(self, data_id):
        matching_items = [item for item in self.global_data_manager.in_market_items if item['data_id'] == data_id]
        if matching_items:
            return min(item['price'] for item in matching_items)
        return 0

    def get_highest_market_price(self, data_id):
        matching_items = [item for item in self.global_data_manager.in_market_items if item['data_id'] == data_id]
        if matching_items:
            return max(item['price'] for item in matching_items)
        return 0
    
    def auto_refresh_table(self):
        self.refresh_table()
        if self.selling_window_open:
            self.refresh_task = self.root.after(self.refresh_price_time, self.auto_refresh_table)

    def stop_auto_refresh(self):
        if self.refresh_task:
            self.root.after_cancel(self.refresh_task)
            self.refresh_task = None

    def buy_selected_item(self):
        selected_item = self.demands_tree.focus()
        if selected_item:
            item_values = self.demands_tree.item(selected_item, 'values')
            item_name = item_values[1]
            price_per_item = int(item_values[3])

            self.show_amount_popup(item_name, price_per_item, "buy")

    def sell_selected_item(self):
        selected_item = self.demands_tree.focus()
        if selected_item:
            item_values = self.demands_tree.item(selected_item, 'values')
            item_name = item_values[1]
            price_per_item = int(item_values[2])

            self.show_amount_popup(item_name, price_per_item, "sell")

    def sell_selected_item(self):
        """Handle selling the selected item to the market."""
        selected_item = self.demands_tree.focus()
        if selected_item:
            item_values = self.demands_tree.item(selected_item, 'values')
            item_name = item_values[1]
            price_per_item = int(item_values[2])  # Market's buying price (Buy Price from User)

            # Display a popup window to select the quantity
            self.show_amount_popup(item_name, price_per_item, "sell")

    def show_amount_popup(self, item_name, price_per_item, action):
        """Display a popup window to select the quantity to buy/sell."""
        
        # Calculate total available currency (convert to copper for simplicity)
        total_copper = (self.global_data_manager.gold * 10000) + (self.global_data_manager.silver * 100) + self.global_data_manager.copper
        
        # Calculate the maximum amount the player can afford based on the price per item
        max_affordable_amount = total_copper // price_per_item
        
        # If the action is to "buy", we need to cap the maximum amount by both what the player can afford and item availability
        if action == "buy":
            # Find the target item to check available amount
            target_item = next(item for item in self.global_data_manager.items_list if item['name'] == item_name)
            available_amount = target_item['amount']

            # Set the slider's maximum to the lesser of what the player can afford and what's available
            max_amount = min(max_affordable_amount, available_amount)
        
        elif action == "sell":
            # For selling, set max_amount to the player's inventory amount of the selected item
            user_item = next((item for item in self.global_data_manager.user_items if item['name'] == item_name), None)
            if user_item:
                max_amount = user_item['amount']
            else:
                max_amount = 0

        def update_amount_from_slider(event=None):
            """Update the entry when the user moves the slider."""
            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, str(amount_slider.get()))
            update_total_price_label(amount_slider.get())

        def update_amount_from_entry(event=None):
            """Update the slider when the user types in the entry."""
            try:
                amount = int(amount_entry.get())
                if 1 <= amount <= max_amount:  # Ensure the value stays within the valid range
                    amount_slider.set(amount)  # Update the slider to match the entry
                    update_total_price_label(amount)
                else:
                    amount_entry.delete(0, tk.END)  # Clear invalid input
            except ValueError:
                pass  # Ignore invalid input

        def update_total_price_label(amount):
            """Update the total price display."""
            total_price = amount * price_per_item
            total_price_label.config(text=f"Total Price: {total_price} copper")

        def confirm_action():
            """Confirm the purchase or sale and process it."""
            try:
                amount = int(amount_entry.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Please enter a valid amount.")
                    return
                
                total_price = amount * price_per_item

                if action == "buy":
                    # Check if the user has enough money
                    if self.backpack_manager.deduct_currency(total_price):
                        # Add the item to the user's inventory
                        target_item = next(target_item for target_item in self.global_data_manager.items_list if target_item['name'] == item_name)
                        self.backpack_manager.add_to_inventory(target_item, amount)
                        self.backpack_manager.auto_convert_money()
                        messagebox.showinfo("Purchase Successful", f"You bought {amount}x {item_name} for {total_price} copper!")
                    else:
                        messagebox.showerror("Insufficient Funds", "You don't have enough money to buy this item.")
                elif action == "sell":
                    # Check if the user has the item in their inventory
                    user_item = next((item for item in self.global_data_manager.user_items if item['name'] == item_name), None)
                    if user_item and user_item['amount'] >= amount:
                        # Sell the item and give the user currency
                        self.backpack_manager.receive_currency(total_price)
                        user_item['amount'] -= amount
                        if user_item['amount'] <= 0:
                            self.global_data_manager.user_items.remove(user_item)
                        messagebox.showinfo("Sell Successful", f"You sold {amount}x {item_name} for {total_price} copper!")
                    else:
                        messagebox.showerror("Error", f"You don't have enough {item_name} to sell.")
                popup_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.")

        # Create the popup window
        popup_window = tk.Toplevel(self.root)
        popup_window.title(f"Confirm {action.capitalize()}")

        # Display item name and price per item
        item_label = tk.Label(popup_window, text=f"Item: {item_name}\nPrice per unit: {price_per_item} copper")
        item_label.pack(pady=10)

        # Slider for selecting the amount
        amount_slider = tk.Scale(popup_window, from_=1, to=max_amount, orient=tk.HORIZONTAL, label="Select Amount")  # Max value is set based on player's affordability and availability
        amount_slider.pack(pady=5)
        amount_slider.bind("<Motion>", update_amount_from_slider)  # Update entry when slider moves

        # Entry for manual amount input
        amount_label = tk.Label(popup_window, text="Or enter amount:")
        amount_label.pack(pady=5)
        amount_entry = tk.Entry(popup_window)
        amount_entry.pack(pady=5)
        amount_entry.bind("<KeyRelease>", update_amount_from_entry)  # Update slider when entry changes

        # Total price display
        total_price_label = tk.Label(popup_window, text="Total Price: 0 copper")
        total_price_label.pack(pady=5)

        # Confirm and Cancel buttons
        confirm_button = tk.Button(popup_window, text="Confirm", command=confirm_action)
        confirm_button.pack(pady=5)
        cancel_button = tk.Button(popup_window, text="Cancel", command=popup_window.destroy)
        cancel_button.pack(pady=5)

        # Set initial values
        amount_slider.set(1)
        amount_entry.insert(0, "1")
        update_total_price_label(1)

    def on_close(self):
        self.selling_window_open = False
        self.stop_auto_refresh()
        self.selling_window.destroy()
