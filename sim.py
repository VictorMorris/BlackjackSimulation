import random
import matplotlib.pyplot as plt


# Game constants
WIN_PROBABILITY = 49
LOSS_PROBABILITY = 42
TIE_PROBABILITY = 9
EXPECTED_VALUE_PER_DOLLAR = -0.07


class BlackjackSimulator:
    """Simulates multiple hands of blackjack and tracks statistics."""
    
    def __init__(self, num_hands, bet_amount):
        self.num_hands = num_hands
        self.bet_amount = bet_amount
        
        # Tracking variables
        self.total_profit = 0
        self.hand_results = []
        self.profit_history = []
        self.expected_value_history = []
        
        # Statistics
        self.longest_win_streak = 0
        self.current_win_streak = 0
        self.highest_profit = 0
    
    def play_hand(self):
        """Simulates a single hand of blackjack."""
        outcome = random.random() * 100
        
        if outcome <= WIN_PROBABILITY:
            return -1  # Loss
        elif outcome <= WIN_PROBABILITY + LOSS_PROBABILITY:
            return 1   # Win
        else:
            return 0   # Tie
    
    def update_statistics(self, result, hand_number):
        """Updates running statistics based on hand result."""
        # Update profit
        if result == -1:
            self.total_profit -= self.bet_amount
            self.current_win_streak = 0
        elif result == 1:
            self.total_profit += self.bet_amount
            self.current_win_streak += 1
        
        # Track histories
        self.hand_results.append(result)
        self.profit_history.append(self.total_profit)
        self.expected_value_history.append(
            EXPECTED_VALUE_PER_DOLLAR * self.bet_amount * hand_number
        )
        
        # Update peak statistics
        if self.total_profit > self.highest_profit:
            self.highest_profit = self.total_profit
        
        if self.current_win_streak > self.longest_win_streak:
            self.longest_win_streak = self.current_win_streak
    
    def run_simulation(self):
        """Runs the complete blackjack simulation."""
        for hand_number in range(self.num_hands):
            result = self.play_hand()
            self.update_statistics(result, hand_number)
    
    def get_statistics(self):
        """Calculates and returns game statistics."""
        wins = self.hand_results.count(1)
        losses = self.hand_results.count(-1)
        ties = self.hand_results.count(0)
        total_hands = wins + losses + ties
        
        return {
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'win_percentage': (wins / total_hands) * 100,
            'loss_percentage': (losses / total_hands) * 100,
            'tie_percentage': (ties / total_hands) * 100,
            'longest_win_streak': self.longest_win_streak,
            'highest_profit': self.highest_profit,
            'final_profit': self.total_profit
        }
    
    def plot_results(self, stats):
        """Visualizes the simulation results with statistics."""
        hand_numbers = list(range(self.num_hands))
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot profit lines
        ax.plot(hand_numbers, self.profit_history, label='Actual Profit', linewidth=2)
        ax.plot(hand_numbers, self.expected_value_history, 
                 label='Expected Value', linestyle='--', linewidth=2)
        
        ax.set_xlabel('Hands Played')
        ax.set_ylabel('Profit ($)')
        ax.set_title('Blackjack Simulation Results', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # Add statistics text box
        stats_text = f"""SIMULATION STATISTICS
{'─' * 30}
Wins:   {stats['wins']:5d} ({stats['win_percentage']:5.2f}%)
Losses: {stats['losses']:5d} ({stats['loss_percentage']:5.2f}%)
Ties:   {stats['ties']:5d} ({stats['tie_percentage']:5.2f}%)
{'─' * 30}
Longest Win Streak:  {stats['longest_win_streak']}
Highest Profit:      ${stats['highest_profit']}
Final Profit/Loss:   ${stats['final_profit']}"""
        
        # Position text box in the plot
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=props, family='monospace')
        
        plt.tight_layout()
        plt.show()


def print_statistics(stats):
    """Prints formatted statistics."""
    print(f"\n{'='*50}")
    print("SIMULATION RESULTS")
    print(f"{'='*50}")
    print(f"Wins:   {stats['wins']:5d} ({stats['win_percentage']:5.2f}%)")
    print(f"Losses: {stats['losses']:5d} ({stats['loss_percentage']:5.2f}%)")
    print(f"Ties:   {stats['ties']:5d} ({stats['tie_percentage']:5.2f}%)")
    print(f"{'-'*50}")
    print(f"Longest win streak:  {stats['longest_win_streak']}")
    print(f"Highest profit:      ${stats['highest_profit']}")
    print(f"Final profit/loss:   ${stats['final_profit']}")
    print(f"{'='*50}\n")


def main():
    """Main function to run the blackjack simulator."""
    print("Welcome to Blackjack Simulator!")
    print("-" * 50)
    
    # Get user input
    num_hands = int(input("How many hands would you like to play? "))
    bet_amount = int(input("How much is being bet per hand? $"))
    
    # Run simulation
    simulator = BlackjackSimulator(num_hands, bet_amount)
    simulator.run_simulation()
    
    # Display results
    stats = simulator.get_statistics()
    print_statistics(stats)
    
    # Plot results with stats embedded
    simulator.plot_results(stats)


if __name__ == "__main__":
    main()

