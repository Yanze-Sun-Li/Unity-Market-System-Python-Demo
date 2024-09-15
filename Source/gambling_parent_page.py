import tkinter as tk
from lottery_center import LotteryCenter
from mystery_box import MysteryBoxGame
from number_guessing import NumberGuessGame

class GamblingPageUI:
    def __init__(self, root, global_data_manager, backpack_manager):
        self.root = root
        self.lottery_center = LotteryCenter(root, global_data_manager, backpack_manager)
        self.guess_game = NumberGuessGame(root, global_data_manager, backpack_manager)
        self.mystery_box = MysteryBoxGame(root, global_data_manager, backpack_manager)

        # Create the gambling page interface
        self.gambling_window = None

    def open_gambling_page(self):
        """Open the gambling page with a well-organized layout and show prices."""
        self.gambling_window = tk.Toplevel(self.root)
        self.gambling_window.title("Gambling Page")

        # Create a main frame for the layout
        main_frame = tk.Frame(self.gambling_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create sections for different games
        lottery_frame = tk.LabelFrame(main_frame, text="Lottery", padx=10, pady=10)
        lottery_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        guess_frame = tk.LabelFrame(main_frame, text="Number Guessing Game", padx=10, pady=10)
        guess_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        mystery_box_frame = tk.LabelFrame(main_frame, text="Mystery Boxes", padx=10, pady=10)
        mystery_box_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Add lottery button and price
        lottery_button = tk.Button(lottery_frame, text="Buy Lottery Ticket", command=lambda: self.lottery_center.buy_ticket())
        lottery_button.grid(row=0, column=0, sticky="ew")
        tk.Label(lottery_frame, text=f"Price: {self.lottery_center.ticket_price} copper").grid(row=0, column=1, padx=10)

        # Add guessing game button and price
        guess_button = tk.Button(guess_frame, text="Guess a Number", command=lambda: self.guess_game.guess_number())
        guess_button.grid(row=0, column=0, sticky="ew")
        tk.Label(guess_frame, text=f"Price: {self.guess_game.default_cost_per_guess} copper").grid(row=0, column=1, padx=10)

        # Add mystery box buttons and prices
        tk.Button(mystery_box_frame, text="Buy Copper Mystery Box", 
                  command=lambda: self.mystery_box.buy_mystery_box("copper")).grid(row=0, column=0, sticky="ew")
        tk.Label(mystery_box_frame, text=f"Price: {self.mystery_box.box_details['copper']['price']} copper").grid(row=0, column=1, padx=10)

        tk.Button(mystery_box_frame, text="Buy Silver Mystery Box", 
                  command=lambda: self.mystery_box.buy_mystery_box("silver")).grid(row=1, column=0, sticky="ew")
        tk.Label(mystery_box_frame, text=f"Price: {self.mystery_box.box_details['silver']['price']/100} silver").grid(row=1, column=1, padx=10)

        tk.Button(mystery_box_frame, text="Buy Gold Mystery Box", 
                  command=lambda: self.mystery_box.buy_mystery_box("gold")).grid(row=2, column=0, sticky="ew")
        tk.Label(mystery_box_frame, text=f"Price: {self.mystery_box.box_details['gold']['price']/10000} gold").grid(row=2, column=1, padx=10)

        # Configure grid layout to expand nicely
        self.gambling_window.grid_columnconfigure(0, weight=1)
        self.gambling_window.grid_columnconfigure(1, weight=1)
        self.gambling_window.grid_rowconfigure(0, weight=1)
        self.gambling_window.grid_rowconfigure(1, weight=1)
