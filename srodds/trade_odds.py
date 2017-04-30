from itertools import combinations, combinations_with_replacement
from collections import Counter
from scipy.misc import comb

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


########### Calculate once at start of program ################################
card_trade_values_by_total = {}

card_trade_values = [0, 1, 2, 3, 4]
card_trade_value_combinations = combinations_with_replacement(card_trade_values, 5)

for prod in card_trade_value_combinations:
    total = sum(prod)
    count = Counter(prod)
    try:
        card_trade_values_by_total[total].append(count)
    except KeyError:
        card_trade_values_by_total[total] = [count]
###############################################################################

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


# Since n-choose-k operations will be repeated frequently,
# create a table for all our ns (total populations of cards with
# a particular trade value) and all our ks (the number of cards with
# a particular trade value we're interested in drawing)
# (Later, modify this to accept defense, authority, damage, draw, etc)
def get_k_val_lookup(deck):
    cards_with_value = Counter([card['trade'] for card in deck])

    k_val_odds = {}
    for trade_value, K in cards_with_value.items():
        # We're limited by the hand size of 5 as well as the total population.
        cap = min(K, 5)
        for k in range(0, cap + 1):
            k_val = (k, trade_value)
            k_val_odds[k_val] = comb(K, k)
    return k_val_odds


def get_trade_odds(deck):
    k_val_lookup = get_k_val_lookup(deck)

    odds_of_trade_totals = {}
    for trade_total, value_counts in card_trade_values_by_total.items():
        odds_of_trade_total = 0
        for value_count in value_counts:
            numerator_factors = []
            for value, count in value_count.items():
                try:
                    numerator_factors.append(k_val_lookup[count, value])
                except KeyError:
                    break
            # Only possible values were calculated for k_val,
            # so if a lookup fails, its odds are 0, which will
            # zero out the entire numerator and then denominator.
            # So we only need to calculate when the above loop
            # does not prematurely terminate.
            else:
                numerator = reduce(lambda x, y: x * y, numerator_factors, 1)
                denominator = comb(len(deck), 5) * 1.0
                odds_of_value_count = numerator / denominator
                odds_of_trade_total += odds_of_value_count
        if odds_of_trade_total != 0:
            odds_of_trade_totals[trade_total] = odds_of_trade_total
    return odds_of_trade_totals


######################
def with_n_explorers(n):
    return start_deck + [explorer] * n
