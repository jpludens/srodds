from scipy.misc import comb
from scipy.stats import hypergeom
from itertools import combinations_with_replacement, product
from collections import Counter


###############################################################################
# This only needs to be calculated once at the start of the program
# (This loses usefulness when trying to take 'draw' cards into account)
card_trade_values_by_total = {}

card_trade_values = [0, 1, 2, 3, 4]
card_trade_value_combinations = combinations_with_replacement(
    card_trade_values, 5)

for prod in card_trade_value_combinations:
    total = sum(prod)
    count = Counter(prod)
    try:
        card_trade_values_by_total[total].append(count)
    except KeyError:
        card_trade_values_by_total[total] = [count]
###############################################################################


class GeneralStarRealmsDeckStats(object):
    # Currently excludes bottom-decked cards from consideration
    """Provides functions for probabilities of events about a Star Realms
    deck that fits some pattern, but not any particular deck."""

    @staticmethod
    def ally_abilities_triggered(deck_size, number_in_faction):
        """Provide the probabilities that possible total numbers of ally
        abilities will be triggered given deck and faction size."""
        # Get the various distributions of faction cards across 5-card hands.
        # Account for the bottom-deck by excluding distributions whose f-count
        # exceeds the expected size of the bottom deck, then exclude the
        # bottom-deck itself from the final counts.
        number_of_full_hands = deck_size / 5
        bottom_hand_size = deck_size % 5
        faction_distributions = [dist[:-1] for dist
                                 in product(range(0, 6), repeat=number_of_full_hands + 1)
                                 if sum(dist) == number_in_faction and dist[-1] <= bottom_hand_size]

        # Determine the odds of each faction distribution. Fairly straightforward:
        # Starting at 1, keep multiplying the odds so far by the odds of drawing
        # the next count, given the changing hypergeometric distributions.
        faction_distribution_odds = {}
        for f_dist in faction_distributions:
            odds = 1
            number_of_previous_hands = 0
            number_of_previous_faction_cards = 0
            for f in f_dist:
                odds *= hypergeom(
                    deck_size - number_of_previous_hands * 5,
                    number_in_faction - number_of_previous_faction_cards,
                    5).pmf(f)
                number_of_previous_hands += 1
                number_of_previous_faction_cards += f
            faction_distribution_odds[f_dist] = odds

        # Determine total abilities triggered by each faction distribution.
        # Sum the probabilities of each possible total.
        abilities_triggered_by_faction_count = {
            0: 0,
            1: 0,
            2: 2,
            3: 3,
            4: 4,
            5: 5
        }
        result = {}
        for f_dist, prob in faction_distribution_odds.items():
            number_of_abilities_triggered = sum(
                [abilities_triggered_by_faction_count[f]
                 for f in f_dist])
            try:
                result[number_of_abilities_triggered] += prob
            except KeyError:
                result[number_of_abilities_triggered] = prob
        return result


class StarRealmsDeckStats(object):
    """Provides probabilities of events occurring in ANY full hand of a deck.
     Bottom-decked cards are ignored."""
    def __init__(self, deck):
        self.deck = list(deck)
        self.N = len(deck)

    def attribute_vector(self, attribute):
        return [card[attribute] for card in self.deck]

    def attribute_value_count(self, attribute, value):
        return len([card for card in self.deck
                    if card[attribute] == value])

    def ally_abilities_triggered(self, faction):
        return GeneralStarRealmsDeckStats.ally_abilities_triggered(
            self.N, self.attribute_value_count('faction', faction))


class StarRealmsHandStats(StarRealmsDeckStats):
    """Provides probabilities of events occurring in a deck's next hand."""

    def get_trade_odds(self):
        """Return the probabilities of possible trade values."""
        cards_with_value = Counter(self.attribute_vector('trade'))

        # TODO instead of this, make a caching wrapper for comb()
        k_val_lookup = {}
        for trade_value, K in cards_with_value.items():
            # We're limited by the hand size of 5 as well as the total population.
            cap = min(K, 5)
            for k in range(0, cap + 1):
                k_val = (k, trade_value)
                k_val_lookup[k_val] = comb(K, k)

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
