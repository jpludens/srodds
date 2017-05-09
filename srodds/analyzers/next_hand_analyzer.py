from collections import Counter
from itertools import product

from scipy.special import comb
from scipy.stats import hypergeom

from srodds.analyzers.deck_analyzer import StarRealmsDeckStats
from srodds.cards import Abilities, Attributes, Factions


class StarRealmsHandStats(StarRealmsDeckStats):
    """Provides probabilities of events occurring in a deck's next hand."""

    @staticmethod
    def get_size_odds(cardlist):
        # TODO Account for ally draws
        # TODO Account for multiple draws (Mothership, Command Ship)
        # Odds of getting some number of draw cards,
        # times the odds that the final card is not a draw card.

        # Consider all the cards in the hand as the first group,
        # and the last card of the hand as the second group
        draws = [card.get(Abilities.DRAW, 0) for card in cardlist]

        # cards_in_deck = self.N
        draws_in_deck = sum(draws)
        return {
            cards_in_hand:
                # Odds of this number of cards such that exactly 5 do not add draws
                hypergeom(len(cardlist), draws_in_deck, cards_in_hand).pmf(cards_in_hand - 5)
                # Odds that the very last card does not add more draws
                * hypergeom(cards_in_hand, 5, 1).pmf(1)
            for cards_in_hand in range(5, 5 + draws_in_deck + 1)}

    @staticmethod
    def get_ability_odds(ability, cardlist):
        result = {}
        for size_value, p_size in StarRealmsHandStats.get_size_odds(cardlist).items():
            for attr_value, p_attr\
                in StarRealmsHandStats.get_ability_odds_for_hand_size(
                    ability, cardlist, size_value).items():
                p = p_size * p_attr
                try:
                    result[attr_value] += p
                except KeyError:
                    result[attr_value] = p
        return result

    @staticmethod
    def get_ability_odds_for_hand_size(ability, cardlist, hand_size):
        """Return the probabilities of possible totals for an attribute."""

        # Determine odds of trade possibilities across cards with draws
        draw_cards_with_value = Counter([card.get(ability, 0)
                                         for card in cardlist
                                         if card.get(Abilities.DRAW)])
        num_draw_population = sum(draw_cards_with_value.values())
        num_draw_selections = hand_size - 5
        if num_draw_population < num_draw_selections:
            # TODO handle this better
            raise ValueError('Not enough cards to support this hand size.')
        draw_lookup = get_k_val_lookup(draw_cards_with_value, hand_size - 5)
        draw_trade_odds = value_probabilities(ability, draw_lookup, num_draw_population, num_draw_selections)

        # Determine odds of trade possibilities across cards without draws
        dead_cards_with_value = Counter([card.get(ability, 0)
                                         for card in cardlist
                                         if not card.get(Abilities.DRAW)])
        dead_lookup = get_k_val_lookup(dead_cards_with_value, 5)
        num_dead_population = sum(dead_cards_with_value.values())
        dead_trade_odds = value_probabilities(ability, dead_lookup, num_dead_population, 5)

        result = {}
        for pair in product(draw_trade_odds.items(), dead_trade_odds.items()):
            (draw_value, draw_odds), (dead_value, dead_odds) = pair
            try:
                result[draw_value + dead_value] += draw_odds * dead_odds
            except KeyError:
                result[draw_value + dead_value] = draw_odds * dead_odds
        return result

    @staticmethod
    # TODO test against original function. need to construct a deck.
    # TODO Delete next_hand_odds_target_drawn_and_faction_triggered from faction_odds when completes
    def get_trigger_probability(card, cardlist):
        faction = card.get(Attributes.FACTION)
        if not faction:
            return 0

        faction_cards = [other for other in cardlist if other.get(Attributes.FACTION) == faction]
        num_target_copies = len([ally for ally in faction_cards
                                 if ally.get(Attributes.NAME) == card[Attributes.NAME]])
        result = 0
        for hand_size, p_size in StarRealmsHandStats.get_size_odds(cardlist).items():
            p_target = hypergeom(len(cardlist),
                                 num_target_copies,
                                 hand_size).pmf(1)
            p_ally = 1 - hypergeom(len(cardlist) - 1,
                                   len(faction_cards) - num_target_copies,
                                   hand_size - 1).pmf(0)
            result += p_target * p_ally * p_size
        return result


def get_k_val_lookup(value_count, num_picks):
    # TODO instead of this, make a caching wrapper for comb() (???)
    result = {}
    for trade_value, K in value_count.items():
        # Limited by the number we're choosing, as well as the population with this ability value.
        cap = min(K, num_picks)
        for k in range(0, cap + 1):
            k_val = (k, trade_value)
            result[k_val] = comb(K, k)
    return result


# TODO what does this do again? It does something and is used, so name it.
def value_probabilities(ability, lookup, num_population, num_selections):
    # TODO This is pretty magical. Fix it.
    from srodds.cards import Abilities
    potential_ability_values = {
        Abilities.TRADE: [0, 1, 2, 3, 4],
        Abilities.COMBAT: [0, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    distributions = {}
    from itertools import combinations_with_replacement
    for prod in combinations_with_replacement(potential_ability_values[ability], num_selections):
        total = sum(prod)
        count = Counter(prod)
        try:
            distributions[total].append(count)
        except KeyError:
            distributions[total] = [count]
    # End magic

    probabilities = {}
    for total, card_values in distributions.items():
        p_total = 0
        for value_count in card_values:
            numerator_factors = []
            for value, count in value_count.items():
                try:
                    numerator_factors.append(lookup[count, value])
                except KeyError:
                    break
            # Only possible values were calculated for k_val,
            # so if a lookup fails, its odds are 0, which will
            # zero out the entire numerator and then denominator.
            # So we only need to calculate when the above loop
            # does not prematurely terminate.
            else:
                numerator = reduce(lambda x, y: x * y, numerator_factors, 1)
                denominator = comb(num_population, num_selections) * 1.0
                p_card_values = numerator / denominator
                p_total += p_card_values
        if p_total != 0:
            probabilities[total] = p_total
    return probabilities
