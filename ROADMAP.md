# Feuille de route

Sept étapes, chacune livrable et testable seule. On ne passe à la suivante que
quand le critère de réussite passe.

| | MVP | État |
|---|---|---|
| 1 | Squelette qui répond | ✅ terminé |
| 2 | Règles externalisées | ✅ terminé |
| 3 | Formats à préfixe | ✅ terminé |
| 4 | Scoring et tri | 🔜 en cours |
| 5 | CLI utilisable | ⬜ |
| 6 | Tests de non-régression | 🔸 partiel |
| 7 | Formes composées | ⬜ |

---

## MVP 1 — Le squelette qui répond ✅

**Objectif** — `identify("un hash")` retourne la liste des algorithmes possibles,
du plus probable au moins probable.

**Périmètre**
- `strip_wrappers()` et `normalize()` — nettoyage, retour d'un `Parsed`
- `is_hex()` — prédicat d'alphabet
- `identify()` — boucle sur les règles, tri décroissant, `[:top]`
- table des longueurs hex dans `rules.json` : 8, 16, 32, 40, 48, 56, 64, 80, 96, 128

**Critère de réussite** — `identify("5d41402abc4b2a76b9719d911017c592")` renvoie
au moins 2 candidats avec MD5 en tête.

**Décisions prises**
- `identify()` appelle `normalize()` lui-même : l'appelant n'a pas à y penser.
- `re.fullmatch`, jamais `match` ni `search`. Le bug est silencieux : `search`
  fait dire « MD5 » sur des chaînes de 33 caractères.
- Jamais un candidat unique sur du hex brut. 32 hex = 9 algorithmes plausibles.

---

## MVP 2 — Règles externalisées ✅

**Objectif** — sortir la connaissance métier du code Python.

**Périmètre**
- `Rule` et `Candidate` dans `models.py`
- `load_rules()` lit `data/rules.json` via `importlib.resources`
- `identify()` ne connaît aucun nom d'algorithme

**Critère de réussite** — ajouter le support de SHA-224 = **1 objet JSON,
0 ligne de Python**.

**Pourquoi en deuxième** — c'est le seul refactor pénible du projet. Fait tôt il
coûte une heure ; fait après 300 lignes de `if/elif`, il coûte une journée.

---

## MVP 3 — Formats à préfixe ✅

**Objectif** — les cas à haute confiance, ceux où la réponse est certaine.

**Périmètre** — 46 règles `exclusive: true` : `$1$`, `$apr1$`, `$P$`, `$2[abxy]$`,
`$5$`, `$6$`, `$7$`, `$y$`, `$argon2*$`, `{SHA}`, `{SSHA*}`, AIX, Django, Cisco,
MySQL, MSSQL, Oracle, Kerberos, NetNTLM, WPA, JWT, pwdump, shadow.

**Critère de réussite** — un hash bcrypt renvoie **exactement un** candidat.

**Règle d'ordre** — dans `rules.json`, les `exclusive: true` doivent rester
**avant** les règles ambiguës. Sinon le court-circuit ne sert à rien.

---

## MVP 4 — Scoring et tri 🔜

**Objectif** — que le candidat le plus probable soit systématiquement en tête.

**Périmètre**
- implémenter `score()` dans `engine.py` (aujourd'hui un stub)
- séparer les deux notions aujourd'hui mélangées dans `base_score` :
  - `base_score` = précision intrinsèque du motif
  - un dictionnaire de popularité = fréquence réelle sur le terrain

```python
def score(rule: Rule) -> int:
    return int(rule.base_score * POPULARITE.get(rule.name, 1.0))
```

- rebasculer `score=rule.base_score` vers `score=score(rule)` dans `identify()`

**Critère de réussite** — sur 32 hex : MD5, NTLM, MD4, LM, MD2, RIPEMD-128,
HAVAL-128, Tiger-128, Snefru-128, dans cet ordre, avec les scores affichés.

**Invariant à préserver** — jamais deux scores identiques dans un même groupe de
longueur. Une égalité rend le classement dépendant de l'ordre du JSON.
Le test `test_identify_pas_de_score_ex_aequo` le vérifie.

---

## MVP 5 — CLI utilisable ⬜

**Objectif** — l'outil sort de l'interpréteur Python.

**Périmètre** — quatre fonctions dans `cli.py`, toutes des stubs aujourd'hui :

| Fonction | Rôle |
|---|---|
| `build_parser()` | `hash` positionnel, `-f/--file`, `-j/--json`, `-n/--top`, `-q/--quiet` |
| `format_human()` | une ligne par candidat : score, nom, hashcat, John |
| `format_json()` | JSON Lines, une ligne par hash |
| `main()` | assemble, retourne le code de sortie |

Si ni `hash` ni `--file` : lire stdin. `cat hashes.txt \| hashid` marche alors
gratuitement.

**Critère de réussite**

```bash
hashid 5d41402abc4b2a76b9719d911017c592
cat hashes.txt | hashid --json
hashid -f hashes.txt --top 3
```

Le point d'entrée est déjà déclaré dans `pyproject.toml` — la commande `hashid`
existe, elle échoue simplement sur `NotImplementedError`.

**À afficher** — `confidence` et `note` sont transportés jusqu'au `Candidate`
mais personne ne les lit encore. Ce sont eux qui rendent la sortie honnête :
« ambigu » et l'indice de désambiguïsation valent mieux qu'un nom seul.

---

## MVP 6 — Tests de non-régression 🔸

**Objectif** — pouvoir ajouter des règles sans casser les précédentes.

**État actuel** — 55 tests verts, 15 skippés.

| Fichier | Couvre |
|---|---|
| `test_charset.py` | `is_hex` |
| `test_normalize.py` | `strip_wrappers`, `normalize` |
| `test_engine.py` | chargement, unicité des noms, `identify()`, cas limites |

**Ce qui manque** — les fixtures ne couvrent que 7 algorithmes sur 101 règles.
Une suite verte prouve que ce qui est testé fonctionne, pas que tout est couvert.

**Critère de réussite** — au moins 15 algorithmes dans
`tests/fixtures/known_hashes.json`, un par famille et par longueur.

**Méthode** — générer les hashes de référence avec `hashlib` et `passlib` plutôt
que de les recopier. Un hash mal recopié produit un test faux qui passe.

---

## MVP 7 — Formes composées ⬜

**Objectif** — accepter les lignes réelles, pas seulement les hashes nus.

**Périmètre** — étape 3 de `normalize()`, qui remplit les champs aujourd'hui
laissés à `None` :

| Entrée | `.value` | `.salt` | `.username` |
|---|---|---|---|
| `hash:sel` | le hash | le sel | — |
| `user:rid:LM:NTLM:::` | le champ NTLM | — | `user` |
| `user:$6$sel$hash:18000:0:` | le champ 2 | — | `user` |
| `*ABCDEF...` | inchangé, astérisque compris | — | — |

**Critère de réussite** — les 3 tests marqués
`@pytest.mark.skip(reason="MVP 7")` dans `test_normalize.py` passent une fois le
marqueur retiré. Leur contrat est déjà écrit.

**Où `is_hex()` sert enfin** — pour découper `a:b`, il faut décider quel côté est
le hash. La regex n'aide pas : on ne sait pas encore quel algorithme on cherche.

---

## Au-delà

- **base64** — `is_base64()` et `is_bcrypt_b64()`, tests déjà écrits et skippés
- **règles négatives** — refuser explicitement ce qui n'est pas un hash
- **sortie enrichie** — la commande hashcat prête à copier-coller
- **interface web** — un fichier de plus à côté de `cli.py`, rien d'autre à
  changer si le sens des dépendances a été respecté

---

## Limites assumées

Trois faux amis n'auront jamais de règle, parce qu'ils sont indétectables :

- **SHA de commit Git** — c'est un vrai SHA-1, regex identique
- **Clé API hexadécimale** — `[a-f0-9]{32,64}` avalerait MD5 et SHA-256
- **Blob base64 générique** — trop large, casserait tout le reste

Un identifieur qui prétendrait les distinguer mentirait. Ces cas restent des
notes dans la documentation, pas des règles dans le moteur.
