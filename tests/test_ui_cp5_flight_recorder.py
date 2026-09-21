"""`UI-CP5 FLIGHT_RECORDER` — les gardes du DEBRIEFING.

CE QUE CES GARDES FERMENT
--------------------------
L'arbitrage opérateur a corrigé la proposition sur deux points, et chacun se
franchit sans que le rendu proteste :

1. **UN MOTEUR DE « PLUS SIGNIFICATIF » S'INSTALLE.** Un score composite, un
   tri par ampleur, une pondération entre kilos et anomalies — et l'instrument
   se met à décider ce qui compte, opaquement. C'est exactement ce que
   `OPERATOR_DECISION C8` interdit ailleurs dans ce produit.
2. **LE SIGNAL VIENT DE LA MAUVAISE SÉANCE.** Le défaut existe *déjà* dans le
   dépôt : `weekly_loop._pick_top_anomaly` trie `started_at.asc()` et rend la
   **première** séance qui porte une anomalie — donc la plus ANCIENNE de la
   semaine. Un instrument qui dit « depuis ta dernière séance » en parlant
   d'avant-hier ment sans qu'aucune garde ne le voie.

S'y ajoute le cas que la directive nomme **obligatoire** : l'historique MINCE.
Mesuré avant cette tranche — à deux séances, la plus grosse typographie de
`/progress` devenait un *titre de section* ; à zéro, tout le partiel était
supprimé. Un vide silencieux, sur l'état de tout compte neuf.
"""
from __future__ import annotations

import ast
import pathlib
from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE = ROOT / "app/services/flight_recorder.py"


# ────────────────────────── fabriques ──────────────────────────


def _progression(**kw):
    """La sortie de `build_progression_view`, avec ses sept clés."""
    base = {
        "lead": None, "rows": [], "more": [], "awaiting": [],
        "unresolved": 0, "unresolved_names": [], "any": False,
    }
    base.update(kw)
    return base


def _lead(**kw):
    base = {
        "slug": "rdl", "name": "Romanian Deadlift", "previous": "70 × 10",
        "latest": "72,5 × 10", "latest_weight": "72,5", "latest_reps": "10",
        "previous_weight": "70", "previous_reps": "10",
        "delta_weight": "+2,5 kg", "delta_reps": "= reps",
        "trace": ["70", "72,5"], "href": "/exercise-history/rdl",
    }
    base.update(kw)
    return base


class _SetLog:
    def __init__(self, kind="work", idx=1, weight=None, reps=None, done=True):
        self.kind, self.set_index = kind, idx
        self.weight_kg, self.reps, self.completed = weight, reps, done


class _SE:
    def __init__(self, code="E1", name="Ex1", score=None, logs=(),
                 substituted=None, te=None):
        self.exercise_code_snapshot = code
        self.exercise_name_snapshot = name
        self.substituted_name = substituted
        self.success_score = score
        self.set_logs = list(logs)
        self.template_exercise = te


class _Seance:
    def __init__(self, exercices=(), sid=1, gabarit="Push A"):
        self.session_exercises = list(exercices)
        self.id = sid
        self.template_name_snapshot = gabarit


# ═════════ 1. LA PRÉCÉDENCE EST SÉMANTIQUE, VERSIONNÉE, ET N'EST PAS UN SCORE


def test_la_precedence_est_versionnee_et_son_ordre_est_epingle():
    """Les deux dans la MÊME assertion, et c'est le mécanisme d'application.

    Réordonner la précédence oblige à toucher la ligne qui porte la version.
    Deux assertions séparées auraient laissé réordonner sans reversionner.
    """
    from app.services import flight_recorder as fr

    assert (fr.ORDRE_PRECEDENCE, fr.PRECEDENCE_VERSION) == (
        (fr.SIGNAL_ATTENTION, fr.SIGNAL_MOUVEMENT, fr.SIGNAL_INSUFFISANT),
        "L1-DEBRIEF/1",
    )


def test_aucun_moteur_de_signification_ne_peut_s_y_cacher():
    """Garde STRUCTURELLE, sur l'AST — pas sur la prose.

    Un score composite a besoin d'ORDONNER ou de PONDÉRER. Les deux sont
    absents du module, et une garde qui lit l'arbre le prouve là où une
    relecture ne le promettrait que jusqu'au prochain commit.
    """
    arbre = ast.parse(MODULE.read_text(encoding="utf-8"))
    appels = [
        n.func.id for n in ast.walk(arbre)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    ]
    for interdit in ("sorted", "max", "min"):
        assert interdit not in appels, (
            f"`{interdit}` classe ou pondère — un moteur de signification "
            f"commence exactement là"
        )
    produits = [
        n for n in ast.walk(arbre)
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Mult, ast.Div, ast.Pow))
    ]
    assert not produits, "une pondération est apparue dans le debriefing"


def test_aucune_variante_ne_peut_porter_un_rang():
    """L'état illégal est INEXPRIMABLE, pas seulement non affiché.

    ⚠ `dataclasses.fields()`, PAS `__dataclass_fields__` : le second inclut les
    pseudo-champs `ClassVar`, et l'interroger m'avait fait conclure à tort
    qu'une `ClassVar` était devenue une donnée d'instance (leçon `UI-CP4`).
    """
    import dataclasses

    from app.services.flight_recorder import (
        DebriefAttention,
        DebriefInsuffisant,
        DebriefMouvement,
    )

    for variante in (DebriefAttention, DebriefMouvement, DebriefInsuffisant):
        champs = {f.name for f in dataclasses.fields(variante)}
        for interdit in ("score", "rang", "poids_signal", "gravite", "priorite"):
            assert interdit not in champs, f"{variante.__name__} porte {interdit}"
        assert "signal" not in champs, (
            f"{variante.__name__}.signal est devenu un champ : une instance "
            f"pourrait mentir sur son propre type"
        )


def test_un_debriefing_insuffisant_ne_peut_pas_porter_un_ecart():
    """Une comparaison inventée dans l'état « pas encore comparable ».

    C'est le mensonge le plus tentant de cette tranche, et il devient
    inexprimable : la variante n'a aucun champ où l'écrire.
    """
    import dataclasses

    from app.services.flight_recorder import DebriefInsuffisant

    champs = {f.name for f in dataclasses.fields(DebriefInsuffisant)}
    for interdit in ("ecart_poids", "ecart_reps", "dernier_poids",
                     "precedent_poids", "trace"):
        assert interdit not in champs, (
            f"`{interdit}` permettrait d'afficher une comparaison là où il n'y "
            f"en a pas"
        )


def test_le_debriefing_reste_hors_base_et_hors_horloge():
    """Pur : ni `sqlalchemy`, ni `datetime`. Patron `TRAIN1-B`."""
    arbre = ast.parse(MODULE.read_text(encoding="utf-8"))
    importes = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            importes.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            importes.add(n.module.split(".")[0])
    assert "sqlalchemy" not in importes
    assert "datetime" not in importes


# ═════════ 2. LE SIGNAL VIENT DE LA DERNIÈRE SÉANCE ═════════


def test_le_signal_d_attention_vient_de_la_derniere_seance_pas_de_la_plus_ancienne(
    client,
):
    """⚠ LA GARDE VÉRIFIÉE PAR MUTATION — ET LE DÉFAUT EST DÉJÀ DANS LE DÉPÔT.

    Deux séances terminées dans la MÊME semaine ISO : l'ancienne ne porte que
    des échauffements (règle D), la récente a un score élevé avec des reps sous
    la cible (règle E).

    Brancher `weekly_loop._pick_top_anomaly` à la place du sélecteur rend
    « D » — il trie `started_at.asc()` et prend la première. Aucune mutation
    artificielle n'est nécessaire : la garde mord sur le code d'hier.
    """
    from app.database import SessionLocal
    from app.services.flight_recorder import SIGNAL_ATTENTION, construire_debriefing
    from app.services.flight_recorder_inputs import derniere_seance_exploitable
    from tests.test_anomalies import _mk_session_for_anomalies

    ancienne = _mk_session_for_anomalies(exercises=[{
        "code": "OLD", "name": "Exercice ancien",
        "warmup_sets": [{"weight_kg": 20, "reps": 12, "completed": True}],
        "work_sets": [{"weight_kg": 40, "reps": 8, "completed": False}],
    }])
    recente = _mk_session_for_anomalies(exercises=[{
        "code": "NEW", "name": "Exercice récent", "success_score": 100,
        "rep_targets": [{"min_reps": 8, "max_reps": 10}],
        "work_sets": [{"weight_kg": 60, "reps": 3, "completed": True}],
    }])

    base = datetime.now(UTC)
    with SessionLocal() as db:
        from app.models.session import WorkoutSession

        db.get(WorkoutSession, ancienne).started_at = base - timedelta(days=2)
        db.get(WorkoutSession, recente).started_at = base - timedelta(hours=2)
        db.commit()

    with SessionLocal() as db:
        seance = derniere_seance_exploitable(db, get_test_user_id())
        assert seance is not None, "prémisse : une séance exploitable doit exister"
        assert seance.id == recente, (
            "le sélecteur a pris une autre séance que la plus récente"
        )
        d = construire_debriefing(db and seance, _progression())

    assert d.signal == SIGNAL_ATTENTION
    assert d.rule_code == "E", (
        f"le signal vient de la mauvaise séance : « {d.rule_code} » au lieu de "
        f"« E ». `_pick_top_anomaly` rend « D » — la plus ancienne gagne."
    )


def test_une_seance_exclue_des_stats_ne_parle_pas(client):
    """L'utilisateur l'a retirée de ses KPI : elle ne revient pas par le
    debriefing."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.flight_recorder_inputs import derniere_seance_exploitable
    from tests.test_anomalies import _mk_session_for_anomalies

    gardee = _mk_session_for_anomalies(exercises=[{"code": "K", "name": "Gardée"}])
    exclue = _mk_session_for_anomalies(exercises=[{"code": "X", "name": "Exclue"}])

    base = datetime.now(UTC)
    with SessionLocal() as db:
        db.get(WorkoutSession, gardee).started_at = base - timedelta(days=1)
        e = db.get(WorkoutSession, exclue)
        e.started_at = base
        e.excluded_from_stats = True
        db.commit()

    with SessionLocal() as db:
        assert derniere_seance_exploitable(db, get_test_user_id()).id == gardee


# ═════════ 3. LA RARETÉ EST UN CAS DE PREMIÈRE CLASSE ═════════


def test_une_comparaison_insuffisante_dit_toujours_pourquoi():
    """⚠ CINQ corpus, paramétrés — la rareté n'est pas un `if` défensif planqué.

    La 5ᵉ cause (`aucun_mouvement`) a été trouvée en traçant le compte
    cardio-seulement : les quatre autres rendaient un tuple **vide**, donc
    « pas encore possible » SANS DIRE POURQUOI — exactement le vide silencieux
    que cette tranche corrige.
    """
    from app.services.flight_recorder import (
        CAUSE_AUCUN_MOUVEMENT,
        CAUSE_AUCUNE_SEANCE,
        CAUSE_AUCUNE_SERIE,
        CAUSE_NOM_NON_RATTACHE,
        CAUSE_UNE_SEULE_SEANCE,
        ETAT_INCONNU,
        ETAT_PARTIEL,
        ETAT_ZERO,
        SIGNAL_INSUFFISANT,
        construire_debriefing,
    )
    from app.services.progression_view import (
        RAISON_AUCUNE_SERIE,
        RAISON_UNE_SEULE_SEANCE,
    )

    corpus = [
        ("aucune séance", None, _progression(), CAUSE_AUCUNE_SEANCE, ETAT_INCONNU),
        ("cardio seul", _Seance(), _progression(), CAUSE_AUCUN_MOUVEMENT, ETAT_ZERO),
        ("pratiqué une fois", _Seance(),
         _progression(any=True, awaiting=[{"reason": RAISON_UNE_SEULE_SEANCE}]),
         CAUSE_UNE_SEULE_SEANCE, ETAT_ZERO),
        ("sans série notée", _Seance(),
         _progression(any=True, awaiting=[{"reason": RAISON_AUCUNE_SERIE}]),
         CAUSE_AUCUNE_SERIE, ETAT_ZERO),
        ("nom non rattaché", _Seance(),
         _progression(any=True, unresolved=3, unresolved_names=["X", "Y", "Z"]),
         CAUSE_NOM_NON_RATTACHE, ETAT_PARTIEL),
    ]

    for nom, seance, prog, cause_attendue, etat_attendu in corpus:
        d = construire_debriefing(seance, prog)
        assert d.signal == SIGNAL_INSUFFISANT, nom
        assert d.causes != (), (
            f"« {nom} » : « pas encore possible » sans dire pourquoi"
        )
        assert cause_attendue in {c.code for c in d.causes}, nom
        assert d.etat == etat_attendu, nom
        assert all(c.libelle for c in d.causes), nom


def test_un_compte_vide_rend_un_debriefing_et_non_rien():
    """Le L1 possède la hiérarchie MÊME quand il n'a rien à comparer.

    Contre-mesure directe au vide mesuré : à zéro séance, `progression.any` est
    `False` et tout le partiel de progression était supprimé. L'instrument
    parlait donc d'autant moins qu'il avait moins à dire.
    """
    from app.services.flight_recorder import SIGNAL_INSUFFISANT, construire_debriefing

    d = construire_debriefing(None, _progression())
    assert d is not None
    assert d.signal == SIGNAL_INSUFFISANT
    assert d.libelle
    assert d.sr, "un état sans équivalent textuel n'est pas un état rendu"


# ═════════ 4. LES TROIS RANGS, ET LEUR ORDRE ═════════


def test_l_attention_passe_devant_une_comparaison_disponible():
    """Le rung 1 prime, même quand le rung 2 aurait quelque chose à dire."""
    from app.services.flight_recorder import SIGNAL_ATTENTION, construire_debriefing

    seance = _Seance([_SE(
        code="A1", name="Développé", score=100,
        te=type("TE", (), {"rep_targets": [type("RT", (), {"min_reps": 8})()]})(),
        logs=[_SetLog(weight=60, reps=3)],
    )])
    d = construire_debriefing(seance, _progression(any=True, lead=_lead()))
    assert d.signal == SIGNAL_ATTENTION


def _contexte_progress(client) -> dict:
    """Le dict de contexte rendu par `/progress`.

    On observe le CONTEXTE et non le HTML : la propriété tenue ici est une
    décision de view-model, et l'épingler sur du balisage la rendrait fausse au
    premier renommage de classe — le mode d'échec déjà payé trois fois sur ce
    dépôt (`test_the_history_row_is_the_primary_action`).
    """
    import app.routers.pages as pages

    vus: dict = {}
    vrai = pages.templates.TemplateResponse

    def espion(request, name, context=None, *a, **k):
        if name == "progress.html":
            vus.update(context or {})
        return vrai(request, name, context, *a, **k)

    pages.templates.TemplateResponse = espion
    try:
        assert client.get("/progress").status_code == 200
    finally:
        pages.templates.TemplateResponse = vrai
    assert vus, "le contexte n'a pas été observé — la sonde ne mesure rien"
    return vus


def test_le_rang_souverain_appartient_au_l1_quel_que_soit_le_signal(client):
    """⚠ CETTE GARDE NAÎT D'UN DÉFAUT MESURÉ AU RENDU, PAS D'UNE HYPOTHÈSE.

    La première écriture de la route ne vidait `progression.lead` que sur le
    signal `mouvement`. Sur le compte de labo `pilote-anomalie`, le L1
    annonçait « À VÉRIFIER · Rowing machine chest-supported » à 22 px et le
    relevé de progression gardait ses **32 px** juste en dessous : le plus gros
    objet de l'écran était un « 37,5 » sans rapport avec la réponse.

    C'est l'inversion de hiérarchie que `UI-CP5` existe pour fermer, revenue
    par la branche qu'on regardait le moins. Elle était invisible aux gardes de
    `test_progression_sovereign_readout.py`, qui comparent des tailles
    DÉCLARÉES dans la feuille : aucune taille n'était fautive, c'est leur
    COEXISTENCE sur un même écran qui l'était.

    L'invariant est donc énoncé sans condition : `/progress` rend TOUJOURS le
    L1, donc `lead` n'y survit JAMAIS. Un `if` sur le signal serait déjà la
    porte par laquelle le défaut est entré.

    ⚠ LE CORPUS EST SEMÉ, ET LA PREMIÈRE ÉCRITURE NE L'ÉTAIT PAS.

    Écrite sur la fixture `client` seule, cette garde restait **verte le défaut
    planté** : ce compte n'a aucun mouvement comparable, donc `lead` y vaut
    déjà `None` et il n'y avait rien à démettre. Une garde qui observe un état
    que son corpus ne produit jamais n'est pas une garde. L'état discriminant —
    un mouvement comparable ET une anomalie sur la dernière séance — est donc
    semé ici, et sa présence est vérifiée AVANT l'invariant.
    """
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.exercise_identity import ensure_exercise
    from app.services.flight_recorder import SIGNAL_ATTENTION
    from tests.test_anomalies import _mk_session_for_anomalies

    # ⚠ `ensure_exercise`, PAS UN `Exercise` POSÉ À LA MAIN. La résolution passe
    # par la table d'ALIAS (`resolve_exercise` joint `ExerciseAlias`), et un
    # exercice sans son propre alias reste introuvable : la première écriture
    # de ce semis rendait `unresolved=['Développé couché barre']` et la garde
    # accusait le produit d'avoir perdu une ligne qu'il n'avait jamais eue.
    nom = "Développé couché barre"
    with SessionLocal() as db:
        ensure_exercise(db, nom)
        db.commit()

    # Deux passages du même mouvement → `build_progression_view` a un `lead`.
    veille = _mk_session_for_anomalies(exercises=[{
        "code": "BP", "name": nom,
        "work_sets": [{"weight_kg": 60, "reps": 8, "completed": True}],
    }])
    # La séance la plus récente porte EN PLUS un signal nommable : le L1
    # annoncera `attention`, et parlera donc d'autre chose que du mouvement.
    aujourdhui = _mk_session_for_anomalies(exercises=[
        {"code": "BP", "name": nom,
         "work_sets": [{"weight_kg": 62.5, "reps": 8, "completed": True}]},
        {"code": "ROW", "name": "Rowing", "success_score": 100,
         "rep_targets": [{"min_reps": 8, "max_reps": 10}],
         "work_sets": [{"weight_kg": 50, "reps": 3, "completed": True}]},
    ])

    base = datetime.now(UTC)
    with SessionLocal() as db:
        db.get(WorkoutSession, veille).started_at = base - timedelta(days=2)
        db.get(WorkoutSession, aujourdhui).started_at = base - timedelta(hours=1)
        db.commit()

    contexte = _contexte_progress(client)
    debrief, progression = contexte["debrief"], contexte["progression"]

    # PRÉMISSES — sans elles, les assertions qui suivent passeraient à vide.
    assert debrief.signal == SIGNAL_ATTENTION, (
        f"le corpus ne produit pas l'état discriminant : signal "
        f"« {debrief.signal} », donc rien à démettre et la garde ne mesure rien"
    )
    assert any(r["name"] == nom for r in progression["rows"]), (
        f"« {nom} » n'est plus rendu du tout — le relevé démis a été supprimé "
        f"au lieu de redescendre (`§5.3`). rows={[r['name'] for r in progression['rows']]} "
        f"awaiting={[a.get('name') for a in progression['awaiting']]} "
        f"unresolved={progression['unresolved_names']}"
    )

    assert progression["lead"] is None, (
        "un second relevé souverain est rendu sous le L1 — c'est lui que l'œil "
        "prend en premier, quoi que le L1 annonce"
    )


def test_le_mouvement_demis_perd_son_rang_mais_pas_son_existence():
    """`§5.3` — JAMAIS UNE SOUSTRACTION SEULE, ET ICI ELLE ÉTAIT FACILE À FAIRE.

    Vider `lead` suffit à fermer le rang. Mais `build_progression_view` l'avait
    SORTI de `rows` en le promouvant (`test_the_promoted_row_leaves_the_list`) :
    se contenter de le vider ferait disparaître l'exercice de la page entière.

    La règle a donc deux moitiés, et cette garde tient la seconde :

      · sur `mouvement`, le L1 EST ce mouvement → il ne redescend pas, sinon la
        promotion se lit comme une duplication ;
      · sur tout autre signal, le L1 parle d'autre chose → le mouvement
        redescend en ligne ordinaire, en tête.
    """
    from app.routers.pages import _demettre_le_releve_de_progression
    from app.services.flight_recorder import SIGNAL_ATTENTION, SIGNAL_MOUVEMENT

    tete = _lead(slug="tete", name="Tête")
    suite = _lead(slug="suite", name="Suite")
    vue = _progression(any=True, lead=tete, rows=[suite])

    attention = _demettre_le_releve_de_progression(vue, SIGNAL_ATTENTION)
    assert attention["lead"] is None
    assert [r["slug"] for r in attention["rows"]] == ["tete", "suite"], (
        "le mouvement démis a disparu de la page au lieu de redescendre"
    )

    mouvement = _demettre_le_releve_de_progression(vue, SIGNAL_MOUVEMENT)
    assert mouvement["lead"] is None
    assert [r["slug"] for r in mouvement["rows"]] == ["suite"], (
        "le L1 et la liste rendent le même mouvement deux fois"
    )


def test_le_rung_2_suit_la_recence_et_non_l_ampleur():
    """Le debriefing PROJETTE `lead` ; il ne re-parcourt pas les lignes.

    `lead` est déjà le mouvement le plus récemment pratiqué, pas le plus gros
    écart (gelé par `test_progression_sovereign_readout.py`). La précédence n'a
    pas le droit de contredire cette souveraineté.
    """
    from app.services.flight_recorder import SIGNAL_MOUVEMENT, construire_debriefing

    recent = _lead(slug="recent", name="Récent", delta_weight="+1 kg")
    enorme = _lead(slug="enorme", name="Énorme", delta_weight="+30 kg")
    d = construire_debriefing(
        None, _progression(any=True, lead=recent, rows=[enorme]),
    )
    assert d.signal == SIGNAL_MOUVEMENT
    assert d.slug == "recent", "le debriefing a promu le plus gros écart"


def test_le_rung_2_projette_sans_reformater():
    """Aucun `format_*` ici : le relevé souverain a déjà choisi son vocabulaire.

    ⚠ `delta.format_delta` est explicitement proscrit — il émet un
    `score_trend`, jugement que cette surface exclut contractuellement.
    """
    import app.services.flight_recorder as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod)
    assert "format_delta" not in code
    assert "score_trend" not in code


# ═════════ 5. LA GRAMMAIRE DE CONFIANCE EST EMPRUNTÉE ═════════


def test_la_grammaire_de_confiance_ne_derive_pas_de_zone_exposure():
    """Les quatre littéraux sont recopiés — donc surveillés.

    `zone_exposure` est la référence TRUST EXPRESSION et elle existe déjà. On
    n'en écrit pas une seconde ; on emprunte la sienne, et une garde rougit si
    l'un des deux jeux dérive.
    """
    from app.services import flight_recorder as fr
    from app.services import zone_exposure as ze

    assert (fr.ETAT_CONNU, fr.ETAT_ZERO, fr.ETAT_PARTIEL, fr.ETAT_INCONNU) == (
        ze.STATE_KNOWN, ze.STATE_ZERO, ze.STATE_PARTIAL, ze.STATE_UNKNOWN,
    )


def test_aucun_second_systeme_de_confiance():
    """Ni score global, ni badge, ni couche de fiabilité."""
    import app.services.flight_recorder as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod).lower()
    for interdit in ("confidence", "score_de_confiance", "badge", "fiabilite"):
        assert interdit not in code, f"« {interdit} » est un second système"


def test_l_etat_partiel_signale_une_ignorance_pas_une_absence():
    """Règle sémantique de `zone_exposure`, appliquée à la comparaison."""
    from app.services.flight_recorder import ETAT_PARTIEL, construire_debriefing

    d = construire_debriefing(
        _Seance(), _progression(any=True, unresolved=4, unresolved_names=["a"]),
    )
    assert d.etat == ETAT_PARTIEL
    assert d.non_rattachees == 4, "le comptage de preuve non attribuée a disparu"


# ═════════ 6. CE QUE LES LIBELLÉS NE DISENT JAMAIS ═════════


def test_les_libelles_ne_revendiquent_jamais_une_importance():
    """§4 — l'interface expose la règle par son étiquette, pas par un score.

    « ton changement le plus significatif » est une affirmation que le produit
    ne peut pas prouver. Elle n'est donc écrite nulle part.

    ⚠ LA GARDE LIT LES CHAÎNES QUI ATTEIGNENT L'UTILISATEUR, PAS LE FICHIER.
    Première écriture : elle balayait toute la source et tombait sur la prose
    qui EXPLIQUE le défaut corrigé (« le plus gros objet de l'écran devenait un
    titre de section »). Une garde qui lit son propre commentaire comme une
    revendication est le mode d'échec le plus fréquent de ce dépôt — celui-ci
    en est la quatorzième instance recensée.
    """
    from app.services import flight_recorder as fr

    rendues = [fr.EN_TETE, fr.LIBELLE_ATTENTION, fr.LIBELLE_MOUVEMENT,
               fr.LIBELLE_INSUFFISANT]
    for seance, prog in (
        (None, _progression()),
        (_Seance(), _progression()),
        (_Seance(), _progression(any=True, unresolved=2)),
    ):
        d = fr.construire_debriefing(seance, prog)
        rendues.append(d.sr)
        rendues.extend(c.libelle for c in d.causes)

    assert len(rendues) > 6, "la garde n'observe presque aucune chaîne rendue"
    for texte in rendues:
        bas = texte.lower()
        for revendication in ("plus significatif", "plus important",
                              "le plus gros", "principal", "top ", "meilleur"):
            assert revendication not in bas, (
                f"revendication d'importance dans « {texte} » : "
                f"« {revendication} »"
            )


# ═════════ 7. LES DÉCISIONS GELÉES ═════════


def test_la_regle_c_reste_dormante_sur_cette_surface():
    """DÉCISION, pas oubli — et une garde empêche de la réveiller en silence.

    `last_time_by_exercise_code` scope « la dernière fois » sur l'identité
    HÉRITÉE que `progression_facts` a abandonnée. La réveiller ici ferait
    cohabiter deux « dernière fois » contradictoires dans le même instrument.
    """
    import app.services.flight_recorder as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod)
    assert "prior_weight_by_code" not in code
    assert "last_time_by_exercise_code" not in code


def test_une_anomalie_innommable_ne_produit_aucun_signal():
    """Une anomalie qu'on ne sait pas nommer n'est pas une information.

    Hérite de `test_anomaly_is_nameable.py` : on descend d'un rang plutôt que
    d'afficher un objet vide.
    """
    from app.services.flight_recorder import SIGNAL_MOUVEMENT, construire_debriefing

    class _Muette:
        exercise_code, rule_code, severity, message = "E1", "", "info", ""

    import app.services.flight_recorder as mod

    originale = mod.compute_anomalies
    mod.compute_anomalies = lambda s: [_Muette()]
    try:
        d = construire_debriefing(_Seance(), _progression(any=True, lead=_lead()))
    finally:
        mod.compute_anomalies = originale
    assert d.signal == SIGNAL_MOUVEMENT


def test_une_erreur_du_detecteur_degrade_vers_le_rang_suivant():
    """Le debriefing ne fait jamais tomber la page."""
    import app.services.flight_recorder as mod
    from app.services.flight_recorder import SIGNAL_MOUVEMENT, construire_debriefing

    def _explose(_):
        raise RuntimeError("le détecteur a échoué")

    originale = mod.compute_anomalies
    mod.compute_anomalies = _explose
    try:
        d = construire_debriefing(_Seance(), _progression(any=True, lead=_lead()))
    finally:
        mod.compute_anomalies = originale
    assert d.signal == SIGNAL_MOUVEMENT


def test_le_nom_d_exercice_suit_la_substitution():
    """Même politique que `weekly_loop._exercise_name_for`.

    Réimplémentée ici (pour la pureté), donc surveillée : ce qui a été
    RÉELLEMENT exécuté prime sur ce qui était prescrit.
    """
    from app.services.flight_recorder import construire_debriefing

    seance = _Seance([_SE(
        code="A1", name="Prescrit", substituted="Réellement fait", score=100,
        te=type("TE", (), {"rep_targets": [type("RT", (), {"min_reps": 8})()]})(),
        logs=[_SetLog(weight=60, reps=3)],
    )])
    d = construire_debriefing(seance, _progression())
    assert d.exercice == "Réellement fait"
