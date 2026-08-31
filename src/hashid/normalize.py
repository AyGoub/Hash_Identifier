"""Nettoyage de l'entree et decoupage des formes composees.

Ce module ne devine aucun algorithme : il produit une chaine propre et
signale ce qu'il a trouve autour (sel, utilisateur, contexte).
"""

from .models import Parsed


def normalize(raw: str) -> Parsed:
    """Transforme une entree brute en Parsed exploitable par le moteur.

    Etapes attendues :

    1. strip() des espaces, tabulations et retours ligne
    2. retirer les guillemets englobants (' et ")
    3. detecter les formes composees et remplir Parsed :
         - "hash:sel"                  -> value + salt
         - "user:rid:LM:NTLM:::"       -> ligne pwdown, value = champ NTLM
         - "user:$6$sel$hash:18000:0:" -> ligne shadow, value = champ 2
         - "*ABCDEF..."                -> MySQL5, garder l'asterisque dans value
    4. NE PAS mettre en minuscules `value` : la casse est un indice
       (NTLM et Oracle sortent souvent en majuscules). La comparaison
       insensible a la casse se fait dans les regex, pas ici.

    TODO (MVP 1 pour les etapes 1-2, MVP 7 pour l'etape 3)
    """
    s=strip_wrappers(raw)
    return Parsed(original=raw, value=s)



def strip_wrappers(s: str) -> str:
    """Retire guillemets, espaces et caracteres de fin de ligne.
    """
    s=s.strip()
    for wrapper in ("'", '"'):
        if s.startswith(wrapper) and s.endswith(wrapper):
            s = s[1:-1]
    return s.strip()
