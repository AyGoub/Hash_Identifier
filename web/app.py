"""API web pour hash-identifier.

Une fine couche Flask par-dessus hashid.identify() : elle sert la page
statique ET l'endpoint JSON, sur la meme origine (donc aucun CORS a gerer).
La logique d'identification n'est pas dupliquee ici, elle vit dans le paquet.
"""

from dataclasses import asdict
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from hashid import identify

STATIC = Path(__file__).parent / "static"

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


if __name__ == "__main__":
    # Lancement local (developpement). En production c'est gunicorn qui
    # importe l'objet `app`, ce bloc n'est alors pas execute.
    app.run(host="127.0.0.1", port=5000, debug=True)
