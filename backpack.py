import tkinter as tk
from tkinter import ttk

class BackpackManager:
    def __init__(self, root, global_data_manager):
        self.root = root
        self.auto_update_id = None
        self.gold_label = None
        self.silver_label = None
        self.copper_label = None
        self.user_tree = None
        self.global_data_manager = global_data_manager
        self.backpack_window = None
        
    def update_money_display(self):
        """Update the money display in the backpack window if the labels exist."""
        if self.backpack_window and self.backpack_window.winfo_exists():
            if self.gold_label and self.gold_label.winfo_exists():
                self.gold_label.config(text=f"Gold: {self.global_data_manager.gold}")
            if self.silver_label and self.silver_label.winfo_exists():
                self.silver_label.config(text=f"Silver: {self.global_data_manager.silver}")
            if self.copper_label and self.copper_label.winfo_exists():
                self.copper_label.config(text=f"Copper: {self.global_data_manager.copper}")
        else:
            self.stop_auto_update()  # Stop updating if the window no longer exists


    def auto_convert_money(self):
        """Automatically convert copper to silver and silver to gold based on the conversion rate."""
        if not self.backpack_window or not self.backpack_window.winfo_exists():
            self.stop_auto_update()  # Stop if the window is closed
            return

        copper = self.global_data_manager.copper
        silver = self.global_data_manager.silver
        gold = self.global_data_manager.gold
        
        # Convert copper to silver (100 copper = 1 silver)
        if copper >= 100:
            converted_silver = copper // 100
            copper -= converted_silver * 100
            silver += converted_silver

        # Convert silver to gold (100 silver = 1 gold)
        if silver >= 100:
            converted_gold = silver // 100
            silver -= converted_gold * 100
            gold += converted_gold

        self.global_data_manager.copper = copper
        self.global_data_manager.silver = silver
        self.global_data_manager.gold = gold
        
        # Update the currency display
        self.update_money_display()

        # Schedule the next conversion and update, only if the window still exists
        if self.backpack_window and self.backpack_window.winfo_exists():
            self.auto_update_id = self.root.after(1000, self.auto_convert_money)
        else:
            self.stop_auto_update()

    def stop_auto_update(self):
        """Stop the auto-conversion updates when the backpack window is closed."""
        if self.auto_update_id:
            self.root.after_cancel(self.auto_update_id)
            self.auto_update_id = None

    def refresh_backpack_inventory(self):
        """Refresh the inventory table in the backpack window."""
        if self.backpack_window and self.backpack_window.winfo_exists():
            if self.user_tree and self.user_tree.winfo_exists():
                # Clear current inventory
                for row in self.user_tree.get_children():
                    self.user_tree.delete(row)

                # Insert updated inventory
                for item in self.global_data_manager.user_items:
                    self.user_tree.insert("", tk.END, values=(item["data_id"], item["name"], item["amount"]))
        else:
            self.stop_auto_update()

    def show_backpack(self):
        """Display the backpack window with the user's inventory and currency."""
        if self.backpack_window and self.backpack_window.winfo_exists():
            return  # Don't open multiple windows

        # Create the backpack window
        self.backpack_window = tk.Toplevel(self.root)
        self.backpack_window.title("Backpack")

        # Ensure auto-conversion stops when the backpack window is closed
        self.backpack_window.protocol("WM_DELETE_WINDOW", lambda: (self.stop_auto_update(), self.backpack_window.destroy()))

        # Create a frame to hold the currency display
        self.money_frame = tk.Frame(self.backpack_window)
        self.money_frame.pack(fill=tk.X, padx=10, pady=10)

        # Display the currency labels
        self.gold_label = tk.Label(self.money_frame, text=f"Gold: {self.global_data_manager.gold}")
        self.gold_label.pack(side=tk.LEFT, padx=5)
        self.silver_label = tk.Label(self.money_frame, text=f"Silver: {self.global_data_manager.silver}")
        self.silver_label.pack(side=tk.LEFT, padx=5)
        self.copper_label = tk.Label(self.money_frame, text=f"Copper: {self.global_data_manager.copper}")
        self.copper_label.pack(side=tk.LEFT, padx=5)

        # Create a frame to display the user's inventory
        self.user_tree_frame = tk.Frame(self.backpack_window)
        self.user_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.user_columns = ("Data ID", "Name", "Amount")
        self.user_tree = ttk.Treeview(self.user_tree_frame, columns=self.user_columns, show="headings")
        self.user_tree.heading("Data ID", text="Data ID")
        self.user_tree.heading("Name", text="Name")
        self.user_tree.heading("Amount", text="Amount")

        # Insert the user's inventory items into the tree view
        for item in self.global_data_manager.user_items:
            self.user_tree.insert("", tk.END, values=(item["data_id"], item["name"], item["amount"]))

        self.user_tree.pack(fill=tk.BOTH, expand=True)

        # Start the auto-conversion process
        self.auto_convert_money()
        
    def deduct_currency(self, item_price):
        """Deduct currency from the user based on the item price."""
        copper = self.global_data_manager.copper
        silver = self.global_data_manager.silver
        gold = self.global_data_manager.gold
        
        
        # Convert all user currency to copper for easy calculations
        total_user_copper = (gold * 10000) + (silver * 100) + copper

        if total_user_copper >= item_price:
            # Deduct the item price from the user's total copper
            total_user_copper -= item_price

            # Convert back to gold, silver, and copper
            gold = total_user_copper // 10000
            remaining_copper = total_user_copper % 10000
            silver = remaining_copper // 100
            copper = remaining_copper % 100


            self.global_data_manager.copper = copper
            self.global_data_manager.silver = silver
            self.global_data_manager.gold = gold


            # Update the currency display after purchase
            self.update_money_display()
            return True
        else:
            return False


    def receive_currency(self, amount_received):
        """Add currency to the user's balance based on the amount received."""
        
        copper = self.global_data_manager.copper
        silver = self.global_data_manager.silver
        gold = self.global_data_manager.gold
        
        # Convert all user currency to copper for easy calculations
        total_user_copper = (gold * 10000) + (silver * 100) + copper

        # Add the received amount to the user's total copper
        total_user_copper += amount_received

        # Convert back to gold, silver, and copper
        gold = total_user_copper // 10000
        remaining_copper = total_user_copper % 10000
        silver = remaining_copper // 100
        copper = remaining_copper % 100

        self.global_data_manager.copper = copper
        self.global_data_manager.silver = silver
        self.global_data_manager.gold = gold
        
        # Update the currency display after receiving money
        self.update_money_display()
        
    
    def add_to_inventory(self,item, amount):
        """Add purchased item to the user's inventory."""
        for user_item in  self.global_data_manager.user_items:
            if user_item["item_id"] == item["item_id"]:
                user_item["amount"] += amount  # Increase amount if the item exists
                return
        # If the item doesn't exist, add it
        self.global_data_manager.user_items.append({"item_id": item['item_id'], "name": item['name'], "amount":  amount, "data_id" : item['data_id']})
        