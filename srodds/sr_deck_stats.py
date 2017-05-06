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
        return [card.get(attribute, 0) for card in self.deck]

    def attribute_value_count(self, attribute, value):
        return len([card for card in self.deck
                    if card.get(attribute, 0) == value])

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
                    denominator = comb(self.N, 5) * 1.0
                    odds_of_value_count = numerator / denominator
                    odds_of_trade_total += odds_of_value_count
            if odds_of_trade_total != 0:
                odds_of_trade_totals[trade_total] = odds_of_trade_total
        return odds_of_trade_totals

    def f(self):
        # Odds of getting some number of draw cards,
        # times the odds that the final card is not a draw card.

        # Consider the first n-1 cards as the "hand",
        # and the final card as the first card in the rest of the deck.
        draws = self.attribute_vector('draw')

        cards_in_deck = self.N
        draws_in_deck = sum(draws)
        return {
            cards_in_hand: (
                [cards_in_deck, draws_in_deck, cards_in_hand - 1, cards_in_hand - 5],
                hypergeom(
                    cards_in_deck,
                    draws_in_deck,
                    cards_in_hand - 1)
                .pmf(cards_in_hand - 5),
                [cards_in_deck - cards_in_hand + 1,
                 cards_in_deck - draws_in_deck - 4,
                 1,
                 1],
                hypergeom(
                    cards_in_deck - cards_in_hand + 1,
                    cards_in_deck - draws_in_deck - 4,
                    1)
                .pmf(1)
            )
            for cards_in_hand in range(5, 5 + draws_in_deck + 1)}

    def g(self):
        # Odds of getting some number of draw cards,
        # times the odds that the final card is not a draw card.

        # Consider all the cards in the hand as the first group,
        # and the last card of the hand as the second group
        draws = self.attribute_vector('draw')

        cards_in_deck = self.N
        draws_in_deck = sum(draws)
        return {
            cards_in_hand: (
                [cards_in_deck, draws_in_deck, cards_in_hand, cards_in_hand - 5],
                hypergeom(
                    cards_in_deck,
                    draws_in_deck,
                    cards_in_hand)
                .pmf(cards_in_hand - 5),
                [cards_in_hand, 5, 1, 1],
                hypergeom(cards_in_hand, 5, 1)
                .pmf(1)
            )
            for cards_in_hand in range(5, 5 + draws_in_deck + 1)}

    def calc(self, result):
        return {s: result[s][1] * result[s][3] for s in result}

    def size_odds(self):
        draws = self.attribute_vector('draw')

        possible_sizes = range(5, 5 + sum(draws) + 1)

        def f(draws, hits, hits_left):
            if hits_left == 0:
                pass

            hypergeom(self.N, sum(draws), 5).pmf(size - 5)

        # odds that the bonus draws become bonus draws...
        # drew: 5
        # draw: 2

        def odds_of_bonus_draws(pool, draws, hits):
            return {d: hypergeom(pool, hits, draws).pmf(d)
                    for d in range(max(0, hits + draws - pool), min(hits, draws) + 1)}

        # odds of any particular number need to be multipied by the odds that its extra draws do not yield further additional draws
        # odds of any particular number need to be adjust upward by adding the odds of lower ones yielding it via additional draws




        # use sum(draws) for now. works for representing all primary draw 1s.
        # does NOT represent command ship's draw 2
        # does NOT represent ally draws
        return {size: hypergeom(self.N, sum(draws), 5).pmf(size - 5)
                for size in possible_sizes}
