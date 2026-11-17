"""Règles métier pures (sans base ni réseau) : idéales pour des tests unitaires rapides."""

TAUX_TVA = 0.19  # taux de TVA normal appliqué dans le TP


def calculer_tva(montant_ht: float, taux: float = TAUX_TVA) -> float:
    """Renvoie le montant de TVA, arrondi au centime. Exemple : calculer_tva(100) -> 19.0"""
    if montant_ht < 0:
        raise ValueError("Le montant HT ne peut pas être négatif")
    return round(montant_ht * taux, 2)


def prix_ttc(montant_ht: float, taux: float = TAUX_TVA) -> float:
    """Prix toutes taxes comprises = HT + TVA."""
    return round(montant_ht + calculer_tva(montant_ht, taux), 2)


def appliquer_remise(prix: float, pourcentage: float) -> float:
    """Applique une remise comprise entre 0 et 100 %."""
    if not 0 <= pourcentage <= 100:
        raise ValueError("La remise doit être comprise entre 0 et 100 %")
    return round(prix * (1 - pourcentage / 100), 2)
