"""Connexion à la base de données.
PostgreSQL quand DATABASE_URL est fournie (TP2 docker-compose), SQLite sinon (poste local, CI, TP3)."""
import os

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Principe « 12-factor app » : la configuration vient de l'environnement, jamais du code.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# check_same_thread n'existe que pour SQLite (FastAPI sert les requêtes sur plusieurs threads).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# pool_pre_ping : vérifie la connexion avant usage (utile si la base redémarre).
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class Produit(Base):
    """Table « produits » du catalogue."""

    __tablename__ = "produits"
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prix_ht = Column(Float, nullable=False)
    stock = Column(Integer, default=0)


def get_session():
    """Fournit une session par requête HTTP et la ferme toujours à la fin (dépendance FastAPI)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
