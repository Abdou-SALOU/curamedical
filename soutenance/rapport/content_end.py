# -*- coding: utf-8 -*-
"""Conclusion générale, bibliographie/webographie et annexes."""
from docx.shared import Pt
from engine import PRIMARY, PRIMARY_DARK, ACCENT, INK, GREY, shot


# ════════════════════════════════════════════════════════════════════════════
# CONCLUSION
# ════════════════════════════════════════════════════════════════════════════
def conclusion(r):
    r.chapter("", "Conclusion générale et perspectives")

    r.h2("Bilan du projet")
    r.body(
        "Au terme de ce projet, nous avons conçu et réalisé CuraMedical, une plateforme complète "
        "de gestion de cabinet médical qui répond à la problématique posée en introduction. La "
        "solution centralise l'information médicale au sein d'un dossier patient électronique, "
        "dématérialise la planification des rendez-vous, structure les consultations, génère et "
        "transmet automatiquement les documents médicaux, et — surtout — assiste le praticien dans "
        "sa démarche diagnostique grâce à un module d'intelligence artificielle. L'ensemble repose "
        "sur une architecture moderne, sécurisée et entièrement conteneurisée.")
    r.body(
        "Ce travail nous a permis de mettre en pratique, sur un cas concret et exigeant, "
        "l'intégralité de la chaîne de développement d'un système d'information : de l'analyse du "
        "besoin et de la modélisation UML jusqu'au déploiement, en passant par le développement "
        "full-stack, l'intégration de l'apprentissage automatique et l'automatisation des "
        "processus.")

    r.h2("Objectifs atteints")
    r.body("Au regard des objectifs fixés, le bilan fonctionnel est le suivant :")
    r.table(
        ["Objectif", "État"],
        [
            ["Dossier patient électronique centralisé", [("Atteint", {'b': True, 'color': PRIMARY})]],
            ["Planification des rendez-vous et téléconsultation", [("Atteint", {'b': True, 'color': PRIMARY})]],
            ["Aide au diagnostic par IA (top 3 + confiance)", [("Atteint", {'b': True, 'color': PRIMARY})]],
            ["Génération et envoi automatisés des PDF", [("Atteint", {'b': True, 'color': PRIMARY})]],
            ["Sécurité, contrôle par rôle et traçabilité", [("Atteint", {'b': True, 'color': PRIMARY})]],
            ["Déploiement conteneurisé reproductible", [("Atteint", {'b': True, 'color': PRIMARY})]],
        ],
        caption="Bilan des objectifs du projet", widths=[11.5, 4.5], font_size=10)
    r.body(
        "Les six familles de besoins fonctionnels (BF-01 à BF-06) sont couvertes, et plusieurs "
        "extensions à forte valeur ajoutée — assistant conversationnel, téléconsultation intégrée, "
        "notifications multicanal — ont été menées à bien.")

    r.h2("Difficultés rencontrées et solutions proposées")
    r.body("Plusieurs défis techniques ont jalonné le projet ; chacun a appelé une réponse concrète :")
    r.bullets([
        [("Hétérogénéité linguistique du module d'IA : ", {'b': True}),
         "le jeu de données raisonne en anglais alors que la saisie est en français. Nous avons "
         "construit un dictionnaire de correspondance étoffé et une normalisation des accents pour "
         "fiabiliser la traduction des symptômes et des pathologies."],
        [("Temps de réponse lors de l'envoi des documents : ", {'b': True}),
         "la génération et l'expédition des PDF auraient bloqué l'interface. Nous avons déporté ces "
         "traitements dans des fils d'exécution asynchrones, rendant la réponse instantanée pour le "
         "médecin."],
        [("Démarrage lent du microservice d'IA : ", {'b': True}),
         "réentraîner le modèle à chaque démarrage était inacceptable. En entraînant le modèle "
         "pendant la construction de l'image Docker, nous avons rendu le démarrage instantané."],
        [("Cloisonnement strict des données : ", {'b': True}),
         "garantir qu'aucun rôle n'accède aux données d'un autre a nécessité un filtrage "
         "systématique des requêtes, doublé de permissions appliquées à chaque action."],
    ])

    r.h2("Perspectives d'évolution")
    r.body(
        "CuraMedical constitue une base solide et extensible. Plusieurs axes d'enrichissement se "
        "dessinent pour les versions futures :")
    r.h3("Intégration d'un module de facturation")
    r.body(
        "Compléter le parcours par la facturation des actes et le suivi des paiements, afin de "
        "couvrir la dimension financière du cabinet.")
    r.h3("Amélioration du modèle d'IA")
    r.body(
        "Enrichir et équilibrer le jeu de données, comparer d'autres algorithmes, intégrer des "
        "données structurées supplémentaires (constantes, antécédents) et mesurer finement les "
        "performances afin d'accroître la pertinence des suggestions.")
    r.h3("Intégration d'un chatbot conversationnel")
    r.body(
        "Étendre l'assistant vers un agent conversationnel plus autonome, capable d'exécuter "
        "directement des actions (créer un rendez-vous, ouvrir un dossier) à partir d'instructions "
        "en langage naturel.")
    r.h3("Développement d'une application mobile")
    r.body(
        "Proposer une application mobile native pour les patients et les médecins, offrant "
        "notifications push, accès hors ligne aux documents et téléconsultation nomade.")

    r.callout(
        "En définitive,",
        "CuraMedical démontre qu'il est possible de conjuguer rigueur médicale, exigence de "
        "sécurité et innovation par l'intelligence artificielle au sein d'une solution cohérente, "
        "ergonomique et déployable. Ce projet aura été, pour notre équipe, une expérience "
        "formatrice à la croisée du génie logiciel, de la science des données et de la santé "
        "numérique.")


# ════════════════════════════════════════════════════════════════════════════
# BIBLIOGRAPHIE / WEBOGRAPHIE
# ════════════════════════════════════════════════════════════════════════════
def bibliographie(r):
    r.chapter("", "Bibliographie / Webographie")
    r.body("Les ressources suivantes ont accompagné la conception et la réalisation du projet.")

    r.h3("Documentation technique")
    r.bullets([
        "Django Software Foundation — Documentation officielle de Django 4.2. https://docs.djangoproject.com",
        "Django REST Framework — Documentation officielle. https://www.django-rest-framework.org",
        "Simple JWT — Authentification par jetons pour DRF. https://django-rest-framework-simplejwt.readthedocs.io",
        "React — Documentation officielle. https://react.dev",
        "Vite — Build tool nouvelle génération. https://vitejs.dev",
        "Tailwind CSS — Framework CSS utilitaire. https://tailwindcss.com",
        "Flask — Documentation officielle. https://flask.palletsprojects.com",
        "Scikit-learn — Machine Learning in Python. https://scikit-learn.org",
        "PostgreSQL 15 — Documentation officielle. https://www.postgresql.org/docs",
        "Docker & Docker Compose — Documentation officielle. https://docs.docker.com",
        "ReportLab — Génération de documents PDF en Python. https://www.reportlab.com",
        "n8n — Workflow automation. https://docs.n8n.io",
        "Jitsi Meet SDK — Visioconférence open source. https://jitsi.github.io/handbook",
    ])
    r.h3("Articles et ressources scientifiques")
    r.bullets([
        "Breiman, L. (2001). « Random Forests », Machine Learning, 45(1), 5-32.",
        "Pedregosa, F. et al. (2011). « Scikit-learn: Machine Learning in Python », JMLR, 12, 2825-2830.",
        "Ressources et jeux de données publics reliant symptômes et pathologies (datasets « Diseases and Symptoms »).",
    ])


# ════════════════════════════════════════════════════════════════════════════
# ANNEXES
# ════════════════════════════════════════════════════════════════════════════
def annexes(r):
    r.chapter("", "Annexes")

    # A1
    r.h2("A1 : Extraits de code significatifs")
    r.body(
        "Cette annexe rassemble quelques extraits de code représentatifs, complémentaires de ceux "
        "présentés dans le corps du rapport.")
    r.h3("Détection des conflits horaires d'un rendez-vous")
    r.code(
        "def clean(self):\n"
        "    \"\"\"Validation des conflits horaires côté modèle.\"\"\"\n"
        "    if not self.date_heure or not self.medecin_id:\n"
        "        return\n"
        "    fin = self.get_heure_fin()\n"
        "    conflits = RendezVous.objects.filter(\n"
        "        medecin=self.medecin,\n"
        "        statut__in=['PLANIFIE', 'CONFIRME', 'EN_COURS'],\n"
        "        date_heure__lt=fin,\n"
        "        date_heure__gte=self.date_heure - timedelta(minutes=self.duree),\n"
        "    ).exclude(pk=self.pk)\n"
        "    if conflits.exists():\n"
        "        raise ValidationError(\"Conflit horaire détecté pour ce médecin.\")",
        filename="backend/apps/appointments/models.py", language="python")
    r.h3("Calcul automatique de l'âge du patient")
    r.code(
        "@property\n"
        "def age(self):\n"
        "    from datetime import date\n"
        "    aujourd_hui = date.today()\n"
        "    anniversaire_passe = (\n"
        "        (aujourd_hui.month, aujourd_hui.day)\n"
        "        < (self.date_naissance.month, self.date_naissance.day)\n"
        "    )\n"
        "    return aujourd_hui.year - self.date_naissance.year - (1 if anniversaire_passe else 0)",
        filename="backend/apps/patients/models.py", language="python")
    r.h3("Entraînement du classifieur d'intentions (TF-IDF + SVM)")
    r.code(
        "pipeline = Pipeline([\n"
        "    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1)),\n"
        "    ('clf', LinearSVC(C=1.0, random_state=42)),\n"
        "])\n"
        "pipeline.fit(examples, labels)        # 15 intentions, ~180 exemples\n"
        "joblib.dump(pipeline, INTENT_MODEL_PATH)",
        filename="ia-service/intent_classifier.py", language="python")

    # A2
    r.h2("A2 : Workflow n8n de rappel automatique")
    r.body(
        "Le backend transmet à n8n un événement structuré (au format JSON) via un webhook. "
        "L'orchestrateur enchaîne alors les nœuds de traitement : réception de l'événement, "
        "préparation du message, puis envoi par e-mail et par WhatsApp. Le découplage ainsi obtenu "
        "permet de faire évoluer les canaux de communication sans modifier le code applicatif.")
    r.code(
        "{\n"
        "  \"event\": \"new_consultation_report\",\n"
        "  \"patient\": \"LAHLOU Fatima Zahra\",\n"
        "  \"email\": \"patient@example.com\",\n"
        "  \"patient_tel\": \"+2126xxxxxxxx\",\n"
        "  \"doctor\": \"Dr Nouredine SAWADOGO\",\n"
        "  \"date\": \"02/06/2026\",\n"
        "  \"pdf_url\": \"https://.../media/consultations/compte_rendu_42.pdf\",\n"
        "  \"file\": \"<PDF encodé en base64>\"\n"
        "}",
        filename="Charge utile transmise au webhook n8n", language="json")

    # A3
    r.h2("A3 : Exemples d'ordonnances et comptes rendus PDF")
    r.body(
        "Les documents ci-dessous sont générés dynamiquement par la plateforme à partir des données "
        "saisies. Ils reprennent l'en-tête du médecin et de la clinique, la charte verte de "
        "CuraMedical, le tableau des prescriptions ou la synthèse de la consultation, ainsi que le "
        "cachet et la signature du praticien.")
    r.figure(shot("38-ordonnance-pdf.png"), "Exemple d'ordonnance générée au format PDF", width_cm=10.5)
    r.figure(shot("39-compte-rendu-pdf.png"), "Exemple de compte rendu de consultation au format PDF",
             width_cm=10.5)

    # A4
    r.h2("A4 : Configuration SMTP et variables d'environnement")
    r.body(
        "La configuration sensible est externalisée dans un fichier .env. L'extrait ci-dessous en "
        "présente les principales variables (les valeurs réelles sont masquées).")
    r.code(
        "# Base de données\n"
        "POSTGRES_DB=medpredict_db\n"
        "POSTGRES_USER=medpredict_user\n"
        "POSTGRES_PASSWORD=********\n"
        "\n"
        "# Sécurité Django\n"
        "SECRET_KEY=********\n"
        "DEBUG=False\n"
        "\n"
        "# Courriel (SMTP Gmail)\n"
        "EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend\n"
        "EMAIL_HOST=smtp.gmail.com\n"
        "EMAIL_PORT=587\n"
        "EMAIL_USE_TLS=True\n"
        "EMAIL_HOST_USER=********\n"
        "EMAIL_HOST_PASSWORD=********\n"
        "\n"
        "# Services IA et messagerie\n"
        "GROQ_API_KEY=********\n"
        "TWILIO_ACCOUNT_SID=********\n"
        "TWILIO_AUTH_TOKEN=********",
        filename=".env — variables d'environnement", language="ini")

    # A5
    r.h2("A5 : Fichiers Docker et Docker Compose")
    r.body(
        "Extrait du fichier d'orchestration docker-compose.yml décrivant les principaux services "
        "et leur mise en réseau.")
    r.code(
        "services:\n"
        "  db:\n"
        "    image: postgres:15\n"
        "    healthcheck:\n"
        "      test: [\"CMD-SHELL\", \"pg_isready -U $POSTGRES_USER\"]\n"
        "  backend:\n"
        "    build: ./backend\n"
        "    command: gunicorn curamedical.wsgi:application --bind 0.0.0.0:8000 --workers 4\n"
        "    depends_on:\n"
        "      db: { condition: service_healthy }\n"
        "  frontend:\n"
        "    build: ./frontend\n"
        "    ports: [\"3000:3000\"]\n"
        "  ia-service:\n"
        "    build: ./ia-service\n"
        "    ports: [\"5000:5000\"]\n"
        "  n8n:\n"
        "    image: n8nio/n8n:latest\n"
        "networks:\n"
        "  curamedical_network: { driver: bridge }",
        filename="docker-compose.yml", language="yaml")

    # A6
    r.h2("A6 : Mise en place des outils et services externes")
    r.body(
        "Cette annexe décrit, de façon synthétique et reproductible, la procédure de mise en place "
        "des principaux outils et services tiers utilisés par CuraMedical. Pour chacun, le rôle, la "
        "démarche suivie et le lien officiel sont précisés.")
    r.table(
        ["Outil / Service", "Rôle dans CuraMedical", "Lien officiel"],
        [
            [("Docker", {'b': True}), "Conteneurisation et orchestration des services", [("docker.com", {'mono': True})]],
            [("n8n", {'b': True}), "Automatisation des notifications (e-mail, WhatsApp)", [("n8n.io", {'mono': True})]],
            [("Jitsi Meet", {'b': True}), "Téléconsultation vidéo", [("jitsi.org", {'mono': True})]],
            [("ngrok", {'b': True}), "Exposition publique du backend en développement", [("ngrok.com", {'mono': True})]],
            [("Twilio", {'b': True}), "Passerelle WhatsApp (messages et documents)", [("twilio.com", {'mono': True})]],
            [("Groq", {'b': True}), "Inférence du modèle de langage Llama 3", [("groq.com", {'mono': True})]],
        ],
        caption="Outils et services externes du projet", widths=[3.4, 8.6, 4.0], font_size=9.5)

    r.h3("Docker et Docker Compose")
    r.body(
        "Après installation de Docker Desktop, l'ensemble de la plateforme se construit et se lance "
        "depuis la racine du dépôt avec une seule commande, « docker-compose up --build ». Les "
        "images sont mises en cache, si bien que les démarrages suivants sont quasi immédiats. "
        "Site officiel : https://www.docker.com — Documentation : https://docs.docker.com.")

    r.h3("n8n — automatisation des notifications")
    r.body(
        "n8n est lancé comme un conteneur du projet et son interface est accessible sur le port "
        "5678. Nous y avons créé un workflow démarrant par un nœud « Webhook » (chemin "
        "/webhook/prescriptions), suivi de nœuds d'envoi d'e-mail et d'appel HTTP. Le backend "
        "transmet l'événement et le document à ce webhook ; n8n se charge de l'acheminement. "
        "Site officiel : https://n8n.io — Documentation : https://docs.n8n.io.")

    r.h3("Jitsi Meet — téléconsultation")
    r.body(
        "L'intégration de Jitsi ne nécessite aucune clé d'API : nous utilisons le SDK React "
        "« @jitsi/react-sdk » avec le serveur public meet.jit.si. À chaque rendez-vous en ligne, le "
        "backend génère un nom de salle unique (de la forme « CuraMedical-RDV-xxxxxxxx ») que le "
        "médecin et le patient rejoignent. Site officiel : https://jitsi.org — Service : "
        "https://meet.jit.si.")

    r.h3("ngrok — exposition du backend en développement")
    r.body(
        "Twilio doit pouvoir joindre notre serveur par une URL publique en HTTPS pour livrer les "
        "messages WhatsApp entrants. En développement local, ngrok crée un tunnel sécurisé vers le "
        "backend (« ngrok http 8000 ») ; l'URL générée est renseignée dans la variable "
        "PUBLIC_BASE_URL et déclarée comme webhook dans la console Twilio. "
        "Site officiel : https://ngrok.com — Documentation : https://ngrok.com/docs.")

    r.h3("Twilio — passerelle WhatsApp")
    r.body(
        "Après création d'un compte Twilio, nous avons activé le bac à sable WhatsApp (Sandbox), "
        "récupéré l'identifiant de compte (ACCOUNT_SID) et le jeton d'authentification "
        "(AUTH_TOKEN), puis configuré le numéro expéditeur (whatsapp:+14155238886). L'URL de "
        "rappel entrante (exposée via ngrok) pointe vers le point d'entrée WhatsApp du backend, qui "
        "relaie les messages au microservice d'IA. Site officiel : https://www.twilio.com — "
        "WhatsApp : https://www.twilio.com/whatsapp.")

    r.h3("Groq — inférence du modèle Llama 3")
    r.body(
        "Le raisonnement en langage naturel de l'assistant s'appuie sur le modèle "
        "« llama-3.1-8b-instant » servi par Groq, réputé pour sa très faible latence. Une clé "
        "d'API gratuite est générée depuis la console, puis renseignée dans la variable "
        "GROQ_API_KEY ; en son absence, le système bascule automatiquement sur un raisonnement "
        "local par mots-clés. Site officiel : https://groq.com — Console : https://console.groq.com.")

    r.h3("SMTP Gmail — envoi des courriels")
    r.body(
        "Pour l'envoi des e-mails en production, nous avons activé la validation en deux étapes sur "
        "le compte Google, puis généré un « mot de passe d'application » dédié, renseigné dans "
        "EMAIL_HOST_USER et EMAIL_HOST_PASSWORD. La connexion est chiffrée via TLS sur le port 587. "
        "Gestion des mots de passe d'application : https://myaccount.google.com/apppasswords.")


# ════════════════════════════════════════════════════════════════════════════
# TABLE DES MATIÈRES (détaillée, en fin de document — style mémoire)
# ════════════════════════════════════════════════════════════════════════════
def table_des_matieres(r):
    from engine import _field, BODY_FONT
    r.chapter("", "Table des matières")
    p = r.doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    _field(p, 'TOC \\o "1-3" \\h \\z \\u',
           cached="Table des matières détaillée — sélectionner puis F9 pour actualiser.",
           font=BODY_FONT, size=10, color=GREY)


# ════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ (placé en toute fin — style mémoire)
# ════════════════════════════════════════════════════════════════════════════
def resume(r):
    r.chapter("", "Résumé")
    r.body(
        ("CuraMedical", {'b': True}),
        (" est une plateforme web de gestion de cabinet médical conçue pour unifier, dans un flux "
         "de travail unique et fluide, l'ensemble du parcours de soins : gestion des dossiers "
         "patients, planification des rendez-vous, réalisation des consultations, génération des "
         "ordonnances et des comptes rendus, téléconsultation et communication automatisée avec le "
         "patient. La solution se distingue par l'intégration d'un module d'aide au diagnostic "
         "fondé sur l'apprentissage automatique : à partir des symptômes saisis par le médecin, un "
         "modèle Random Forest propose les trois hypothèses pathologiques les plus probables, "
         "assorties d'un score de confiance et d'un niveau de risque.", {}))
    r.body(
        "Sur le plan technique, le système repose sur une architecture hybride associant un "
        "backend monolithique modulaire (Django REST Framework), un frontend moderne (React 19 et "
        "Vite), un microservice d'intelligence artificielle dédié (Flask et Scikit-learn) et une "
        "base de données relationnelle PostgreSQL. L'ensemble est conteneurisé avec Docker et "
        "orchestré par Docker Compose. La sécurité s'appuie sur une authentification par jetons "
        "JWT, un contrôle d'accès strict basé sur les rôles (médecin, secrétaire, administrateur, "
        "patient) et une journalisation exhaustive des actions. Les rappels de rendez-vous et "
        "l'envoi des documents médicaux sont automatisés au moyen d'un orchestrateur de flux (n8n), "
        "de l'e-mail et de la messagerie WhatsApp.")
    r.body(
        ("Mots-clés : ", {'b': True}),
        ("dossier médical électronique, aide au diagnostic, apprentissage automatique, Random "
         "Forest, Django REST Framework, React, microservices, Docker, téléconsultation, "
         "automatisation, JWT, PostgreSQL.", {'i': True}))
