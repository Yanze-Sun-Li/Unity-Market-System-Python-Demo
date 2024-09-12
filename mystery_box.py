import random
from tkinter import messagebox
import tkinter as tk

class MysteryBoxGame:
    def __init__(self, root, global_data_manager,backpack_manager):
        self.root = root
        self.global_data_manager = global_data_manager
        self.backpack_manager = backpack_manager
        self.box_details = {
            'copper': {
                'price': 10,
                'items': [1, 2, 30],
                'weights': [0.6, 0.3, 0.1],  # Higher chance to get 5 items
                'color': {1: 'lightblue', 2: 'lightgreen', 30: 'orange'}
            },
            'silver': {
                'price': 1000,
                'items': [5, 50, 250],
                'weights': [0.6, 0.3, 0.1],  # Moderate chance distribution
                'color': {5: 'lightblue', 50: 'lightgreen', 250: 'orange'}
            },
            'gold': {
                'price': 100000,
                'items': [200, 400, 10000],
                'weights': [0.7, 0.3, 0.05],  # More evenly distributed chances
                'color': {200: 'lightblue', 400: 'lightgreen', 10000: 'orange'}
            }
        }

    def buy_mystery_box(self, box_type):
        """Buy a mystery box (copper, silver, or gold) and receive random items."""

        # Validate box type
        if box_type not in self.box_details:
            messagebox.showerror("Invalid", "Invalid box type.")
            return

        # Get cost, item count options, and weights for the selected box
        cost = self.box_details[box_type]['price']
        possible_item_counts = self.box_details[box_type]['items']
        item_weights = self.box_details[box_type]['weights']
        item_colors = self.box_details[box_type]['color']

        # Deduct the cost from the user's currency
        if self.backpack_manager.deduct_currency(cost):
            # Randomly select the number of items based on weights
            num_items = random.choices(possible_item_counts, weights=item_weights)[0]
            items_awarded = self.random_items(num_items)

            # Add the random items to the user's inventory
            self.backpack_manager.add_to_inventory(items_awarded, num_items)

            # Notify the user of their reward with a color-coded dialog
            self.show_color_dialog(f"You received {num_items} x {items_awarded['name']} from the {box_type} mystery box!", item_colors[num_items])
            self.backpack_manager.refresh_backpack_inventory()
        else:
            messagebox.showerror("Insufficient Funds", f"You don't have enough money to buy a {box_type} mystery box.")

    def show_color_dialog(self, message, color):
        """Display a messagebox with a colored background."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Mystery Box Result")
        dialog.configure(bg=color)

        label = tk.Label(dialog, text=message, bg=color, font=("Arial", 12))
        label.pack(padx=20, pady=20)

        ok_button = tk.Button(dialog, text="OK", command=dialog.destroy, bg=color)
        ok_button.pack(pady=10)

    def random_items(self, num_items):
        """Generate a list of random items."""
        all_items = self.global_data_manager.items_list  # Assuming a list of available items
        return random.choice(all_items)
