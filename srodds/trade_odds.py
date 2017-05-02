from itertools import combinations, combinations_with_replacement
from collections import Counter

sample = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2]


hands = combinations(sample, 5)
trade_totals = [sum(hand) for hand in hands]

occurrences_of_totals = Counter(trade_totals)
occurrences = sum(occurrences_of_totals.values())

odds = {amt: occurrences_of_totals[amt] * 1.0 / occurrences
        for amt in occurrences_of_totals}


# Trade hand events
# 0/1/2/3/4/5


# odds = ...
# {3: 0.027972027972027972,
#  4: 0.1258741258741259,
#  5: 0.2757242757242757,
#  6: 0.3096903096903097,
#  7: 0.1998001998001998,
#  8: 0.056943056943056944,
#  9: 0.003996003996003996}



#######################################
scout = {
    'trade': 1,
    'combat': 0
}

viper = {
    'trade': 0,
    'combat': 1
}

explorer = {
    'trade': 2,
    'combat': 0
}

start_deck = [scout] * 8 + [viper] * 2
######################################






######################
def with_n_explorers(n):
    return start_deck + [explorer] * n

def percentage(deck):
    return {k: round(100 * v, 2) for k, v in get_trade_odds(deck).items()}


k_deck = [{'trade': n} for n in [0, 1, 0, 1, 0, 1, 0, 1, 1, 3, 1, 0, 1, 3, 3, 3, 1]]
w_deck = [{'trade': n} for n in [2, 2, 2, 3, 4, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]]
