from os import environ

ADMIN_USERNAME = 'admin_otree'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = 'w3-9l3a364t1%7uh74n9^zarmk2jho%0vpk4d71y1a(q4!vqp^'
INSTALLED_APPS = ['otree']
SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=5,
    fill_auto=False,
)
DEMO_PAGE_INTRO_HTML = (
    f"<div class='d-flex align-items-center justify-content-center' style='min-height: 150px;'>"
    f"  <figure class='m-0'>"
    f"    <img src='/static/global/img/LEEM.png' style='width: 180px;' class='img-fluid' />"
    f"  </figure>"
    f"</div>"
)
ROOMS = []

LANGUAGE_CODE = 'fr'
REAL_WORLD_CURRENCY_CODE = 'EUR'
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 2
USE_POINTS = False
POINTS_CUSTOM_NAME = 'ECU'
DEBUG = True

SESSION_CONFIGS = [
    dict(
        name='expe_haies_combinatoire',
        display_name='Haies – traitement combinatoire',
        app_sequence=['welcome', 'FC_haies', 'FC_bret', 'FC_final'],
        num_demo_participants=5,
        treatment='combinatoire',
        numsession=1  # A changer pour chaque nouvelle session car cela change les tirages de gains
    ),
    dict(
        name='expe_haies_unitaire',
        display_name='Haies – traitement unitaire',
        app_sequence=['welcome', 'FC_haies', 'FC_bret', 'FC_final'],
        num_demo_participants=5,
        treatment='unitaire',
        numsession=1  # A changer pour chaque nouvelle session car cela change les tirages de gains
    ),
 ]
