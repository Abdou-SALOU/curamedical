"""Normalisation des numéros de téléphone au format international E.164.

Indispensable pour que l'identification d'un patient par son numéro WhatsApp
soit fiable : WhatsApp envoie toujours un numéro international (« +212600112233 »)
alors que les fiches sont souvent saisies en local (« 0600112233 »). Sans
normalisation, les deux ne correspondent pas — ou pire, peuvent correspondre au
mauvais dossier.

Pays par défaut : Maroc (indicatif 212). Adapter DEFAULT_COUNTRY_CODE au besoin.
"""
import re

DEFAULT_COUNTRY_CODE = "212"  # Maroc


def normalize_phone(raw, default_cc=DEFAULT_COUNTRY_CODE):
    """Retourne le numéro au format E.164 (« +212600112233 »).

    Gère les saisies courantes :
      « 0600112233 »        -> « +212600112233 »
      « 06 00 11 22 33 »    -> « +212600112233 »
      « +212600112233 »     -> inchangé
      « 00212600112233 »    -> « +212600112233 »
      « 212600112233 »      -> « +212600112233 »
      « 600112233 »         -> « +212600112233 »

    Renvoie une chaîne vide pour une entrée vide, et la valeur nettoyée telle
    quelle si elle ne correspond à aucun motif connu (on ne devine pas).
    """
    if raw is None:
        return raw
    # Ne garder que les chiffres et un éventuel « + »
    s = re.sub(r"[^\d+]", "", str(raw))
    if not s:
        return ""

    # 00xx -> +xx
    if s.startswith("00"):
        s = "+" + s[2:]

    # Déjà international
    if s.startswith("+"):
        return s

    # Numéro local marocain « 0X… » -> « +212X… »
    if s.startswith("0"):
        return "+" + default_cc + s[1:]

    # Numéro déjà préfixé par l'indicatif pays mais sans « + »
    if s.startswith(default_cc):
        return "+" + s

    # Numéro national « nu » (sans 0 ni indicatif)
    return "+" + default_cc + s
