import random
import tkinter as tk
from tkinter import messagebox

class LotteryCenter:
    def __init__(self, root, global_data_manager,backpack_manager):
        self.root = root
        self.global_data_manager = global_data_manager
        self.backpack_manager = backpack_manager
        self.user_has_ticket = False  # Track if the user has bought a ticket
        self.lottery_running = False
        self.lottery_task = None
        self.ticket_price = 10  # Example ticket price in copper

    def start_lottery(self):
        """Start the lottery that picks a winner every 30 seconds."""
        if not self.lottery_running:
            self.lottery_running = True
            self.lottery_loop()  # Start the loop automatically
        #     messagebox.showinfo("Lottery", "The lottery has started! Buy your ticket!")
        # else:
        #     messagebox.showwarning("Lottery", "Lottery is already running!")

    def buy_ticket(self):
        """User buys a ticket for the lottery, but only one ticket per round."""
        if not self.lottery_running:
            messagebox.showwarning("Lottery", "Lottery is not running.")
            return

        if self.user_has_ticket:
            messagebox.showerror("Lottery", "You have already bought a ticket!")
            return

        # Deduct currency for the ticket
        if self.backpack_manager.deduct_currency(self.ticket_price):
            self.user_has_ticket = True
            messagebox.showinfo("Lottery", f"You bought a ticket for {self.ticket_price} copper, please wait for the draw day!")
        else:
            messagebox.showerror("Insufficient Funds", "You don't have enough money to buy a ticket.")

    def lottery_loop(self):
        """Run the lottery loop, picking the user as the winner every 30 seconds if they have a ticket."""
        if self.user_has_ticket:
                # Generate a random number between 1 and 1000
                if random.randint(1, 1000) == 1:
                    reward = random.randint(10000, 50000)  # Random reward for the user, always an integer
                    self.backpack_manager.receive_currency(reward) 
                    messagebox.showinfo("Lottery Winner!", f"Congratulations! You won {reward} coins!")
                self.user_has_ticket = False  # Reset for the next round
        # No prompt if the user didn't buy a ticket

        # Schedule the next lottery in 30 seconds
        if self.lottery_running:
            self.lottery_task = self.root.after(30000, self.lottery_loop)  # 30 seconds

    def stop_lottery(self):
        """Stop the lottery."""
        self.lottery_running = False
        if self.lottery_task:
            self.root.after_cancel(self.lottery_task)
        messagebox.showinfo("Lottery", "Lottery has been stopped.")

    def create_gambling_ui(self):
        """Create the UI for the Lottery Center."""
        lottery_button = tk.Button(self.root, text=f"Buy Lottery Ticket ({self.ticket_price} copper)", command=self.buy_ticket)
        lottery_button.pack(pady=10)
