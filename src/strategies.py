"""Betting strategy implementations."""


class BettingStrategy:
    """Base class for betting strategies."""
    def get_bet_amount(self, base_bet, current_streak, total_profit, hand_number, max_bet):
        raise NotImplementedError
    
    def get_name(self):
        raise NotImplementedError


class FlatBetting(BettingStrategy):
    """Bet the same amount every hand."""
    def get_bet_amount(self, base_bet, current_streak, total_profit, hand_number, max_bet):
        # cap the flat bet just in case user set max lower than base
        return min(base_bet, max_bet)
    
    def get_name(self):
        return "Flat Betting"


class Martingale(BettingStrategy):
    """Double bet after each loss, reset to base after win."""
    def get_bet_amount(self, base_bet, current_streak, total_profit, hand_number, max_bet):
        if current_streak >= 0:
            # positive or zero streak means we won last hand or just started, go back to base
            return min(base_bet, max_bet)
        # negative streak length = how many losses in a row, classic martingale
        bet = base_bet * (2 ** abs(current_streak))
        return min(bet, max_bet)
    
    def get_name(self):
        return "Martingale"


class Fibonacci(BettingStrategy):
    """Follow Fibonacci sequence after losses."""
    def __init__(self):
        # precomputed so we do not keep growing the list mid sim
        self.fib_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    
    def get_bet_amount(self, base_bet, current_streak, total_profit, hand_number, max_bet):
        if current_streak >= 0:
            # on a win or fresh start we reset the ladder
            return min(base_bet, max_bet)
        loss_count = abs(current_streak)
        # do not run off the end if we lose more than we planned for
        fib_index = min(loss_count, len(self.fib_sequence) - 1)
        return min(base_bet * self.fib_sequence[fib_index], max_bet)
    
    def get_name(self):
        return "Fibonacci"


class Paroli(BettingStrategy):
    """Double bet after each win for up to 3 wins, then reset."""
    def __init__(self, max_progression=3):
        # how many steps we are willing to press the win
        self.max_progression = max_progression
    
    def get_bet_amount(self, base_bet, current_streak, total_profit, hand_number, max_bet):
        if current_streak <= 0:
            # lost or neutral, start the press over
            return min(base_bet, max_bet)
        # only press up to the cap so one heater does not go crazy
        progression = min(current_streak, self.max_progression)
        return min(base_bet * (2 ** progression), max_bet)
    
    def get_name(self):
        return "Paroli"


class Progressive(BettingStrategy):
    """Increase bet by 1 unit after win, decrease by 1 after loss."""
    def get_bet_amount(self, base_bet, current_streak, total_profit, hand_number, max_bet):
        if current_streak > 0:
            # n wins in a row bumps the bet by 0.5 base per win
            bet = base_bet + (current_streak * base_bet * 0.5)
        elif current_streak < 0:
            # on losses we step down but do not go below half base
            bet = max(base_bet * 0.5, base_bet + (current_streak * base_bet * 0.5))
        else:
            bet = base_bet
        return min(bet, max_bet)
    
    def get_name(self):
        return "Progressive"