from srodds.sr_deck_stats import *

def percentage(deck):
    return {k: round(100 * v, 2) for k, v in StarRealmsHandStats(deck).get_trade_odds().items()}
