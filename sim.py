import random
import matplotlib.pyplot as plt


odds = [49, 42, 9]

def main():
    print("Welcome to blackjack")
    
    print("How many hands would you like to play?")
    hands = int(input())
    print("How much is being bet per hand")
    bet = int(input())

    player_total = 0
    result = 0
    result_table = []
    hands_table = []
    for hand in range(hands):
        result = random.random() * 100
        #0-49
        if result <= odds[0]:
            player_total -= bet
        #49-91
        elif odds[0] < result <= odds[0] + odds[1]:
            player_total += bet

        result_table.append(player_total)
        hands_table.append(hand)

    plt.plot(hands_table, result_table)
    plt.xlabel("Hands")
    plt.ylabel("Profit")
    plt.title("Blackjack Results")

    plt.show()



    #print(f"Player wins {result} in {hands} hands.")

main()
