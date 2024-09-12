import json
import os
import sys
import atexit

class GlobalDataManager:
    def __init__(self, user_items_file='user_items.json', market_items_file='market_items.json', data_file='data.json', items_file='items.json', demands_file='demands.json', wallet_file='wallet.json'):
        # Determine the correct path for the Data folder
        self.data_folder = self.get_data_folder()

        # Define file paths using the Data folder
        self.user_items_file = os.path.join(self.data_folder, user_items_file)
        self.market_items_file = os.path.join(self.data_folder, market_items_file)
        self.data_file = os.path.join(self.data_folder, data_file)  # Read-only
        self.items_file = os.path.join(self.data_folder, items_file)  # Read-only
        self.demands_file = os.path.join(self.data_folder, demands_file)
        self.wallet_file = os.path.join(self.data_folder, wallet_file)

        # Initialize shared data
        self.user_items = []  # User's inventory
        self.in_market_items = []  # Runtime items in the market
        self.items_list = []  # Original items from JSON (Read-only)
        self.data_list = []  # Original data from JSON (Read-only)
        self.removed_item_ids = []
        self.removed_demands_ids = []
        self.demands_list = []
        
        self.gold = 0
        self.silver = 0
        self.copper = 0
        
        atexit.register(self.save_all_data)  # Ensure data is saved at exit

    def get_data_folder(self):
        """Determine the correct path to the 'Data' folder, whether running from source or packaged."""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, "Data")

    def load_json_file(self, file_path):
        """Load data from a JSON file."""
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    print(f"Failed to load {file_path}.")
                    return []
        return []

    def save_json_file(self, file_path, data):
        """Save data to a JSON file."""
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def load_all_data(self):
        """Load all data from JSON files."""
        # Load read-only files
        self.items_list = self.load_json_file(self.items_file)  # Read-only
        self.data_list = self.load_json_file(self.data_file)  # Read-only

        # Load read-write files, creating defaults if necessary
        self.user_items = self.load_or_create(self.user_items_file, [])
        self.in_market_items = self.load_or_create(self.market_items_file, [])
        self.demands_list = self.load_or_create(self.demands_file, [])
        wallet = self.load_or_create(self.wallet_file, {'Gold': 0, 'Silver': 0, 'Copper': 50})
        
        # Set currency based on the wallet data
        self.gold = wallet.get('Gold', 0)
        self.silver = wallet.get('Silver', 0)
        self.copper = wallet.get('Copper', 50)

    def load_or_create(self, file_path, default_data):
        """Load a file if it exists, otherwise create it with default data."""
        if os.path.exists(file_path):
            return self.load_json_file(file_path)
        else:
            self.save_json_file(file_path, default_data)  # Create the file with default data
            return default_data

    def save_all_data(self):
        """Save all data to JSON files."""
        # Save only the read-write data
        self.save_json_file(self.user_items_file, self.user_items)
        self.save_json_file(self.market_items_file, self.in_market_items)
        self.save_json_file(self.demands_file, self.demands_list)
        
        # Save wallet data (gold, silver, copper)
        wallet_data = {
            'Gold': self.gold,
            'Silver': self.silver,
            'Copper': self.copper
        }
        self.save_json_file(self.wallet_file, wallet_data)
        print("All data saved successfully.")
        
    def restart(self):
        """Reset the data and set copper to 50."""
        # Reset currency
        self.gold = 0
        self.silver = 0
        self.copper = 50
        
        # Reset other game data (if needed)
        self.user_items.clear()  # Clear user items
        self.in_market_items.clear()  # Clear market items
        self.demands_list.clear()  # Clear demands list
        self.removed_item_ids.clear()  # Clear removed item IDs
        self.removed_demands_ids.clear()  # Clear removed demand IDs

        print("Game data reset and copper set to 50.")

        # Optionally, save the reset data
        self.save_all_data()
        self.load_all_data()
