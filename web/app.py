"""API web pour hash-identifier.

Une fine couche Flask par-dessus hashid.identify() : elle sert la page
statique ET l'endpoint JSON, sur la meme origine (donc aucun CORS a gerer).
La logique d'identification n'est pas dupliquee ici, elle vit dans le paquet.
"""

import os
from dataclasses import asdict
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory

from hashid import identify

STATIC = Path(__file__).parent / "static"

# API Groq (gratuite, compatible OpenAI). La cle vit dans la variable
# d'environnement GROQ_API_KEY, cote serveur uniquement — jamais dans le front.
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# Modele de raisonnement : il consomme des tokens a "reflechir" (champ
# reasoning) avant d'ecrire dans content, d'ou un max_tokens genereux.
# Verifier les modeles dispo : GET https://api.groq.com/openai/v1/models
GROQ_MODEL = "openai/gpt-oss-120b"

app = Flask(__name__, static_folder=None)


@app.get("/")
def index():
    """Sert la page d'accueil."""
    return send_from_directory(STATIC, "index.html")


@app.get("/api/identify")
def api_identify():
    """Identifie un hash. Ex : /api/identify?hash=5d41402a...&top=5

    Retourne toujours du JSON, meme quand rien n'est trouve (liste vide).
    """
    value = request.args.get("hash", "").strip()
    if not value:
        return jsonify(error="parametre 'hash' manquant"), 400

    try:
        top = int(request.args.get("top", 10))
    except ValueError:
        return jsonify(error="'top' doit etre un entier"), 400

    candidats = identify(value, top=top)
    return jsonify(
        hash=value,
        count=len(candidats),
        candidates=[asdict(c) for c in candidats],
    )


@app.post("/api/explain")
def api_explain():
    """Explication pedagogique d'un resultat, via l'API gratuite Groq.

    Corps JSON attendu : {"hash": "...", "context": "..."(optionnel)}.
    L'explication est FONDEE sur les candidats de identify() — le modele
    n'invente pas d'algorithme, il commente ceux qu'on lui fournit.
    """
    data = request.get_json(silent=True) or {}
    value = (data.get("hash") or "").strip()
    context = (data.get("context") or "").strip()

    if not value:
        return jsonify(error="parametre 'hash' manquant"), 400

    candidats = identify(value, top=5)
    if not candidats:
        return jsonify(error="aucun algorithme reconnu : rien a expliquer"), 404

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify(error="explication indisponible : GROQ_API_KEY non configuree"), 503

    liste = "\n".join(
        f"- {c.name} (confiance : {c.confidence}, hashcat {c.hashcat or '-'}, "
        f"john {c.john or '-'})"
        for c in candidats
    )
    system = (
        "Tu es un expert en cybersecurite qui explique un resultat "
        "d'identification de hash a un debutant, en francais. Regles : "
        "(1) fonde-toi UNIQUEMENT sur la liste de candidats fournie, "
        "n'invente aucun autre algorithme ; "
        "(2) explique en 3 a 5 phrases, ton clair et concret ; "
        "(3) rappelle que l'identification par la forme est ambigue quand "
        "il y a plusieurs candidats ; "
        "(4) termine par la commande hashcat ou john la plus utile pour "
        "tester le candidat le plus probable ; "
        "(5) n'essaie jamais de deviner ou casser la valeur en clair."
    )
    user = (
        f"Hash analyse : {value}\n"
        f"Contexte fourni par l'utilisateur : {context or 'aucun'}\n"
        f"Candidats, du plus au moins probable :\n{liste}\n\n"
        "Explique ce que c'est probablement, pourquoi, et l'implication securite."
    )

    try:
        resp = requests.post(
            GROQ_URL,
            timeout=30,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": GROQ_MODEL,
                "temperature": 0.3,
                # large : couvre les tokens de raisonnement + la reponse
                "max_tokens": 1200,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        resp.raise_for_status()
        texte = resp.json()["choices"][0]["message"]["content"].strip()
    except requests.Timeout:
        return jsonify(error="le service d'explication n'a pas repondu a temps"), 504
    except requests.RequestException:
        return jsonify(error="echec de l'appel au service d'explication"), 502
    except (KeyError, IndexError, ValueError):
        return jsonify(error="reponse inattendue du service d'explication"), 502

    return jsonify(hash=value, model=GROQ_MODEL, explanation=texte)


if __name__ == "__main__":
    # Lancement local (developpement). En production c'est gunicorn qui
    # importe l'objet `app`, ce bloc n'est alors pas execute.
    app.run(host="127.0.0.1", port=5000, debug=True)
