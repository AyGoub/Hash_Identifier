"""Types de donnees partages. Aucune logique ici, aucun import du projet.

C'est la couche la plus interne : tous les autres modules peuvent l'importer,
elle n'importe rien d'eux.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Rule:
    """Une regle de detection, chargee depuis data/rules.json."""

    name: str
    regex: str
    hashcat: Optional[str] = None
    john: Optional[str] = None
    base_score: int = 50
    # "unique" | "ambigu" | "contexte" | "faux-ami"
    confidence: str = "ambigu"
    # Si True, un match arrete l'evaluation des regles suivantes
    # (cas des formats a prefixe : $2b$, {SSHA}, ...).
    exclusive: bool = False
    note: str = ""


@dataclass(frozen=True)
class Candidate:
    """Un resultat d'identification, prêt a etre affiche."""

    name: str
    score: int
    hashcat: Optional[str] = None
    john: Optional[str] = None
    confidence: str = "ambigu"
    note: str = ""


@dataclass
class Parsed:
    """Sortie de normalize() : l'entree decoupee en ses composants."""

    original: str
    # La partie a soumettre au moteur de regles
    value: str = ""
    # Composants detectes pendant le decoupage (sel, utilisateur, prefixe '*'...)
    salt: Optional[str] = None
    username: Optional[str] = None
    # Indices contextuels a remonter dans la sortie ("ligne pwdump", "shadow"...)
    hints: List[str] = field(default_factory=list)
