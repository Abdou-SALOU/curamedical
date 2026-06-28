# -*- coding: utf-8 -*-
"""Chapitres 1 à 6 du rapport CuraMedical (version détaillée)."""
from docx.shared import Pt
from engine import (
    PRIMARY, PRIMARY_DARK, ACCENT, INK, GREY,
    shot, ARCHI, UC_FULL, UC_SIMPLE, SEQ_JWT, SEQ_IA, SEQ_DOCS,
    ACT_PAT, CLASS_DIAG, SEQ_CONSULT, ACT_DETAIL, DEPLOY,
)


# ════════════════════════════════════════════════════════════════════════════
# CHAPITRE 1
# ════════════════════════════════════════════════════════════════════════════
def chapter1(r):
    r.chapter("Chapitre 1", "Présentation du projet et cahier des charges")
    r.body(
        "Tout projet logiciel d'envergure commence par une phase de cadrage rigoureuse. Avant "
        "d'écrire la moindre ligne de code, il est indispensable de comprendre le terrain sur "
        "lequel la solution viendra s'implanter, de recenser les attentes des futurs utilisateurs "
        "et de fixer les frontières de ce qui sera — ou ne sera pas — réalisé. Ce premier chapitre "
        "remplit cette fonction : il analyse la situation existante d'un cabinet médical "
        "fonctionnant de manière traditionnelle, formalise l'ensemble des besoins fonctionnels et "
        "non fonctionnels que CuraMedical doit satisfaire, identifie les acteurs du système et "
        "leurs prérogatives, puis délimite précisément le périmètre de la solution développée.")

    # 1.1
    r.h2("1.1 Étude de l'existant et identification des problèmes")
    r.body(
        "L'étude de l'existant vise à objectiver les difficultés rencontrées au quotidien dans la "
        "gestion d'un cabinet médical, afin d'en déduire les axes d'amélioration prioritaires. "
        "Trois grands constats se dégagent.")

    r.h3("Les limites des processus médicaux traditionnels")
    r.body(
        "Dans un cabinet fonctionnant de manière classique, le dossier d'un patient se matérialise "
        "souvent par une chemise cartonnée regroupant des feuilles manuscrites, des résultats "
        "d'analyses et des ordonnances passées. Cette organisation, bien qu'éprouvée, présente des "
        "inconvénients structurels majeurs. La recherche d'une information précise (un antécédent, "
        "une allergie, un traitement en cours) peut s'avérer longue et fastidieuse, en particulier "
        "lorsque le volume de dossiers augmente. Le support papier est par nature fragile : il peut "
        "être égaré, détérioré, ou rendu illisible ; il n'offre aucune sauvegarde et reste "
        "inaccessible à distance.")
    r.body(
        "La planification des rendez-vous souffre de limites comparables. Tenue sur un agenda "
        "papier ou un tableur, elle ne prévient pas automatiquement les conflits horaires, ne "
        "permet aucun rappel et oblige le personnel à de nombreuses relances téléphoniques. Il en "
        "résulte un taux élevé de rendez-vous non honorés — les fameux « lapins » — qui désorganisent "
        "le planning et représentent une perte de temps médical considérable.")
    r.body(
        "Enfin, la rédaction manuelle des ordonnances et des comptes rendus est chronophage et "
        "sujette aux erreurs de transcription ; leur archivage et leur transmission au patient "
        "reposent le plus souvent sur le seul support papier, sans aucune traçabilité.")

    r.h3("Le besoin d'assistance diagnostique intelligente")
    r.body(
        "Le raisonnement diagnostique consiste, pour l'essentiel, à mettre en relation un ensemble "
        "de symptômes observés avec un répertoire de pathologies connues. Face à des tableaux "
        "cliniques parfois atypiques, ou en présence de symptômes communs à de nombreuses "
        "affections, le praticien gagnerait à disposer d'un outil capable de hiérarchiser "
        "rapidement les hypothèses les plus probables. Un tel outil ne vise nullement à se "
        "substituer au médecin, dont l'expertise et le jugement clinique restent souverains ; il "
        "agit comme un second regard statistique, élargissant le champ des possibles et réduisant "
        "le risque d'oubli d'une hypothèse pertinente. C'est précisément le rôle dévolu au module "
        "d'intelligence artificielle de CuraMedical.")

    r.h3("Le besoin de digitalisation et de communication automatisée")
    r.body(
        "La relation entre le cabinet et le patient implique de nombreux échanges : confirmation "
        "de rendez-vous, rappels, remise d'ordonnances et de comptes rendus, réponses aux questions "
        "courantes. Réalisés manuellement, ces échanges mobilisent un temps précieux et restent "
        "exposés aux oublis. Leur automatisation — par courrier électronique et par messagerie "
        "instantanée — libère le personnel des tâches répétitives, améliore sensiblement "
        "l'expérience du patient, qui reçoit ses documents sans délai et de façon traçable, et "
        "renforce l'image de modernité du cabinet.")

    r.h4("Synthèse comparative")
    r.body(
        "Le tableau suivant met en regard la situation traditionnelle, les solutions logicielles "
        "génériques du marché et l'approche retenue par CuraMedical.")
    r.table(
        ["Critère", "Gestion traditionnelle", "Logiciel générique", "CuraMedical"],
        [
            ["Centralisation des données", "Faible (papier dispersé)", "Moyenne", [("Élevée", {'b': True, 'color': PRIMARY})]],
            ["Aide au diagnostic", "Inexistante", "Rare", [("Intégrée (IA)", {'b': True, 'color': PRIMARY})]],
            ["Téléconsultation", "Non", "Optionnelle / payante", [("Native", {'b': True, 'color': PRIMARY})]],
            ["Communication automatisée", "Manuelle", "Partielle", [("E-mail + WhatsApp", {'b': True, 'color': PRIMARY})]],
            ["Traçabilité / audit", "Nulle", "Variable", [("Complète", {'b': True, 'color': PRIMARY})]],
            ["Coût de déploiement", "—", "Licences élevées", [("Open source", {'b': True, 'color': PRIMARY})]],
        ],
        caption="Comparaison de l'existant avec la solution proposée",
        widths=[3.6, 4.2, 4.0, 4.2], font_size=9)

    # 1.2
    r.h2("1.2 Expression des besoins")
    r.body(
        "L'expression des besoins traduit les constats précédents en exigences précises. On "
        "distingue les besoins fonctionnels, qui décrivent ce que le système doit faire, des "
        "besoins non fonctionnels, qui décrivent comment il doit le faire (qualité, performance, "
        "sécurité).")

    r.h3("1.2.1 Besoins fonctionnels")
    r.body(
        "Les besoins fonctionnels ont été regroupés en six grandes familles, codifiées de BF-01 à "
        "BF-06. Chacune est détaillée ci-après.")

    bf_detail = [
        ("BF-01 : Gestion des dossiers patients",
         "Le système doit permettre de créer, consulter, mettre à jour et archiver le dossier "
         "complet d'un patient. Ce dossier comprend l'identité (nom, prénom, date de naissance, "
         "sexe, numéro de carte d'identité), les coordonnées (téléphone, e-mail, adresse, ville) et "
         "les informations médicales (groupe sanguin, allergies, antécédents, traitements en "
         "cours). Une recherche instantanée et une corbeille — permettant un archivage réversible "
         "— complètent la gestion."),
        ("BF-02 : Gestion et planification des rendez-vous",
         "Le système doit permettre de planifier des rendez-vous, qu'ils soient présentiels ou en "
         "téléconsultation, en détectant automatiquement les conflits horaires sur l'agenda du "
         "médecin. Chaque rendez-vous suit un cycle de vie (en attente, planifié, confirmé, en "
         "cours, terminé, annulé) et s'affiche dans un calendrier interactif."),
        ("BF-03 : Gestion des consultations médicales",
         "Le médecin doit pouvoir enregistrer une consultation rattachée à un patient et, le cas "
         "échéant, à un rendez-vous : symptômes observés, résultats de l'examen clinique, "
         "diagnostic retenu et notes personnelles. La clôture d'une consultation met "
         "automatiquement à jour le statut du rendez-vous associé."),
        ("BF-04 : Génération d'ordonnances et de comptes rendus PDF",
         "Le système doit permettre de composer une ordonnance ligne par ligne (médicament, "
         "dosage, posologie, durée, instructions) et produire automatiquement l'ordonnance ainsi "
         "que le compte rendu de consultation au format PDF, conformes à une charte professionnelle "
         "et prêts à être imprimés ou transmis."),
        ("BF-05 : Assistance au diagnostic par intelligence artificielle",
         "À partir des symptômes saisis et de quelques éléments de contexte, le système doit "
         "interroger un module d'intelligence artificielle qui retourne les trois pathologies les "
         "plus probables, chacune assortie d'un score de confiance et d'un niveau de risque. Les "
         "suggestions sont conservées à titre de trace, sans jamais se substituer au diagnostic du "
         "médecin."),
        ("BF-06 : Tableau de bord et statistiques médicales",
         "Le système doit restituer des indicateurs d'activité : nombre de patients actifs, de "
         "rendez-vous et de consultations, répartition des statuts de rendez-vous, évolution "
         "mensuelle de l'activité, répartition des pathologies diagnostiquées et taux d'adoption du "
         "module d'IA."),
    ]
    for titre, desc in bf_detail:
        r.h4(titre)
        r.body(desc)

    r.body(
        "Le tableau ci-dessous récapitule ces besoins et indique, pour chacun, le ou les acteurs "
        "principalement concernés.")
    r.table(["Code", "Intitulé", "Acteur(s) principal(aux)"],
            [
                ["BF-01", "Gestion des dossiers patients", "Secrétaire, Médecin"],
                ["BF-02", "Planification des rendez-vous", "Secrétaire, Médecin, Patient"],
                ["BF-03", "Gestion des consultations", "Médecin"],
                ["BF-04", "Génération des documents PDF", "Médecin"],
                ["BF-05", "Aide au diagnostic par IA", "Médecin"],
                ["BF-06", "Tableau de bord et statistiques", "Médecin, Secrétaire"],
            ],
            caption="Récapitulatif des besoins fonctionnels et acteurs concernés",
            widths=[1.8, 7.2, 7.0], font_size=10)

    r.h3("1.2.2 Besoins non fonctionnels")
    r.body(
        "Au-delà des services rendus, la plateforme doit satisfaire un ensemble d'exigences de "
        "qualité qui conditionnent son acceptation par les utilisateurs et sa pérennité dans le "
        "temps. Six exigences ont été retenues comme prioritaires.")
    nfr = [
        ("Performance", "Les opérations courantes de l'interface doivent répondre en moins d'une "
         "seconde. Les traitements longs (génération et envoi des documents) sont exécutés en "
         "arrière-plan afin de ne jamais bloquer l'utilisateur."),
        ("Sécurité", "Les données de santé étant particulièrement sensibles, l'accès doit être "
         "protégé par une authentification robuste, le chiffrement des échanges, un contrôle "
         "d'accès strict par rôle et une protection contre les tentatives d'intrusion."),
        ("Ergonomie", "L'interface doit être épurée, cohérente et adaptative (responsive), guidant "
         "l'utilisateur par des parcours clairs et un retour visuel immédiat sous forme de "
         "notifications."),
        ("Disponibilité", "L'architecture conteneurisée doit assurer le redémarrage automatique "
         "des services en cas d'incident et vérifier l'état de la base de données avant de démarrer "
         "les applications qui en dépendent."),
        ("Maintenabilité", "Le code doit être modulaire, organisé par domaine métier, avec une "
         "séparation nette des responsabilités et une documentation automatique de l'API, afin de "
         "faciliter les évolutions futures."),
        ("Traçabilité", "Toute création, modification ou suppression d'une donnée sensible doit "
         "être journalisée avec l'identité de son auteur et un horodatage, pour répondre aux "
         "exigences de conformité et d'investigation."),
    ]
    r.table(["Exigence", "Description"], [[(a, {'b': True}), b] for a, b in nfr],
            caption="Besoins non fonctionnels de CuraMedical", widths=[3.4, 12.6], font_size=10)

    # 1.3
    r.h2("1.3 Identification des acteurs")
    r.body(
        "Un acteur désigne un rôle joué par une entité externe (généralement un utilisateur) qui "
        "interagit avec le système. Quatre profils ont été identifiés. À chacun correspond un rôle "
        "technique qui détermine, de façon stricte, les fonctionnalités accessibles. Ce "
        "cloisonnement constitue l'un des piliers de la sécurité de la plateforme.")
    r.h4("Le Médecin")
    r.body(
        "Le médecin est l'acteur central du volet clinique. Il réalise les consultations, sollicite "
        "l'aide au diagnostic, rédige les ordonnances, génère les documents médicaux et anime les "
        "téléconsultations. Pour garantir la confidentialité, il n'accède qu'à ses propres patients "
        "et à ses propres consultations.")
    r.h4("La Secrétaire")
    r.body(
        "La secrétaire est le pivot administratif du cabinet. Elle crée et met à jour les dossiers "
        "patients, planifie les rendez-vous et gère le planning, sans toutefois accéder au contenu "
        "médical détaillé des consultations, qui relève du seul médecin.")
    r.h4("Le Patient")
    r.body(
        "Le patient est le bénéficiaire du service. Après s'être inscrit, il dispose d'un espace "
        "personnel pour suivre ses rendez-vous, consulter l'historique de ses consultations, "
        "télécharger ses ordonnances et comptes rendus et rejoindre, le moment venu, une "
        "téléconsultation.")
    r.h4("L'Administrateur")
    r.body(
        "L'administrateur est le garant technique du système. Il gère les comptes des utilisateurs "
        "(création, activation, désactivation), la configuration générale et la supervision des "
        "journaux d'audit. Par conception, il n'a aucun accès au contenu médical des patients, ce "
        "qui sépare clairement l'administration technique de l'exercice médical.")
    r.body(
        "La matrice ci-dessous synthétise les droits d'accès accordés à chaque rôle sur les "
        "principales ressources du système.")
    r.table(
        ["Acteur", "Patients", "Rendez-vous", "Consultations / IA", "Ordonnances", "Comptes / Audit"],
        [
            [("Médecin", {'b': True}), "Lecture (les siens)", "Gérer (les siens)", "Gérer + IA", "Gérer", "—"],
            [("Secrétaire", {'b': True}), "Gérer", "Gérer (tous)", "Liste seule", "—", "—"],
            [("Patient", {'b': True}), "Son profil", "Les siens", "Les siennes (lecture)", "Les siennes (lecture)", "—"],
            [("Administrateur", {'b': True}), "—", "—", "—", "—", "Gérer"],
        ],
        caption="Matrice des droits d'accès par rôle",
        widths=[2.6, 2.7, 2.7, 3.0, 2.4, 2.6], font_size=8.5)

    # 1.4
    r.h2("1.4 Périmètre et contraintes du projet")
    r.h3("Périmètre fonctionnel")
    r.body(
        "Le périmètre du projet couvre l'intégralité du parcours de soins ambulatoire : de "
        "l'inscription du patient et de la prise de rendez-vous jusqu'à la remise des documents "
        "médicaux, en passant par la consultation assistée par IA et la téléconsultation. Les six "
        "familles de besoins fonctionnels décrites précédemment sont toutes couvertes par la "
        "version livrée et présentée lors de la soutenance.")
    r.h3("Extensions réalisées")
    r.body(
        "Au-delà du cahier des charges initial, plusieurs extensions à forte valeur ajoutée ont été "
        "développées et intégrées :")
    r.bullets([
        "un assistant conversationnel interne (chatbot) capable de comprendre des intentions en "
        "langage naturel, d'extraire des symptômes d'une phrase libre et de restituer des "
        "statistiques du cabinet ;",
        "la téléconsultation vidéo intégrée, par génération automatique de salles sécurisées, sans "
        "installation de logiciel tiers ;",
        "l'envoi automatisé des ordonnances et des comptes rendus par e-mail et par WhatsApp ;",
        "un module de statistiques avancées alimentant en temps réel le tableau de bord du médecin.",
    ])
    r.h3("Limites du projet")
    r.body(
        "Certaines fonctionnalités, volontairement exclues du périmètre pour respecter les délais, "
        "sont identifiées comme perspectives d'évolution : la facturation et la gestion comptable, "
        "l'interfaçage avec des dispositifs médicaux ou des laboratoires d'analyses, et le "
        "développement d'une application mobile native. Par ailleurs, et c'est un point capital, le "
        "module d'IA constitue un outil d'aide à la décision : il ne pose jamais de diagnostic et "
        "n'engage aucunement la responsabilité médicale, qui demeure entièrement celle du "
        "praticien.")


# ════════════════════════════════════════════════════════════════════════════
# CHAPITRE 2
# ════════════════════════════════════════════════════════════════════════════
def chapter2(r):
    r.chapter("Chapitre 2", "Analyse et conception")
    r.body(
        "Après avoir défini le « quoi » au chapitre précédent, ce chapitre s'attache au « comment » "
        "sur le plan conceptuel. Il traduit les besoins exprimés en modèles formels au moyen du "
        "langage de modélisation unifié (UML), véritable lingua franca du génie logiciel. La "
        "modélisation fonctionnelle décrit les interactions entre acteurs et système ; la "
        "modélisation dynamique en détaille la chronologie ; enfin, la conception de la base de "
        "données pose les fondations de la persistance.")

    # 2.1
    r.h2("2.1 Modélisation fonctionnelle")
    r.h3("Diagramme global des cas d'utilisation")
    r.body(
        "Le diagramme de cas d'utilisation offre une vue synthétique des services rendus par le "
        "système et des acteurs qui les déclenchent. Il met en évidence plusieurs éléments "
        "structurants : la généralisation de l'acteur abstrait « Utilisateur » vers les rôles "
        "concrets (médecin, secrétaire, administrateur, patient) ; le cas pivot « S'authentifier », "
        "dont dépendent toutes les actions protégées ; les relations d'extension liant la "
        "consultation à la sollicitation de l'IA, et la rédaction d'un document à sa génération en "
        "PDF ; enfin, l'ouverture des cas d'utilisation propres au patient (s'inscrire, prendre et "
        "suivre un rendez-vous, recevoir ses documents, analyser ses symptômes).")
    r.figure(UC_FULL, "Diagramme global des cas d'utilisation de CuraMedical", width_cm=14.5)

    r.h3("Description des scénarios principaux")
    r.body(
        "Pour préciser le comportement attendu, les cas d'utilisation les plus significatifs font "
        "l'objet d'une description textuelle structurée (acteur, préconditions, scénario nominal, "
        "scénarios alternatifs, postconditions).")

    r.h4("Cas d'utilisation : S'authentifier")
    r.table(
        ["Rubrique", "Description"],
        [
            [("Acteur", {'b': True}), "Tout utilisateur (médecin, secrétaire, administrateur, patient)"],
            [("Précondition", {'b': True}), "L'utilisateur possède un compte actif"],
            [("Scénario nominal", {'b': True}),
             "1. L'utilisateur saisit son identifiant et son mot de passe. "
             "2. Le système vérifie les informations. "
             "3. Le système délivre une paire de jetons JWT. "
             "4. L'utilisateur est redirigé vers le tableau de bord correspondant à son rôle."],
            [("Scénario alternatif", {'b': True}),
             "2a. Identifiants invalides → message d'erreur, nouvelle tentative (dans la limite du "
             "débit autorisé)."],
            [("Postcondition", {'b': True}), "Une session sécurisée est ouverte côté client"],
        ],
        caption="Description du cas d'utilisation « S'authentifier »", widths=[3.4, 12.6], font_size=9.5)

    r.h4("Cas d'utilisation : Réaliser une consultation assistée par IA")
    r.table(
        ["Rubrique", "Description"],
        [
            [("Acteur", {'b': True}), "Médecin"],
            [("Précondition", {'b': True}), "Le médecin est authentifié ; le patient existe"],
            [("Scénario nominal", {'b': True}),
             "1. Le médecin sélectionne un patient. "
             "2. Il saisit les symptômes observés et le contexte clinique. "
             "3. Il sollicite l'aide au diagnostic. "
             "4. Le système affiche les trois pathologies les plus probables. "
             "5. Le médecin renseigne son diagnostic et ses notes, puis enregistre. "
             "6. Le système clôture le rendez-vous associé et déclenche l'envoi des documents."],
            [("Scénario alternatif", {'b': True}),
             "3a. Le médecin choisit de ne pas solliciter l'IA → la consultation est enregistrée "
             "sans suggestion. "
             "4a. Symptômes trop imprécis → le système signale l'impossibilité de conclure."],
            [("Postcondition", {'b': True}),
             "La consultation est enregistrée ; les suggestions de l'IA sont conservées comme trace"],
        ],
        caption="Description du cas d'utilisation « Réaliser une consultation assistée par IA »",
        widths=[3.4, 12.6], font_size=9.5)

    r.h4("Cas d'utilisation : Planifier un rendez-vous")
    r.table(
        ["Rubrique", "Description"],
        [
            [("Acteur", {'b': True}), "Secrétaire (ou patient pour une demande)"],
            [("Précondition", {'b': True}), "Le patient et le médecin existent dans le système"],
            [("Scénario nominal", {'b': True}),
             "1. La secrétaire choisit le patient, le médecin, la date et l'heure. "
             "2. Elle précise le motif et le type (présentiel ou en ligne). "
             "3. Le système vérifie l'absence de conflit horaire. "
             "4. Le rendez-vous est créé ; une salle de visioconférence est générée si nécessaire."],
            [("Scénario alternatif", {'b': True}),
             "3a. Conflit détecté → le système refuse et propose un autre créneau."],
            [("Postcondition", {'b': True}), "Le rendez-vous figure dans le planning ; le patient est notifié"],
        ],
        caption="Description du cas d'utilisation « Planifier un rendez-vous »",
        widths=[3.4, 12.6], font_size=9.5)

    # 2.2
    r.h2("2.2 Modélisation dynamique")
    r.body(
        "Les diagrammes de séquence décrivent la chronologie des messages échangés entre les "
        "composants pour réaliser une fonctionnalité donnée. Quatre scénarios critiques sont "
        "détaillés ; ils mettent en lumière la coopération entre le frontend, le backend, le "
        "microservice d'IA, la base de données et les services externes.")

    r.h3("Diagramme de séquence : prédiction IA")
    r.body(
        "Lorsqu'il demande une analyse, le médecin déclenche un appel du frontend React vers le "
        "backend Django, lequel relaie la requête au microservice Flask. Ce dernier construit un "
        "vecteur binaire des symptômes, interroge le modèle Random Forest pour obtenir les "
        "probabilités par pathologie, retient les trois plus élevées, les traduit en français et "
        "leur associe un niveau de risque, avant de renvoyer le résultat qui s'affiche sous forme "
        "de barres de progression.")
    r.figure(SEQ_IA, "Diagramme de séquence — aide au diagnostic par IA", width_cm=15.5)
    r.body("Les principales étapes de cet échange sont récapitulées ci-dessous.")
    r.table(
        ["#", "Émetteur → Récepteur", "Message"],
        [
            ["1", "Médecin → Frontend", "Saisit les symptômes et le contexte"],
            ["2", "Frontend → Backend", "POST /api/consultations/suggestions-ia/"],
            ["3", "Backend → Microservice IA", "POST /predict { symptoms, … }"],
            ["4", "Microservice → Modèle", "predict_proba(vecteur de symptômes)"],
            ["5", "Modèle → Microservice", "Probabilités par pathologie"],
            ["6", "Microservice → Backend", "Top 3 + traduction FR + niveau de risque"],
            ["7", "Backend → Frontend", "{ disponible: true, suggestions: […] }"],
        ],
        caption="Étapes du scénario d'aide au diagnostic", widths=[1.0, 6.0, 9.0], font_size=9)

    r.h3("Diagramme de séquence : authentification JWT")
    r.body(
        "L'authentification repose sur le standard JSON Web Token. L'utilisateur soumet ses "
        "identifiants ; le backend les vérifie et délivre une paire de jetons (accès et "
        "rafraîchissement) que le client stocke. Le jeton d'accès est ensuite joint à chaque "
        "requête protégée pour identifier l'utilisateur et son rôle, et conditionner la "
        "redirection vers le tableau de bord adéquat. Lorsqu'il expire, le jeton de rafraîchissement "
        "permet d'en obtenir un nouveau de manière transparente.")
    r.figure(SEQ_JWT, "Diagramme de séquence — authentification par jeton JWT", width_cm=15.5)

    r.h3("Diagramme de séquence : envoi automatique des documents")
    r.body(
        "Après l'enregistrement d'une ordonnance, le backend répond immédiatement au médecin "
        "(réponse HTTP 201) tandis qu'un fil d'exécution asynchrone prend en charge la suite : "
        "génération des PDF via ReportLab, puis transmission au patient par courriel (SMTP) et par "
        "WhatsApp (Twilio), le tout orchestré par n8n. Le praticien n'attend jamais la fin de ces "
        "traitements, ce qui garantit une interface réactive.")
    r.figure(SEQ_DOCS, "Diagramme de séquence — génération et envoi automatisé des documents",
             width_cm=16.0)

    r.h3("Diagramme d'activité : parcours du patient")
    r.body(
        "Le diagramme d'activité formalise le parcours complet du patient, depuis son inscription "
        "jusqu'à la réception de ses documents, en distinguant les branches « téléconsultation » et "
        "« présentiel ». Un second diagramme détaille, du point de vue interne, le déroulement "
        "d'une consultation côté médecin, depuis la prise de rendez-vous jusqu'à la remise de "
        "l'ordonnance.")
    r.figure(ACT_PAT, "Diagramme d'activité — parcours global du patient", width_cm=9.5)
    r.figure(ACT_DETAIL, "Diagramme d'activité — déroulement détaillé d'une consultation",
             width_cm=8.5)

    # 2.3
    r.h2("2.3 Conception de la base de données")
    r.h3("Modèle conceptuel de données (MCD)")
    r.body(
        "Le modèle conceptuel identifie les entités métier et leurs associations, indépendamment de "
        "toute implémentation technique. Les entités principales sont l'Utilisateur (porteur du "
        "rôle), le Patient, le Rendez-vous, la Consultation et l'Ordonnance (avec ses lignes de "
        "prescription). Les cardinalités traduisent les règles de gestion suivantes :")
    r.bullets([
        "un médecin (utilisateur) peut être associé à plusieurs rendez-vous, consultations et "
        "ordonnances ;",
        "un patient peut avoir plusieurs rendez-vous et plusieurs consultations ;",
        "un rendez-vous donne lieu à au plus une consultation ;",
        "une consultation donne lieu à au plus une ordonnance ;",
        "une ordonnance regroupe une ou plusieurs lignes de prescription.",
    ])

    r.h3("Diagramme de classes UML")
    r.body(
        "Le diagramme de classes raffine le modèle conceptuel en précisant les attributs et leurs "
        "types. Il constitue le socle direct des modèles de l'ORM Django : chaque classe se "
        "matérialise par une table, et chaque association par une clé étrangère.")
    r.figure(CLASS_DIAG, "Diagramme de classes du domaine métier", width_cm=13.5)

    r.h3("Modèle logique de données (MLD) PostgreSQL")
    r.body(
        "La traduction en modèle logique aboutit aux tables relationnelles suivantes, matérialisées "
        "par l'ORM dans la base PostgreSQL. Les noms reprennent la convention Django "
        "« application_modèle ».")
    r.table(
        ["Table", "Rôle", "Clés étrangères principales"],
        [
            [("users_user", {'mono': True}), "Comptes et rôles (médecin, secrétaire, patient, admin)", "—"],
            [("patients_patient", {'mono': True}), "Dossiers patients", [("→ users_user", {'mono': True})]],
            [("appointments_rendezvous", {'mono': True}), "Rendez-vous présentiels / en ligne",
             [("→ patient, → médecin", {'mono': True})]],
            [("consultations_consultation", {'mono': True}), "Consultations + suggestions IA (JSON)",
             [("→ patient, médecin, rdv", {'mono': True})]],
            [("prescriptions_prescription", {'mono': True}), "Ordonnances", [("→ consultation, patient, médecin", {'mono': True})]],
            [("prescriptions_ligneprescription", {'mono': True}), "Lignes de médicaments", [("→ prescription", {'mono': True})]],
            [("auditlog_logentry", {'mono': True}), "Journal d'audit des modifications", [("→ user", {'mono': True})]],
        ],
        caption="Principales tables du modèle logique de données",
        widths=[5.4, 6.8, 3.8], font_size=9)

    r.h3("Dictionnaire de données")
    r.body(
        "Le dictionnaire de données précise, pour les attributs les plus significatifs, leur type "
        "et leur signification métier. L'extrait ci-dessous porte sur les entités centrales du "
        "domaine.")
    r.table(
        ["Entité", "Attribut", "Type", "Description"],
        [
            ["User", ("role", {'mono': True}), "Énum.", "administrateur, medecin, secretaire, patient"],
            ["User", ("specialite", {'mono': True}), "Énum.", "Spécialité médicale (17 valeurs)"],
            ["Patient", ("nom, prenom", {'mono': True}), "Texte", "Identité du patient"],
            ["Patient", ("date_naissance", {'mono': True}), "Date", "Sert au calcul automatique de l'âge"],
            ["Patient", ("cin", {'mono': True}), "Texte (unique)", "Numéro de carte d'identité"],
            ["Patient", ("groupe_sanguin", {'mono': True}), "Énum.", "A+, A-, …, O-"],
            ["Patient", ("allergies, antecedents", {'mono': True}), "Texte long", "Informations médicales libres"],
            ["RendezVous", ("date_heure", {'mono': True}), "Date-heure", "Horodatage du rendez-vous"],
            ["RendezVous", ("duree", {'mono': True}), "Entier", "Durée estimée en minutes (30 par défaut)"],
            ["RendezVous", ("statut", {'mono': True}), "Énum.", "DEMANDE, PLANIFIE, CONFIRME, EN_COURS, TERMINE, ANNULE"],
            ["RendezVous", ("type_consultation", {'mono': True}), "Énum.", "PRESENTIEL ou EN_LIGNE"],
            ["RendezVous", ("lien_visio", {'mono': True}), "Texte", "Salle Jitsi générée (UUID) pour la téléconsultation"],
            ["Consultation", ("symptomes", {'mono': True}), "JSON", "Liste des symptômes observés"],
            ["Consultation", ("suggestions_ia", {'mono': True}), "JSON", "Top 3 pathologies + scores de confiance"],
            ["Consultation", ("ia_utilisee", {'mono': True}), "Booléen", "Trace l'usage du module d'IA"],
            ["LignePrescription", ("medicament, dosage", {'mono': True}), "Texte", "Médicament et dosage (ex. 500 mg)"],
            ["LignePrescription", ("frequence, duree", {'mono': True}), "Texte", "Posologie et durée du traitement"],
        ],
        caption="Extrait du dictionnaire de données",
        widths=[3.0, 4.4, 2.4, 6.2], font_size=8.5)


# ════════════════════════════════════════════════════════════════════════════
# CHAPITRE 3
# ════════════════════════════════════════════════════════════════════════════
def chapter3(r):
    r.chapter("Chapitre 3", "Architecture technique et choix technologiques")
    r.body(
        "Ce chapitre présente l'architecture retenue pour CuraMedical et justifie, couche par "
        "couche, les choix technologiques opérés. Chaque décision a été guidée par un équilibre "
        "entre robustesse, performance, sécurité, et adéquation aux compétences de l'équipe.")

    # 3.1
    r.h2("3.1 Architecture globale du système")
    r.h3("Architecture hybride : monolithe modulaire et microservice IA")
    r.body(
        "L'architecture de CuraMedical est qualifiée d'« hybride » car elle combine deux styles "
        "architecturaux complémentaires. Le cœur métier est un monolithe modulaire bâti avec "
        "Django : il regroupe, au sein d'un même processus, des applications cloisonnées par "
        "domaine (utilisateurs, patients, rendez-vous, consultations, ordonnances). Ce choix "
        "garantit la cohérence transactionnelle des données — essentielle pour un dossier médical — "
        "et simplifie considérablement le développement et le débogage.")
    r.body(
        "À côté de ce noyau, le traitement d'intelligence artificielle est volontairement isolé "
        "dans un microservice Flask indépendant. Cette séparation présente trois avantages : elle "
        "permet de faire évoluer ou de réentraîner le modèle sans impacter l'application "
        "principale ; elle isole la pile scientifique (Scikit-learn, NumPy, Pandas), lourde et "
        "spécifique, du reste du backend ; elle ouvre la voie à une montée en charge indépendante "
        "du composant d'IA, le plus coûteux en calcul.")
    r.h3("Architecture logicielle générale")
    r.body(
        "Le schéma ci-dessous présente l'organisation d'ensemble : une interface React consommée "
        "par les acteurs, un backend Django exposant une API REST, un microservice d'IA, une base "
        "PostgreSQL, un orchestrateur d'automatisation (n8n) et des services externes (Jitsi pour "
        "la visioconférence, Groq pour le raisonnement en langage naturel, Twilio et SMTP pour la "
        "messagerie). L'ensemble s'exécute dans des conteneurs Docker reliés par un réseau privé.")
    r.figure(ARCHI, "Architecture globale du système CuraMedical", width_cm=15.5)
    r.h3("Communication inter-services")
    r.body(
        "Les composants communiquent par des protocoles standard et faiblement couplés. Le frontend "
        "dialogue avec le backend via une API REST en JSON, sécurisée par JWT. Le backend interroge "
        "le microservice d'IA en HTTP interne et persiste les données dans PostgreSQL via l'ORM. "
        "Les notifications sortantes sont déléguées à n8n, qui relaie vers l'e-mail et WhatsApp. "
        "L'ensemble des conteneurs partage un réseau Docker privé, ce qui isole le trafic interne du "
        "réseau public et permet aux services de se joindre par leur nom plutôt que par une adresse "
        "IP.")
    r.table(
        ["De", "Vers", "Protocole", "Usage"],
        [
            ["Frontend", "Backend", "HTTPS / REST", "Toutes les opérations métier"],
            ["Backend", "PostgreSQL", "SQL (ORM)", "Persistance des données"],
            ["Backend", "Microservice IA", "HTTP / JSON", "Prédiction et chatbot"],
            ["Backend", "n8n", "Webhook HTTP", "Déclenchement des notifications"],
            ["Backend", "SMTP / Twilio", "SMTP / API", "E-mail et WhatsApp"],
            ["Frontend", "Jitsi", "WebRTC", "Téléconsultation vidéo"],
        ],
        caption="Matrice de communication entre composants", widths=[3.0, 3.6, 3.4, 6.0], font_size=9)

    # 3.2
    r.h2("3.2 Technologies du backend")
    r.h3("Django et Django REST Framework")
    r.body(
        "Le backend est bâti sur Django 4.2 et Django REST Framework (DRF). Django apporte un ORM "
        "puissant, une interface d'administration générée automatiquement, un système de migrations "
        "et un écosystème mature et éprouvé. DRF y ajoute tout l'outillage nécessaire à la "
        "construction d'API REST : sérialiseurs (validation et transformation des données), jeux de "
        "vues (ViewSets) regroupant les opérations CRUD, routage automatique, filtrage, pagination "
        "et limitation de débit. La documentation de l'API est, de surcroît, générée "
        "automatiquement au format OpenAPI grâce à drf-spectacular, ce qui facilite son exploration "
        "et son intégration.")
    r.body(
        "L'API expose un ensemble cohérent de points d'entrée, organisés par ressource. Le tableau "
        "suivant en présente les principaux.")
    r.table(
        ["Méthode & route", "Description"],
        [
            [("POST /api/token/", {'mono': True}), "Authentification, délivrance des jetons JWT"],
            [("GET /api/users/me/", {'mono': True}), "Profil de l'utilisateur connecté"],
            [("GET·POST /api/patients/", {'mono': True}), "Liste et création des patients"],
            [("GET·POST /api/appointments/", {'mono': True}), "Liste et planification des rendez-vous"],
            [("GET·POST /api/consultations/", {'mono': True}), "Liste et création des consultations"],
            [("POST /api/consultations/suggestions-ia/", {'mono': True}), "Aide au diagnostic (IA)"],
            [("GET /api/consultations/{id}/compte-rendu-pdf/", {'mono': True}), "Compte rendu en PDF"],
            [("GET·POST /api/prescriptions/", {'mono': True}), "Liste et création des ordonnances"],
            [("GET /api/consultations/stats/", {'mono': True}), "Statistiques du tableau de bord"],
        ],
        caption="Principaux points d'entrée de l'API REST", widths=[8.4, 7.6], font_size=9)

    r.h3("PostgreSQL")
    r.body(
        "Le système de gestion de base de données retenu est PostgreSQL 15, pour sa robustesse, sa "
        "conformité au standard SQL, sa gestion transactionnelle (propriétés ACID) et son support "
        "natif du type JSON. Cette dernière caractéristique est précieuse : elle permet de stocker "
        "directement, dans la table des consultations, la liste des symptômes et le détail des "
        "suggestions de l'IA, sans recourir à des tables annexes ni perdre en souplesse.")

    r.h3("Authentification JWT avec SimpleJWT")
    r.body(
        "L'authentification s'appuie sur la bibliothèque djangorestframework-simplejwt. À la "
        "connexion, l'utilisateur reçoit un jeton d'accès (valable 8 heures) et un jeton de "
        "rafraîchissement (valable 7 jours), avec rotation des jetons à chaque renouvellement. "
        "Cette approche « sans état » dispense le serveur de gérer des sessions et s'intègre "
        "naturellement à une application monopage. La configuration est centralisée dans les "
        "paramètres du projet.")
    r.code(
        "SIMPLE_JWT = {\n"
        "    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),\n"
        "    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),\n"
        "    'ROTATE_REFRESH_TOKENS': True,\n"
        "}",
        filename="backend/curamedical/settings.py", language="python")

    r.h3("Gestion des permissions et rôles")
    r.body(
        "Le modèle utilisateur, personnalisé, étend la classe d'authentification de Django et porte "
        "un champ « rôle » ainsi qu'une éventuelle spécialité médicale. Des propriétés de confort "
        "(est_medecin, est_secretaire…) facilitent les contrôles.")
    r.code(
        "class User(AbstractUser):\n"
        "    ROLE_CHOICES = [\n"
        "        ('administrateur', 'Administrateur'),\n"
        "        ('medecin', 'Médecin'),\n"
        "        ('secretaire', 'Secrétaire'),\n"
        "        ('patient', 'Patient'),\n"
        "    ]\n"
        "    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')\n"
        "    specialite = models.CharField(max_length=30, choices=SPECIALITE_CHOICES, null=True)\n"
        "\n"
        "    @property\n"
        "    def est_medecin(self):\n"
        "        return self.role == 'medecin'",
        filename="backend/apps/users/models.py", language="python")

    r.h3("Django Signals")
    r.body(
        "Les signaux de Django permettent de réagir à des événements du cycle de vie des objets — "
        "par exemple la création d'une consultation — afin de déclencher des traitements annexes "
        "tels que la génération de documents ou l'envoi de notifications, sans coupler ces "
        "traitements à la logique des vues. Cette approche événementielle favorise un code propre "
        "et faiblement couplé.")

    r.h3("Configuration SMTP")
    r.body(
        "L'envoi de courriels est paramétré de façon flexible. En développement, les messages sont "
        "affichés dans la console pour faciliter les tests ; en production, ils transitent par un "
        "serveur SMTP (Gmail) via une connexion chiffrée TLS. Conformément aux bonnes pratiques, "
        "les paramètres sensibles (hôte, identifiants, mot de passe d'application) sont injectés par "
        "variables d'environnement et n'apparaissent jamais dans le code source.")

    # 3.3
    r.h2("3.3 Technologies du frontend")
    r.h3("React et Vite")
    r.body(
        "L'interface est une application monopage (SPA) développée avec React 19 et outillée par "
        "Vite, qui offre un serveur de développement quasi instantané (grâce au rechargement à "
        "chaud des modules) et une compilation optimisée pour la production. Le routage est assuré "
        "par React Router, et la communication avec l'API par le client HTTP Axios. Celui-ci est "
        "configuré au moyen d'intercepteurs qui joignent automatiquement le jeton d'accès à chaque "
        "requête et rafraîchissent la session de manière transparente lorsqu'elle expire.")
    r.code(
        "// Injecte le token JWT dans chaque requête\n"
        "api.interceptors.request.use(config => {\n"
        "  const token = localStorage.getItem('access_token')\n"
        "  if (token) config.headers.Authorization = `Bearer ${token}`\n"
        "  return config\n"
        "})\n"
        "\n"
        "// Si 401 → rafraîchissement automatique du token\n"
        "api.interceptors.response.use(r => r, async error => {\n"
        "  if (error.response?.status === 401 && !error.config._retry) {\n"
        "    error.config._retry = true\n"
        "    const refresh = localStorage.getItem('refresh_token')\n"
        "    const res = await axios.post('/api/token/refresh/', { refresh })\n"
        "    localStorage.setItem('access_token', res.data.access)\n"
        "    return api(error.config)   // on rejoue la requête\n"
        "  }\n"
        "  return Promise.reject(error)\n"
        "})",
        filename="frontend/src/api/axios.js", language="javascript")
    r.h3("Design System et CSS personnalisé")
    r.body(
        "L'identité visuelle de CuraMedical s'articule autour d'une teinte verte émeraude, évoquant "
        "l'univers médical, la santé et la sérénité. Le design system, mis en œuvre avec Tailwind "
        "CSS, garantit la cohérence des composants (cartes, boutons, formulaires, tableaux, "
        "badges) et leur adaptation fluide aux différentes tailles d'écran. Les espaces "
        "professionnels (médecin, secrétaire, administrateur) adoptent un thème clair sobre rehaussé "
        "d'accents verts et d'une barre latérale sombre, tandis que la page d'accueil publique "
        "déploie un thème sombre plus marqué pour affirmer la dimension « augmentée par l'IA ».")
    r.h3("Gestion d'état avec Zustand")
    r.body(
        "L'état global de l'application — utilisateur connecté, jetons, file de notifications — est "
        "géré par Zustand, une bibliothèque légère et performante qui évite la verbosité des "
        "solutions plus lourdes tout en offrant une persistance simple dans le navigateur. Cette "
        "sobriété se traduit par un code plus lisible et une courbe d'apprentissage réduite.")
    r.h3("Bibliothèques utilisées")
    r.table(
        ["Bibliothèque", "Usage dans CuraMedical"],
        [
            [("Recharts", {'b': True}), "Graphiques du tableau de bord : courbe d'activité, anneau de répartition des rendez-vous"],
            [("Lucide React", {'b': True}), "Jeu d'icônes vectorielles cohérent dans toute l'interface"],
            [("FullCalendar", {'b': True}), "Affichage et interaction du planning des rendez-vous"],
            [("Jitsi Meet SDK", {'b': True}), "Intégration de la visioconférence pour la téléconsultation"],
            [("TanStack Query", {'b': True}), "Récupération, mise en cache et synchronisation des données serveur"],
            [("React Hot Toast", {'b': True}), "Notifications non bloquantes (succès, erreurs, informations)"],
            [("date-fns", {'b': True}), "Manipulation et formatage des dates"],
        ],
        caption="Principales bibliothèques du frontend", widths=[3.8, 12.2], font_size=10)

    # 3.4
    r.h2("3.4 Module d'Intelligence Artificielle")
    r.h3("Microservice Flask")
    r.body(
        "Le module d'IA est un microservice autonome écrit en Flask, un micro-framework Python léger "
        "particulièrement adapté à l'exposition d'une poignée de points d'entrée. Il met à "
        "disposition plusieurs routes HTTP : /predict pour l'aide au diagnostic, /brain pour "
        "l'assistant conversationnel et la classification d'intentions, et /symptoms pour la liste "
        "des symptômes reconnus. Le modèle est entraîné une seule fois, lors de la construction de "
        "l'image Docker, puis chargé en mémoire au démarrage du conteneur.")
    r.h3("Prétraitement et exploitation du dataset")
    r.body(
        "Le modèle est entraîné sur un jeu de données de grande ampleur reliant des symptômes à des "
        "pathologies. Le prétraitement supprime les observations incomplètes, sépare les variables "
        "explicatives (les symptômes, encodés en variables binaires de présence/absence) de la "
        "variable cible (la maladie), puis encode cette dernière au moyen d'un LabelEncoder. Les "
        "données sont enfin partitionnées en ensembles d'entraînement et de test.")
    r.table(
        ["Caractéristique", "Valeur"],
        [
            [("Observations (lignes)", {'b': True}), "≈ 15 000"],
            [("Symptômes (variables binaires)", {'b': True}), "377"],
            [("Pathologies (classes cibles)", {'b': True}), "> 650"],
            [("Algorithme", {'b': True}), "Random Forest Classifier"],
            [("Sortie du modèle", {'b': True}), "Top 3 des pathologies + probabilité de chacune"],
            [("Format de persistance", {'b': True}), "Sérialisation joblib (.pkl)"],
        ],
        caption="Caractéristiques du jeu de données et du modèle d'IA", widths=[7.0, 9.0], font_size=10)
    r.h3("Algorithme Random Forest Classifier")
    r.body(
        "Le choix s'est porté sur l'algorithme des forêts aléatoires (Random Forest). Cet ensemble "
        "d'arbres de décision, entraînés sur des sous-échantillons aléatoires des données et des "
        "variables, est particulièrement adapté à des données binaires de grande dimension. Il "
        "résiste naturellement au surapprentissage par effet de moyenne, gère sans difficulté les "
        "interactions complexes entre symptômes et fournit, pour chaque pathologie, une probabilité "
        "directement exploitable comme score de confiance. L'entraînement, réalisé par le script "
        "ci-dessous, sérialise le modèle, l'encodeur de labels et la liste des symptômes.")
    r.code(
        "from sklearn.ensemble import RandomForestClassifier\n"
        "from sklearn.preprocessing import LabelEncoder\n"
        "import joblib\n"
        "\n"
        "FEATURES = [c for c in df.columns if c != 'diseases']\n"
        "X, y = df[FEATURES], LabelEncoder().fit_transform(df['diseases'])\n"
        "\n"
        "clf = RandomForestClassifier(n_estimators=30, random_state=42)\n"
        "clf.fit(X_train, y_train)\n"
        "\n"
        "joblib.dump(clf, 'model/classifier.pkl')        # modèle entraîné\n"
        "joblib.dump(FEATURES, 'model/features_list.pkl')  # 377 symptômes",
        filename="ia-service/train.py", language="python")
    r.h3("API de prédiction médicale")
    r.body(
        "À la réception d'une requête, le service construit un vecteur binaire représentant la "
        "présence des symptômes, calcule les probabilités via le modèle, puis retient les trois "
        "pathologies les plus probables. Chacune est renvoyée avec son score exprimé en "
        "pourcentage, un niveau de risque (faible, modéré ou élevé selon des seuils) et une courte "
        "explication mentionnant les symptômes pris en compte.")
    r.code(
        "@app.route('/predict', methods=['POST'])\n"
        "def predict():\n"
        "    symptoms = request.get_json().get('symptoms', [])\n"
        "    vector, final = encode_patient_profile({'symptoms': symptoms})\n"
        "    probabilities = model.predict_proba(vector)[0]\n"
        "    top_indices = np.argsort(probabilities)[-3:][::-1]      # top 3\n"
        "    suggestions = []\n"
        "    for index in top_indices:\n"
        "        confidence = float(probabilities[index]) * 100\n"
        "        disease = EN_TO_FR_DISEASE.get(encoder.classes_[index])\n"
        "        suggestions.append({\n"
        "            'disease': disease,\n"
        "            'confidence': round(confidence, 1),\n"
        "            'risk_level': 'eleve' if confidence > 70 else (\n"
        "                          'modere' if confidence > 30 else 'faible'),\n"
        "        })\n"
        "    return jsonify({'suggestions': suggestions})",
        filename="ia-service/app.py — endpoint /predict", language="python")
    r.h3("Mapping des symptômes")
    r.body(
        "Les médecins saisissant en français alors que le modèle raisonne sur des libellés anglais, "
        "un dictionnaire de correspondance riche — plusieurs centaines de termes et de synonymes — "
        "traduit les symptômes du français vers l'anglais, et les pathologies de l'anglais vers le "
        "français. Une normalisation préalable (passage en minuscules, suppression des accents) "
        "fiabilise cette mise en correspondance et évite les bugs d'encodage.")
    r.code(
        "FR_TO_EN = {\n"
        "    'fièvre': 'fever', 'fievre': 'fever', 'temperature': 'fever',\n"
        "    'toux': 'cough', 'toux sèche': 'cough', 'toux grasse': 'coughing up sputum',\n"
        "    'maux de tête': 'headache', 'migraine': 'headache',\n"
        "    'difficulté respiratoire': 'shortness of breath', 'essoufflement': 'shortness of breath',\n"
        "    # … plusieurs centaines de termes et synonymes couverts\n"
        "}",
        filename="ia-service/app.py — dictionnaire FR→EN", language="python")
    r.body(
        "À ce dispositif s'ajoutent deux briques complémentaires. D'une part, un classifieur "
        "d'intentions, fondé sur une vectorisation TF-IDF et une machine à vecteurs de support "
        "(SVM) linéaire, aiguille l'assistant conversationnel parmi quinze intentions (salutations, "
        "recherche de patient, prise de rendez-vous, statistiques, etc.). D'autre part, un appel "
        "optionnel à un grand modèle de langage (Llama 3, via l'API Groq) permet d'extraire finement "
        "les symptômes d'une phrase libre et de formuler des réponses en langage naturel, avec un "
        "repli automatique sur la correspondance par mots-clés si le service distant est "
        "indisponible.")

    # 3.5
    r.h2("3.5 Automatisation et communication")
    r.h3("Workflow n8n pour les rappels automatiques")
    r.body(
        "n8n est un orchestrateur de flux de travail open source, déployé comme un conteneur du "
        "système. Le backend lui transmet des événements structurés (nouvelle ordonnance, nouveau "
        "compte rendu, rappel programmé) via un webhook ; n8n se charge ensuite d'acheminer les "
        "notifications vers les canaux appropriés. Ce découplage présente l'avantage de pouvoir "
        "modifier ou enrichir les scénarios de communication — ajouter un canal, changer la mise en "
        "forme d'un message — sans toucher au code applicatif.")
    r.h3("Génération des emails médicaux")
    r.body(
        "Les courriels adressés au patient sont composés côté backend et accompagnés des documents "
        "PDF en pièce jointe. Leur envoi s'effectue systématiquement en arrière-plan, dans un fil "
        "d'exécution dédié, afin de ne jamais ralentir l'interface du médecin, même si le serveur "
        "de messagerie répond lentement.")
    r.h3("Génération dynamique des PDF avec ReportLab")
    r.body(
        "Les ordonnances et les comptes rendus sont produits dynamiquement avec la bibliothèque "
        "ReportLab. Les documents reprennent la charte de la clinique (en-tête du médecin et de "
        "l'établissement, couleur verte, tableau des prescriptions, cachet et signature) et sont "
        "générés à la volée à partir des données réellement enregistrées, ce qui garantit leur "
        "exactitude et leur fraîcheur.")
    r.h3("Journalisation avec django-auditlog")
    r.body(
        "La traçabilité est assurée par django-auditlog, qui enregistre automatiquement toute "
        "création, modification ou suppression sur les modèles sensibles (patients, consultations, "
        "ordonnances), avec horodatage et identification de l'auteur. Ce mécanisme, transversal à "
        "l'application, est détaillé au chapitre 5.")


# ════════════════════════════════════════════════════════════════════════════
# CHAPITRE 4
# ════════════════════════════════════════════════════════════════════════════
def chapter4(r):
    r.chapter("Chapitre 4", "Réalisation et implémentation")
    r.body(
        "Ce chapitre illustre la concrétisation des choix de conception exposés précédemment. Il "
        "présente d'abord l'organisation concrète du code, puis les interfaces réalisées pour "
        "chaque profil d'utilisateur, et enfin les fonctionnalités avancées qui font la "
        "singularité de CuraMedical. Les captures d'écran qui jalonnent ce chapitre sont issues de "
        "l'application réellement déployée et fonctionnelle.")

    # 4.1
    r.h2("4.1 Environnement de développement")
    r.h3("Structure Monorepo")
    r.body(
        "Le projet est organisé en monorepo : un dépôt Git unique regroupe les trois composants "
        "applicatifs et leur orchestration. Cette structure simplifie la cohérence des versions, le "
        "partage de la configuration et la coordination entre les membres de l'équipe, chacun "
        "pouvant travailler sur son composant sans rompre l'ensemble.")
    r.code(
        "curamedical/\n"
        "├── backend/        # API REST (Django + DRF)\n"
        "├── frontend/       # Interface (React 19 + Vite)\n"
        "├── ia-service/     # Microservice IA (Flask + Scikit-learn)\n"
        "├── docker-compose.yml\n"
        "└── .env            # variables d'environnement (non versionné)",
        filename="Arborescence du dépôt", language="text")
    r.h3("Organisation du backend Django")
    r.body(
        "Le backend suit le principe « une application par domaine métier ». Chaque application "
        "encapsule ses propres modèles, sérialiseurs, vues, routes et signaux, ce qui favorise la "
        "lisibilité, la réutilisation et la maintenabilité du code.")
    r.code(
        "backend/apps/\n"
        "├── users/          # comptes, rôles, authentification\n"
        "├── patients/       # dossiers patients\n"
        "├── appointments/   # rendez-vous et planning\n"
        "├── consultations/  # consultations + client IA + PDF\n"
        "├── prescriptions/  # ordonnances + génération PDF\n"
        "├── chat/           # assistant conversationnel\n"
        "├── whatsapp/       # notifications WhatsApp (Twilio)\n"
        "└── common/         # utilitaires partagés (n8n, permissions)",
        filename="backend/apps/ — applications métier", language="text")
    r.h3("Organisation du frontend React")
    r.body(
        "Le frontend distingue clairement les pages (une par espace fonctionnel), les composants "
        "réutilisables (barre de navigation, fenêtres de confirmation, widget de chatbot), les "
        "magasins d'état (authentification, notifications) et la couche d'accès à l'API.")
    r.code(
        "frontend/src/\n"
        "├── pages/        # Login, Dashboard, Patients, Appointments,\n"
        "│                 # Consultations, Prescriptions, Admin, Video…\n"
        "├── components/   # Navbar, Layout, ChatbotWidget, PrivateRoute…\n"
        "├── store/        # authStore, toastStore (Zustand)\n"
        "└── api/          # axios (intercepteurs JWT)",
        filename="frontend/src/ — organisation", language="text")

    # 4.2
    r.h2("4.2 Interfaces utilisateur (UI/UX)")
    r.body(
        "Cette section présente, espace par espace, les principales interfaces de la plateforme. "
        "L'ensemble respecte une charte cohérente — vert émeraude, typographie claire, composants "
        "uniformes — et un principe de retour visuel immédiat.")

    r.h3("Authentification et inscription")
    r.body(
        "La page d'accueil publique présente la plateforme et met en avant sa dimension « augmentée "
        "par l'IA ». Elle adopte un thème sombre rehaussé d'accents verts, conférant à la solution "
        "une identité moderne et professionnelle, et expose un aperçu du tableau de bord pour "
        "donner immédiatement à voir la valeur du produit.")
    r.figure(shot("01-accueil-landing.png"), "Page d'accueil publique de CuraMedical")
    r.body(
        "La connexion s'effectue via une fenêtre modale épurée. Le formulaire valide les "
        "informations saisies et signale clairement toute erreur d'authentification.")
    r.figure(shot("02-connexion-modale.png"), "Fenêtre de connexion")
    r.figure(shot("40-connexion-formulaire-rempli.png"), "Formulaire de connexion renseigné")
    r.body(
        "L'inscription est réservée au patient, qui crée lui-même son compte pour accéder à son "
        "espace personnel. Les autres comptes (médecin, secrétaire) sont créés par "
        "l'administrateur.")
    r.figure(shot("03-inscription-patient.png"), "Formulaire d'inscription d'un patient")
    r.figure(shot("31-inscription-patient-abdou-salou.png"), "Exemple d'inscription renseignée")

    r.h3("Tableau de bord Médecin")
    r.body(
        "Dès sa connexion, le médecin accède à un tableau de bord synthétique matérialisant le "
        "besoin BF-06 : indicateurs clés (patients actifs, rendez-vous, consultations, analyses "
        "IA), courbe d'évolution mensuelle de l'activité, anneau de répartition des statuts de "
        "rendez-vous, taux d'adoption de l'IA et liste des principaux diagnostics. Chaque carte "
        "affiche en outre la variation par rapport au mois précédent.")
    r.figure(shot("08-medecin-tableau-de-bord.png"), "Tableau de bord du médecin")
    r.body(
        "La liste des patients offre une recherche instantanée et un accès rapide à chaque dossier. "
        "La recherche filtre dynamiquement la liste à mesure de la saisie.")
    r.figure(shot("09-medecin-liste-patients.png"), "Liste des patients du médecin")
    r.figure(shot("32-medecin-recherche-patient.png"), "Recherche instantanée d'un patient")
    r.body(
        "La fiche patient agrège l'ensemble des informations administratives et médicales (identité, "
        "coordonnées, groupe sanguin, allergies, antécédents) ainsi que l'historique des "
        "consultations et des documents associés.")
    r.figure(shot("11-medecin-fiche-patient.png"), "Fiche détaillée d'un patient")

    r.h3("Tableau de bord Secrétaire")
    r.body(
        "L'espace de la secrétaire est centré sur l'administratif. Le tableau de bord récapitule "
        "l'activité du jour, tandis que la gestion des patients et du planning constitue le cœur de "
        "son activité quotidienne.")
    r.figure(shot("22-secretaire-tableau-de-bord.png"), "Tableau de bord de la secrétaire")
    r.figure(shot("23-secretaire-patients.png"), "Gestion des patients par la secrétaire")
    r.body(
        "La création d'un dossier patient s'effectue via un formulaire structuré et guidé, "
        "regroupant identité, coordonnées et informations médicales.")
    r.figure(shot("10-secretaire-nouveau-patient.png"), "Création d'un nouveau dossier patient")
    r.body(
        "Le planning des rendez-vous est présenté sous forme de calendrier interactif, autorisant "
        "une lecture immédiate de la charge et la détection visuelle des créneaux disponibles.")
    r.figure(shot("24-secretaire-planning-rdv.png"), "Planning des rendez-vous (vue calendrier)")

    r.h3("Tableau de bord Administrateur")
    r.body(
        "L'administrateur supervise les comptes et la configuration. Son tableau de bord présente "
        "des indicateurs de gestion du système, distincts des données médicales auxquelles il n'a "
        "pas accès.")
    r.figure(shot("04-admin-tableau-de-bord.png"), "Tableau de bord de l'administrateur")
    r.body(
        "Il crée les comptes du personnel (médecins, secrétaires), gère leur cycle de vie et "
        "dispose d'une corbeille permettant un archivage réversible.")
    r.figure(shot("05-admin-gestion-utilisateurs.png"), "Gestion des comptes utilisateurs")
    r.figure(shot("06-admin-creation-compte.png"), "Création d'un compte utilisateur")
    r.figure(shot("07-admin-corbeille-patients.png"), "Corbeille (archivage réversible)")

    r.h3("Portail Patient")
    r.body(
        "Le patient dispose d'un espace personnel clair où il retrouve, en un coup d'œil, ses "
        "prochains rendez-vous et ses documents récents.")
    r.figure(shot("26-patient-espace-personnel.png"), "Espace personnel du patient")
    r.figure(shot("27-patient-mes-rendez-vous.png"), "Suivi des rendez-vous du patient")
    r.figure(shot("28-patient-mes-consultations.png"), "Historique des consultations du patient")
    r.body(
        "Il télécharge ses ordonnances et comptes rendus au format PDF, et met à jour les "
        "informations de son profil.")
    r.figure(shot("29-patient-mes-ordonnances.png"), "Ordonnances accessibles depuis le portail")
    r.figure(shot("30-patient-mon-profil.png"), "Profil du patient")

    # 4.3
    r.h2("4.3 Implémentation des fonctionnalités avancées")
    r.h3("Consultation assistée par IA")
    r.body(
        "La consultation est l'espace clinique central. La liste des consultations en présente "
        "l'historique, avec une indication visuelle de celles ayant mobilisé le module d'IA.")
    r.figure(shot("15-medecin-consultations.png"), "Liste des consultations")
    r.body(
        "La création d'une consultation constitue le scénario le plus riche de l'application. Le "
        "médecin sélectionne un patient, coche les symptômes observés parmi une liste structurée, "
        "renseigne quelques éléments de contexte (âge, sexe, tension, cholestérol) puis lance "
        "l'analyse.")
    r.figure(shot("16-medecin-nouvelle-consultation-ia.png"),
             "Saisie d'une consultation et sélection des symptômes")
    r.body(
        "Le module d'IA retourne en quelques instants les trois pathologies les plus probables, "
        "chacune assortie d'un pourcentage de confiance et d'un niveau de risque représenté "
        "visuellement par une barre de progression colorée.")
    r.figure(shot("33-medecin-consultation-analyse-ia.png"),
             "Résultats de l'aide au diagnostic (top 3 des pathologies)")
    r.body(
        "Côté serveur, l'enregistrement d'une consultation déclenche, dans un fil d'exécution "
        "asynchrone, la production et l'envoi du compte rendu, sans bloquer la réponse au médecin.")
    r.code(
        "def perform_create(self, serializer):\n"
        "    consultation = serializer.save(medecin=self.request.user, patient=patient)\n"
        "    if consultation.rendez_vous:\n"
        "        consultation.rendez_vous.statut = 'TERMINE'\n"
        "        consultation.rendez_vous.save(update_fields=['statut'])\n"
        "    # Envoi du compte rendu en arrière-plan (thread non bloquant)\n"
        "    threading.Thread(\n"
        "        target=self._send_consultation_report_notification,\n"
        "        args=(consultation.id,), daemon=True,\n"
        "    ).start()",
        filename="backend/apps/consultations/views.py", language="python")
    r.body(
        "L'enchaînement technique complet de ce scénario — de la saisie des symptômes jusqu'au "
        "téléchargement du PDF de l'ordonnance — est résumé par le diagramme de séquence ci-dessous.")
    r.figure(SEQ_CONSULT, "Diagramme de séquence complet du processus de consultation",
             width_cm=16.0)
    r.body(
        "Une fois la consultation enregistrée, son détail récapitule les symptômes, le diagnostic "
        "retenu par le médecin et les suggestions de l'IA, conservées à titre de trace.")
    r.figure(shot("17-medecin-consultation-detail.png"), "Détail d'une consultation enregistrée")

    r.h3("Génération des documents PDF")
    r.body(
        "La liste des ordonnances permet de retrouver et de rééditer chaque document. Depuis la "
        "consultation, le médecin compose l'ordonnance ligne par ligne : médicament, dosage, unité, "
        "fréquence, durée et instructions particulières.")
    r.figure(shot("18-medecin-ordonnances.png"), "Liste des ordonnances")
    r.figure(shot("19-medecin-nouvelle-ordonnance.png"), "Rédaction d'une ordonnance")
    r.body(
        "À l'enregistrement, l'ordonnance et le compte rendu sont générés au format PDF avec la "
        "charte de la clinique, puis transmis au patient. Des exemples de ces documents figurent en "
        "annexe A3.")

    r.h3("Téléconsultation avec Jitsi Meet")
    r.body(
        "La gestion des rendez-vous distingue les consultations présentielles des téléconsultations. "
        "Le médecin visualise ses rendez-vous et peut en créer de nouveaux en quelques clics, avec "
        "détection automatique des conflits horaires.")
    r.figure(shot("12-medecin-rendez-vous.png"), "Vue des rendez-vous du médecin")
    r.figure(shot("13-medecin-nouveau-rdv.png"), "Création d'un nouveau rendez-vous")
    r.body(
        "Lorsqu'un rendez-vous est de type « en ligne », le système génère automatiquement un "
        "identifiant de salle unique, comme l'illustre l'extrait de code suivant.")
    r.code(
        "def save(self, *args, **kwargs):\n"
        "    # Identifiant de salle unique pour une téléconsultation\n"
        "    if self.type_consultation == 'EN_LIGNE' and not self.lien_visio:\n"
        "        unique_id = uuid.uuid4().hex[:8]\n"
        "        self.lien_visio = f\"CuraMedical-RDV-{unique_id}\"\n"
        "    super().save(*args, **kwargs)",
        filename="backend/apps/appointments/models.py", language="python")
    r.body(
        "Le médecin et le patient rejoignent alors une salle de visioconférence sécurisée, intégrée "
        "directement dans l'interface grâce au SDK Jitsi Meet, sans installation de logiciel tiers. "
        "Un espace de prise de notes accompagne la séance.")
    r.figure(shot("20-medecin-teleconsultation.png"), "Salle de téléconsultation intégrée")
    r.figure(shot("37-medecin-teleconsultation-salle-notes.png"),
             "Téléconsultation avec prise de notes en direct")
    r.body(
        "Une corbeille des rendez-vous permet par ailleurs d'annuler et de restaurer un rendez-vous "
        "sans suppression définitive immédiate.")
    r.figure(shot("14-medecin-rdv-corbeille.png"), "Corbeille des rendez-vous")

    r.h3("Assistant conversationnel (chatbot IA)")
    r.body(
        "Un assistant conversationnel est accessible en permanence depuis l'interface du personnel "
        "soignant. Comprenant des intentions formulées en langage naturel, il oriente l'utilisateur "
        "vers les fonctionnalités et répond à ses questions courantes.")
    r.figure(shot("21-medecin-chatbot-ia.png"), "Assistant conversationnel intégré")
    r.body(
        "Il sait notamment renseigner le nombre de patients, lister les rendez-vous du jour ou "
        "restituer des statistiques d'activité, en s'appuyant sur le contexte réel du cabinet.")
    r.figure(shot("34-medecin-chatbot-nombre-patients.png"), "L'assistant indique le nombre de patients")
    r.figure(shot("35-medecin-chatbot-rendez-vous-jour.png"), "L'assistant liste les rendez-vous du jour")
    r.figure(shot("36-medecin-chatbot-statistiques.png"), "L'assistant restitue des statistiques")

    # 4.4
    r.h2("4.4 Workflows automatisés")
    r.h3("Confirmation automatique des rendez-vous")
    r.body(
        "À la création d'un rendez-vous par la secrétaire, le patient reçoit une confirmation "
        "automatique récapitulant la date, l'heure, le motif et, le cas échéant, le lien de "
        "téléconsultation. Aucune démarche manuelle n'est requise de la part du personnel.")
    r.h3("Rappel automatique 24 h avant la consultation")
    r.body(
        "Un flux n8n programmé adresse au patient un rappel la veille de son rendez-vous. Ce "
        "dispositif réduit sensiblement le nombre de rendez-vous manqués et fluidifie "
        "l'organisation du cabinet.")
    r.h3("Envoi automatisé des documents médicaux")
    r.body(
        "À l'issue d'une consultation et de la rédaction de l'ordonnance, les PDF sont produits en "
        "arrière-plan puis transmis au patient par courriel et par WhatsApp. La fonction utilitaire "
        "ci-dessous encapsule l'appel au webhook n8n, en y joignant le document encodé.")
    r.code(
        "def send_to_n8n_automation(data, binary_data=None, filename=None):\n"
        "    url = settings.N8N_WEBHOOK_URL\n"
        "    payload = {\n"
        "        'event': data.get('event'),\n"
        "        'patient': data.get('patient_name'),\n"
        "        'email': data.get('patient_email'),\n"
        "        'doctor': data.get('doctor_name'),\n"
        "        'date': data.get('date'),\n"
        "    }\n"
        "    if binary_data:                       # PDF en pièce jointe\n"
        "        payload['file'] = base64.b64encode(binary_data).decode('utf-8')\n"
        "        payload['filename'] = filename or 'document.pdf'\n"
        "    requests.post(url, json=payload, timeout=15)",
        filename="backend/apps/common/utils.py", language="python")
    r.body(
        "Ce traitement, totalement transparent pour le praticien, garantit que le patient dispose "
        "de ses documents sans délai et de façon traçable, tout en préservant la réactivité de "
        "l'interface.")

    r.h3("Assistant WhatsApp conversationnel (Twilio)")
    r.body(
        "L'une des fonctionnalités les plus abouties de CuraMedical est l'assistant WhatsApp, qui "
        "prolonge la plateforme directement dans la messagerie du patient. Connecté à l'API Twilio "
        "et au microservice d'IA, cet agent conversationnel comprend aussi bien les messages texte "
        "que les notes vocales : la parole du patient est transcrite, puis analysée afin d'en "
        "extraire l'intention (prendre un rendez-vous, demander un document) et les informations "
        "utiles (date, heure, motif). Le patient peut ainsi gérer son parcours de soins sans jamais "
        "quitter WhatsApp.")
    r.body(
        "La séquence de captures ci-dessous illustre un échange réel de bout en bout : le patient "
        "salue l'assistant, exprime par une note vocale son souhait de « prendre un rendez-vous en "
        "ligne pour le lundi 8 juin à 9 h », précise le motif (« fièvre ») et le type "
        "(téléconsultation). L'assistant établit un récapitulatif, enregistre la demande après "
        "confirmation, génère et transmet le lien de visioconférence Jitsi, puis — sur simple "
        "demande vocale — renvoie l'ordonnance correspondante au format PDF.")
    r.figures_row(
        [shot("Whatsap_Test_1.jpg"), shot("Whatsap_Test_2.jpg"), shot("Whatsap_Test_3.jpg")],
        "Parcours patient complet via l'assistant WhatsApp (Twilio + IA)",
        width_cm_each=5.0,
        sublabels=["1. Note vocale → prise de RDV",
                   "2. Confirmation + lien Jitsi",
                   "3. Envoi de l'ordonnance PDF"])
    r.body(
        "Cet assistant met en synergie l'ensemble des briques du projet : la reconnaissance "
        "d'intentions et l'extraction d'entités du module d'IA, la génération automatique des "
        "salles Jitsi, la production des PDF par ReportLab et l'acheminement multicanal orchestré "
        "par n8n. Il offre au patient une expérience moderne et accessible, depuis l'outil de "
        "messagerie qu'il utilise déjà au quotidien.")


# ════════════════════════════════════════════════════════════════════════════
# CHAPITRE 5
# ════════════════════════════════════════════════════════════════════════════
def chapter5(r):
    r.chapter("Chapitre 5", "Sécurité et traçabilité")
    r.body(
        "Les données de santé comptent parmi les informations les plus sensibles qui soient ; leur "
        "protection est une exigence à la fois éthique, réglementaire et technique. La sécurité et "
        "la traçabilité ont donc constitué une préoccupation transversale tout au long du projet, "
        "et non une couche ajoutée après coup. Ce chapitre détaille les mécanismes mis en œuvre, "
        "organisés selon le principe de défense en profondeur.")

    # 5.1
    r.h2("5.1 Sécurité de l'application")
    r.h3("Authentification et autorisation JWT")
    r.body(
        "L'accès à la plateforme est conditionné par une authentification par jeton JWT. Le serveur "
        "ne conserve aucune session : chaque requête protégée porte le jeton d'accès, dont la "
        "validité est limitée dans le temps (8 heures), tandis qu'un jeton de rafraîchissement "
        "permet de prolonger la session de façon contrôlée et avec rotation. Cette conception "
        "« sans état » réduit la surface d'attaque, simplifie la montée en charge et s'intègre "
        "naturellement à l'application monopage.")
    r.h3("Sécurisation des routes API")
    r.body(
        "Par défaut, toutes les routes de l'API exigent une authentification. Au-delà, des "
        "permissions fines, fondées sur le rôle, sont appliquées à chaque action ; ces permissions "
        "sont déclarées sous forme de classes réutilisables.")
    r.code(
        "class EstMedecin(permissions.BasePermission):\n"
        "    def has_permission(self, request, view):\n"
        "        return request.user.is_authenticated and request.user.role == 'medecin'\n"
        "\n"
        "class EstAdministrateur(permissions.BasePermission):\n"
        "    def has_permission(self, request, view):\n"
        "        return (request.user.is_authenticated and\n"
        "                (request.user.role == 'administrateur' or request.user.is_superuser))",
        filename="backend/apps/users/permissions.py", language="python")
    r.body(
        "En complément, les jeux de requêtes sont systématiquement filtrés selon l'utilisateur "
        "courant, de sorte qu'un médecin ne puisse jamais accéder aux consultations d'un confrère, "
        "et que l'administrateur reste exclu de toute donnée médicale.")
    r.code(
        "def get_queryset(self):\n"
        "    user = self.request.user\n"
        "    qs = Consultation.objects.filter(est_supprime=False)\n"
        "    if user.role == 'medecin':\n"
        "        return qs.filter(medecin=user)        # ses seules consultations\n"
        "    if user.role == 'patient':\n"
        "        return qs.filter(patient__utilisateur=user)\n"
        "    if user.role == 'secretaire':\n"
        "        return qs.all()\n"
        "    return Consultation.objects.none()        # admin : aucun accès médical",
        filename="backend/apps/consultations/views.py", language="python")
    r.body(
        "Cette défense « en profondeur » se vérifie aussi côté interface : lorsqu'un utilisateur "
        "tente d'atteindre une page non autorisée par son rôle, l'accès lui est explicitement "
        "refusé, comme l'illustre la capture suivante.")
    r.figure(shot("25-secretaire-acces-refuse.png"),
             "Refus d'accès à une page réservée (contrôle d'accès par rôle)")
    r.h3("Protection des données et validation")
    r.body(
        "Plusieurs garde-fous renforcent la robustesse de l'ensemble : limitation du débit des "
        "requêtes pour contrer les attaques par force brute sur la connexion, validation "
        "systématique des données entrantes par les sérialiseurs, restriction des origines "
        "autorisées (CORS), chiffrement des échanges et externalisation des secrets dans des "
        "variables d'environnement plutôt que dans le code source. La limitation de débit est "
        "configurée globalement.")
    r.code(
        "REST_FRAMEWORK = {\n"
        "    'DEFAULT_THROTTLE_CLASSES': [\n"
        "        'rest_framework.throttling.AnonRateThrottle',\n"
        "        'rest_framework.throttling.UserRateThrottle',\n"
        "    ],\n"
        "    'DEFAULT_THROTTLE_RATES': {\n"
        "        'anon': '30/minute',     # protège /api/token/ du brute-force\n"
        "        'user': '300/minute',\n"
        "    },\n"
        "}",
        filename="backend/curamedical/settings.py", language="python")
    r.table(
        ["Mécanisme", "Mise en œuvre"],
        [
            [("Authentification", {'b': True}), "Jetons JWT (accès 8 h, rafraîchissement 7 j, rotation)"],
            [("Autorisation", {'b': True}), "Permissions DRF par rôle + filtrage systématique des requêtes"],
            [("Anti-force brute", {'b': True}), "Limitation de débit (30/min anonyme, 300/min authentifié)"],
            [("Validation", {'b': True}), "Sérialiseurs DRF, contraintes de modèle, unicité du CIN"],
            [("Cloisonnement réseau", {'b': True}), "CORS restreint, réseau Docker privé"],
            [("Gestion des secrets", {'b': True}), "Variables d'environnement (clé secrète, SMTP, clés d'API)"],
            [("Confidentialité", {'b': True}), "Administrateur exclu des données médicales"],
        ],
        caption="Synthèse des mesures de sécurité", widths=[4.4, 11.6], font_size=10)

    # 5.2
    r.h2("5.2 Traçabilité et audit")
    r.h3("Utilisation de django-auditlog")
    r.body(
        "Les modèles sensibles (Patient, Consultation, Prescription) sont enregistrés auprès de "
        "django-auditlog. Toute opération de création, de modification ou de suppression est ainsi "
        "automatiquement consignée, avec la valeur des champs avant et après l'action. "
        "L'enregistrement est déclaratif et tient en une ligne par modèle.")
    r.code(
        "from auditlog.registry import auditlog\n"
        "\n"
        "class Consultation(models.Model):\n"
        "    # … champs du modèle …\n"
        "    pass\n"
        "\n"
        "auditlog.register(Consultation)   # journalisation automatique",
        filename="backend/apps/consultations/models.py", language="python")
    r.h3("Interface d'administration des journaux")
    r.body(
        "Les journaux sont consultables depuis l'interface d'administration de Django, où "
        "l'administrateur peut filtrer les entrées par modèle, par type d'action ou par auteur, et "
        "remonter l'historique complet d'un enregistrement donné. Cette traçabilité est "
        "indispensable tant pour la conformité réglementaire que pour l'investigation en cas "
        "d'incident.")
    r.h3("Identification des actions utilisateurs via middleware JWT")
    r.body(
        "Un intergiciel (middleware) dédié associe chaque entrée de journal à l'utilisateur "
        "réellement à l'origine de la requête, identifié grâce au jeton JWT. Il devient ainsi "
        "possible de répondre précisément à la question « qui a fait quoi, et quand ? » sur "
        "n'importe quelle donnée sensible, ce qui constitue un pilier de la responsabilité et de la "
        "transparence du système.")


# ════════════════════════════════════════════════════════════════════════════
# CHAPITRE 6
# ════════════════════════════════════════════════════════════════════════════
def chapter6(r):
    r.chapter("Chapitre 6", "Déploiement avec Docker")
    r.body(
        "Le déploiement de CuraMedical repose entièrement sur la conteneurisation, gage de "
        "portabilité et de reproductibilité. Ce chapitre décrit la mise en conteneur de chaque "
        "service, leur orchestration au moyen de Docker Compose et la procédure de mise en "
        "production.")

    # 6.1
    r.h2("6.1 Conteneurisation des services")
    r.body(
        "Chaque composant dispose de son propre fichier Dockerfile, qui décrit, étape par étape, "
        "l'image à construire. Une attention particulière a été portée à l'ordre des instructions "
        "afin de tirer parti du cache de Docker : les dépendances, qui changent rarement, sont "
        "installées avant la copie du code source, qui change souvent. Les reconstructions s'en "
        "trouvent considérablement accélérées.")
    r.h3("Dockerfile Backend")
    r.body(
        "L'image du backend part d'une base Python légère, installe les dépendances système (pilote "
        "PostgreSQL, compilateur) et Python, copie le code, puis applique automatiquement les "
        "migrations au démarrage avant de lancer le serveur d'application Gunicorn avec plusieurs "
        "processus de travail.")
    r.code(
        "FROM python:3.12-slim\n"
        "WORKDIR /app\n"
        "RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY . .\n"
        "COPY entrypoint.sh /entrypoint.sh\n"
        "RUN chmod +x /entrypoint.sh\n"
        "EXPOSE 8000\n"
        "ENTRYPOINT [\"/entrypoint.sh\"]",
        filename="backend/Dockerfile", language="docker")
    r.h3("Dockerfile Frontend")
    r.body(
        "L'image du frontend repose sur Node.js. Les dépendances sont installées en premier — pour "
        "bénéficier du cache — puis le code est copié et le serveur Vite est lancé.")
    r.code(
        "FROM node:20-alpine\n"
        "WORKDIR /app\n"
        "COPY package.json package-lock.json ./\n"
        "RUN npm install\n"
        "COPY . .\n"
        "EXPOSE 3000\n"
        "CMD [\"npm\", \"run\", \"dev\"]",
        filename="frontend/Dockerfile", language="docker")
    r.h3("Dockerfile Microservice IA")
    r.body(
        "Particularité notable : le modèle d'IA est entraîné pendant la construction de l'image — "
        "et non au démarrage du conteneur. Ainsi, tant que le jeu de données et le script "
        "d'entraînement ne changent pas, Docker réutilise la couche en cache et le conteneur "
        "démarre instantanément, avec le modèle déjà prêt en mémoire.")
    r.code(
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "RUN apt-get update && apt-get install -y --no-install-recommends build-essential\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY Fast_Dataset.csv train.py intent_classifier.py intents_data.py ./\n"
        "RUN python train.py            # entraînement pendant le BUILD\n"
        "COPY . .\n"
        "EXPOSE 5000\n"
        "CMD [\"python\", \"app.py\"]",
        filename="ia-service/Dockerfile", language="docker")
    r.h3("Base de données PostgreSQL conteneurisée")
    r.body(
        "La base de données s'appuie sur l'image officielle PostgreSQL 15. Ses données sont "
        "persistées dans un volume Docker dédié — elles survivent donc à la recréation du conteneur "
        "— et une sonde de santé (healthcheck) garantit que le backend ne démarre qu'une fois la "
        "base réellement prête à accepter des connexions.")

    # 6.2
    r.h2("6.2 Orchestration avec Docker Compose")
    r.h3("Configuration du fichier docker-compose.yml")
    r.body(
        "Le fichier docker-compose.yml décrit l'ensemble des services et leurs relations : base de "
        "données, backend, frontend, microservice d'IA et orchestrateur n8n. Il fixe pour chacun "
        "l'image ou le contexte de construction, les ports exposés, les variables d'environnement "
        "et les dépendances de démarrage.")
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
    r.figure(DEPLOY, "Diagramme de déploiement des conteneurs", width_cm=10.5)
    r.h3("Gestion des variables d'environnement")
    r.body(
        "La configuration sensible (clé secrète, identifiants de base de données, paramètres SMTP, "
        "clés d'API) est centralisée dans un fichier .env, injecté au moment de l'exécution. Cette "
        "séparation entre code et configuration respecte les bonnes pratiques (méthodologie « "
        "Twelve-Factor App ») et facilite le passage d'un environnement à l'autre sans modifier le "
        "code.")
    r.table(
        ["Service", "Image / Build", "Port", "Rôle"],
        [
            [("db", {'mono': True}), "postgres:15", "5432", "Base de données relationnelle"],
            [("backend", {'mono': True}), "build ./backend", "8000", "API REST Django (Gunicorn)"],
            [("frontend", {'mono': True}), "build ./frontend", "3000", "Interface React (Vite)"],
            [("ia-service", {'mono': True}), "build ./ia-service", "5000", "Microservice IA Flask"],
            [("n8n", {'mono': True}), "n8nio/n8n", "5678", "Automatisation des notifications"],
        ],
        caption="Services orchestrés par Docker Compose", widths=[2.8, 4.4, 1.8, 7.0], font_size=9.5)
    r.h3("Communication inter-conteneurs")
    r.body(
        "Tous les services partagent un réseau Docker privé de type « bridge ». Au sein de ce "
        "réseau, ils se joignent par leur nom de service plutôt que par une adresse IP ; le backend "
        "atteint ainsi le microservice d'IA et l'orchestrateur n8n de façon transparente, sans "
        "exposer ce trafic au réseau extérieur.")

    # 6.3
    r.h2("6.3 Procédure de déploiement")
    r.h3("Étapes de mise en production")
    r.body(
        "La mise en service complète tient en quelques commandes, ce qui illustre la portabilité "
        "obtenue grâce à la conteneurisation :")
    r.bullets([
        "cloner le dépôt et renseigner le fichier .env à partir du modèle fourni ;",
        "construire et lancer l'ensemble des conteneurs avec Docker Compose ;",
        "appliquer les migrations de base de données et initialiser les comptes par défaut.",
    ], style='number')
    r.h3("Commandes de démarrage et d'arrêt")
    r.code(
        "# Construction et démarrage de tous les services\n"
        "docker-compose up --build\n"
        "\n"
        "# Initialisation de la base (dans un autre terminal)\n"
        "docker-compose exec backend python manage.py migrate\n"
        "docker-compose exec backend python manage.py init_accounts\n"
        "\n"
        "# Arrêt des services\n"
        "docker-compose down",
        filename="Terminal — déploiement", language="bash")
    r.callout(
        "À retenir.",
        "Grâce à Docker, l'intégralité de la plateforme — base de données, backend, frontend, "
        "microservice d'IA et automatisation — se déploie de manière identique sur n'importe quel "
        "poste disposant de Docker, en une seule commande. Cette reproductibilité a grandement "
        "fiabilisé le travail collaboratif et la préparation de la démonstration de soutenance.")
