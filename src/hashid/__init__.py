"""hashid - identification du type d'un hash par analyse de format.

API publique du paquet :

    >>> from hashid import identify
    >>> identify("5d41402abc4b2a76b9719d911017c592")
    [Candidate(name='MD5', score=..., hashcat='0', ...), ...]
"""

from .engine import identify, load_rules
from .models import Candidate, Parsed, Rule

__version__ = "0.1.0"
__all__ = ["identify", "load_rules", "Candidate", "Rule", "Parsed"]
