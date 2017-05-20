"""A small but growing definition of Star Realms card data.
Likely to live in its own project once it becomes big enough."""
from enum import Enum


class Factions(Enum):
    BLOB = 0
    MACHINE_CULT = 1
    STAR_EMPIRE = 2
    TRADE_FEDERATION = 3


class Attributes(Enum):
    NAME = 0
    CARD_TYPE = 1
    FACTION = 2
    COST = 3
    ABILITIES = 4


class CardTypes(Enum):
    SHIP = 0
    BASE = 1


class AbilityTypes(Enum):
    PRIMARY = 0
    ALLY = 1
    SCRAP = 2


class Abilities(Enum):
    AUTHORITY = 0
    TRADE = 1
    COMBAT = 2
    DRAW = 3
    CHOICE = 4


scout = {
    Attributes.NAME: 'Scout',
    Abilities.TRADE: 1,
}

viper = {
    Attributes.NAME: 'Viper',
    Abilities.COMBAT: 1,
}

explorer = {
    Attributes.NAME: 'Explorer',
    Abilities.TRADE: 2,
}

survey_ship = {
    Attributes.NAME: 'Survey Ship',
    Attributes.FACTION: Factions.STAR_EMPIRE,
    Abilities.TRADE: 1,
    Abilities.DRAW: 1,
}

cutter = {
    Attributes.NAME: 'Cutter',
    Attributes.FACTION: Factions.TRADE_FEDERATION,
    Abilities.TRADE: 2,
    Abilities.AUTHORITY: 4
}

federation_shuttle = {
    Attributes.NAME: 'Federation Shuttle',
    Attributes.FACTION: Factions.TRADE_FEDERATION,
    Abilities.TRADE: 2
}

patrol_mech = {
    Attributes.NAME: 'Patrol Mech',
    Attributes.FACTION: Factions.MACHINE_CULT,
    Abilities.CHOICE: [
        {Abilities.TRADE: 3},
        {Abilities.COMBAT: 5}
    ]
}

# I need a draw 1 for tinkering purposes. The rest of these sound fun.
tick = {
    Attributes.NAME: 'Tick',
    Abilities.DRAW: 1
}

dolt = {
    Attributes.NAME: 'Dolt',
}
