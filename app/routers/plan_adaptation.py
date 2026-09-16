"""`UI-CP3.5` — écarter un ajustement du plan.

UNE SEULE ROUTE, ET ELLE EST EN `POST`
--------------------------------------
Écarter change le comportement du produit : l'adaptation cesse de composer le
plan effectif. C'est une écriture, donc un `POST`. Un lien l'aurait rendue
déclenchable par une pré-lecture de navigateur.

AUCUNE MODALE
-------------
Il n'y a rien à confirmer. L'adaptation n'a jamais rien imposé — elle a réduit
une cible et l'a dit. L'écarter la retire. Un dialogue de confirmation pour un
geste réversible et sans perte serait du cérémonial.

RIEN N'EST SUPPRIMÉ
-------------------
La trace historique survit intacte : on écarte un EFFET, pas une preuve.
*« L'historique survit ; le comportement, non. »*
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from app.deps import CurrentUser, DbSession
from app.services.plan_adaptation_store import dismiss

router = APIRouter(tags=["plan-adaptation"])


@router.post("/plan-adaptations/dismiss", response_model=None,
             name="dismiss_adaptation")
def dismiss_adaptation(
    decision_id: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Écarte une adaptation et revient à l'accueil.

    Un identifiant vide ou inconnu **ne lève pas** : l'utilisateur retrouve son
    accueil. Une adaptation déjà écartée, ou supersédée entre l'affichage et le
    clic, n'est pas une erreur de sa part.
    """
    identifiant = (decision_id or "").strip()
    if identifiant:
        dismiss(db, user.id, identifiant)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
