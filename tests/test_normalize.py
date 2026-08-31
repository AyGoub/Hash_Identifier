"""Tests du nettoyage de l'entree (MVP 1).

Contrat du MVP 1 : normalize() nettoie et renvoie un Parsed.
Elle ne decoupe RIEN (ni sel, ni pwdump) : ces tests-la sont marques skip
et deviendront la specification du MVP 7.
"""

import pytest

from hashid.models import Parsed
from hashid.normalize import normalize, strip_wrappers


# ------------------------------------------------------------ strip_wrappers

@pytest.mark.parametrize("brut,attendu", [
    ("  5d41402a  ", "5d41402a"),           # espaces
    ("\t5d41402a\n", "5d41402a"),           # tabulation et retour ligne
    ("5d41402a\r\n", "5d41402a"),           # fin de ligne Windows
    ('"5d41402a"', "5d41402a"),             # guillemets doubles
    ("'5d41402a'", "5d41402a"),             # guillemets simples
    ('  "5d41402a"  ', "5d41402a"),         # les deux combines
    ("5d41402a", "5d41402a"),               # rien a faire
    ("", ""),                               # chaine vide
    ("   ", ""),                            # que des espaces
])
def test_strip_wrappers(brut, attendu):
    assert strip_wrappers(brut) == attendu


@pytest.mark.parametrize("brut", ['"5d41402a', "5d41402a'", "'5d41402a\""])
def test_strip_wrappers_ne_touche_pas_aux_guillemets_non_apparies(brut):
    """Un guillemet seul fait peut-etre partie du hash : on n'y touche pas."""
    assert strip_wrappers(brut) == brut


# ------------------------------------------------------------------ normalize

def test_normalize_retourne_un_parsed():
    assert isinstance(normalize("5d41402a"), Parsed)


def test_normalize_conserve_l_entree_brute():
    """`original` sert a recoller la sortie aux lignes du fichier d'entree."""
    brut = "  5d41402abc4b2a76b9719d911017c592  \n"
    p = normalize(brut)
    assert p.original == brut          # intact, espaces compris
    assert p.value == "5d41402abc4b2a76b9719d911017c592"


def test_normalize_preserve_la_casse():
    """La casse est un indice (NTLM et Oracle sortent souvent en MAJ)."""
    p = normalize("5D41402ABC4B2A76B9719D911017C592")
    assert p.value == "5D41402ABC4B2A76B9719D911017C592"


def test_normalize_champs_non_remplis_au_mvp1():
    p = normalize("5d41402abc4b2a76b9719d911017c592")
    assert p.salt is None
    assert p.username is None
    assert p.hints == []


def test_normalize_chaine_vide():
    """Ne doit pas lever d'exception."""
    p = normalize("")
    assert p.value == ""


def test_normalize_ne_decoupe_pas_encore_le_sel():
    """Comportement ASSUME du MVP 1 : le sel reste colle.

    Quand tu implementeras le MVP 7, ce test devra etre supprime et
    remplace par test_normalize_decoupe_le_sel ci-dessous.
    """
    p = normalize("5d41402abc4b2a76b9719d911017c592:7050461")
    assert p.value == "5d41402abc4b2a76b9719d911017c592:7050461"
    assert p.salt is None


# ------------------------------------------------------- specification MVP 7

@pytest.mark.skip(reason="decoupage des formes composees : MVP 7")
def test_normalize_decoupe_le_sel():
    p = normalize("5d41402abc4b2a76b9719d911017c592:7050461")
    assert p.value == "5d41402abc4b2a76b9719d911017c592"
    assert p.salt == "7050461"


@pytest.mark.skip(reason="decoupage des formes composees : MVP 7")
def test_normalize_ligne_pwdump():
    ligne = "Admin:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::"
    p = normalize(ligne)
    assert p.value == "31d6cfe0d16ae931b73c59d7e0c089c0"
    assert p.username == "Admin"


@pytest.mark.skip(reason="decoupage des formes composees : MVP 7")
def test_normalize_ligne_shadow():
    ligne = "root:$6$52450745$k5ka2p8bFuSmoVT1tzOyyu:19000:0:99999:7:::"
    p = normalize(ligne)
    assert p.value.startswith("$6$")
    assert p.username == "root"
