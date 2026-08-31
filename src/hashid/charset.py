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


def is_base64(s: str) -> bool:
    """True si s ressemble a du base64 standard.

    Trois criteres cumulatifs :
      - charset [A-Za-z0-9+/] avec au plus 2 '=' finaux
      - longueur multiple de 4
      - le padding est coherent avec la longueur

    TODO (MVP 7 / bonus)
    """
    raise NotImplementedError


def is_bcrypt_b64(s: str) -> bool:
    """True si s utilise l'alphabet base64 de crypt(3) : [./A-Za-z0-9].

    Piege : cet alphabet contient '.' et '/' mais jamais '+' ni '='.
    C'est ce qui distingue un blob crypt d'un blob base64 standard.

    TODO (MVP 3)
    """
    raise NotImplementedError


