import random
from pathlib import Path

from otree.api import *

doc = """
BRET - Bomb Risk Elicitation Task <br>
Crosetto, P., & Filippin, A. (2013). The "bomb" risk elicitation task. Journal of Risk and Uncertainty, 47(1), 31–65.
"""
app_name = Path(__file__).parent.name


class C(BaseConstants):
    NAME_IN_URL = 'fcb'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NB_ROWS = 10
    NB_COLS = 10

    BOX_VAL = 0.10  # en euros


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    n_boxes = models.IntegerField(label="Combien de boîtes souhaitez-vous collecter ?", min=0, max=100)
    bomb_box = models.IntegerField(min=0, max=100)
    explode = models.BooleanField()
    payoff_ecu = models.IntegerField()

    def bomb(self):
        self.bomb_box = random.randint(1, 100)
        self.explode = self.n_boxes > self.bomb_box
        self.payoff_ecu = self.n_boxes * (1 - self.explode)
        self.payoff = cu(self.payoff_ecu * C.BOX_VAL)

        txt_final = (f"Vous avez ouvert {self.n_boxes} boîtes. La bombe était dans la boîte {self.bomb_box}. "
                     f"Votre gain est donc de {self.payoff}.")
        self.participant.vars[app_name] = dict(txt_final=txt_final, payoff=self.payoff, n_boxes=self.n_boxes)
        # n_boxes c'est pour le custom_export


# ======================================================================================================================
#
# -- PAGES
#
# ======================================================================================================================
class MyPage(Page):
    @staticmethod
    def js_vars(player: Player):
        return dict(fill_auto=player.session.config.get("fill_auto", False))


class Decision(MyPage):
    form_model = 'player'
    form_fields = ['n_boxes']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant._is_bot = True
            player.n_boxes = random.randint(0, 100)
        player.bomb()


class Result(MyPage):
    @staticmethod
    def js_vars(player: Player):
        existing = MyPage.js_vars(player)
        existing.update(dict(
            n_boxes=player.n_boxes,
            bomb_box=player.bomb_box,
            explode=player.explode,
        ))
        return existing


page_sequence = [Decision, Result]
