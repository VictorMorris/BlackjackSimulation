import random
import matplotlib.pyplot as plt


ODDS = [49, 42, 9]
EV = -0.07

def main():
    print("Welcome to blackjack")
    
    print("How many hands would you like to play?")
    hands = int(input())
    print("How much is being bet per hand")
    bet = int(input())

    player_total = 0
    hand_result = 0
    result_table_y = []
    hand_table_x = []
    player_result = []
    player_ev = []

    longest_win_streak = 0
    current_win_streak = 0
    highest_profit = 0
    
    for hand in range(hands):
        hand_result = random.random() * 100
        #0-49
        if hand_result <= ODDS[0]:
            player_total -= bet
            player_result.append(-1)
            current_win_streak = 0
        #49-91
        elif ODDS[0] < hand_result <= (ODDS[0] + ODDS[1]):
            player_total += bet
            player_result.append(1)
            current_win_streak += 1

        else:
            player_result.append(0)

        result_table_y.append(player_total)
        hand_table_x.append(hand)
        player_ev.append(EV * bet * hand)

        if result_table_y[-1] > highest_profit:
            highest_profit = result_table_y[-1]

        if current_win_streak > longest_win_streak:
            longest_win_streak = current_win_streak

    wins = player_result.count(1)
    losses = player_result.count(-1)
    ties = player_result.count(0)

    print(f"""Player wins {wins} for a total win percentage of {wins / (wins + losses + ties) * 100}
Player losses {losses} for a total loss percentage of {losses / (wins + losses + ties) * 100}
Player ties {ties} for a total tie percentage of {ties / (wins + losses + ties) * 100}
Players longest win streak was {longest_win_streak}
Players highest profit was {highest_profit}
Player wins a total of {result_table_y[-1]}""")

    plt.plot(hand_table_x, result_table_y)
    plt.plot(hand_table_x, player_ev)
    plt.xlabel("Hands")
    plt.ylabel("Profit")
    plt.title("Blackjack Results")

    plt.show()



    #print(f"Player wins {result} in {hands} hands.")

main()
