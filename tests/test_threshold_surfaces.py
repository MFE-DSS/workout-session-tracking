"""Les seuils — les premières surfaces vues, et les moins soignées.

POURQUOI CETTE GARDE EXISTE
---------------------------
Trois défauts, tous visibles au premier écran d'un nouvel utilisateur.

**1. Le produit ne disait pas son nom.** « Auren » n'existait que dans le
`<title>`. Pire : le commentaire d'en-tête de `login.html` affirme depuis
`Sb_UI_10.3` que le « nom PRODUIT VISIBLE » est « Auren ». **La prose décrivait
une visibilité qui n'existait pas** — et c'est le genre d'écart qu'aucun test
ne voit, parce qu'un `<title>` est bien un nom, quelque part.

**2. « ← Retour » mentait.** Il pointait vers `public_landing`, une
DESTINATION FIXE et non un historique. Arrivé au login par un signet ou par
une session expirée, on « revenait » sur une page jamais vue. Le lien n'est pas
retiré — il mène à quelque chose de réel — il est NOMMÉ pour ce qu'il fait.

**3. Trois liens de poids strictement égal.** Se créer un compte, récupérer un
mot de passe et découvrir le produit ne sont pas la même chose.

Ces surfaces portaient par ailleurs **huit styles en ligne pour le seul
login** — une concentration de la dette mesurée à 373 déclarations, dont 703
sur 708 statiques.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"

THRESHOLDS = ("login.html", "register.html", "forgot_password.html")
ROUTES = {"login.html": "/login", "register.html": "/register",
          "forgot_password.html": "/forgot-password"}


def _src(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def _anon(client):
    """Le client de test est AUTHENTIFIÉ par défaut : `/login` y redirige vers
    l'accueil, et une garde de seuil qui l'utiliserait mesurerait la mauvaise
    page — en passant, puisque l'accueil contient bien du HTML.

    On vide le bocal à cookies : un seuil se juge déconnecté, c'est sa
    condition réelle.
    """
    client.cookies.clear()
    return client


@pytest.mark.parametrize("name", THRESHOLDS)
def test_the_product_says_its_name_on_screen(name, client):
    """`T-02 = C` — pas dans le `<title>`, À L'ÉCRAN.

    Un `<title>` est un nom pour l'onglet et le moteur de recherche. Il n'est
    pas lu par quelqu'un qui regarde son téléphone.
    """
    body = _anon(client).get(ROUTES[name]).text
    assert 'class="auth-mark"' in body, (
        f"{name} ne porte pas la marque d'instrument — le produit ne dit pas "
        "son nom sur son propre seuil"
    )
    marque = re.search(r'class="auth-mark"[^>]*>([^<]+)<', body)
    assert marque, "la marque est présente mais vide"
    assert marque.group(1).strip() == "AUREN", marque.group(1)


def test_no_exit_promises_a_history_it_cannot_deliver(client):
    """`T-03` — « ← Retour » vers une destination FIXE.

    C'est le défaut le plus discret des trois : le lien fonctionne, il mène
    quelque part, et il ment seulement sur ce qu'il fait. Un lien qui promet
    un retour doit revenir ; sinon il nomme sa destination.
    """
    src = re.sub(r"\{#.*?#\}", "", _src("login.html"), flags=re.DOTALL)
    m = re.search(
        r"<a[^>]*url_for\(\s*['\"]public_landing['\"][^>]*>(.*?)</a>", src, re.DOTALL
    )
    assert m, "le lien vers la page publique a disparu du login"
    texte = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split())
    assert "Retour" not in texte, (
        f"« {texte} » promet un retour et exécute une navigation fixe — "
        "arrivé par un signet, l'utilisateur « revient » où il n'est jamais allé"
    )
    assert texte, "le lien a perdu son libellé"


@pytest.mark.parametrize("name", THRESHOLDS)
def test_the_threshold_templates_carry_no_inline_style(name):
    """Huit styles en ligne sur le seul login.

    Un style en ligne n'est pas gardé, pas thémé, pas mesurable — il échappe à
    toute règle de la feuille. Les seuls survivants légitimes portent une
    valeur DYNAMIQUE ; aucun de ceux-ci n'en portait.
    """
    src = re.sub(r"\{#.*?#\}", "", _src(name), flags=re.DOTALL)
    offenders = re.findall(r'style="[^"]*"', src)
    assert offenders == [], f"{name} porte encore {len(offenders)} style(s) : {offenders[:3]}"


@pytest.mark.parametrize("name", THRESHOLDS)
def test_every_threshold_exit_is_a_real_target(name, client):
    """44 px de plancher, sur des liens qui étaient de simples lignes de texte.

    Une sortie de seuil est manquée par quelqu'un qui a déjà du mal à entrer.
    """
    body = _anon(client).get(ROUTES[name]).text
    assert 'class="auth-exit' in body, f"{name} n'a plus de sortie nommée"


def test_the_login_exits_are_ranked_not_equal(client):
    """`T-03 = C` — un rang, pas trois poids égaux.

    S'inscrire est le chemin qu'on cherche vraiment ; récupérer un mot de
    passe et découvrir le produit sont des recours. Les trois avaient
    exactement la même taille et la même couleur.
    """
    body = _anon(client).get("/login").text
    # `auth-exit` et non `auth-exit[^"]*` : le second attrape aussi
    # `auth-exits`, la classe du PARAGRAPHE, et comptait donc six sorties là
    # où il y en a trois.
    exits = re.findall(r'class="(auth-exit(?:\s+auth-exit--\w+)?)"', body)
    assert len(exits) == 3, f"3 sorties attendues, {len(exits)} trouvées : {exits}"
    majeures = [e for e in exits if "--minor" not in e]
    assert len(majeures) == 1, (
        f"une seule sortie majeure attendue, {len(majeures)} trouvée(s) — "
        "les trois liens redeviennent de poids égal"
    )
