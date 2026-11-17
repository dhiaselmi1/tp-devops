"""Tests d'INTÉGRATION : l'API + la base (SQLite de test) fonctionnent ensemble."""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"   # base jetable, AVANT d'importer l'application
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)    # simule un client HTTP sans lancer de serveur


def test_health():
    reponse = client.get("/health")
    assert reponse.status_code == 200
    assert reponse.json() == {"status": "ok"}


def test_creer_puis_lire_un_produit():
    cree = client.post("/produits", json={"nom": "Clavier", "prix_ht": 50, "stock": 3})
    assert cree.status_code == 201
    produit = cree.json()
    assert produit["prix_ttc"] == 59.5
    assert client.get(f"/produits/{produit['id']}").json()["nom"] == "Clavier"


def test_produit_inexistant():
    assert client.get("/produits/999999").status_code == 404


def test_prix_negatif_refuse():
    assert client.post("/produits", json={"nom": "X", "prix_ht": -1}).status_code == 422
