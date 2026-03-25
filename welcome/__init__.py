from otree.api import *

author = 'D. DUBOIS'

doc = """
Ecran d'accueil + consentement
"""


class C(BaseConstants):
    NAME_IN_URL = 'welcome'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


class Welcome(Page):
    @staticmethod
    def js_vars(player: Player):
        return dict(
            fill_auto=player.subsession.session.config.get("fill_auto", False)
        )


page_sequence = [Welcome]
