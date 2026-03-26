import random
from pathlib import Path

from otree.api import *

from _commons import S2C2H_UM

app_name = Path(__file__).parent.name


class C(BaseConstants):
    NAME_IN_URL = 'fcf'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(
        label="Quel est votre âge ?",
        min=18,
        max=99
    )
    gender = models.StringField(
        label="Quel est votre genre ?",
        choices=[
            ['M', 'Masculin'],
            ['F', 'Féminin'],
            ['NR', 'Préfère ne pas répondre'],
        ],
        widget=widgets.RadioSelect
    )
    education = models.StringField(
        label="Quel est votre diplôme le plus élevé ?",
        choices=[
            ['SD', "Sans diplôme d’études secondaires"],
            ['DS', "Diplôme d’études secondaires (CAP, BEP, Bac)"],
            ['B2', "Bac +2 (BTS, DUT, etc.)"],
            ['L', "Licence (Bac +3)"],
            ['M', "Master (Bac +5)"],
            ['D', "Doctorat ou diplôme supérieur"],
        ],
        widget=widgets.RadioSelect
    )
    niveaudevie = models.IntegerField(
        min=0,
        max=10,
        label="Concernant votre pouvoir d'achat, vous vous situeriez parmi :"
    )
    income = models.StringField(
        label="Quel est approximativement votre revenu mensuel net (avant impôts) ?",
        choices=[
            ['1', "Moins de 1100 €"],
            ['2', "Entre 1100 € et 1899 €"],
            ['3', "Entre 1900 € et 2299 €"],
            ['4', "Entre 2300 € et 3099 €"],
            ['5', "Entre 3100 € et 3999 €"],
            ['6', "Entre 4000 € et 6499 €"],
            ['7', "Plus de 6500 €"],
            ['NR', "Préfère ne pas répondre"],
        ],
        widget=widgets.RadioSelect
    )
    status = models.StringField(
        label="5. Quel est votre statut socioprofessionnel ?",
        choices=[
            ['ETU', "Étudiant.e"],
            ['SAL', "Salarié.e"],
            ['AGR', "Agriculteur.rice"],
            ['ACE', "Artisan.e, commerçant.e, entrepreneur.e"],
            ['CPI', "Cadres / Profession intellectuelle supérieure"],
            ['RET', "Retraité.e"],
            ['CHO', "En recherche d’emploi"],
            ['SANS', "Sans activité professionnelle"],
            ['NR', "Préfère ne pas répondre"],
        ],
        widget=widgets.RadioSelect
    )

    def compute_final_payoff(self):
        payoff_haies = self.participant.vars.get("FC_haies", {}).get("payoff", cu(0))
        payoff_bret = self.participant.vars.get("FC_bret", {}).get("payoff", cu(0))
        self.payoff = payoff_haies + payoff_bret
        self.participant.payoff = self.payoff
        txt_final = (
            f"Votre gain pour l'expérience est de {self.participant.payoff}. <br>"
            f"Avec le forfait de déplacement cela fait un total de {self.participant.payoff_plus_participation_fee()}."
        )
        self.participant.vars[app_name] = dict(txt_final=txt_final, payoff=self.participant.payoff)


# ======================================================================================================================
#
# --- PAGES ---
#
# ======================================================================================================================

class MyPage(Page):
    @staticmethod
    def vars_for_templates(player: Player):
        return dict()

    @staticmethod
    def js_vars(player: Player):
        return dict(
            fill_auto=player.session.config.get("fill_auto", False),
        )


class Demographics(MyPage):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'income', 'status']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.age = random.randint(18, 99)
            player.gender = random.choice(['M', 'F', 'NR'])
            player.education = random.choice(['SD', 'DS', 'B2', 'L', 'M', 'D'])
            player.income = random.choice(list(map(str, range(1, 8))) + ['NR'])
            player.status = random.choice(['ETU', 'SAL', 'AGR', 'ACE', 'CPI', 'RET', 'CHO', 'SANS', 'NR'])
        # pour custom_export
        player.participant.vars['demog'] = {field: getattr(player, field) for field in Demographics.form_fields}
        player.compute_final_payoff()


class Final(MyPage):
    template_name = "global/final.html"

    # template_name = "global/final_s2c2h.html"

    @staticmethod
    def is_displayed(player: Player):
        return {"FC_haies", "FC_bret"}.issubset(player.session.config["app_sequence"])

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            final_template="FC_final/Final.html",
        )

    @staticmethod
    def js_vars(player: Player):
        existing = MyPage.js_vars(player)
        if Final.template_name == "global/final_s2c2h.html":
            existing.update(
                devis_id=S2C2H_UM,
                subject_id=f"{S2C2H_UM}_{player.session.code}_{player.participant.code}",
                subject_payoff=player.participant.payoff_plus_participation_fee()
            )
        return existing


page_sequence = [Demographics, Final]
