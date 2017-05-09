from srodds.analyzers import GeneralStarRealmsDeckStats


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