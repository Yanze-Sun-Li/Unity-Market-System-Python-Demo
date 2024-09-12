import math
import random
import tkinter as tk

class DemandsManager:
    def __init__(self, root,global_data_manager,selling_market_manager):
        self.global_data_manager = global_data_manager
        selling_market_manager.set_demands_control(self)
        self.selling_market_manager = selling_market_manager
        
        self.adjust_demands_with_market = False;
  
        self.demands_tree = None
        self.refresh_task = None
        self.MAX_DEMANDS = 50
        self.DEMAND_GENERATION_DELAY_MIN = 0.5
        self.DEMAND_GENERATION_DELAY_MAX = 2.5
        self.demands_generation_interval_min = 500
        self.demands_generation_interval_max = 1000
        self.root = root
        
        self.max_demand_amount = 20  # Maximum demand amount per item
        self.amount_divisor = 50  # Divisor for calculating demand amount
        self.not_available_timer_min = 30  # Minimum time for not available timer
        self.not_available_timer_max = 120  # Maximum time for not available timer
        self.demand_timer_divisor = 100  # Divisor for adjusting the timer based on demand amount
        self.default_price_multiplier = 1.8  # Default price multiplier when no matching items in market
        self.market_divisor = 100  # Divisor for adjusting price based on market supply
        self.min_price_multiplier = 0.3  # Minimum price multiplier
        self.max_demands = 50  # Maximum number of demands allowed
        
    def generate_demands(self):
        """Generate a new demand periodically based on available items, considering their weights."""
        if len(self.global_data_manager.demands_list) >= self.max_demands:
            return

        # Check if there are items to generate demands from
        if not self.global_data_manager.items_list:
            return

        # Select a base item from the items list based on their weights
        base_item = random.choices(
            self.global_data_manager.items_list,
            weights=[item['weight'] for item in self.global_data_manager.items_list],
            k=1
        )[0]

        # Adjust demand price based on the availability of similar items in the market
        adjusted_price = self.adjust_demand_price(base_item)

        # Generate random demand amount, not to exceed the base item's stock
        demand_amount = random.randint(1, min(self.max_demand_amount, base_item['amount'])) + \
                        int(math.floor((base_item['amount'] / self.amount_divisor) ** 2))

        # Calculate the price influence on the timer
        price_influence_factor = max(0.3, adjusted_price / base_item['price'])  # Higher prices increase the timer

        # Set the random not available timer, scaled by the price influence
        demand_not_available_timer = (random.uniform(self.not_available_timer_min, self.not_available_timer_max) +
                                      int(demand_amount / self.demand_timer_divisor)) * price_influence_factor
        
        # One more time adjustment, based on the demand's price, decrease the max value, minimum to 1.
        def adjust_max_demand_based_on_price(adjusted_price, base_price, max_demand_amount):
            """Adjust the maximum demand amount based on the demand's generated price."""
            price_scale_factor = max(0.1, 1.0 - ((adjusted_price / base_price) - 1.0))  # Scales down as price increases
            return max(1, int(max_demand_amount * price_scale_factor))  # Ensure minimum is 1

        # Adjust max demand amount based on the adjusted demand price
        max_demand_scaled = adjust_max_demand_based_on_price(adjusted_price, base_item['price'], self.max_demand_amount)
        
        # Generate the final demand amount with the adjusted max value
        demand_amount = random.randint(1, min(max_demand_scaled, base_item['amount'])) + \
                        int(math.floor((base_item['amount'] / self.amount_divisor) ** 2))

        

        # Reuse a removed demand ID if available, otherwise generate a new one
        if self.global_data_manager.removed_demands_ids:
            demand_id = self.global_data_manager.removed_demands_ids.pop(0)
        else:
            demand_id = len(self.global_data_manager.demands_list) + 1

        # Create the new demand
        new_demand = {
            "demand_id": int(demand_id),
            "item_id": base_item["item_id"],
            "buy_price": int(adjusted_price),
            "max_amount": int(demand_amount),
            "not_available_timer": demand_not_available_timer
        }

        # Add the new demand to the list
        self.global_data_manager.demands_list.append(new_demand)
        self.selling_market_manager.refresh_table()

    def adjust_demand_price(self, base_item):
        """Adjust demand price based on supply in the market and average market prices with added randomness."""
        # Pre-filter matching items in the market only once
        matching_items = [item for item in self.global_data_manager.in_market_items if item['data_id'] == base_item['data_id']]
        count = len(matching_items)
        
        # Calculate the average price of matching items in the market
        if matching_items:
            average_market_price = sum(item['price'] for item in matching_items) / count
        else:
            average_market_price = base_item['price']  # Fallback to base item price if no matching items

        # Randomly adjust the supply influence to add more variability
        supply_influence_randomness = random.uniform(0.8, 1.2)  # Adding randomness to supply influence
        supply_influence = (1.0 - (0.5 * (count / self.market_divisor))) * supply_influence_randomness if count > 0 else self.default_price_multiplier

        # Stronger influence of the average market price with random variability
        price_increase_randomness = random.uniform(1.0, 1.3)  # Adding randomness to price increase factor
        price_increase_factor = max(1.0, (average_market_price / base_item['price']) ** (1.5 * price_increase_randomness))

        # Random fluctuation to simulate market volatility
        random_fluctuation = random.uniform(0.90, 1.10)  # Adjusted fluctuation range for more volatility
        
        # Combine the influences with more variability
        final_price_multiplier = (0.7 * price_increase_factor) + (0.3 * supply_influence)

        # Apply the random fluctuation to the final price
        final_price = base_item['price'] * final_price_multiplier * random_fluctuation

        # Ensure the price stays above the minimum multiplier
        return int(max(final_price, base_item['price'] * self.min_price_multiplier))


    def all_demands_change(self):
        """Refresh all demand prices based on the item name."""
        # Create a dictionary to store adjusted prices by item ID
        item_price_map = {}

        # Iterate through all demands to adjust prices for each unique item
        for demand in self.global_data_manager.demands_list:
            item_id = demand['item_id']
            
            # If the item's price hasn't been adjusted yet, adjust it
            if item_id not in item_price_map:
                base_item = next((item for item in self.global_data_manager.items_list if item['item_id'] == item_id), None)
                if base_item:
                    # Adjust the price for this item
                    adjusted_price = self.adjust_demand_price(base_item)
                    item_price_map[item_id] = adjusted_price  # Store the adjusted price in the map

            # Update the demand's buy_price with the adjusted price
            demand['buy_price'] = item_price_map[item_id]

        # After all demands have been updated, refresh the demands table
        self.selling_market_manager.refresh_table()

    def get_filtered_demands(self, search_term):
        """Return a list of filtered demands based on the search term, using the actual data structure."""
        filtered_demands = []
        search_term = search_term.lower().strip()

        for demand in self.global_data_manager.demands_list:
            item_name = self.find_item_name(demand["item_id"])
            if item_name and search_term in item_name.lower():
                # Append the entire demand object from the original data structure
                filtered_demands.append(demand)

        return filtered_demands




    def find_item_name(self, item_id):
        """Find the item name based on item_id."""
        item = next((item for item in self.global_data_manager.items_list if item["item_id"] == item_id), None)
        return item["name"] if item else "Unknown"

    def clear_demands(self):
        """Clear all current demands."""
        self.global_data_manager.demands_list.clear()
        self.selling_market_manager.refresh_table()
        
    def refresh_loop(self):    
        """Refresh circle, 
        Decrease the not_available_timer for each demand and refresh the table,
        Update All price.
        """
        # This currently disable the demands refresh based on the current supply market.
        if self.adjust_demands_with_market:
            self.all_demands_change()
            
            
        to_remove = []  # List to store demands that should be removed
        for demand in self.global_data_manager.demands_list:
            if demand["not_available_timer"] > 0:
                demand["not_available_timer"] -= 0.5  # Decrement by 0.5 seconds
            
            if demand["not_available_timer"] <= 0:
                to_remove.append(demand)  # Add expired demands to the removal list

        # Remove expired demands and add their IDs to the removed list
        for demand in to_remove:
            self.global_data_manager.removed_demands_ids.append(demand["demand_id"])
            self.global_data_manager.demands_list.remove(demand)

        self.selling_market_manager.refresh_table()  # Refresh the table to update the changes


    def random_generate_demands_loop(self):
        
        """Generate demands at random intervals controlled by a class variable."""
        # Generate a new demand
        self.generate_demands()
        # Calculate the next demand generation time
        next_interval = random.randint(int(self.demands_generation_interval_min), int(self.demands_generation_interval_max))

        # Schedule the next execution of this loop
        self.root.after(next_interval, self.random_generate_demands_loop)
        
    def filter_demands(self, search_term):
        """Filter the demands based on the search term."""
        search_term = search_term.lower().strip()
        # Toggle search_active flag
        if search_term:
            self.search_active = True  # Search is active
        else:
            self.search_active = False  # No search, so allow refresh
