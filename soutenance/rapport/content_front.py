# -*- coding: utf-8 -*-
"""Pages liminaires + introduction générale."""
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from engine import (
    PRIMARY, PRIMARY_DARK, ACCENT, INK, GREY, HEAD_FONT, BODY_FONT,
    _field, set_borders, para_shading, HEX_FILL,
)


def _toc_field(r, instr, hint):
    p = r.doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    _field(p, instr, cached=hint, font=BODY_FONT, size=10, color=GREY)


def front_matter(r):
    doc = r.doc

    # ── REMERCIEMENTS ───────────────────────────────────────────────────────
    r.h1_plain("Remerciements")
    r.body(
        "Au terme de ce projet, qu'il nous soit permis d'exprimer notre profonde gratitude à "
        "toutes les personnes qui, de près ou de loin, ont contribué à son aboutissement.")
    r.body(
        ("Nous adressons nos remerciements les plus sincères à notre encadrante, ", {}),
        ("Dr. Soumia CHOKRI", {'b': True}),
        (", pour la confiance qu'elle nous a accordée, la qualité de son encadrement, sa "
         "disponibilité constante et la pertinence de ses conseils. Ses orientations ont été "
         "déterminantes dans la conduite de ce travail, depuis l'analyse du besoin jusqu'à la "
         "validation de la solution.", {}))
    r.body(
        "Nos remerciements s'étendent à l'ensemble du corps professoral et administratif de "
        "l'Institut Supérieur d'Ingénierie et des Affaires (ISGA), dont la rigueur pédagogique et "
        "l'esprit d'ouverture nous ont permis d'acquérir les compétences mobilisées tout au long "
        "de ce projet.")
    r.body(
        "Nous tenons également à saluer l'esprit d'entraide et de complémentarité qui a animé "
        "notre groupe de travail. La répartition des tâches — conception, développement backend, "
        "intégration de l'intelligence artificielle, réalisation de l'interface et automatisation "
        "— n'a été possible que grâce à un engagement collectif et à une communication permanente.")
    r.body(
        "Enfin, nous exprimons notre reconnaissance à nos familles et à nos camarades de promotion "
        "pour leur soutien indéfectible et leurs encouragements tout au long de cette aventure "
        "académique et technique.")

    # ── AVANT-PROPOS ────────────────────────────────────────────────────────
    r.h1_plain("Avant-propos")
    r.body(
        "L'Institut Supérieur d'Ingénierie et des Affaires (ISGA) forme, depuis plus de quatre "
        "décennies, des ingénieurs et des cadres appelés à accompagner la transformation numérique "
        "des organisations. Dans le cadre du cycle d'ingénierie en informatique et systèmes "
        "d'information (2CI-ISI), le module « Projet en Systèmes Informatiques » offre aux étudiants "
        "l'occasion de mener, en équipe et de bout en bout, un projet logiciel d'envergure : de "
        "l'analyse du besoin jusqu'au déploiement, en passant par la conception, le développement "
        "et les tests.")
    r.body(
        "Le présent rapport rend compte d'un tel projet, baptisé CuraMedical. Réalisé par un groupe "
        "de trois étudiants et encadré par Dr. Soumia CHOKRI, il s'inscrit dans le champ porteur de "
        "la santé numérique (e-santé) et conjugue génie logiciel, intelligence artificielle et "
        "automatisation des processus. Au-delà de la solution livrée, ce travail témoigne de la "
        "démarche d'ingénierie suivie et des compétences acquises au cours de notre formation.")

    # ── GLOSSAIRE ───────────────────────────────────────────────────────────
    r.h1_plain("Glossaire")
    r.body(
        "Ce glossaire réunit les sigles et les principaux termes techniques employés dans le "
        "présent rapport.")
    r.h3("Sigles et acronymes")
    abbr = [
        ("API", "Application Programming Interface — interface de programmation applicative"),
        ("CORS", "Cross-Origin Resource Sharing — partage de ressources entre origines"),
        ("CRUD", "Create, Read, Update, Delete — opérations de base sur les données"),
        ("CSV", "Comma-Separated Values — format de fichier tabulaire"),
        ("DME", "Dossier Médical Électronique"),
        ("DRF", "Django REST Framework"),
        ("HTTP/HTTPS", "HyperText Transfer Protocol (Secure)"),
        ("IA", "Intelligence Artificielle"),
        ("JSON", "JavaScript Object Notation — format d'échange de données"),
        ("JWT", "JSON Web Token — jeton d'authentification"),
        ("LLM", "Large Language Model — grand modèle de langage"),
        ("MCD / MLD", "Modèle Conceptuel / Logique de Données"),
        ("ORM", "Object-Relational Mapping — correspondance objet-relationnel"),
        ("PDF", "Portable Document Format"),
        ("RBAC", "Role-Based Access Control — contrôle d'accès basé sur les rôles"),
        ("RDV", "Rendez-vous"),
        ("REST", "Representational State Transfer — style d'architecture d'API"),
        ("SDK", "Software Development Kit — kit de développement"),
        ("SMTP", "Simple Mail Transfer Protocol — protocole d'envoi de courriels"),
        ("SPA", "Single Page Application — application monopage"),
        ("SQL", "Structured Query Language"),
        ("SVM", "Support Vector Machine — machine à vecteurs de support"),
        ("TF-IDF", "Term Frequency – Inverse Document Frequency"),
        ("UML", "Unified Modeling Language — langage de modélisation unifié"),
        ("UUID", "Universally Unique Identifier — identifiant unique universel"),
    ]
    r.table(["Sigle", "Signification"], [[(a, {'b': True}), b] for a, b in abbr],
            widths=[3.0, 13.0], font_size=10)

    r.h3("Termes techniques")
    terms = [
        ("Conteneur (Docker)", "Unité logicielle isolée embarquant une application et toutes ses "
         "dépendances, garantissant un comportement identique d'un environnement à l'autre."),
        ("Endpoint (point d'entrée)", "URL exposée par une API à laquelle un client adresse ses "
         "requêtes (ex. /api/consultations/)."),
        ("Microservice", "Service applicatif autonome, déployable indépendamment, dédié à une "
         "responsabilité unique — ici, l'intelligence artificielle."),
        ("ORM", "Couche logicielle traduisant les objets du code en lignes de base de données, et "
         "inversement, sans écrire de SQL à la main."),
        ("Random Forest", "Algorithme d'apprentissage automatique combinant de nombreux arbres de "
         "décision pour produire une prédiction robuste et une probabilité par classe."),
        ("Sérialiseur", "Composant de Django REST Framework convertissant les objets en JSON (et "
         "inversement) tout en validant les données."),
        ("Téléconsultation", "Consultation médicale réalisée à distance par visioconférence, "
         "ici via une salle Jitsi sécurisée générée automatiquement."),
        ("Webhook", "Mécanisme par lequel un service notifie un autre en temps réel, en appelant "
         "une URL prédéfinie lorsqu'un événement survient."),
    ]
    r.table(["Terme", "Définition"], [[(a, {'b': True}), b] for a, b in terms],
            widths=[3.6, 12.4], font_size=10)

    # ── LISTE DES CAPTURES ──────────────────────────────────────────────────
    r.h1_plain("Liste des captures")
    _toc_field(r, 'TOC \\h \\z \\c "Capture"',
               "Liste des captures — sélectionner puis F9 pour actualiser.")

    # ── LISTE DES FIGURES ───────────────────────────────────────────────────
    r.h1_plain("Liste des figures")
    _toc_field(r, 'TOC \\h \\z \\c "Figure"',
               "Liste des figures — sélectionner puis F9 pour actualiser.")

    # ── LISTE DES TABLEAUX ──────────────────────────────────────────────────
    r.h1_plain("Liste des tableaux")
    _toc_field(r, 'TOC \\h \\z \\c "Tableau"',
               "Liste des tableaux — sélectionner puis F9 pour actualiser.")

    # ── SOMMAIRE (chapitres + sections principales) ─────────────────────────
    r.h1_plain("Sommaire")
    _toc_field(r, 'TOC \\o "1-2" \\h \\z \\u',
               "Sommaire — sélectionner puis F9 pour actualiser.")


def introduction(r):
    r.chapter("", "Introduction générale")

    r.h2("Contexte du projet tutoré")
    r.body(
        "La transformation numérique du secteur de la santé constitue aujourd'hui un enjeu majeur. "
        "Les cabinets médicaux, qu'ils soient individuels ou regroupés, sont confrontés à une "
        "augmentation continue du volume d'informations à traiter : dossiers patients, "
        "antécédents, planning des rendez-vous, ordonnances, comptes rendus et correspondances. "
        "Or, dans de nombreuses structures, la gestion de ces données demeure partiellement "
        "manuelle, dispersée entre des registres papier, des fichiers bureautiques isolés et des "
        "outils hétérogènes qui ne communiquent pas entre eux.")
    r.body(
        "C'est dans ce contexte que s'inscrit notre projet tutoré, réalisé dans le cadre du module "
        "« Projet en Systèmes Informatiques » du cycle d'ingénierie de l'ISGA. Il a pour ambition "
        "de concevoir et de réaliser une plateforme intégrée, baptisée ",
        ("CuraMedical", {'b': True}),
        ", capable de couvrir l'ensemble du cycle de vie d'une consultation médicale tout en "
        "introduisant une dimension innovante : l'assistance au diagnostic par l'intelligence "
        "artificielle.")

    r.h2("Problématique")
    r.body(
        "Le fonctionnement traditionnel d'un cabinet médical fait apparaître plusieurs limites qui "
        "nuisent à la fois à la qualité du soin et à l'efficacité organisationnelle :")
    r.bullets([
        [("Fragmentation de l'information : ", {'b': True}),
         "les données d'un même patient sont éclatées sur plusieurs supports, ce qui complique "
         "leur consultation rapide et augmente le risque d'erreur ou de perte."],
        [("Charge administrative : ", {'b': True}),
         "la prise de rendez-vous, les rappels téléphoniques et la rédaction manuelle des "
         "documents mobilisent un temps considérable au détriment du temps médical."],
        [("Absence d'outil d'aide à la décision : ", {'b': True}),
         "le praticien ne dispose d'aucun support numérique pour structurer son raisonnement "
         "diagnostique à partir des symptômes observés."],
        [("Manque de traçabilité : ", {'b': True}),
         "il est difficile de savoir qui a consulté ou modifié une donnée sensible, alors même "
         "que la confidentialité des données de santé est une exigence absolue."],
    ])
    r.body(
        "La question centrale qui structure ce travail peut donc être formulée ainsi : ",
        ("comment concevoir une plateforme unifiée, sécurisée et automatisée qui fluidifie le "
         "parcours de soins du cabinet médical, tout en assistant le praticien dans sa démarche "
         "diagnostique grâce à l'intelligence artificielle ?", {'i': True, 'b': True}))

    r.h2("Objectifs du projet")
    r.body("Pour répondre à cette problématique, nous avons fixé les objectifs suivants :")
    r.bullets([
        "Centraliser l'ensemble des données médicales et administratives dans un dossier patient "
        "électronique unique et structuré ;",
        "Dématérialiser et automatiser la planification des rendez-vous, y compris la "
        "téléconsultation ;",
        "Doter le médecin d'un module d'aide au diagnostic restituant, à partir des symptômes, les "
        "pathologies les plus probables avec un indice de confiance ;",
        "Générer automatiquement les ordonnances et les comptes rendus au format PDF, puis les "
        "transmettre au patient par e-mail et messagerie ;",
        "Garantir la sécurité et la confidentialité des données par une authentification robuste, "
        "un cloisonnement par rôle et une journalisation complète ;",
        "Assurer un déploiement reproductible et portable grâce à la conteneurisation.",
    ])

    r.h2("Méthodologie adoptée")
    r.body(
        "La conduite du projet a suivi une démarche itérative et incrémentale, inspirée des "
        "principes agiles. Après une phase d'analyse du besoin et de modélisation UML (cas "
        "d'utilisation, diagrammes de séquence, d'activité et de classes), le développement a été "
        "organisé par incréments fonctionnels successifs : socle d'authentification et de gestion "
        "des rôles, puis gestion des patients et des rendez-vous, puis consultations et module "
        "d'IA, et enfin automatisation et téléconsultation. Chaque incrément a fait l'objet de "
        "tests fonctionnels et d'une validation au regard du cahier des charges. Le code source a "
        "été versionné avec Git, et l'environnement de développement standardisé au moyen de "
        "Docker afin de garantir l'homogénéité entre les postes des membres de l'équipe.")
    r.body(
        "Le projet s'est déroulé en quatre grandes phases, de l'analyse au déploiement, comme le "
        "résume le tableau suivant.")
    r.table(
        ["Phase", "Activités principales", "Livrables"],
        [
            ["1. Analyse", "Étude de l'existant, cahier des charges, modélisation UML",
             "Diagrammes UML, cahier des charges"],
            ["2. Conception", "Architecture, modèle de données, maquettes",
             "Schéma d'architecture, MCD/MLD"],
            ["3. Développement", "Backend, frontend, microservice IA, automatisation",
             "Application fonctionnelle"],
            ["4. Tests & déploiement", "Tests fonctionnels, conteneurisation, documentation",
             "Plateforme dockerisée, rapport"],
        ],
        caption="Phases de réalisation du projet", widths=[3.4, 8.0, 4.6], font_size=9.5)

    r.h4("Répartition des tâches au sein de l'équipe")
    r.body(
        "Le projet a été mené collectivement, chaque membre assumant un domaine de prédilection tout "
        "en contribuant aux revues croisées et aux tests d'intégration.")
    r.table(
        ["Membre", "Contributions principales"],
        [
            [("Abdou SALOU ABDOU", {'b': True}),
             "Microservice d'IA (modèle, dataset, API de prédiction), intégration du chatbot, "
             "architecture et conteneurisation Docker."],
            [("Kamara MACIRE", {'b': True}),
             "Backend Django (modèles, API REST, sécurité JWT et rôles), automatisation n8n et "
             "génération des documents PDF."],
            [("Nouridine SAWADOGO", {'b': True}),
             "Frontend React (interfaces, tableaux de bord, téléconsultation), design system et "
             "expérience utilisateur."],
        ],
        caption="Répartition des tâches entre les membres du groupe", widths=[4.6, 11.4], font_size=10)

    r.h2("Organisation du rapport")
    r.body("Le présent rapport est structuré en six chapitres :")
    r.bullets([
        [("Chapitre I — Présentation du projet et cahier des charges : ", {'b': True}),
         "étude de l'existant, expression des besoins fonctionnels et non fonctionnels, "
         "identification des acteurs et délimitation du périmètre."],
        [("Chapitre II — Analyse et conception : ", {'b': True}),
         "modélisation fonctionnelle, dynamique et conception de la base de données en UML."],
        [("Chapitre III — Architecture technique et choix technologiques : ", {'b': True}),
         "présentation de l'architecture hybride et justification de la pile technologique."],
        [("Chapitre IV — Réalisation et implémentation : ", {'b': True}),
         "environnement de développement, interfaces et fonctionnalités avancées."],
        [("Chapitre V — Sécurité et traçabilité : ", {'b': True}),
         "mécanismes de protection des données et d'audit."],
        [("Chapitre VI — Déploiement avec Docker : ", {'b': True}),
         "conteneurisation, orchestration et procédure de mise en production."],
    ])
    r.body(
        "Une conclusion générale dresse le bilan des objectifs atteints, expose les difficultés "
        "rencontrées et trace les perspectives d'évolution de la plateforme.")
