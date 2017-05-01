import numpy
from scipy.stats import hypergeom
from itertools import product

dist_all = hypergeom(12, 3, 5)

dist_target_card = hypergeom(12, 1, 5)
dist_non_target = hypergeom(12, 11, 5)

dist_non_target_faction = hypergeom(12, 2, 5)
dist_non_target_non_faction = hypergeom(12, 9, 5)

dist_faction_except_target = hypergeom(11, 2, 4)


class NextHandOdds:
    pass


def next_hand_odds_target_drawn_and_faction_triggered(D, F):
    odds_of_target = hypergeom(D, 1, 5).pmf(1)
    odds_of_any_faction = 1 - hypergeom(D-1, F, 4).pmf(0)
    return odds_of_target * odds_of_any_faction


def next_hand_odds_trigger_made_impossible(D, F):
    p_target_except_allies = hypergeom(D, 1, 5).pmf(1) * hypergeom(D-1, F, 4).pmf(0)
    p_allies_except_target = hypergeom(D, 1, 5).pmf(0) * hypergeom(D-1, F, 5).pmf(F)
    print p_target_except_allies, p_allies_except_target
    return p_target_except_allies + p_allies_except_target


def second_next_hand_odds_target_drawn_and_faction_triggered(D, F):
    # Turns out, (obviously, in retrospect) that this is
    # equal to chance of this event in the first hand.
    p_target_remains = hypergeom(D, 1, 5).pmf(0)
    p_f_removed = hypergeom(D-1, F, 5).pmf(numpy.arange(0, 6))
    p_f_remain = [p_f_removed[F-f] for f in numpy.arange(0, 6)]

    odds_of_hit_with_f_remaining = []
    for f, pf in enumerate(p_f_remain):
        print f, pf, pf * p_target_remains
        odds_of_hit_with_f_remaining.append(
            p_target_remains *
            pf *
            next_hand_odds_target_drawn_and_faction_triggered(D - 5, f)
        )
    print odds_of_hit_with_f_remaining

    return sum(odds_of_hit_with_f_remaining)


def hands_this_cycle_odds_target_drawn_and_faction_triggered(D, F):
    # If there are fewer than 5 cards, we're facing a cycle
    # (Unless there there aren't any cards in discard, but ignore that for now)
    if D < 5:
        return 0

    # Base case: This is the last hand before a cycle
    if D < 10:
        return next_hand_odds_target_drawn_and_faction_triggered(D, F)

    else:
        pass
        # return odds of making it this hand
        # append:
        # sum of odds of not making and drawing Fthis * hands_this_cycle(D, F-Fthis) from 0 tto F
    return


# if __name__ == '__main__':
#     def next_hand_odds_target_not_drawn_k_allies_not_drawn(D, F, k):
#         pass
#     pass


###############################################################################
# Odds of triggering f ally abilities in a deck with F cards of a faction
# Return the odds of triggering numbers of faction abilities across FULL hands.
# (This excludes bottom-decked cards.)
def ally_ability_odds(deck, number_in_faction):
    # Get the various distributions of faction cards across 5-card hands.
    # Account for the bottom-deck by excluding distributions whose f-count
    # exceeds the expected size of the bottom deck, then exclude the
    # bottom-deck itself from the final counts.
    number_of_full_hands = len(deck) / 5
    bottom_hand_size = len(deck) % 5
    faction_distributions = [dist[:-1] for dist
                             in product(range(0, 6), repeat=number_of_full_hands+1)
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
                len(deck) - number_of_previous_hands * 5,
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
