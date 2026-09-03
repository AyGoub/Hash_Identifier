# hash-identifier

Identifie le type d'un hash par **analyse de format** : préfixe, alphabet, longueur, contexte.
Aucun calcul cryptographique — uniquement de la reconnaissance de motifs.

Le résultat est toujours une **liste classée**, jamais une réponse unique : `32` caractères
hexadécimaux correspondent à huit algorithmes plausibles, et prétendre le contraire serait faux.

**Démo en ligne :** <https://hash-identifier-9qwi.onrender.com/>
_(hébergement gratuit : la première requête peut prendre ~30 s, le temps que le service se réveille.)_

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
- `POST /api/explain` — explication pédagogique via IA (voir ci-dessous)

Déployé gratuitement sur [Render](https://render.com) via le `render.yaml` du
dépôt (New → Blueprint). Chaque `git push` redéclenche le déploiement.

### Explication pédagogique (optionnelle, IA)

Après l'identification, un bouton « expliquer » demande à un LLM de commenter le
résultat en clair : ce que c'est probablement, pourquoi, l'implication sécurité,
et la commande hashcat/john utile. L'explication est **bridée aux candidats de
`identify()`** — le modèle ne peut pas inventer d'algorithme.

- Corps : `POST /api/explain` avec `{"hash": "...", "context": "..."(optionnel)}`
- Fournisseur : [Groq](https://console.groq.com) (palier gratuit), modèle
  `llama-3.3-70b-versatile`
- L'identification reste **gratuite et instantanée** ; l'IA est isolée dans cet
  endpoint, jamais sur le chemin par défaut.

**Clé API** — l'endpoint lit `os.environ["GROQ_API_KEY"]` ; sans elle il répond
`503` et le reste de l'app fonctionne normalement. La clé ne figure jamais dans
le code ni dans un commit.

```bash
# local (PowerShell) — le temps de la session
$env:GROQ_API_KEY = "gsk_..."
python web/app.py
```

Sur Render : onglet **Environment** → variable `GROQ_API_KEY` (Render l'injecte
dans le processus au démarrage ; elle n'est pas transmise par `git push`).

## Structure

| Chemin | Rôle | Ne fait jamais |
|---|---|---|
| `src/hashid/models.py` | Types partagés : `Rule`, `Candidate`, `Parsed` | aucune logique |
| `src/hashid/normalize.py` | Entrée sale → entrée propre | ne devine aucun algorithme |
| `src/hashid/charset.py` | Prédicats sur l'alphabet | ne connaît aucun nom d'algorithme |
| `src/hashid/engine.py` | Règles → candidats → scores → tri | aucun `print()` |
| `src/hashid/cli.py` | Arguments, E/S, affichage | aucune logique d'identification |
| `src/hashid/data/rules.json` | Toute la connaissance métier | — |
| `web/app.py` | API Flask : sert la page + `/api/identify` + `/api/explain` | aucune logique d'identification |
| `web/static/index.html` | Front (terminal) qui appelle l'API | — |
| `tests/` | Non-régression sur des hashes réels | — |

**Sens des dépendances** — toujours vers l'intérieur, jamais l'inverse :

```
cli.py  ┐
web/app.py ┼→ engine.py → normalize.py / charset.py → models.py
```

Le CLI et l'API sont deux façades sur le même `engine.identify()`. Ajouter
une interface = un fichier de plus, zéro modification du moteur.

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
| 4 | Scoring et tri | ✅ |
| 5 | CLI utilisable | ✅ |
| 6 | Tests de non-régression | 🔸 partiel |

Bonus livré : interface web (API Flask + front terminal) déployée sur Render, et
explication pédagogique optionnelle via IA (Groq).

## Ajouter un algorithme

Une entrée dans `src/hashid/data/rules.json`, zéro ligne de Python :

```json
{
  "name": "SHA-224",
  "regex": "[a-fA-F0-9]{56}",
  "hashcat": "1300",
  "john": "raw-sha224",
  "base_score": 50,
  "confidence": "ambigu",
  "exclusive": false,
  "note": ""
}
```

`base_score` est **uniforme par groupe de longueur** (50 pour du hex brut) : il
mesure la précision du motif, pas la popularité. Ce qui départage deux algos de
même longueur, c'est le dictionnaire `POPULARITE` dans `engine.py` — ajoute-y une
ligne seulement si l'algo est notablement plus ou moins courant que la moyenne.

Puis `pytest`. Si un test casse, la nouvelle règle est trop large.

