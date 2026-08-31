"""Tests des predicats d'alphabet (MVP 1).

Ces fonctions sont pures : une entree, une sortie, aucun effet de bord.
Ce sont les plus faciles a tester, et les plus faciles a casser par
inadvertance en les "optimisant" plus tard.
"""

import pytest

from hashid.charset import is_base64, is_bcrypt_b64, is_hex


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




# --------------------------------------------------------- au-dela du MVP 1

@pytest.mark.skip(reason="is_base64 : bonus, pas le MVP 1")
@pytest.mark.parametrize("value,attendu", [
    ("qvTGHdzF6KLavt4POzQs2a6pQ00=", True),    # SHA-1 encode
    ("XUFAKrxLKna5cZ2REBfFkg==", True),        # MD5 encode
    ("SGVsbG8gd29ybGQh", True),
    ("qvTGHdzF6KLavt4POzQs2a6pQ00", False),    # longueur non multiple de 4
    ("qvTGHdzF6KLavt4POzQs2a6pQ0=0", False),   # padding au milieu
    ("./abcABC123", False),                    # alphabet crypt, pas base64
    ("", False),
])
def test_is_base64(value, attendu):
    assert is_base64(value) is attendu


@pytest.mark.skip(reason="is_bcrypt_b64 : MVP 3")
@pytest.mark.parametrize("value,attendu", [
    ("LhayLxezLhK1LhWvKxCyLO", True),
    ("./ABCabc0189", True),
    ("abc+def", False),      # '+' n'existe pas dans l'alphabet crypt
    ("abc=", False),         # pas de padding en crypt
    ("", False),
])
def test_is_bcrypt_b64(value, attendu):
    assert is_bcrypt_b64(value) is attendu
