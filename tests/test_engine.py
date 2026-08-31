"""Tests de non-regression : le filet qui permet d'ajouter des regles sereinement.

Lance-les avec `pytest` apres CHAQUE ajout dans rules.json.
Une regle trop large casse silencieusement le classement des autres.
"""

import json
from pathlib import Path

import pytest

from hashid import identify, load_rules

FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "known_hashes.json").read_text(encoding="utf-8")
)


def test_rules_are_loadable():
    """Le JSON est valide et chaque entree correspond au schema Rule."""
    rules = load_rules()
    assert rules, "rules.json ne doit pas etre vide"


def test_rule_names_are_unique():
    names = [r.name for r in load_rules()]
    assert len(names) == len(set(names)), "deux regles portent le meme nom"


@pytest.mark.parametrize("case", FIXTURES["cases"], ids=lambda c: c["expect"])
def test_known_hash_is_ranked(case):
    """L'algorithme attendu doit apparaitre dans les `max_rank` premiers."""
    candidates = identify(case["hash"])
    names = [c.name for c in candidates]
    assert case["expect"] in names, f"{case['expect']} absent des candidats : {names}"
    rank = names.index(case["expect"]) + 1
    assert rank <= case["max_rank"], f"{case['expect']} au rang {rank}, attendu <= {case['max_rank']}"


def test_ambiguous_hex_returns_several_candidates():
    """Une chaine 32 hex ne doit jamais produire une reponse unique."""
    assert len(identify("5d41402abc4b2a76b9719d911017c592")) > 1


# ===================================================== identify() : MVP 1

MD5_HASH = "5d41402abc4b2a76b9719d911017c592"
BCRYPT = "$2a$05$LhayLxezLhK1LhWvKxCyLOj0j1u.Kj0jZ0pEmm134uzrQlFvQJLF6"


def test_identify_retourne_des_candidates():
    from hashid.models import Candidate
    for c in identify(MD5_HASH):
        assert isinstance(c, Candidate)


def test_identify_nettoie_son_entree():
    """identify() appelle normalize() : espaces et guillemets sont tolérés."""
    attendu = [c.name for c in identify(MD5_HASH)]
    assert [c.name for c in identify("  " + MD5_HASH + "  \n")] == attendu
    assert [c.name for c in identify('"' + MD5_HASH + '"')] == attendu


def test_identify_est_insensible_a_la_casse():
    assert [c.name for c in identify(MD5_HASH.upper())] == [
        c.name for c in identify(MD5_HASH)
    ]


def test_identify_trie_par_score_decroissant():
    scores = [c.score for c in identify(MD5_HASH)]
    assert scores == sorted(scores, reverse=True)


def test_identify_pas_de_score_ex_aequo_dans_un_groupe():
    """Deux scores égaux rendent le classement dépendant de l'ordre du JSON."""
    scores = [c.score for c in identify(MD5_HASH)]
    assert len(scores) == len(set(scores))


def test_identify_respecte_top():
    assert len(identify(MD5_HASH, top=1)) == 1


def test_identify_court_circuite_sur_regle_exclusive():
    """bcrypt a exclusive=true : un seul candidat, pas de bruit derrière."""
    resultats = identify(BCRYPT)
    assert len(resultats) == 1
    assert resultats[0].name == "bcrypt"


@pytest.mark.parametrize("value", [
    "",
    "bonjour",
    "a" * 31,      # une longueur en-dessous : re.search matcherait, pas fullmatch
    "a" * 33,      # une longueur au-dessus
    "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz",   # 32 caractères mais pas hex
])
def test_identify_ne_matche_rien(value):
    assert identify(value) == []
