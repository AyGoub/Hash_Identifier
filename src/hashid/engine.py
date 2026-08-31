"""Moteur : charge les regles, les applique, score et trie les candidats.

Regle d'or de ce module : il n'affiche RIEN. Pas un seul print().
Il retourne des donnees, l'affichage est le travail de cli.py.
"""

import json
import re
from functools import lru_cache
from typing import List

from .normalize import normalize

from .models import Candidate, Rule

# importlib.resources plutot qu'un chemin relatif : open("data/rules.json")
# casse des que le script est lance depuis un autre repertoire ou installe.
try:  # Python >= 3.9
    from importlib.resources import files as _files
except ImportError:  # pragma: no cover
    from importlib_resources import files as _files  # type: ignore


@lru_cache(maxsize=1)
def load_rules() -> List[Rule]:
    """Charge et met en cache les regles de data/rules.json."""
    # On vise le paquet `hashid` puis le sous-chemin : `hashid.data` n'est pas
    # un paquet (pas d'__init__.py) et echouerait sous Python 3.9.
    raw = _files("hashid").joinpath("data/rules.json").read_text(encoding="utf-8")
    payload = json.loads(raw)
    return [Rule(**item) for item in payload["rules"]]


def identify(value: str, top: int = 10) -> List[Candidate]:
    """Retourne les candidats plausibles pour `value`, du plus au moins probable.

    Une regle marquee `exclusive` (prefixe auto-descriptif : $2b$, {SSHA}...)
    court-circuite l'evaluation : rien d'autre ne peut ressembler a ca.

    Ne retourne JAMAIS un candidat unique pour une chaine hex brute :
    32 caracteres hex, c'est huit algorithmes plausibles.
    """
    value=normalize(value).value
    candidats = []

    for rule in load_rules():
        if re.fullmatch(rule.regex, value):
            candidat = Candidate(
                name=rule.name,
                score=score(rule),
                hashcat=rule.hashcat,
                john=rule.john,
                confidence=rule.confidence,
                note=rule.note,
            )
            if rule.exclusive:
                return [candidat]
            candidats.append(candidat)

    candidats.sort(key=lambda c: c.score, reverse=True)
    return candidats[:top]


# Frequence relative de chaque algorithme sur le terrain. 1.0 = frequence
# ordinaire ; on ne liste donc QUE les exceptions, pas les 101 regles.
#
# Ces valeurs sont subjectives et assumees comme telles : un outil oriente
# pentest Active Directory remonterait NTLM au-dessus de MD5. La seule
# validation possible est empirique -> tests/fixtures/known_hashes.json.
#
# Invariant : deux algorithmes de meme longueur ne doivent jamais aboutir
# au meme score final, sinon le classement depend de l'ordre du JSON.
POPULARITE = {
    # 8 hex
    "CRC-32": 1.6, "MurmurHash": 0.8, "FNV-1a 32": 0.6,
    # 16 hex
    "MySQL323": 2.0, "xxHash64": 0.8, "Oracle 7-10g": 0.5,
    "Cisco-PIX / ASA": 0.9, "Cisco type 7": 0.35,
    # 32 hex
    "MD5": 3.0, "NTLM": 2.5, "MD4": 0.7, "LM": 0.6, "MD2": 0.5,
    "RIPEMD-128": 0.4, "HAVAL-128": 0.3, "Tiger-128": 0.24, "Snefru-128": 0.2,
    # 40 hex
    "SHA-1": 3.0, "RIPEMD-160": 0.5, "Tiger-160": 0.3, "HAVAL-160": 0.24,
    # 48 hex
    "Tiger-192": 1.4, "HAVAL-192": 0.8,
    # 56 hex
    "SHA-224": 1.6, "SHA3-224": 0.6, "Keccak-224": 0.4, "HAVAL-224": 0.24,
    # 64 hex
    "SHA-256": 3.0, "SHA3-256": 0.6, "Keccak-256": 0.5, "BLAKE2s-256": 0.44,
    "Streebog-256": 0.36, "GOST R 34.11-94": 0.3, "RIPEMD-256": 0.24,
    "SM3": 0.2, "HAVAL-256": 0.16,
    # 96 hex
    "SHA-384": 1.6, "SHA3-384": 0.6, "Keccak-384": 0.4,
    # 128 hex
    "SHA-512": 2.0, "SHA3-512": 0.6, "Whirlpool": 0.5, "BLAKE2b-512": 0.44,
    "Keccak-512": 0.3, "Streebog-512": 0.24,
    # formes composees
    "Hash sale generique": 0.5,
    # non exclusifs a ne pas laisser dominer
    "Cisco type 4": 0.3,
}


def score(rule: Rule) -> int:
    """Combine la precision du motif et la frequence reelle de l'algorithme.

    base_score repond a "ce motif est-il discriminant ?" et vaut la meme
    chose pour tout un groupe de longueur. POPULARITE repond a "cet
    algorithme se rencontre-t-il souvent ?" et departage le groupe.

    Separer les deux permet d'ajouter une regle en ne choisissant qu'une
    valeur, au lieu de renumeroter la moitie du groupe.
    """
    return round(rule.base_score * POPULARITE.get(rule.name, 1.0))


def _compile(pattern: str) -> "re.Pattern":
    """Compile une regex de regle (cache-la si le profilage le justifie)."""
    return re.compile(pattern)
