import random
import tkinter as tk
from tkinter import messagebox

class NumberGuessGame:
    def __init__(self, root, global_data_manager, backpack_manager):
        self.root = root
        self.global_data_manager = global_data_manager
        self.backpack_manager = backpack_manager
        self.default_cost_per_guess = 10 

    def guess_number(self):
        """Allow the user to guess a number between 1 and 6, with the option to bid a custom amount."""
        # Create a popup window to let the user enter their bid
        bid_window = tk.Toplevel(self.root)
        bid_window.title("Place Your Bid")

        tk.Label(bid_window, text="Enter your bid amount (copper):").pack(padx=20, pady=10)
        bid_entry = tk.Entry(bid_window)
        bid_entry.pack(padx=20, pady=5)

        def start_guessing():
            try:
                bid_amount = int(bid_entry.get())
                if bid_amount <= 0:
                    raise ValueError
                bid_window.destroy()  # Close bid window after valid bid

                # Deduct the bid amount from the user's currency
                if not self.backpack_manager.deduct_currency(bid_amount):
                    messagebox.showerror("Insufficient Funds", "You don't have enough copper to play.")
                    return

                self.start_guessing_game(bid_amount)

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive integer for the bid amount.")

        tk.Button(bid_window, text="Submit Bid", command=start_guessing).pack(pady=10)

    def start_guessing_game(self, bid_amount):
        """Start the guessing game with the given bid amount."""
        # Generate a random number between 1 and 6
        correct_number = random.randint(1, 6)

        # Create a popup window for guessing
        guess_window = tk.Toplevel(self.root)
        guess_window.title("Guess a Number (1-6)")

        tk.Label(guess_window, text="Guess a number between 1 and 6:").pack(padx=20, pady=10)
        guess_entry = tk.Entry(guess_window)
        guess_entry.pack(padx=20, pady=5)

        def check_guess():
            try:
                user_guess = int(guess_entry.get())
                if user_guess < 1 or user_guess > 6:
                    raise ValueError

                reward = bid_amount * 4  # Reward is bid amount times 4

                if user_guess == correct_number:
                    self.backpack_manager.receive_currency(reward)
                    messagebox.showinfo("Correct!", f"Congratulations! You guessed right and won {reward} copper!")
                else:
                    messagebox.showinfo("Incorrect", f"Sorry, the correct number was {correct_number}. Better luck next time!")

                guess_window.destroy()  # Close the guessing window after the attempt

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number between 1 and 6.")

        # Add a button to submit the guess
        tk.Button(guess_window, text="Submit Guess", command=check_guess).pack(pady=10)
