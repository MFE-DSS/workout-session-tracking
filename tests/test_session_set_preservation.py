"""La recomposition de la séance ne doit pas effacer de série.

POURQUOI CETTE GARDE EXISTE
---------------------------
`_persist_set_values` (`app/routers/sessions.py`) boucle sur **toutes** les
`set_logs` de l'exercice et écrit sans condition ::

    sl.weight_kg = to_float(form.get(f"set_{sl.id}_weight_kg"))
    sl.reps      = to_int(form.get(f"set_{sl.id}_reps"))
    sl.completed = (new_weight is not None) or (new_reps is not None)

**Un champ absent du DOM renvoyait `None` : la série était effacée et
dé-complétée.** Silencieusement, au premier enregistrement suivant.

⚠ **`UI-CP2.0` A FERMÉ CE DÉFAUT À LA SOURCE** (2026-09-08). Une série absente
du formulaire est désormais **INCHANGÉE** ; seul un champ soumis VIDE efface,
et l'effacement nommé (`clear_set`) reste explicite. Ce fichier ne surveille
donc plus une perte imminente : il **fige l'acquis**, et vérifie que la
composition reste auto-suffisante. Le libellé ci-dessus est conservé au passé
parce que la raison d'être de la suite se lit dans son histoire.

Le dépôt gardait déjà cet invariant — mais en lisant le **source du gabarit** :
présence de la macro `set_values`, appelée par `past_line` et `future_line`.
Cette forme protège **une composition donnée**, pas l'invariant. Le programme
UI en cours remplace précisément cette composition par l'instrument M3 : le
jour où les macros changent de nom, la garde de source tombe, et rien ne dit
plus si des données se perdent.

Ces tests-ci vérifient le **comportement** : on rend une vraie séance, on
rejoue le formulaire **exactement comme le navigateur l'enverrait** — c'est-à-
dire uniquement les champs présents dans le HTML — et on vérifie qu'aucune
série n'a perdu ses valeurs. Ils survivent à n'importe quelle composition.

Tier : **T1** — perte de données. Ne se retire pas, ne s'assouplit pas.
"""

from __future__ import annotations

import re

import pytest
from sqlalchemy import select


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    assert r.status_code in (302, 303), r.status_code
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _sets_of(session_id: int):
    """`{set_id: (session_exercise_id, weight, reps, completed)}` pour la séance."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        rows = db.execute(
            select(SetLog, SessionExercise.id)
            .join(SessionExercise, SetLog.session_exercise_id == SessionExercise.id)
            .where(SessionExercise.session_id == session_id)
        ).all()
        return {
            sl.id: (se_id, sl.weight_kg, sl.reps, sl.completed)
            for sl, se_id in rows
        }


#: Tout `name="…"` d'un `<input>`/`<select>`/`<textarea>` du HTML rendu.
_FIELD = re.compile(
    r"<(?:input|select|textarea)\b[^>]*\bname=\"([^\"]+)\"[^>]*>", re.I
)


#: Un formulaire d'exercice, repéré par sa cible `…/exercises/<id>`.
#: HTML interdit les formulaires imbriqués : un non-greedy suffit et n'est pas
#: une approximation douteuse.
_EXERCISE_FORM = re.compile(
    r"<form\b[^>]*\baction=\"[^\"]*/exercises/(\d+)\"[^>]*>(.*?)</form>",
    re.I | re.DOTALL,
)


def _fields_in(fragment: str) -> dict[str, str]:
    """Ce qu'un navigateur enverrait pour CE fragment : nom → valeur.

    Générreux côté valeurs (on relit `value=`), STRICT côté présence : un champ
    absent du HTML est absent du POST. C'est exactement ce qui efface une série.
    """
    out: dict[str, str] = {}
    for m in _FIELD.finditer(fragment):
        tag, name = m.group(0), m.group(1)
        if re.search(r'\btype="(submit|button|image|reset)"', tag, re.I):
            continue
        if re.search(r'\btype="(checkbox|radio)"', tag, re.I) and "checked" not in tag:
            continue
        v = re.search(r'\bvalue="([^"]*)"', tag)
        out[name] = v.group(1) if v else ""
    return out


def _exercise_forms(html: str) -> dict[int, dict[str, str]]:
    """`{session_exercise_id: champs de SON formulaire}`.

    ⚠ Le périmètre compte. `_persist_set_values` ne touche que les
    `set_logs` de l'exercice POSTÉ (`se.set_logs`). Exiger que toute la page
    porte toutes les séries de la séance serait un faux positif : chaque
    exercice a son propre formulaire, et c'est correct.
    """
    return {
        int(m.group(1)): _fields_in(m.group(2))
        for m in _EXERCISE_FORM.finditer(html)
    }


@pytest.fixture
def session_with_a_logged_set(client):
    """Une séance réelle dont la première série de l'exercice actif est saisie."""
    session_id = _start(client)
    sets = _sets_of(session_id)
    assert sets, "aucune série — la garde tournerait à vide"

    forms = _exercise_forms(client.get(f"/sessions/{session_id}").text)
    assert forms, "aucun formulaire d'exercice — le sélecteur a dérivé"

    se_id = min(forms)
    own = sorted(sid for sid, row in sets.items() if row[0] == se_id)
    assert own, f"l'exercice {se_id} n'a aucune série"
    target = own[0]

    data = dict(forms[se_id])
    data[f"set_{target}_weight_kg"] = "82"
    data[f"set_{target}_reps"] = "9"
    data["nav"] = "stay_norest"
    client.post(
        f"/sessions/{session_id}/exercises/{se_id}", data=data, follow_redirects=False
    )

    assert _sets_of(session_id)[target][1] == 82, "la mise en place n'a rien enregistré"
    return session_id, se_id, target


def test_every_form_carries_all_the_sets_it_will_overwrite(client):
    """L'invariant, énoncé sur le RENDU et non sur le gabarit.

    Pour CHAQUE formulaire d'exercice, les deux champs de CHACUNE de ses
    séries doivent être présents — visibles ou cachés, peu importe la
    composition. Le formulaire écrase toutes ses séries : ce qu'il ne porte
    pas, il l'efface.
    """
    session_id = _start(client)
    sets = _sets_of(session_id)
    forms = _exercise_forms(client.get(f"/sessions/{session_id}").text)
    assert forms, "aucun formulaire d'exercice trouvé — sélecteur à revoir"

    missing = []
    for se_id, fields in forms.items():
        for sid, row in sets.items():
            if row[0] != se_id:
                continue  # série d'un AUTRE exercice : ce POST n'y touche pas
            missing += [
                f"exercice {se_id} → set_{sid}_{f}"
                for f in ("weight_kg", "reps")
                if f"set_{sid}_{f}" not in fields
            ]
    assert missing == [], (
        f"{len(missing)} champ(s) absent(s) : {missing[:6]}. "
        "Le formulaire d'exercice doit rester AUTO-SUFFISANT : il porte toutes "
        "ses séries, donc un aller-retour restitue l'état complet. Depuis "
        "`UI-CP2.0` un champ absent n'efface plus rien — cette garde tient "
        "désormais la COMPOSITION, plus la perte de données."
    )


def test_replaying_a_form_unchanged_loses_nothing(session_with_a_logged_set, client):
    """Le vrai test : rejouer le formulaire n'efface rien.

    On renvoie le formulaire tel que le navigateur le composerait, sans y
    toucher. C'est précisément ce qu'une composition qui oublie un champ
    caché casse — et c'est ce que fait l'utilisateur à chaque série.
    """
    session_id, se_id, target = session_with_a_logged_set
    before = _sets_of(session_id)

    forms = _exercise_forms(client.get(f"/sessions/{session_id}").text)
    data = dict(forms[se_id])
    data["nav"] = "stay_norest"
    client.post(
        f"/sessions/{session_id}/exercises/{se_id}", data=data, follow_redirects=False
    )

    after = _sets_of(session_id)
    lost = [
        sid for sid, row in before.items()
        if row[1] is not None and after[sid][1] is None
    ]
    assert lost == [], (
        f"séries effacées par un simple aller-retour : {lost}. "
        "Un champ manquant dans le rendu suffit."
    )
    assert after[target][1] == before[target][1]
    assert after[target][2] == before[target][2]


def test_the_probe_would_notice_a_missing_field(session_with_a_logged_set, client):
    """Garde de la garde — **RÉÉCRITE PAR `UI-CP2.0`, SUR SA PROPRE CONSIGNE**.

    Son écriture d'origine retirait deux champs du formulaire et vérifiait que
    la série était **bel et bien effacée** : c'est ainsi qu'elle prouvait que
    les deux gardes ci-dessus ne passaient pas à vide.

    Elle portait aussi son propre mode d'emploi : *« si ce test cesse d'échouer
    à l'effacement, c'est que `_persist_set_values` a changé de comportement —
    les réécrire avant de continuer »*. C'est exactement ce qui vient
    d'arriver : `UI-CP2.0` a fait d'une série absente une série **INCHANGÉE**,
    et la sonde a perdu son objet. Elle est donc réécrite, pas assouplie.

    CE QUI POURRAIT ENCORE RENDRE LES GARDES CI-DESSUS CREUSES : un routeur qui
    n'écrirait plus RIEN. « Aucune série perdue » serait alors trivialement
    vrai. La sonde prouve donc les deux moitiés du contrat :

      1. l'écrivain est VIVANT — une valeur soumise et modifiée est persistée ;
      2. le chemin destructeur reste ATTEIGNABLE — un champ soumis VIDE efface
         toujours, ce qui est la sémantique `Sx_24 §E` et une capacité réelle.

    Sans la moitié 2, « préservation » serait satisfaite par un écrivain inerte.
    """
    session_id, se_id, target = session_with_a_logged_set

    # 1 — L'ÉCRIVAIN EST VIVANT.
    forms = _exercise_forms(client.get(f"/sessions/{session_id}").text)
    data = dict(forms[se_id])
    data[f"set_{target}_weight_kg"] = "91"
    data[f"set_{target}_reps"] = "5"
    data["nav"] = "stay_norest"
    client.post(
        f"/sessions/{session_id}/exercises/{se_id}", data=data, follow_redirects=False
    )
    row = _sets_of(session_id)[target]
    assert row[1] == 91, "une valeur soumise n'est pas écrite — l'écrivain est mort"
    assert row[2] == 5, "les répétitions soumises ne sont pas écrites"

    # 2 — LE CHEMIN DESTRUCTEUR RESTE ATTEIGNABLE, par un champ VIDE et non
    #     par une clé absente.
    forms = _exercise_forms(client.get(f"/sessions/{session_id}").text)
    data = dict(forms[se_id])
    data[f"set_{target}_weight_kg"] = ""
    data[f"set_{target}_reps"] = ""
    data["nav"] = "stay_norest"
    client.post(
        f"/sessions/{session_id}/exercises/{se_id}", data=data, follow_redirects=False
    )
    row = _sets_of(session_id)[target]
    assert row[1] is None, "un champ vidé n'efface plus la charge"
    assert row[2] is None, "un champ vidé n'efface plus les répétitions"
    assert row[3] is False, "la série reste marquée faite après un vidage"


def test_an_absent_field_no_longer_erases(session_with_a_logged_set, client):
    """`UI-CP2.0` — le défaut que la suite entière surveillait est FERMÉ.

    Ce fichier existait parce qu'un champ absent du DOM effaçait sa série au
    prochain enregistrement. La composition devait donc porter tous ses champs,
    faute de quoi elle détruisait des données d'entraînement.

    Le contrat d'écriture a changé : **absent veut désormais dire inchangé**.
    Cette garde fige l'acquis, pour qu'un retour au contrat tout-ou-rien ne
    puisse pas passer inaperçu.
    """
    session_id, se_id, target = session_with_a_logged_set
    avant = _sets_of(session_id)[target]

    forms = _exercise_forms(client.get(f"/sessions/{session_id}").text)
    data = dict(forms[se_id])
    data.pop(f"set_{target}_weight_kg", None)
    data.pop(f"set_{target}_reps", None)
    data["nav"] = "stay_norest"
    client.post(
        f"/sessions/{session_id}/exercises/{se_id}", data=data, follow_redirects=False
    )

    apres = _sets_of(session_id)[target]
    assert apres[1] == avant[1], "une série absente du formulaire a perdu sa charge"
    assert apres[2] == avant[2], "une série absente a perdu ses répétitions"
    assert apres[3] is True, "une série absente a été dé-complétée"
