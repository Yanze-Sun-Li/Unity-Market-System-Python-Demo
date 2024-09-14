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
        """Determine the correct path to the 'Data' folder, and create it if necessary."""
        if getattr(sys, 'frozen', False):  # If running as a bundled executable
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")
        
        data_folder = os.path.join(base_path, "Data")

        # Ensure the Data folder exists
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)  # Create the folder if it doesn't exist

        return data_folder


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
        self.items_list = self.new_item()
        self.data_list = self.new_data()  # Read-only

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
            # Create the file with default data if it doesn't exist
            print(f"File not found, creating new file: {file_path}")
            self.save_json_file(file_path, default_data)
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
    
    def find_target_items_in_user_item(self,name):
        for item in self.user_items:
            if item['name'] == name:
                return item
        
    def new_data(self):
        return [
            {
                "id": "101",
                "name": "Wheat",
                "description": "A staple crop used to make bread and other food products.",
                "default_price": 3,
                "type": "Essentials",
                "stack_number": 100
            },
            {
                "id": "102",
                "name": "Iron Hoe",
                "description": "A basic farming tool used to till the soil.",
                "default_price": 80,
                "type": "Tools",
                "stack_number": 10
            },
            {
                "id": "103",
                "name": "Wood",
                "description": "A versatile material used for building and crafting.",
                "default_price": 12,
                "type": "Materials",
                "stack_number": 500
            },
            {
                "id": "104",
                "name": "Sheep Wool",
                "description": "Wool obtained from sheep, used in making clothes and textiles.",
                "default_price": 15,
                "type": "Materials",
                "stack_number": 100
            },
            {
                "id": "105",
                "name": "Clay Pot",
                "description": "A simple clay pot used for storing grains and liquids.",
                "default_price": 18,
                "type": "Goods",
                "stack_number": 50
            },
            {
                "id": "106",
                "name": "Gold Necklace",
                "description": "A luxurious gold necklace adorned with precious gems.",
                "default_price": 1000,
                "type": "Luxury",
                "stack_number": 1
            },
            {
                "id": "107",
                "name": "Painting",
                "description": "A beautiful piece of art created by a famous artist.",
                "default_price": 450,
                "type": "Arts",
                "stack_number": 5
            },
            {
                "id": "108",
                "name": "Iron Sword",
                "description": "A sturdy sword forged from iron, used for combat.",
                "default_price": 120,
                "type": "Tools",
                "stack_number": 10
            },
            {
                "id": "109",
                "name": "Silk Fabric",
                "description": "Luxurious fabric made from silk, used in high-end clothing.",
                "default_price": 250,
                "type": "Luxury",
                "stack_number": 20
            },
            {
                "id": "110",
                "name": "Stone Block",
                "description": "A solid block of stone used for construction.",
                "default_price": 25,
                "type": "Materials",
                "stack_number": 100
            },
            {
                "id": "111",
                "name": "Apple",
                "description": "A fresh and healthy fruit.",
                "default_price": 8,
                "type": "Essentials",
                "stack_number": 200
            },
            {
                "id": "112",
                "name": "Leather Boots",
                "description": "Boots made of durable leather for protection.",
                "default_price": 60,
                "type": "Goods",
                "stack_number": 50
            },
            {
                "id": "113",
                "name": "Iron Ingots",
                "description": "Refined iron ready for crafting and forging.",
                "default_price": 40,
                "type": "Materials",
                "stack_number": 200
            },
            {
                "id": "114",
                "name": "Wool Blanket",
                "description": "A cozy blanket made from sheep wool.",
                "default_price": 25,
                "type": "Goods",
                "stack_number": 25
            },
            {
                "id": "115",
                "name": "Bronze Statue",
                "description": "A detailed bronze statue of historical importance.",
                "default_price": 500,
                "type": "Arts",
                "stack_number": 2
            },
            {
                "id": "116",
                "name": "Leather Armor",
                "description": "Armor made of tough leather for protection in battle.",
                "default_price": 180,
                "type": "Tools",
                "stack_number": 5
            },
            {
                "id": "117",
                "name": "Silk Scarf",
                "description": "A luxurious scarf made from fine silk.",
                "default_price": 90,
                "type": "Luxury",
                "stack_number": 10
            },
            {
                "id": "118",
                "name": "Bread",
                "description": "A staple food made from wheat.",
                "default_price": 10,
                "type": "Essentials",
                "stack_number": 150
            },
            {
                "id": "119",
                "name": "Silver Ring",
                "description": "A fine ring made from silver.",
                "default_price": 300,
                "type": "Luxury",
                "stack_number": 5
            },
            {
                "id": "120",
                "name": "Fishing Rod",
                "description": "A simple tool for catching fish.",
                "default_price": 70,
                "type": "Tools",
                "stack_number": 15
            },
            {
                "id": "121",
                "name": "Copper Ore",
                "description": "Raw copper ore ready for smelting.",
                "default_price": 15,
                "type": "Materials",
                "stack_number": 300
            },
            {
                "id": "122",
                "name": "Iron Nails",
                "description": "Nails made from iron, used in construction.",
                "default_price": 5,
                "type": "Materials",
                "stack_number": 1000
            },
            {
                "id": "123",
                "name": "Glass Vase",
                "description": "A delicate vase made from glass.",
                "default_price": 45,
                "type": "Goods",
                "stack_number": 20
            },
            {
                "id": "124",
                "name": "Silver Bracelet",
                "description": "A beautiful silver bracelet with intricate designs.",
                "default_price": 320,
                "type": "Luxury",
                "stack_number": 5
            },
            {
                "id": "125",
                "name": "Marble Sculpture",
                "description": "A finely crafted marble sculpture.",
                "default_price": 950,
                "type": "Arts",
                "stack_number": 2
            },
            {
                "id": "126",
                "name": "Pottery Set",
                "description": "A set of handcrafted pottery pieces.",
                "default_price": 35,
                "type": "Goods",
                "stack_number": 10
            },
            {
                "id": "127",
                "name": "Tea Leaves",
                "description": "Freshly harvested tea leaves for brewing.",
                "default_price": 7,
                "type": "Essentials",
                "stack_number": 100
            },
            {
                "id": "128",
                "name": "Bronze Shield",
                "description": "A shield made from bronze, used for protection in battle.",
                "default_price": 230,
                "type": "Tools",
                "stack_number": 8
            },
            {
                "id": "129",
                "name": "Gold Coin",
                "description": "A rare gold coin from an ancient civilization.",
                "default_price": 450,
                "type": "Luxury",
                "stack_number": 50
            },
            {
                "id": "130",
                "name": "Cotton Cloth",
                "description": "Soft cloth made from cotton, used in clothing.",
                "default_price": 12,
                "type": "Materials",
                "stack_number": 500
            },
            {
                "id": "131",
                "name": "Honey",
                "description": "Sweet and natural honey from bees.",
                "default_price": 10,
                "type": "Goods",
                "stack_number": 100
            },
            {
                "id": "132",
                "name": "Iron Pickaxe",
                "description": "A sturdy pickaxe used for mining.",
                "default_price": 140,
                "type": "Tools",
                "stack_number": 10
            },
            {
                "id": "133",
                "name": "Cheese",
                "description": "A delicious dairy product made from milk.",
                "default_price": 12,
                "type": "Essentials",
                "stack_number": 100
            },
            {
                "id": "134",
                "name": "Grapes",
                "description": "Freshly picked grapes, used for making wine and juice.",
                "default_price": 8,
                "type": "Essentials",
                "stack_number": 200
            },
            {
                "id": "135",
                "name": "Carrot",
                "description": "A crunchy vegetable packed with nutrients.",
                "default_price": 7,
                "type": "Essentials",
                "stack_number": 150
            },
            {
                "id": "136",
                "name": "Salt",
                "description": "No one will survive without salt, and purchase make it easier to stay alive.",
                "default_price": 15,
                "type": "Essentials",
                "stack_number": 150
            }
        ]
        
    def new_item(self):
        return [
                {
                    "item_id": "1",
                    "name": "Wheat",
                    "price": 5,
                    "amount": 100,
                    "not_available_timer": 60.0,
                    "data_id": "101",
                    "weight": 10
                },
                {
                    "item_id": "2",
                    "name": "Iron Hoe",
                    "price": 80,
                    "amount": 5,
                    "not_available_timer": 720.0,
                    "data_id": "102",
                    "weight": 1
                },
                {
                    "item_id": "3",
                    "name": "Wood",
                    "price": 12,
                    "amount": 100,
                    "not_available_timer": 60.0,
                    "data_id": "103",
                    "weight": 8
                },
                {
                    "item_id": "4",
                    "name": "Sheep Wool",
                    "price": 15,
                    "amount": 100,
                    "not_available_timer": 60.0,
                    "data_id": "104",
                    "weight": 5
                },
                {
                    "item_id": "5",
                    "name": "Clay Pot",
                    "price": 18,
                    "amount": 10,
                    "not_available_timer": 720.0,
                    "data_id": "105",
                    "weight": 3
                },
                {
                    "item_id": "6",
                    "name": "Gold Necklace",
                    "price": 1000,
                    "amount": 1,
                    "not_available_timer": 1440.0,
                    "data_id": "106",
                    "weight": 0.5
                },
                {
                    "item_id": "7",
                    "name": "Painting",
                    "price": 450,
                    "amount": 3,
                    "not_available_timer": 1440.0,
                    "data_id": "107",
                    "weight": 1
                },
                {
                    "item_id": "8",
                    "name": "Iron Sword",
                    "price": 120,
                    "amount": 10,
                    "not_available_timer": 720.0,
                    "data_id": "108",
                    "weight": 2
                },
                {
                    "item_id": "9",
                    "name": "Silk Fabric",
                    "price": 250,
                    "amount": 20,
                    "not_available_timer": 480.0,
                    "data_id": "109",
                    "weight": 1
                },
                {
                    "item_id": "10",
                    "name": "Stone Block",
                    "price": 25,
                    "amount": 100,
                    "not_available_timer": 60.0,
                    "data_id": "110",
                    "weight": 4
                },
                {
                    "item_id": "11",
                    "name": "Apple",
                    "price": 8,
                    "amount": 200,
                    "not_available_timer": 30.0,
                    "data_id": "111",
                    "weight": 7
                },
                {
                    "item_id": "12",
                    "name": "Leather Boots",
                    "price": 60,
                    "amount": 50,
                    "not_available_timer": 720.0,
                    "data_id": "112",
                    "weight": 3
                },
                {
                    "item_id": "13",
                    "name": "Iron Ingots",
                    "price": 40,
                    "amount": 50,
                    "not_available_timer": 480.0,
                    "data_id": "113",
                    "weight": 5
                },
                {
                    "item_id": "14",
                    "name": "Wool Blanket",
                    "price": 25,
                    "amount": 25,
                    "not_available_timer": 360.0,
                    "data_id": "114",
                    "weight": 4
                },
                {
                    "item_id": "15",
                    "name": "Bronze Statue",
                    "price": 50,
                    "amount": 2,
                    "not_available_timer": 1440.0,
                    "data_id": "115",
                    "weight": 1
                },
                {
                    "item_id": "16",
                    "name": "Leather Armor",
                    "price": 180,
                    "amount": 5,
                    "not_available_timer": 720.0,
                    "data_id": "116",
                    "weight": 2
                },
                {
                    "item_id": "17",
                    "name": "Silk Scarf",
                    "price": 90,
                    "amount": 2,
                    "not_available_timer": 480.0,
                    "data_id": "117",
                    "weight": 1
                },
                {
                    "item_id": "18",
                    "name": "Bread",
                    "price": 10,
                    "amount": 150,
                    "not_available_timer": 60.0,
                    "data_id": "118",
                    "weight": 7
                },
                {
                    "item_id": "19",
                    "name": "Silver Ring",
                    "price": 300,
                    "amount": 5,
                    "not_available_timer": 1440.0,
                    "data_id": "119",
                    "weight": 1
                },
                {
                    "item_id": "20",
                    "name": "Fishing Rod",
                    "price": 20,
                    "amount": 1,
                    "not_available_timer": 360.0,
                    "data_id": "120",
                    "weight": 3
                },
                {
                    "item_id": "21",
                    "name": "Copper Ore",
                    "price": 15,
                    "amount": 20,
                    "not_available_timer": 60.0,
                    "data_id": "121",
                    "weight": 6
                },
                {
                    "item_id": "22",
                    "name": "Iron Nails",
                    "price": 5,
                    "amount": 50,
                    "not_available_timer": 60.0,
                    "data_id": "122",
                    "weight": 9
                },
                {
                    "item_id": "23",
                    "name": "Glass Vase",
                    "price": 45,
                    "amount": 20,
                    "not_available_timer": 720.0,
                    "data_id": "123",
                    "weight": 3
                },
                {
                    "item_id": "24",
                    "name": "Silver Bracelet",
                    "price": 320,
                    "amount": 5,
                    "not_available_timer": 1440.0,
                    "data_id": "124",
                    "weight": 1
                },
                {
                    "item_id": "25",
                    "name": "Marble Sculpture",
                    "price": 950,
                    "amount": 2,
                    "not_available_timer": 1440.0,
                    "data_id": "125",
                    "weight": 0.5
                },
                {
                    "item_id": "26",
                    "name": "Pottery Set",
                    "price": 35,
                    "amount": 10,
                    "not_available_timer": 720.0,
                    "data_id": "126",
                    "weight": 3
                },
                {
                    "item_id": "27",
                    "name": "Tea Leaves",
                    "price": 7,
                    "amount": 100,
                    "not_available_timer": 30.0,
                    "data_id": "127",
                    "weight": 6
                },
                {
                    "item_id": "28",
                    "name": "Bronze Shield",
                    "price": 230,
                    "amount": 1,
                    "not_available_timer": 720.0,
                    "data_id": "128",
                    "weight": 2
                },
                {
                    "item_id": "29",
                    "name": "Gold Coin",
                    "price": 650,
                    "amount": 50,
                    "not_available_timer": 1440.0,
                    "data_id": "129",
                    "weight": 1
                },
                {
                    "item_id": "30",
                    "name": "Cotton Cloth",
                    "price": 12,
                    "amount": 100,
                    "not_available_timer": 60.0,
                    "data_id": "130",
                    "weight": 6
                },
                {
                    "item_id": "31",
                    "name": "Honey",
                    "price": 10,
                    "amount": 100,
                    "not_available_timer": 30.0,
                    "data_id": "131",
                    "weight": 7
                },
                {
                    "item_id": "32",
                    "name": "Iron Pickaxe",
                    "price": 140,
                    "amount": 10,
                    "not_available_timer": 720.0,
                    "data_id": "132",
                    "weight": 3
                },
                {
                    "item_id": "33",
                    "name": "Cheese",
                    "price": 12,
                    "amount": 100,
                    "not_available_timer": 30.0,
                    "data_id": "133",
                    "weight": 6
                },
                {
                    "item_id": "34",
                    "name": "Grapes",
                    "price": 8,
                    "amount": 100,
                    "not_available_timer": 30.0,
                    "data_id": "134",
                    "weight": 7
                },
                {
                    "item_id": "35",
                    "name": "Carrot",
                    "price": 7,
                    "amount": 150,
                    "not_available_timer": 30.0,
                    "data_id": "135",
                    "weight": 7
                },
                {
                    "item_id": "36",
                    "name": "Salt",
                    "price": 15,
                    "amount": 150,
                    "not_available_timer": 30.0,
                    "data_id": "135",
                    "weight": 7
                }
    ]