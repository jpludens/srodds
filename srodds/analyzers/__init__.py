from itertools import product
from scipy.stats import hypergeom

# from enum import Enum
# class AnalysisScopes(Enum):
#     NEXT_CARD = 0
#     NEXT_HAND = 1
#     REMAINING_HANDS = 2
#     CARDLIST = 3


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
