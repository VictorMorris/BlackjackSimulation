"""Core blackjack simulation engine."""

import numpy as np
from constants import (
    WIN_PROBABILITY, 
    LOSS_PROBABILITY, 
    EXPECTED_VALUE_PER_DOLLAR
)


class BlackjackSimulator:
    """Simulates multiple hands of blackjack and tracks statistics."""
    
    def __init__(self, num_hands, base_bet, max_bet, strategy):
        self.num_hands = num_hands
        self.base_bet = base_bet
        self.max_bet = max_bet
        self.strategy = strategy
        
        # running totals and history so we can plot and compute stats later
        self.total_profit = 0
        self.hand_results = []          # -1 loss, 0 tie, 1 win
        self.profit_history = []        # bankroll over time
        self.bet_history = []           # actual dollars risked each hand
        self.expected_value_history = []  # model EV line using actual bet sizes
        
        # streak and extrema tracking for the dashboard
        self.longest_win_streak = 0
        self.current_win_streak = 0
        self.longest_loss_streak = 0    # store as negative for convenience
        self.current_loss_streak = 0
        self.highest_profit = 0         # best point hit
        self.lowest_profit = 0          # worst drawdown
        
        self.current_hand = 0
        self.is_running = False
    
    def play_hand(self):
        """Simulates a single hand of blackjack using numpy."""
        # super simple outcome model, not real rules
        outcome = np.random.random()
        
        if outcome <= WIN_PROBABILITY:
            return -1  # Loss  - probabilities are inverted to make EV negative on average
        elif outcome <= WIN_PROBABILITY + LOSS_PROBABILITY:
            return 1   # Win
        else:
            return 0   # Tie
    
    def update_statistics(self, result, bet_amount):
        """Updates running statistics based on hand result."""
        # profit update and streak bookkeeping
        if result == -1:  # Loss
            self.total_profit -= bet_amount
            self.current_win_streak = 0
            self.current_loss_streak -= 1
        elif result == 1:  # Win
            self.total_profit += bet_amount
            self.current_win_streak += 1
            self.current_loss_streak = 0
        # ties keep streaks as is
        
        # time series for the plot and later metrics
        self.hand_results.append(result)
        self.profit_history.append(self.total_profit)
        self.bet_history.append(bet_amount)

        # expected value line accumulates using the same bet sizing used by the strategy
        if len(self.expected_value_history) == 0:
            cumulative_ev = EXPECTED_VALUE_PER_DOLLAR * bet_amount
        else:
            cumulative_ev = self.expected_value_history[-1] + (EXPECTED_VALUE_PER_DOLLAR * bet_amount)
        self.expected_value_history.append(cumulative_ev)

        # highs and lows so we can show peaks and drawdowns
        if self.total_profit > self.highest_profit:
            self.highest_profit = self.total_profit
        
        if self.total_profit < self.lowest_profit:
            self.lowest_profit = self.total_profit
        
        if self.current_win_streak > self.longest_win_streak:
            self.longest_win_streak = self.current_win_streak
        
        if self.current_loss_streak < self.longest_loss_streak:
            self.longest_loss_streak = self.current_loss_streak
    
    def run_single_hand(self):
        """Runs a single hand and returns if simulation should continue."""
        if self.current_hand >= self.num_hands:
            return False
        
        # pass a signed streak value to strategies so they know win vs loss momentum
        result = self.play_hand()
        bet_amount = self.strategy.get_bet_amount(
            self.base_bet, 
            self.current_win_streak if self.current_win_streak > 0 else self.current_loss_streak,
            self.total_profit,
            self.current_hand,
            self.max_bet
        )
        self.update_statistics(result, bet_amount)
        self.current_hand += 1
        
        return True
    
    def run_all_hands(self):
        """Runs all hands instantly without animation."""
        # faster path when you do not need to watch it happen
        while self.current_hand < self.num_hands:
            self.run_single_hand()
    
    def get_statistics(self):
        """Calculates and returns game statistics."""
        wins = self.hand_results.count(1)
        losses = self.hand_results.count(-1)
        ties = self.hand_results.count(0)
        total_hands = len(self.hand_results)
        
        if total_hands == 0:
            return None
        
        # bundle everything the UI needs so it does not recompute
        return {
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'win_percentage': (wins / total_hands) * 100,
            'loss_percentage': (losses / total_hands) * 100,
            'tie_percentage': (ties / total_hands) * 100,
            'longest_win_streak': self.longest_win_streak,
            'longest_loss_streak': abs(self.longest_loss_streak),
            'highest_profit': self.highest_profit,
            'lowest_profit': self.lowest_profit,
            'final_profit': self.total_profit,
            'total_bet': sum(self.bet_history),
            'avg_bet': np.mean(self.bet_history) if self.bet_history else 0,
            'max_bet_used': max(self.bet_history) if self.bet_history else 0
        }