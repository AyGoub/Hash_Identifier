"""Tests des predicats d'alphabet (MVP 1).

Ces fonctions sont pures : une entree, une sortie, aucun effet de bord.
Ce sont les plus faciles a tester, et les plus faciles a casser par
inadvertance en les "optimisant" plus tard.
"""

import pytest

from hashid.charset import is_hex


# --------------------------------------------------------------------- is_hex

@pytest.mark.parametrize("value", [
    "0123456789",
    "abcdef",
    "ABCDEF",
    "5d41402abc4b2a76b9719d911017c592",
    "5D41402ABC4B2A76B9719D911017C592",
    "aAbB0",
    "0",
])
def test_is_hex_accepte(value):
    assert is_hex(value) is True


@pytest.mark.parametrize("value", [
    "",                                   # vide : le piege classique
    "ghijkl",                             # lettres hors [a-f]
    "5d41402abc4b2a76b9719d911017c59z",   # un seul caractere invalide suffit
    "5d41402a 4b2a76b9719d911017c592",    # espace au milieu
    " 5d41402a",                          # espace en tete
    "5d41402a\n",                         # retour ligne : normalize() doit
                                          # l'avoir retire avant d'arriver ici
    "0x5d41402a",                         # prefixe 0x
    "-1",
])
def test_is_hex_refuse(value):
    assert is_hex(value) is False
