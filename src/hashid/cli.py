"""Interface ligne de commande : arguments, entrees/sorties, affichage.

Seul module autorise a faire des print(). Il ne contient aucune logique
d'identification : il appelle engine.identify() et met en forme le resultat.
"""

import argparse
import sys

from hashid import engine


def build_parser():
    """Construit l'ArgumentParser.

    Arguments vises (MVP 5) :
        hash            hash a identifier (positionnel, optionnel)
        -f, --file      fichier contenant un hash par ligne
        -j, --json      sortie JSON au lieu du texte
        -n, --top N     nombre de candidats affiches (defaut 5)

    Si ni `hash` ni `--file` n'est fourni, lire stdin : cela rend
    `cat hashes.txt | hashid` possible gratuitement.
    """
    parser = argparse.ArgumentParser(
        description="Identifie le type de hash d'une valeur donnee.",
        epilog="Si ni `hash` ni `--file` n'est fourni, lire stdin.",
    )
    parser.add_argument("hash", nargs="?", help="hash a identifier")
    parser.add_argument("-f", "--file", help="fichier contenant un hash par ligne")
    parser.add_argument("-j", "--json", action="store_true", help="sortie JSON au lieu du texte")
    parser.add_argument("-n", "--top", type=int, default=5, help="nombre de candidats affiches (defaut 5)")

    return parser


def format_human(value, candidates) -> str:
    """Rend les candidats en texte lisible dans un terminal.

    Une ligne par candidat : score, nom, mode hashcat, format John.
    """
    if not candidates:
        return f"{value}\n  aucune correspondance"
    lines = [value]
    for c in candidates:
        hashcat = c.hashcat or "-"
        john = c.john or "-"
        lines.append(f"  [{c.score:4d}] {c.name:20s} {c.confidence:9s} hashcat {hashcat:>6s}  john {john}")
    return "\n".join(lines)


def format_json(value, candidates) -> str:
    """Rend les candidats en JSON, une ligne par hash (JSON Lines).
    """
    import json

    return json.dumps(
        {
            "hash": value,
            "candidates": [
                {
                    "score": c.score,
                    "name": c.name,
                    "confidence": c.confidence,
                    "hashcat": c.hashcat,
                    "john": c.john,
                }
                for c in candidates
            ],
        },
        ensure_ascii=False,
    )


def iter_inputs(hash_arg, file_arg):
    """Itere sur les valeurs a identifier, depuis l'argument ou le fichier.

    Si ni `hash_arg` ni `file_arg` n'est fourni, lire stdin.
    """
    if hash_arg:
        yield hash_arg
    elif file_arg:
        # utf-8-sig retire le BOM que Windows place en tete de fichier
        with open(file_arg, "r", encoding="utf-8-sig") as f:
            for line in f:
                yield line.strip()
    else:
        for line in sys.stdin:
            yield line.strip().lstrip("﻿")


def main(argv=None) -> int:
    """Point d'entree console. Retourne le code de sortie du processus.
    """
    args = build_parser().parse_args(argv)
    trouve = False
    for ligne in iter_inputs(args.hash, args.file):
        value = ligne.strip()
        if not value or value.startswith("#"):
            continue
        candidates = engine.identify(value, top=args.top)
        if candidates:
            trouve = True
        if args.json:
            print(format_json(value, candidates))
        elif candidates:
            print(format_human(value, candidates))
        else:
            # sur stderr pour ne pas polluer un pipe
            print(f"{value} : aucune correspondance", file=sys.stderr)

    return 0 if trouve else 1




if __name__ == "__main__":
    sys.exit(main())
