import time
import tkinter as tk

from fixed_price_market import FixedPriceMarketManager
from gambling_parent_page import GamblingPageUI
from items_view import open_items_window
from item_details import open_item_details_window
import market_table
import global_data
import backpack
import selling_market
import demands_control

# Global settings for FPS control
record_GAME_START_TIME = time.time()  # Record the start time
record_LAST_UPDATE_TIME = time.time()  # Initialize the last update time
FRAME_RATE = 24  # Target frame rate (24 FPS)
FIXED_FRAME_GAP = 1 / FRAME_RATE  # Calculate the time gap between frames
GLOBAL_DATA = global_data.GlobalDataManager()
root = None
ENABLE_SWITCH_MARKET = False


def main():
    global GLOBAL_DATA, root

    # Main application setup
    root = tk.Tk()
    root.title("Market")

    # Initialize BackpackManager
    backpack_manager = backpack.BackpackManager(root, GLOBAL_DATA)

    # Initialize MarketManager
    market_manager = market_table.MarketManager(root, GLOBAL_DATA, backpack_manager)

    selling_market_manager = selling_market.SellingMarketManager(root, GLOBAL_DATA)
    selling_market_manager.set_backpack_manager(backpack_manager)

    demands_manager = demands_control.DemandsManager(root, GLOBAL_DATA, selling_market_manager)  # Manages demands
    demands_manager.random_generate_demands_loop()

    # Market table setup
    items_frame = tk.Frame(root)
    items_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    market_manager.create_market_table(items_frame)  # MarketManager manages the table

    # Button frame with fixed width
    button_frame = tk.Frame(root)
    button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

    # Buttons for various actions
    purchase_button = tk.Button(button_frame, text="Purchase Selected Item", command=lambda: market_manager.purchase_selected_item())
    purchase_button.grid(row=0, column=0, sticky="ew", pady=2)  # Using grid for button layout

    if ENABLE_SWITCH_MARKET:
        clear_market_button = tk.Button(button_frame, text="Find New Providers", command=lambda: market_manager.clear_market())
        clear_market_button.grid(row=1, column=0, sticky="ew", pady=2)

    selling_market_button = tk.Button(button_frame, text="Demands Board", command=selling_market_manager.open_selling_market)
    selling_market_button.grid(row=2, column=0, sticky="ew", pady=2)

    fixed_price_market = FixedPriceMarketManager(root, GLOBAL_DATA)
    fixed_price_market.set_backpack_manager(backpack_manager)

    # Button to open the fixed price market, using grid layout
    open_market_button = tk.Button(button_frame, text="Fixed Price Market", command=fixed_price_market.open_fixed_price_market) 
    open_market_button.grid(row=3, column=0, sticky="ew", pady=2)

        # Create an instance of the GamblingPageUI and pass necessary data
    gambling_page_ui = GamblingPageUI(root, GLOBAL_DATA,backpack_manager)
        # Automatically start the lottery when the main function is started
    gambling_page_ui.lottery_center.start_lottery()
    
        # Add the button to open the gambling page
    gambling_button = tk.Button(button_frame, text="Try Your Luck", command=gambling_page_ui.open_gambling_page)
    gambling_button.grid(row=5, column=0, sticky="ew", pady=2)
    

    # Add the Restart button to reset the game and set copper to 50
    restart_button = tk.Button(button_frame, text="Restart", command=lambda: GLOBAL_DATA.restart())
    restart_button.grid(row=4, column=0, sticky="ew", pady=16)

    # Configure grid weights for even distribution and resizing behavior
    root.grid_columnconfigure(0, weight=3)  # Allow more space for the items_frame
    root.grid_columnconfigure(1, weight=1)  # Less space for the buttons
    root.grid_rowconfigure(0, weight=1)

    # Main menu setup
    main_menu = tk.Menu(root)
    root.config(menu=main_menu)

    # Wiki menu
    wiki_menu = tk.Menu(main_menu, tearoff=0)
    main_menu.add_cascade(label="Wiki", menu=wiki_menu)
    wiki_menu.add_command(label="Items", command=lambda: open_items_window(root, GLOBAL_DATA.items_list))
    wiki_menu.add_command(label="Item Details", command=lambda: open_item_details_window(root, GLOBAL_DATA.items_list, GLOBAL_DATA.data_list))

    # Backpack menu item    
    backpack_menu = tk.Menu(main_menu, tearoff=0)
    main_menu.add_cascade(label="Backpack", menu=backpack_menu)
    backpack_menu.add_command(label="Show Backpack", command=lambda: backpack_manager.show_backpack())

    # Load items and data from JSON files
    GLOBAL_DATA.load_all_data()

    # Start the market refresh loop
    market_manager.refresh_market()

    # Start regenerating items periodically
    market_manager.regenerate_items()

    # Start the periodic update for demand timers
    # The time has been hard coded into the function.
    def update_demand_timers():
        demands_manager.refresh_loop()
    
        root.after(500, update_demand_timers)  # Schedule the next update

    update_demand_timers()

    # Start the Tkinter main loop
    root.mainloop()



main()
