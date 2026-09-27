"""`UI-CP8I` — une saisie interrompue n'est plus perdue, et n'engage rien.

LE DÉFAUT, MESURÉ AVANT D'ÊTRE CORRIGÉ
---------------------------------------
Sur le produit qui tourne, une valeur tapée dans la série courante et non
validée disparaissait :

    rechargement                       ['80','8'] → []
    navigation dans AUREN puis retour  ['80','8'] → []
    changement d'exercice puis retour  ['80','8'] → []
    retour / avant du navigateur       ['80','8'] → []

Quatre chemins ordinaires. Deux cas survivaient déjà — arrière-plan et
`pagehide`/`pageshow` — parce que la PAGE vit : c'était du `DOM_ONLY`, pas
une récupération.

CE QUE LA TRANCHE AJOUTE, ET CE QU'ELLE N'AJOUTE PAS
-----------------------------------------------------
Un **tampon de récupération** dans `sessionStorage`. Ce n'est pas de la
persistance de domaine : le serveur reste la seule source durable. Mesuré,
`sessionStorage` survit exactement aux quatre pertes et meurt à la
fermeture de l'onglet — la frontière que le produit promet, sans un
nettoyage à inventer.

**Aucune migration, aucune colonne, aucune table.** `SetLog` reste l'état
canonique ; `completed`, `completed_at` et `rest_dismissed_at` gardent
leur sémantique au mot près.

⚠ CES GARDES LISENT LE CODE. Le comportement lui-même est prouvé au
navigateur (douze preuves, `§14`), et deux mutations ont été jouées :
retirer la garde de péremption et retirer le nettoyage post-POST. Les deux
ont été vues ROUGES.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
JS = ROOT / "app/static/js/session_focus.js"
CARD = ROOT / "app/templates/_partials/exercise_card.html"


def _code() -> str:
    """Le CODE, commentaires retirés.

    ⚠ Ce fichier EXPLIQUE longuement ce qu'il ne fait pas — `localStorage`,
    `beforeunload`, la persistance serveur. Chercher ces noms dans le texte
    brut accuserait la prose qui les refuse. Le dépôt a payé cette erreur
    trois fois pendant `UI-CP8R`.
    """
    src = JS.read_text(encoding="utf-8")
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return re.sub(r"(?m)^\s*//.*$", "", src)


def _balisage() -> str:
    src = CARD.read_text(encoding="utf-8")
    return re.sub(r"\{#.*?#\}", "", src, flags=re.DOTALL)


# ═══════════════════════════════════════════════════════════════════════
#  LE STOCKAGE CHOISI, ET CEUX QUI SONT REFUSÉS
# ═══════════════════════════════════════════════════════════════════════


def test_le_tampon_vit_dans_sessionStorage():
    """`§1` — un tampon de récupération, borné à l'onglet."""
    assert "sessionStorage" in _code()


def test_localStorage_n_est_pas_utilise():
    """`§2` — `localStorage` survivrait au navigateur entier.

    C'est une persistance PLUS LARGE que le défaut prouvé : elle
    promettrait une continuité qu'aucune mesure ne soutient, et exigerait
    une politique d'expiration que la tranche n'a pas à inventer.
    """
    assert "localStorage" not in _code(), (
        "`localStorage` promet plus que le défaut mesuré ne demande"
    )


def test_aucune_persistance_serveur_de_brouillon():
    """`§3` et `§13` — aucune table, aucune colonne, aucune route.

    Un magasin serveur ne se justifierait que sur une preuve de besoin
    au-delà d'une page-session : fermeture d'onglet, continuité entre
    appareils, propriété partagée entre onglets. La mesure n'en a produit
    aucune, donc on n'en construit aucun.
    """
    # ⚠ PREMIÈRE ÉCRITURE TROP LARGE, ET ELLE ACCUSAIT DU CODE SAIN.
    # Elle interdisait le mot « draft » dans toutes les migrations —
    # `user_programs` en porte un depuis des mois, mais c'est un STATUT DE
    # CYCLE DE VIE de programme (`draft / validated / published /
    # archived`), sans le moindre rapport avec une saisie en cours. Une
    # garde qui cherche un mot au lieu d'une propriété trouve des
    # homonymes.
    #
    # La propriété DÉCIDABLE : `CP8I` n'ajoute aucune migration, et les
    # colonnes de `SetLog` sont exactement celles que `CP8R` a laissées.
    from app.models.session import SetLog

    attendues = {
        "id", "session_exercise_id", "kind", "set_index", "weight_kg",
        "reps", "technique", "execution_quality", "reps_target",
        "completed", "completed_at", "rest_dismissed_at",
    }
    assert set(SetLog.__table__.columns.keys()) == attendues, (
        "les colonnes de `SetLog` ont bougé : `CP8I` devait n'en toucher "
        "aucune"
    )


# ═══════════════════════════════════════════════════════════════════════
#  LE MOMENT DE L'ÉCRITURE
# ═══════════════════════════════════════════════════════════════════════


def test_on_ecrit_a_la_frappe_et_jamais_sur_unload():
    """`§8` — `unload` / `beforeunload` ne se déclenchent pas de façon
    fiable sur mobile : un onglet évincé par l'OS ne les voit jamais. En
    faire le mécanisme de sauvegarde, c'est sauvegarder au moment précis où
    le navigateur ne le permet plus.
    """
    code = _code()
    assert '"input"' in code, "aucune écoute de la frappe"
    for interdit in ("beforeunload", "unload"):
        assert interdit not in code, (
            f"`{interdit}` ne se déclenche pas de façon fiable sur mobile"
        )


def test_visibilitychange_est_un_filet_pas_l_unique_occasion():
    """`§8` — défensif, jamais seul."""
    code = _code()
    assert "visibilitychange" in code
    assert code.count('addEventListener("input"') >= 2, (
        "les deux champs doivent écrire, pas seulement le premier"
    )


# ═══════════════════════════════════════════════════════════════════════
#  LA RESTAURATION N'ENGAGE RIEN
# ═══════════════════════════════════════════════════════════════════════


def test_la_restauration_ne_declenche_aucun_evenement():
    """`§9` — LE POINT LE PLUS DANGEREUX DE LA TRANCHE.

    `DF-B` valide la série dès que les deux champs portent une valeur et
    qu'un `change` part. Si la restauration émettait un événement
    synthétique, remplir les champs SOUMETTRAIT la série : une
    récupération d'affichage deviendrait un événement de domaine —
    exactement ce que `§9` interdit, et exactement ce que le mandat de la
    tranche exclut.

    La garde lit la fonction de restauration et exige qu'elle ne
    construise ni ne distribue aucun événement.
    """
    code = _code()
    debut = code.find("function restaurerBrouillons")
    assert debut != -1, "la fonction de restauration a disparu"
    fin = code.find("\n  function ", debut + 10)
    corps = code[debut:fin if fin != -1 else len(code)]

    for interdit in ("dispatchEvent", "new Event", "requestSubmit",
                     "submit()", "click()"):
        assert interdit not in corps, (
            f"la restauration émet `{interdit}` : une valeur restaurée "
            "deviendrait une série enregistrée"
        )


def test_le_tampon_ne_touche_a_aucun_fait_de_domaine():
    """`§1` et `§13` — ni complétion, ni repos, ni recommandation."""
    code = _code()
    debut = code.find("var PREFIXE")
    fin = code.find("function init()")
    tampon = code[debut:fin]
    for interdit in ("completed", "rest_dismissed", "completed_at",
                     "fetch(", "XMLHttpRequest"):
        assert interdit not in tampon, (
            f"le tampon touche `{interdit}` : il a quitté l'affichage"
        )


# ═══════════════════════════════════════════════════════════════════════
#  LA CLÉ, ET CE QU'ELLE NE CONTIENT PAS
# ═══════════════════════════════════════════════════════════════════════


def test_la_cle_porte_la_seance_et_la_serie():
    """`§6` — jamais un global `draft_weight`.

    L'identité de séance suffit à l'isolation entre comptes : le serveur
    refuse une séance qui n'appartient pas à l'utilisateur, donc un autre
    compte ne peut jamais RENDRE la page qui lirait la clé. Y ajouter un
    identifiant d'utilisateur serait de la donnée que la clé n'a pas
    besoin de porter (`§12`).
    """
    code = _code()
    assert 'PREFIXE + sessionId + ":" + setId' in code, (
        "la clé ne porte pas l'identité réelle (séance + série)"
    )
    for global_ in ("draft_weight", "draft_reps", '"draft"'):
        assert global_ not in code, f"clé globale `{global_}`"


def test_le_tampon_ne_stocke_que_la_serie_en_cours():
    """`§12` — pas d'ombre cliente de la base.

    Ni recommandation, ni profil corporel, ni historique, ni identité.
    """
    code = _code()
    for interdit in ("recommendation", "body_", "profile", "username",
                     "history", "bodyweight"):
        assert interdit not in code, (
            f"`{interdit}` n'a rien à faire dans un tampon de saisie"
        )


# ═══════════════════════════════════════════════════════════════════════
#  PÉREMPTION ET NETTOYAGE
# ═══════════════════════════════════════════════════════════════════════


def test_un_brouillon_perime_est_jete_et_non_applique():
    """`§7` — la vérité serveur gagne toujours.

    La base de comparaison est `defaultValue`, pas `value` : le serveur
    rend `value="..."` dans le HTML, le navigateur en fait `defaultValue`,
    et la frappe ne le modifie pas. Comparer `value` aurait comparé le
    brouillon à lui-même — la garde n'aurait jamais rien vu.
    """
    code = _code()
    assert "defaultValue" in code, (
        "la base de comparaison n'est pas la valeur canonique du serveur"
    )
    assert "perime" in code, "aucune détection de brouillon périmé"


def test_le_serveur_declare_les_series_enregistrees():
    """`§10` — effacer APRÈS confirmation, y compris à l'état REPOS.

    À l'état `REST`, la bande de séries n'est pas rendue (`UI-CP2`) : sans
    champ, le client ne peut PAS comparer la valeur canonique, et le
    brouillon de la série qu'on venait d'enregistrer survivait à son
    propre POST. Mesuré — deux preuves rouges.

    Le serveur déclare donc les séries enregistrées. C'est un fait, pas
    une valeur : la liste ne contient que des identifiants déjà présents
    dans la page.
    """
    assert "data-sets-enregistrees" in _balisage(), (
        "le gabarit ne déclare plus les séries enregistrées"
    )
    assert "data-sets-enregistrees" in _code(), (
        "le tampon ne lit plus la déclaration du serveur"
    )


def test_la_deconnexion_purge_les_brouillons():
    """`§10` — portée honnête, et elle est écrite dans le code.

    Ce module ne tourne que sur la console de séance : le nettoyage couvre
    la déconnexion DEPUIS cette surface. Ailleurs, l'isolation reste
    structurelle — `sessionStorage` meurt avec l'onglet, et un autre compte
    ne peut pas rendre la séance. Les pages d'authentification portent un
    contrat « aucun script » qu'une garde épingle : on ne l'ouvre pas pour
    un nettoyage de confort.
    """
    code = _code()
    assert '/logout"]' in code, "aucune purge à la déconnexion"
    assert "removeItem" in code


def test_le_stockage_indisponible_ne_casse_pas_la_page():
    """Un navigateur en navigation privée stricte fait LEVER l'accès au
    stockage lui-même. Une commodité ne doit jamais casser l'exécution
    d'une séance."""
    code = _code()
    assert "try" in code
    debut = code.find("function _ss()")
    assert debut != -1
    corps = code[debut:debut + 400]
    assert "catch" in corps, (
        "l'accès au stockage n'est pas gardé : une session privée "
        "casserait la page entière"
    )


# ═══════════════════════════════════════════════════════════════════════
#  CE QUE LA TRANCHE N'OUVRE PAS
# ═══════════════════════════════════════════════════════════════════════


def test_aucun_service_worker_ni_hors_ligne():
    """`§18` — `CP8I` ne doit pas déborder en travail hors ligne / PWA."""
    code = _code()
    for interdit in ("serviceWorker", "caches.", "navigator.onLine",
                     "IndexedDB", "indexedDB"):
        assert interdit not in code, f"`{interdit}` : dérive hors ligne"
