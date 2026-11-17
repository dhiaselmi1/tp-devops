"""Tests UNITAIRES : une fonction isolée, exécution en millisecondes."""
import pytest

from app.calculs import appliquer_remise, calculer_tva, prix_ttc


def test_tva_sur_100_dinars():
    assert calculer_tva(100) == 19.0          # l'exemple du cours


def test_prix_ttc():
    assert prix_ttc(200) == 238.0


def test_remise_de_10_pourcent():
    assert appliquer_remise(50, 10) == 45.0


def test_montant_negatif_refuse():
    with pytest.raises(ValueError):           # le code doit lever une erreur
        calculer_tva(-5)
