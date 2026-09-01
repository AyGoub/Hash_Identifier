# hash-identifier

Identifie le type d'un hash par **analyse de format** : préfixe, alphabet, longueur, contexte.
Aucun calcul cryptographique — uniquement de la reconnaissance de motifs.

Le résultat est toujours une **liste classée**, jamais une réponse unique : `32` caractères
hexadécimaux correspondent à huit algorithmes plausibles, et prétendre le contraire serait faux.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
```

Le `-e` (éditable) évite de réinstaller à chaque modification.
Le layout `src/` garantit que les tests s'exécutent sur le paquet installé, pas sur les fichiers du dossier courant.

## Usage visé

```bash
hashid 5d41402abc4b2a76b9719d911017c592
cat hashes.txt | hashid --json
hashid -f hashes.txt --top 3
```

```python
from hashid import identify
identify("5d41402abc4b2a76b9719d911017c592")
```

## Interface web

Une couche Flask (`web/app.py`) sert une page et une API JSON par-dessus
`identify()` — le moteur n'est pas dupliqué.

```bash
pip install -e ".[web]"
python web/app.py                 # http://127.0.0.1:5000
```

- `GET /` — la page
- `GET /api/identify?hash=<h>&top=<n>` — JSON `{hash, count, candidates}`

Déploiement gratuit sur [Render](https://render.com) : le dépôt contient un
`render.yaml`, il suffit de connecter le repo (New → Blueprint).

## Structure

| Chemin | Rôle | Ne fait jamais |
|---|---|---|
| `src/hashid/models.py` | Types partagés : `Rule`, `Candidate`, `Parsed` | aucune logique |
| `src/hashid/normalize.py` | Entrée sale → entrée propre + composants détectés | ne devine aucun algorithme |
| `src/hashid/charset.py` | Prédicats sur l'alphabet | ne connaît aucun nom d'algorithme |
| `src/hashid/engine.py` | Règles → candidats → scores → tri | aucun `print()` |
| `src/hashid/cli.py` | Arguments, E/S, affichage | aucune logique d'identification |
| `src/hashid/data/rules.json` | Toute la connaissance métier | — |
| `tests/` | Non-régression sur des hashes réels | — |

**Sens des dépendances** — toujours vers l'intérieur, jamais l'inverse :

```
cli.py → engine.py → normalize.py / charset.py → models.py
```

Si cette règle tient, ajouter une interface web plus tard = un fichier de plus à côté de `cli.py`, zéro modification du reste.

## Ordre de détection

1. **Préfixe** — `$2b$`, `{SSHA}`, `$argon2id$`… Signature unique, court-circuite tout le reste.
2. **Alphabet** — hex, base64 standard, base64 crypt (`./A-Za-z0-9`), décimal.
3. **Longueur** — discrimine la famille, rarement l'algorithme.
4. **Contexte** — séparateurs, sel, ligne pwdump, préfixe `*` de MySQL.

## Feuille de route

| | MVP | État |
|---|---|---|
| 1 | Squelette qui répond | ✅ |
| 2 | Règles externalisées | ✅ |
| 3 | Formats à préfixe | ✅ |
| 4 | Scoring et tri | 🔜 |
| 5 | CLI utilisable | ⬜ |
| 6 | Tests de non-régression | 🔸 |

Périmètre, critères de réussite et décisions de conception : [ROADMAP.md](ROADMAP.md).

## Ajouter un algorithme

Une entrée dans `src/hashid/data/rules.json`, zéro ligne de Python :

```json
{
  "name": "SHA-224",
  "regex": "[a-fA-F0-9]{56}",
  "hashcat": "1300",
  "john": "raw-sha224",
  "base_score": 45,
  "confidence": "ambigu",
  "exclusive": false,
  "note": ""
}
```

Puis `pytest`. Si un test casse, la nouvelle règle est trop large.

