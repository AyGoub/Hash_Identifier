"""Tests du nettoyage de l'entree.

normalize() nettoie et renvoie un Parsed. Elle ne decoupe pas les formes
composees (hash:sel, pwdump...) : ces lignes sont reconnues comme un tout
par les regles de rules.json, pas decoupees ici.
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


def test_normalize_chaine_vide():
    """Ne doit pas lever d'exception."""
    p = normalize("")
    assert p.value == ""


def test_normalize_ne_decoupe_pas_le_sel():
    """La ligne composee est laissee intacte ; c'est une regle de
    rules.json qui la reconnait entiere, pas normalize() qui la decoupe."""
    p = normalize("5d41402abc4b2a76b9719d911017c592:7050461")
    assert p.value == "5d41402abc4b2a76b9719d911017c592:7050461"
