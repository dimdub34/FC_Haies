def get_understanding(params=None):
    understanding = [
        {
            "id": 1,
            "question": "A chaque période, un seul coût de production sera tiré au sort pour les 5 vendeurs de "
                        "votre groupe. Tous les vendeurs auront donc le même coût de production.",
            "propositions": ["Vrai", "Faux"],
            "solution": 1,  # Index 1 = Faux
            "explication": "La réponse est « Faux » car 5 coûts de production (un pour chaque vendeur) "
                           "sont tirés au hasard indépendamment les uns des autres à chaque période. "
                           "Notez qu’il est peu probable que les 5 coûts tirés au sein d’un même groupe soient identiques."
        },
        {
            "id": 2,
            "question": "Votre gain dépend uniquement du prix que vous proposez et de votre coût de production.",
            "propositions": ["Vrai", "Faux"],
            "solution": 1,  # Index 1 = Faux
            "explication": "La réponse est « Faux ». Votre gain dépend aussi des prix proposés par les "
                           "autres vendeurs de votre groupe et du nombre d’unités que l’acheteur souhaite vous acheter."
        },
        {
            "id": 3,
            "question": "Vous êtes en concurrence avec les 4 autres vendeurs de votre groupe.",
            "propositions": ["Vrai", "Faux"],
            "solution": 0,  # Index 0 = Vrai
            "explication": "La réponse est « Vrai ». Vous êtes en concurrence avec les vendeurs de votre zone "
                           "et ceux de l’autre zone. Vous devrez faire un compromis, selon vos préférences,"
                           "entre proposer un prix élevé pour potentiellement gagner plus, ou un prix plus bas pour augmenter "
                           "vos chances de gagner (autrement dit, pour que votre offre de prix soit sélectionnée)."
        },
        {
            "id": 4,
            "question": "Supposons que votre coût de production soit de 2000 € et que vous proposez un prix de "
                        "2750 € (Les valeurs proposées dans cet exemple sont volontairement très différents de celles "
                        "considérées pour l’expérience). Si l’acheteur vous achète 2 unités, quel sera votre gain ?",
            "propositions": [
                "750 €",
                "1500 €",
                "5500 €"
            ],
            "solution": 1,  # Index 1 = 1500 € car (2750 - 2000) * 2
            "explication": "La réponse est '1500 €' car (2750 - 2000) x 2. Votre gain est égal à la différence entre le prix que vous "
                           "proposez et votre coût de production, multipliée par le nombre d’unités que l’acheteur vous achète."
        },
        {
            "id": 5,
            "question": "Dans la même situation, si l’acheteur ne vous achète aucune unité, quel sera votre gain ?",
            "propositions": [
                "-2000 €",
                "0 €",
                "750 €"
            ],
            "solution": 1,  # Index 1 = 0 €
            "explication": "La réponse est '0 €'. Si l’acheteur ne vous achète aucune unité, votre gain est de 0 € "
                           "car vous ne réalisez aucune vente. "
        },
        {
            "id": 6,
            "question": "Proposer un prix plus élevé vous permet nécessairement d'obtenir un gain plus élevé.",
            "propositions": ["Vrai", "Faux"],
            "solution": 1,  # Index 1 = Faux
            "explication": "La réponse est « Faux ». Proposer un prix plus élevé augmente votre gain "
                           "SI votre offre est sélectionnée par l’acheteur ; mais comme vous êtes en concurrence avec les autres vendeurs, "
                           "proposer un prix plus élevé réduit aussi vos chances d’être sélectionné."
        },
        {
            "id": 7,
            "question": "Quelle option crée le plus de valeur pour l’acheteur ?",
            "propositions": [
                "A. Acheter 1 unité dans chaque zone",
                "B. Acheter 2 unités dans la même zone"
            ],
            "solution": 1,  # Index 1 = Option B
            "explication": "La réponse est « B ». Acheter 1 unité dans chaque zone crée une valeur de 200 "
                           "(100 dans chaque zone), tandis qu’acheter 2 unités dans la même zone crée une valeur de 250 "
                           "(2 × 100 + 50). Il y a donc une valeur supplémentaire de 50."
        },
        {
            "id": 8,
            "question": "Quelle situation crée le plus de valeur pour l’acheteur ?",
            "propositions": [
                "A. Acheter 3 unités dans la même zone",
                "B. Acheter 2 unités dans une zone et 1 unité dans l’autre"
            ],
            "solution": 0,  # Index 0 = Option A
            "explication": "La réponse est « A ». Acheter 3 unités dans la même zone crée une valeur de 375 "
                           "(3 × 100 + 75). Acheter 2 unités dans une zone et 1 unité dans l’autre crée une valeur totale de 350 "
                           "(250 + 100)."
        }
    ]
    return understanding
