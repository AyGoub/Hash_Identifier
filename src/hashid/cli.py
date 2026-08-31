"""Interface ligne de commande : arguments, entrees/sorties, affichage.

Seul module autorise a faire des print(). Il ne contient aucune logique
d'identification : il appelle engine.identify() et met en forme le resultat.
"""

import sys


def build_parser():
    """Construit l'ArgumentParser.

    Arguments vises (MVP 5) :
        hash            hash a identifier (positionnel, optionnel)
        -f, --file      fichier contenant un hash par ligne
        -j, --json      sortie JSON au lieu du texte
        -n, --top N     nombre de candidats affiches (defaut 5)
        -q, --quiet     n'affiche que les noms, sans les modes

    Si ni `hash` ni `--file` n'est fourni, lire stdin : cela rend
    `cat hashes.txt | hashid` possible gratuitement.

    TODO (MVP 5)
    """
    raise NotImplementedError


def format_human(value, candidates) -> str:
    """Rend les candidats en texte lisible dans un terminal.

    Une ligne par candidat : score, nom, mode hashcat, format John.

    TODO (MVP 5)
    """
    raise NotImplementedError


def format_json(value, candidates) -> str:
    """Rend les candidats en JSON, une ligne par hash (JSON Lines).

    TODO (MVP 5)
    """
    raise NotImplementedError


def main(argv=None) -> int:
    """Point d'entree console. Retourne le code de sortie du processus.

    TODO (MVP 5)
    """
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
