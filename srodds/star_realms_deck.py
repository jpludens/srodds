from srodds.cards import *


class StarRealmsDeck(object):
    @staticmethod
    def make_start_deck():
        return StarRealmsDeck([scout] * 8 + [viper] * 2)

    @staticmethod
    def make_empty_deck():
        return StarRealmsDeck([])

    def __init__(self, cardlist):
        self.cardlist = cardlist
        self.deck = list(cardlist)

    def copy_with(self, cards):
        return StarRealmsDeck(self.cardlist + cards)

    def copy_with_explorers(self, num_explorers):
        return StarRealmsDeck(self.cardlist + explorer * num_explorers)

