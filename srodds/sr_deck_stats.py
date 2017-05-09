###############################################################################
# This only needs to be calculated once at the start of the program
# (This loses usefulness when trying to take 'draw' cards into account)
###############################################################################


def percentify(odds):
    # TODO make results an object with this as a method
    # TODO add methods for summing values matching criteria (at least, within, etc)
    return {k: round(100 * v, 2) for k, v in odds.items()}


class StarRealmsAnalysis(object):
    def __init__(self):
        self.trade = None
        self.damage = None
        self.authority = None

        self.hand_size = None
        self.hand_count = None
        self.bottom = None

        self.scraps = None
        self.discard_scraps = None
        self.starter_scraps = None
        self.starter_discard_scraps = None

        # ...?
