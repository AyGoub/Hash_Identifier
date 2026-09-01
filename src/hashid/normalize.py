"""Nettoyage de l'entree.

Ce module ne devine aucun algorithme : il produit une chaine propre.
"""

from .models import Parsed


def normalize(raw: str) -> Parsed:
    """Transforme une entree brute en Parsed exploitable par le moteur.

    1. strip() des espaces, tabulations et retours ligne
    2. retirer les guillemets englobants (' et ")
    3. NE PAS mettre en minuscules `value` : la casse est un indice
       (NTLM et Oracle sortent souvent en majuscules). La comparaison
       insensible a la casse se fait dans les regex, pas ici.
    """
    s = strip_wrappers(raw)
    return Parsed(original=raw, value=s)



def strip_wrappers(s: str) -> str:
    """Retire guillemets, espaces et caracteres de fin de ligne.
    """
    s=s.strip()
    for wrapper in ("'", '"'):
        if s.startswith(wrapper) and s.endswith(wrapper):
            s = s[1:-1]
    return s.strip()
