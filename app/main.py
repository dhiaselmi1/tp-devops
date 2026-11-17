"""API REST du TP : catalogue de produits (FastAPI)."""
import os
import socket

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.calculs import prix_ttc
from app.database import Base, Produit, engine, get_session

VERSION = os.getenv("APP_VERSION", "1.0.0")      # fixée par le Dockerfile ou Kubernetes
Base.metadata.create_all(bind=engine)            # crée la table au démarrage (suffisant pour un TP)
app = FastAPI(title="TP DevOps — API Catalogue", version=VERSION)


class ProduitIn(BaseModel):
    """Données attendues pour créer un produit (validées automatiquement par FastAPI)."""

    nom: str = Field(min_length=1, max_length=100)
    prix_ht: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)


def en_dict(p: Produit) -> dict:
    """Convertit une ligne de la base en JSON, avec le prix TTC calculé."""
    return {"id": p.id, "nom": p.nom, "prix_ht": p.prix_ht,
            "prix_ttc": prix_ttc(p.prix_ht), "stock": p.stock}


@app.get("/")
def accueil():
    # hote = nom du conteneur ou du pod : permet de voir la répartition de charge au TP3
    return {"message": "API Catalogue opérationnelle", "version": VERSION,
            "hote": socket.gethostname()}


@app.get("/health")
def health():
    """Sonde de santé : utilisée par Docker (HEALTHCHECK) et Kubernetes (probes)."""
    return {"status": "ok"}


@app.get("/produits")
def lister(session: Session = Depends(get_session)):
    return [en_dict(p) for p in session.query(Produit).order_by(Produit.id)]


@app.get("/produits/{produit_id}")
def lire(produit_id: int, session: Session = Depends(get_session)):
    produit = session.get(Produit, produit_id)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return en_dict(produit)


@app.post("/produits", status_code=201)
def creer(donnees: ProduitIn, session: Session = Depends(get_session)):
    produit = Produit(**donnees.model_dump())
    session.add(produit)
    session.commit()          # écrit réellement en base
    session.refresh(produit)  # récupère l'id généré
    return en_dict(produit)
