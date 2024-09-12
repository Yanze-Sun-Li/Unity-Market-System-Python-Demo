import time
import tkinter as tk
from tkinter import ttk, messagebox
import random


class MarketManager:
    def __init__(self, root, global_data_manager, backpack_manager):
        self.root = root
        self.global_data_manager = global_data_manager  # Use GlobalDataManager for accessing shared data
        self.backpack_manager = backpack_manager  # Use BackpackManager for handling inventory and currency
        self.items_tree = None  # Placeholder for the TreeView widget
        self.search_var = tk.StringVar()  # Search variable for filtering items
        self.refresh_rate = 1
        self.MAX_ITEMS = 100
        self.PRICE_ADJUST_MIN = 0.85
        self.PRICE_ADJUST_MAX = 1.85
        self.TIME_ADJUST_MIN = 0
        self.TIME_ADJUST_MAX = 1
        self.TIMER_ADJUST_MIN = 0.5
        self.TIMER_ADJUST_MAX = 1.5
        self.AMOUNT_ADJUST_MIN = 0.15
        self.AMOUNT_ADJUST_MAX = 2.5
        self.GENERATE_DELAY_MIN = 0.5
        self.GENERATE_DELAY_MAX = 2.5

        self.last_sorted_column = None
        self.sort_reverse = False

    def create_market_table(self, parent):
        """Create the market table with a vertical scrollbar and a search box."""
        # Create a frame for the table
        table_frame = tk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Search bar frame for better alignment
        search_frame = tk.Frame(table_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create search label and entry box
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.refresh_table)  # Update table on key release

        # Create a frame for the table and scrollbar
        tree_frame = tk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create the vertical scrollbar
        scrollbar = tk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Define the remaining columns without 'Item ID'
        columns = ("Name", "Price", "Amount", "Not_Available_Timer")
        self.items_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)

        # Set up the column headers and center-align them
        # Add sorting functionality to each header
        self.items_tree.heading("Name", text="Name", anchor=tk.CENTER, command=lambda: self.sort_by_column("Name", False))
        self.items_tree.heading("Price", text="Price", anchor=tk.CENTER, command=lambda: self.sort_by_column("Price", False))
        self.items_tree.heading("Amount", text="Amount", anchor=tk.CENTER, command=lambda: self.sort_by_column("Amount", False))
        self.items_tree.heading("Not_Available_Timer", text="Available For", anchor=tk.CENTER, command=lambda: self.sort_by_column("Not_Available_Timer", False))

        # Configure the column width and center the text in each column
        self.items_tree.column("Name", anchor=tk.CENTER, width=150)
        self.items_tree.column("Price", anchor=tk.CENTER, width=100)
        self.items_tree.column("Amount", anchor=tk.CENTER, width=100)
        self.items_tree.column("Not_Available_Timer", anchor=tk.CENTER, width=150)

        # Pack the TreeView into the frame
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbar to control the TreeView's yview
        scrollbar.config(command=self.items_tree.yview)

    def sort_by_column(self, col, reverse):
        """Sort the market table by the selected column."""
        data = [(self.items_tree.set(k, col), k) for k in self.items_tree.get_children('')]

        # Convert numeric values to integers for sorting
        if col in ("Price", "Amount", "Not_Available_Timer"):
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        else:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        # Rearrange items in the sorted order
        for index, (val, k) in enumerate(data):
            self.items_tree.move(k, '', index)

        # Reverse the sort order for the next time this column is clicked
        self.items_tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

        # Update last sorted column and order
        self.last_sorted_column = col
        self.sort_reverse = reverse

    def purchase_item(self, item, amount):
        """Handle purchasing an item from the market."""
        total_price = item["price"] * amount
        user_items = self.global_data_manager.user_items
        in_market_items = self.global_data_manager.in_market_items

        if self.backpack_manager.deduct_currency(total_price):  # Deduct currency based on the total price
            # Add the item to the user's inventory
            item_copy = item.copy()  # Create a copy of the item for the inventory
            item_copy["amount"] = amount
            self.backpack_manager.add_to_inventory(item_copy,amount)
            self.backpack_manager.auto_convert_money()

            # Reduce the amount in the market
            item['amount'] -= amount
            if item['amount'] <= 0:
                self.global_data_manager.removed_item_ids.append(item['item_id'])
                in_market_items.remove(item)  # Remove item if it's sold out

            messagebox.showinfo("Purchase Successful", f"You bought {amount}x {item['name']} for {total_price} copper!")

            # Refresh both the money and inventory in the backpack
            self.backpack_manager.update_money_display()
            self.backpack_manager.refresh_backpack_inventory()  # Refresh the inventory table in the backpack
        else:
            messagebox.showerror("Insufficient Funds", "You don't have enough money to complete this purchase.")

    def purchase_confirmation_popup(self, item):
        """Popup window to confirm purchase and input desired amount."""
        
        # Convert the user's currency to copper
        total_copper = (self.global_data_manager.gold * 10000) + (self.global_data_manager.silver * 100) + self.global_data_manager.copper
        
        # Calculate the maximum amount the user can buy
        max_buyable_amount = total_copper // item['price']  # Max units user can afford
        max_amount = min(item['amount'], max_buyable_amount)  # Constrain by available item amount
    
        
        def update_amount_from_entry(event=None):
            """Update the slider when the user types in the entry."""
            try:
                amount = int(amount_entry.get())
                if 0 <= amount <= max_amount:
                    amount_slider.set(amount)  # Update the slider to match the entry
                    self.update_total_price(amount_entry, total_price_label, item)
                else:
                    amount_entry.delete(0, tk.END)  # Clear invalid input
            except ValueError:
                pass  # Ignore invalid input

        def update_amount_from_slider(event=None):
            """Update the entry when the user moves the slider."""
            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, str(int(amount_slider.get())))
            self.update_total_price(amount_entry, total_price_label, item)

        def confirm_purchase():
            """Confirm the purchase and close the window."""
            try:
                amount = int(amount_entry.get())
                if amount > max_amount:
                    messagebox.showerror("Error", "You cannot purchase more than is available or affordable.")
                elif amount <= 0:
                    messagebox.showerror("Error", "Please enter a valid amount.")
                else:
                    self.purchase_item(item, amount)
                    popup_window.destroy()  # Close the confirmation window
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.")

        # Create the popup window
        popup_window = tk.Toplevel()
        popup_window.title("Confirm Purchase")

        # Display the item name and price per unit
        item_label = tk.Label(popup_window, text=f"Item: {item['name']} (Price: {item['price']} copper per unit)")
        item_label.pack(pady=10)

        # Slider for selecting the amount
        amount_slider = tk.Scale(popup_window, from_=1, to=max_amount, orient=tk.HORIZONTAL, label="Select Amount")
        amount_slider.pack(pady=5)

        # Entry for manual input of the amount
        amount_label = tk.Label(popup_window, text="Or enter amount:")
        amount_label.pack()
        amount_entry = tk.Entry(popup_window)
        amount_entry.pack(pady=5)

        # Sync the slider and entry
        amount_slider.bind("<Motion>", update_amount_from_slider)  # Update entry when slider moves
        amount_entry.bind("<KeyRelease>", update_amount_from_entry)  # Update slider when entry changes

        # Total price display (will update when the amount is entered)
        total_price_label = tk.Label(popup_window, text="Total Price: 0 copper")
        total_price_label.pack(pady=5)

        # Confirm and Cancel buttons
        confirm_button = tk.Button(popup_window, text="Confirm", command=confirm_purchase)
        confirm_button.pack(pady=5)

        cancel_button = tk.Button(popup_window, text="Cancel", command=popup_window.destroy)
        cancel_button.pack(pady=5)

        # Set initial values for slider and entry
        amount_slider.set(1)
        amount_entry.insert(0, "1")
        self.update_total_price(amount_entry, total_price_label, item)


        
    def update_total_price(self, amount_entry, total_price_label, item):
        """Update the total price display with gold, silver, and copper."""
        try:
            amount = int(amount_entry.get())
            total_price_in_copper = item["price"] * amount

            # Convert to gold, silver, and copper
            total_gold = total_price_in_copper // 10000  # 1 gold = 10,000 copper
            remaining_copper = total_price_in_copper % 10000
            total_silver = remaining_copper // 100  # 1 silver = 100 copper
            total_copper = remaining_copper % 100  # Remaining copper

            # Display the total price in gold, silver, and copper
            total_price_label.config(
                text=f"Total Price: {total_gold} gold, {total_silver} silver, {total_copper} copper"
            )
        except ValueError:
            total_price_label.config(text="Total Price: 0 copper")

    def purchase_selected_item(self):
        """Purchase the currently selected item from the market table."""
        selected_item = self.items_tree.focus()  # Get the selected item
        if selected_item:
            item_id = int(self.items_tree.item(selected_item, 'tags')[0])
            item_to_purchase = next((item for item in self.global_data_manager.in_market_items if item['item_id'] == item_id), None)

            if item_to_purchase:
                self.purchase_confirmation_popup(item_to_purchase)
        else:
            messagebox.showerror("Error", "Please select an item to purchase.")

    def refresh_table(self, event=None):
        """Refresh the market items table, filtering by the search term."""
        search_term = self.search_var.get().lower().strip()  # Get the search term
        selected_item_id = self.get_selected_item()  # Remember selected item ID

        # Clear the current items in the table
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)

        # Insert the filtered items from the market based on the search term
        for item in self.global_data_manager.in_market_items:
            if search_term in item["name"].lower():
                current_time = time.time()
                if current_time >= item["available_time_at"]:
                    self.items_tree.insert(
                        "", tk.END, values=(item["name"], item["price"], item['amount'], int(item['not_available_timer'])),
                        tags=(str(item['item_id']),)  # Store 'item_id' in tags
                    )

        # Reselect the previously selected item (if available)
        if selected_item_id is not None:
            self.reselect_item(selected_item_id)

        # Apply the last sorting after refresh
        if self.last_sorted_column:
            self.sort_by_column(self.last_sorted_column, self.sort_reverse)


    def get_selected_item(self):
        """Get the selected item's item_id from the TreeView."""
        selected_item = self.items_tree.focus()
        if selected_item:
            return int(self.items_tree.item(selected_item, 'tags')[0])
        return None

    def reselect_item(self, item_id):
        """Reselect an item in the TreeView by its item_id."""
        for row in self.items_tree.get_children():
            item_values = self.items_tree.item(row, 'tags')
            if int(item_values[0]) == item_id:
                self.items_tree.selection_set(row)
                self.items_tree.focus(row)
                break

    def regenerate_items(self):
        """Generate a new item periodically and refresh the market."""
        def generate_runtime_item():
            if len(self.global_data_manager.in_market_items) >= self.MAX_ITEMS:
                return
            if not self.global_data_manager.items_list:
                print("No items available to generate.")
                return

            base_item = random.choices(self.global_data_manager.items_list, weights=[item['weight'] for item in self.global_data_manager.items_list], k=1)[0]

            # Adjust the price within the specified range
            price_adjustment_factor = random.uniform(self.PRICE_ADJUST_MIN, self.PRICE_ADJUST_MAX)
            adjusted_price = int(base_item["price"] * price_adjustment_factor)

            available_time_at = time.time() + random.uniform(self.TIME_ADJUST_MIN, self.TIME_ADJUST_MAX)
            not_available_timer = int(base_item["not_available_timer"] * random.uniform(self.TIMER_ADJUST_MIN, self.TIMER_ADJUST_MAX))
            adjusted_amount = int(base_item["amount"] * random.uniform(self.AMOUNT_ADJUST_MIN, self.AMOUNT_ADJUST_MAX))

            # Reuse removed item ID if available, otherwise find the next unique ID
            if self.global_data_manager.removed_item_ids:
                item_id = self.global_data_manager.removed_item_ids.pop(0)
            else:
                item_id = max([item['item_id'] for item in self.global_data_manager.in_market_items], default=0) + 1

            new_item = {
                "item_id": item_id,
                "name": base_item["name"],
                "price": adjusted_price,
                "amount": adjusted_amount,
                "available_time_at": available_time_at,
                "not_available_timer": not_available_timer,
                "data_id": base_item["data_id"]
            }

            # Add the new item to the market and refresh the table
            self.global_data_manager.in_market_items.append(new_item)
            self.refresh_table()

        def generate_items_loop():
            generate_runtime_item()
            next_delay = int(random.uniform(self.GENERATE_DELAY_MIN, self.GENERATE_DELAY_MAX) * 1000)
            self.root.after(next_delay, generate_items_loop)

        generate_items_loop()

    def refresh_market(self):
        """Refresh the market every second."""
        def update_timers():
            current_time = time.time()
            for item in self.global_data_manager.in_market_items[:]:
                if current_time >= item["available_time_at"]:
                    item['not_available_timer'] -= self.refresh_rate
                    if item['not_available_timer'] <= 0 or item['amount'] <= 0:
                        self.global_data_manager.removed_item_ids.append(item["item_id"])
                        self.global_data_manager.in_market_items.remove(item)

            self.refresh_table()
            self.root.after(self.refresh_rate * 1000, update_timers)

        update_timers()

    def clear_market(self):
        """Clear all items from the market and calculate the cost for changing providers."""
        self.apply_tax_fee()

        # Dynamically calculate the cost to change providers
        change_provider_cost = self.calculate_change_provider_cost()

        # Clear market items
        self.global_data_manager.in_market_items.clear()
        self.refresh_table()

    def apply_tax_fee(self):
        """Apply a 12% tax to the user's total currency (gold, silver, copper)."""
        # Convert the user's currency into copper for easy calculation
        total_copper = (self.global_data_manager.gold * 10000) + (self.global_data_manager.silver * 100) + self.global_data_manager.copper

        # Calculate the 12% tax
        tax_amount = total_copper * 0.12

        # Deduct the tax from the total copper
        total_copper -= int(tax_amount)

        # Convert the total copper back into gold, silver, and copper
        self.global_data_manager.gold = total_copper // 10000  # 1 gold = 10,000 copper
        remaining_copper = total_copper % 10000
        self.global_data_manager.silver = remaining_copper // 100  # 1 silver = 100 copper
        self.global_data_manager.copper = remaining_copper % 100  # Remaining copper

        # Update the display for the user's currency
        self.backpack_manager.update_money_display()

        # Inform the user about the tax deduction
        messagebox.showinfo("Tax Applied", f"A 12% tax fee has been applied: {int(tax_amount)} copper.")

    def calculate_change_provider_cost(self):
        """Calculate the amount of currency required to change providers dynamically."""
        total_copper = (self.global_data_manager.gold * 10000) + (self.global_data_manager.silver * 100) + self.global_data_manager.copper
        return int(total_copper * 0.05)  # For example, 5% of total currency


# Not in use anymore
    # def update_change_provider_label(self, change_provider_cost):
    #     """Update the label to show the required cost for changing providers."""
    #     cost_gold = change_provider_cost // 10000
    #     remaining_copper = change_provider_cost % 10000
    #     cost_silver = remaining_copper // 100
    #     cost_copper = remaining_copper % 100

    #     # Format the label text
    #     cost_text = f"Cost to change provider: {cost_gold} gold, {cost_silver} silver, {cost_copper} copper"
        
    #     # Update the label's text if it exists
    #     if self.change_provider_label:
    #         self.change_provider_label.config(text=cost_text)