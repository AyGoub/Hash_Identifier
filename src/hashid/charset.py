"""Predicats purs sur l'alphabet d'une chaine.

Ce module ne connait AUCUN nom d'algorithme. Il repond uniquement a la
question "de quel alphabet cette chaine est-elle faite ?".
"""


def is_hex(s: str) -> bool:
    """True si s ne contient que [0-9a-fA-F] et n'est pas vide.
    """
    for c in s:
        if c not in "0123456789abcdefABCDEF":
            return False
    return len(s) > 0   




