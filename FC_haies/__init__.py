import itertools
import json
import random
from pathlib import Path

from otree.api import *

from .understanding import get_understanding

app_name = Path(__file__).parent.name

doc = """
Enchères.
"""


# =====================================================
# CONSTANTS
# =====================================================
class C(BaseConstants):
    NAME_IN_URL = "fch"
    PLAYERS_ZONE_1 = 3
    PLAYERS_ZONE_2 = 2
    PLAYERS_PER_GROUP = PLAYERS_ZONE_1 + PLAYERS_ZONE_2
    NUM_ROUNDS = 12
    NUM_PAID_ROUNDS = 9
    COST_MIN = 50
    COST_MAX = 100
    BUYER_BUDGET = 200
    DIVISION_PAYOFF = 3

    # Valeur créée dans UNE zone selon nb d’unités dans la zone
    VALUES = {1: 100, 2: 250, 3: 375}

    TREATMENT_COMB = 'combinatoire'
    TREATMENT_UNIT = 'unitaire'
    TREATMENT_BASE = 'base'


# ======================================================================================================================
#
# METHODES
#
# ======================================================================================================================

def make_balanced_cost_schedule(random_gen):
    # on répartit l'espace 50-100 en 3 intervalles (bins) : 50..66, 67..83, 84..100
    bins = [range(50, 67), range(67, 84), range(84, 101)]

    # nb de valeurs par intervalle et nb valeurs restantes
    nb_par_interval, reste = divmod(C.NUM_ROUNDS, 3)
    counts = [nb_par_interval] * 3  # stocke le nb de valeurs pour chaque intervalle

    # on complète en ajoutant éventuellement des valeurs aux intervalles (selection aléatoire)
    # pour chaque reste, on tire au hasard dans quel intervalle sélectionner la valeur
    for k in random_gen.sample(range(3), reste):
        counts[k] += 1  # un nb de plus à tirer dans cet intervalle

    schedule = []
    for b_range, cnt in zip(bins, counts):  # (intervalle, nb_valeurs à tirer)
        schedule.extend(random_gen.choices(b_range, k=cnt))

    random_gen.shuffle(schedule)
    return schedule


# =====================================================
# MODELS
# =====================================================
class Subsession(BaseSubsession):
    treatment = models.StringField()
    numsession = models.IntegerField()
    seed = models.IntegerField()


def creating_session(subsession: Subsession):
    subsession.treatment = subsession.session.config.get("treatment", C.TREATMENT_COMB)
    subsession.numsession = subsession.session.config.get("numsession", 0)
    subsession.seed = subsession.session.config.get("seed", 0)

    if subsession.round_number == 1:
        subsession.session.vars["understanding"] = get_understanding()
        subsession.group_randomly()  # formation aléatoire des groupes

    groups = subsession.get_groups()
    players = subsession.get_players()

    # générateurs aléatoires groupes
    for group in groups:
        if group.round_number == 1:
            # pour les zones
            rng_zone = random.Random(
                f"seed={subsession.seed}|numsession={subsession.numsession}|group={group.id_in_subsession}|zones")
            group.session.vars[f"g{group.id_in_subsession}_rng_zone"] = rng_zone
            # pour les exaequo
            rng_tie = random.Random(
                f"seed={subsession.seed}|numsession={subsession.numsession}|group={group.id_in_subsession}|tie")
            group.session.vars[f"g{group.id_in_subsession}_rng_tie"] = rng_tie

    # préparation players
    for p in players:
        if p.round_number == 1:
            rng_cost = random.Random(
                f"seed={subsession.seed}|numsession={subsession.numsession}|id={p.id_in_subsession}|costs")
            p.participant.vars["cost_schedule"] = make_balanced_cost_schedule(
                random_gen=rng_cost)  # génération des coûts
            rnd_paid = random.Random(
                f"seed={subsession.seed}|numsession={subsession.numsession}|id={p.id_in_subsession}|paid")
            p.participant.vars["paid_rounds"] = rnd_paid.sample(range(1, C.NUM_ROUNDS + 1), C.NUM_PAID_ROUNDS)
        p.cost = p.participant.vars["cost_schedule"][subsession.round_number - 1]
        p.paid_round = p.round_number in p.participant.vars["paid_rounds"]

    # affectation des zones
    for g in groups:
        rng_zone = subsession.session.vars[f"g{g.id_in_subsession}_rng_zone"]
        g_players = g.get_players()
        zone1_players = rng_zone.sample(g_players, 3)
        for p in g_players:
            p.zone = 1 if p in zone1_players else 2
        g.zone_assignment_json = json.dumps({p.id_in_group: p.zone for p in g_players})


class Group(BaseGroup):
    units_bought = models.IntegerField(initial=0)
    total_spent = models.IntegerField(initial=0)
    total_value = models.IntegerField(initial=0)
    W = models.FloatField(initial=0)

    # stockage JSON (évite eval/str)
    chosen_info_json = models.LongStringField()
    zone_assignment_json = models.LongStringField()

    # stockage nombre d'unités par zone
    z1_units = models.IntegerField(initial=0)
    z2_units = models.IntegerField(initial=0)
    choice_type = models.StringField()

    def compute_round_payoffs(self):
        players = self.get_players()
        treatment = self.subsession.treatment
        budget = C.BUYER_BUDGET

        # indices des joueurs de chaque zone dans la liste des joueurs du groupe
        z1_indices = [i for i, p in enumerate(players) if p.zone == 1]
        z2_indices = [i for i, p in enumerate(players) if p.zone == 2]
        # =========================================================
        # Préparation des capacités (Ranges)
        # =========================================================
        # si base le programme peut acheter 0 ou 1 unité à chaque joueur
        if treatment == C.TREATMENT_BASE:
            ranges = [range(2)] * C.PLAYERS_PER_GROUP
        else:
            # le programme peut acheter 0, 1, 2 ou 3 unités à chaque joueur si c'est la zone 1 et 0, 1 ou 2 unités
            # à chaque joueur si zone 2
            ranges = [range(4) if i in z1_indices else range(3) for i in range(len(players))]

        # =========================================================
        # Recherche des combinaisons valides
        # - la somme des unités achetées dans chaque zone ne dépasse pas la capacité de la zone (3 en zone 1, 2 en zone 2)
        # - la somme ne dépasse pas le budget (C.BUYER_BUDGET)
        # =========================================================
        valid_combos = []
        # itertools.product(*ranges) génère le produit cartésien des ranges, soit toutes les combinaisons possibles
        # de quantités pour les 5 joueurs
        for qs in itertools.product(*ranges):
            # sommes des quantités en zone 1 et en zone 2
            z1_q = sum(qs[i] for i in z1_indices)
            z2_q = sum(qs[i] for i in z2_indices)

            # Filtre 1 : Capacité des zones
            if z1_q > 3 or z2_q > 2:
                continue

            # Filtre 2 : Respect du budget - on récupère les prix proposés par chaque joueur et on multiplie par les
            # quantités que pourrait acheter le programme informatique
            cost = sum(q * p.get_unit_price(q) for p, q in zip(players, qs) if q > 0)
            if cost > budget:
                continue

            # Calcul de la valeur et de W
            val = (C.VALUES[z1_q] if z1_q > 0 else 0) + (C.VALUES[z2_q] if z2_q > 0 else 0)
            w = val / cost if cost > 0 else 0

            # On stocke le résultat de cette combinaison valide pour pouvoir comparer ensuite les différentes
            # combinaisons valides entre elles
            valid_combos.append({
                'W': w, 'val': val, 'cost': cost, 'qs': qs, 'z1_q': z1_q, 'z2_q': z2_q
            })

        # =========================================================
        # 4. Sélection du gagnant et Enregistrement
        # =========================================================
        if not valid_combos:
            # Si aucune offre n'est possible (tout le monde est hors budget)
            self.units_bought = self.total_spent = self.total_value = self.W = self.z1_units = self.z2_units = 0
            self.chosen_info_json = json.dumps({p.id_in_group: 0 for p in players})
            for p in players:
                p.units_sold = p.unit_price_used = 0
                p.earnings = p.payoff = cu(0)
            return

        # On trouve le meilleur score (Priorité 1: W, Priorité 2: Valeur)
        max_score = max(valid_combos, key=lambda x: (x['W'], x['val']))
        # ex-aequo éventuels (si len(ties) > 1)
        ties = [c for c in valid_combos if (c['W'], c['val']) == (max_score['W'], max_score['val'])]
        rng_tie = self.session.vars[f"g{self.id_in_subsession}_rng_tie"]
        best = rng_tie.choice(ties)

        # Enregistrement des données de l'Acheteur (Groupe)
        self.units_bought = sum(best['qs'])
        self.total_spent = best['cost']
        self.total_value = best['val']
        self.W = best['W']
        self.z1_units = best['z1_q']
        self.z2_units = best['z2_q']

        # Enregistrement des données Vendeurs (Joueurs)
        chosen_map = {}
        for p, q in zip(players, best['qs']):
            chosen_map[p.id_in_group] = q
            p.units_sold = q
            if q > 0:
                up = p.get_unit_price(q)
                p.unit_price_used = up
                p.payoff = cu(q * (up - p.cost))
            else:
                p.unit_price_used = 0
                p.payoff = cu(0)
        self.chosen_info_json = json.dumps(chosen_map)


class Player(BasePlayer):
    zone = models.IntegerField()
    cost = models.IntegerField()
    # cost_schedule_json = models.LongStringField(initial='', blank=True)
    decision_imputed = models.BooleanField(initial=False)

    # ====== Questionnaire compréhension =====
    q1_faults = models.IntegerField()
    q2_faults = models.IntegerField()
    q3_faults = models.IntegerField()
    q4_faults = models.IntegerField()
    q5_faults = models.IntegerField()
    q6_faults = models.IntegerField()
    q7_faults = models.IntegerField()
    q8_faults = models.IntegerField()
    total_faults = models.IntegerField(initial=0)

    # ===== Traitement COMBINATOIRE (menus par lots) =====
    offer_1u_zone1 = models.IntegerField(max=C.BUYER_BUDGET)
    offer_2u_zone1 = models.IntegerField(max=C.BUYER_BUDGET)
    offer_3u_zone1 = models.IntegerField(max=C.BUYER_BUDGET)

    offer_1u_zone2 = models.IntegerField(max=C.BUYER_BUDGET)
    offer_2u_zone2 = models.IntegerField(max=C.BUYER_BUDGET)

    # ===== Traitement UNITAIRE (1 prix unitaire par zone) et BASE =====
    unit_price_zone1 = models.IntegerField(max=C.BUYER_BUDGET)
    unit_price_zone2 = models.IntegerField(max=C.BUYER_BUDGET)

    # résultats
    units_sold = models.IntegerField(initial=0)
    unit_price_used = models.IntegerField(initial=0)  # pour affichage (prix unitaire effectivement appliqué)
    earnings = models.CurrencyField(initial=cu(0))
    paid_round = models.BooleanField(doc="True si le round compte pour le gain final ou non")

    # gains finaux
    auction_total_payoff_points = models.FloatField()
    auction_total_payoff_euros = models.FloatField()
    auction_paying_rounds_str = models.StringField()
    auction_total_payoff_before_division = models.FloatField()

    def get_unit_price(self, quantity):
        """
        Retourne le prix unitaire applicable pour ce vendeur.
        - traitement combinatoire: dépend de la quantité (menu)
        - traitement unitaire: ne dépend pas de la quantité (prix unique par zone)
        """
        if quantity == 0:
            return 0  # sécuritié

        if self.subsession.treatment in (C.TREATMENT_UNIT, C.TREATMENT_BASE):
            return self.unit_price_zone1 if self.zone == 1 else self.unit_price_zone2
        else:  # traitement combinatoire
            if self.zone == 1:
                return {1: self.offer_1u_zone1, 2: self.offer_2u_zone1, 3: self.offer_3u_zone1}[quantity]
            else:
                return {1: self.offer_1u_zone2, 2: self.offer_2u_zone2}[quantity]

    def compute_final_payoff(self):
        historique = []
        for p in self.in_all_rounds():
            historique.append({
                'round': p.round_number,
                'zone': p.zone,
                'cost': p.cost,
                'units_sold': p.units_sold,
                'unit_price_used': p.unit_price_used,
                'payoff': p.payoff,
                'paid_round': p.paid_round
            })
        payoff_before_division = cu(sum(p.payoff for p in self.in_all_rounds() if p.paid_round))
        self.participant.payoff = cu(payoff_before_division / C.DIVISION_PAYOFF)
        txt_final = (
            f"Votre gain total pour les {C.NUM_PAID_ROUNDS} périodes tirées au sort est de "
            f"{payoff_before_division}. <br>"
            f"Votre gain total pour la partie 1 de l'expérience est donc de {payoff_before_division} / "
            f"{C.DIVISION_PAYOFF}, soit {self.participant.payoff}.")
        self.participant.vars[app_name] = dict(
            txt_final=txt_final,
            payoff_before_division=payoff_before_division,
            payoff=self.participant.payoff,
            historique=historique
        )


def unit_price_zone1_min(player: Player):
    return player.cost


def unit_price_zone2_min(player: Player):
    return player.cost


# ======================================================================================================================
#
# PAGES
#
# ======================================================================================================================
class MyPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        treatment = player.subsession.treatment
        return dict(
            is_comb=(treatment == 'combinatoire'),
            is_unit=(treatment == 'unitaire'),
            is_base=(treatment == 'base'),
            instructions_template=f"{app_name}/Instructions.html",
            instructions_template_title="Partie 1"
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            fill_auto=player.session.config.get('fill_auto', False),
            **C.__dict__.copy()
        )


class Intro(MyPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions(MyPage):
    template_name = "global/instructions.html"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class InstructionsWaitMonitor(MyPage):
    template_name = "global/instructions_wait_monitor.html"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and not player.session.config.get("test", False)


class InstructionsWaitForAll(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.session.config.get("test", False)


class Understanding(MyPage):
    template_name = "global/understanding.html"
    form_model = "player"

    @staticmethod
    def get_form_fields(player):
        comp = player.session.vars["understanding"]
        return [f"q{i}_faults" for i in range(1, len(comp) + 1)]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        existing = MyPage.vars_for_template(player)
        existing.update(understanding=player.session.vars["understanding"])
        return existing

    @staticmethod
    def js_vars(player: Player):
        existing = MyPage.js_vars(player)
        existing.update(understanding=player.session.vars["understanding"])
        return existing

    @staticmethod
    def before_next_page(player, timeout_happened):
        comp = player.session.vars["understanding"]
        if timeout_happened:
            for q in comp:
                setattr(player, f"q{q['id']}_faults", random.randint(0, len(q['propositions']) - 1))
        player.total_faults = sum(getattr(player, f"q{i}_faults") for i in range(1, len(comp) + 1))


class UnderstandingWaitForAll(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Decision(MyPage):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        if player.subsession.treatment in [C.TREATMENT_UNIT, C.TREATMENT_BASE]:
            return ['unit_price_zone1', 'unit_price_zone2']
        return [
            'offer_1u_zone1', 'offer_2u_zone1', 'offer_3u_zone1',
            'offer_1u_zone2', 'offer_2u_zone2',
        ]

    @staticmethod
    def js_vars(player: Player):
        existing = MyPage.js_vars(player)
        existing.update(cost=player.cost)
        return existing

    @staticmethod
    def error_message(player: Player, values):
        for field_name, submitted_value in values.items():
            # On vérifie chaque champ soumis. S'il est rempli et inférieur au coût : on bloque !
            if submitted_value is not None and submitted_value < player.cost:
                return f"Erreur : Votre prix ne peut pas être inférieur à votre coût de production ({player.cost} €)."
        return ""

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.decision_imputed = True
            for field in Decision.get_form_fields(player):
                setattr(player, field, random.randint(player.cost, C.BUYER_BUDGET))


class DecisionWaitForGroup(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.compute_round_payoffs()


class Results(MyPage):
    @staticmethod
    def vars_for_template(player: Player):
        existing = MyPage.vars_for_template(player)
        existing.update(w_3=round(player.group.W, 3))
        return existing


class ResultsWaitForAll(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        if subsession.round_number == C.NUM_ROUNDS:
            for p in subsession.get_players():
                p.compute_final_payoff()


class Final(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    Intro,
    Instructions, InstructionsWaitMonitor, InstructionsWaitForAll,
    Understanding, UnderstandingWaitForAll,
    Decision, DecisionWaitForGroup,
    Results, ResultsWaitForAll,
    Final
]


def custom_export(players):
    # En-têtes
    yield [
        'session', 'participant', 'treatment', 'num_session',
        'round_number', 'zone', 'cout', 'is_paid',
        'offre_1u_z1', 'offre_2u_z1', 'offre_3u_z1', 'offre_1u_z2', 'offre_2u_z2',
        'prix_unitaire_z1', 'prix_unitaire_z2',
        'unites_vendues', 'prix_applique', 'payoff',
        'total_faults_comprehension',
        # Variables du groupe
        'group_unites_achetees', 'group_depense_totale', 'group_valeur_totale', 'group_W', 'group_z1_units',
        'group_z2_units',
        # Variables de la partie 2 (BRET) extraites de participant.vars
        'bret_n_boxes',
        'part_1_payoff', 'part_2_payoff', 'final_payoff',
        # Variables demographiques
        'age', 'gender', 'education', 'income', 'status'
    ]

    for p in players:
        participant = p.participant
        subsession = p.subsession

        bret = p.participant.vars.get('FC_bret', {})
        demog = p.participant.vars.get('demog', {})

        yield [
            subsession.session.code, participant.code, subsession.treatment, subsession.numsession,
            p.round_number, p.zone, p.cost, p.paid_round,
            # Offres (selon traitement)
            p.offer_1u_zone1, p.offer_2u_zone1, p.offer_3u_zone1,
            p.offer_1u_zone2, p.offer_2u_zone2,
            p.unit_price_zone1, p.unit_price_zone2,
            # Résultats du round
            p.units_sold,
            p.unit_price_used,
            p.payoff,
            # Compréhension (disponible au round 1)
            p.in_round(1).total_faults,
            # variables group
            p.group.units_bought, p.group.total_spent, p.group.total_value, p.group.W, p.group.z1_units,
            p.group.z2_units,
            # Partie 2 (BRET)
            bret.get("n_boxes", "N/A"),
            # Gains finaux
            participant.vars.get(app_name, {}).get('payoff', 0),  # Gain FC_haies
            bret.get('payoff', 0),  # gain FC_Bret
            participant.payoff,  # Gain Total
            # Variables demog
            demog.get("age", "N/A"), demog.get("gender", "N/A"), demog.get("education", "N/A"),
            demog.get("income", "N/A"), demog.get("status", "N/A"),
        ]
