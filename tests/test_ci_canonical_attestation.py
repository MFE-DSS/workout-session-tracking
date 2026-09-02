"""`Sx_CI_CANONICAL_DEDUP_01` — on ne recalcule pas le même verdict.

CE QUE CETTE TRANCHE FERME
---------------------------
Mesuré sur 60 runs (2026-08-23 → 08-31) : le re-run canonique après merge
consomme **39 % de tout le temps de runner**, et **19 des 20 derniers merges**
rejouaient un arbre identique à l'octet à celui que la CI de PR venait de
valider. Une exécution sur un arbre identique ne peut pas, par construction,
produire une information susceptible de changer le verdict.

LA NATURE DE CES GARDES — ET POURQUOI ELLES SONT EN DEUX FAMILLES
------------------------------------------------------------------
Un test qui appelle `attest(...)` ne prouve **rien** sur ce que GitHub Actions
exécute. C'est la leçon de `DF-E`, payée deux fois : *une garde qui construit
elle-même l'état qu'elle observe ne teste que la couche qu'elle appelle.*

D'où deux familles, et la seconde est la plus importante :

1. **LOGIQUE** — l'attestation échoue-t-elle fermé sur les huit cas ?
2. **CÂBLAGE** — le YAML consomme-t-il réellement ce verdict ? Un script
   parfait dont l'output n'est branché nulle part laisserait la CI complète
   tourner (inoffensif) *ou*, bien pire, laisserait les shards sautés sans
   qu'aucune condition ne les rattrape.
"""
from __future__ import annotations

import io
import json
import pathlib
import subprocess
import sys
import zipfile

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/ci.yml"
SCRIPT = ROOT / "scripts/canonical_attestation.py"
ATTESTATION_JOB = "canonical-attestation"
SHARD_JOB = "test-shard"
AGG_JOB = "test"
REQUIRED_CHECK = "pytest + QA scripts"
# Hoistés : chacun revenait 3 fois ou plus et déclenchait `S1192`. Le pré-scan
# AST les voit avant Sonar — la faute de méthode de `DF-B` ne se répète pas.
REPO = "owner/repo"
TOKEN = "tok"
SUCCESS = "success"
RUNS_PATH = "/actions/runs?"
RUNS_KEY = "workflow_runs"
CONCLUSION = "conclusion"
SKIP_KEY = "skip_shards"
WOULD_KEY = "would_reuse"
STARTED = "2026-09-01T00:00:00Z"
SONAR_CHECK = "SonarCloud"
BRANCH_FEATURE = "feature"
GIT_CONFIG = "config"
GIT_COMMIT = "commit"
GIT_REVPARSE = "rev-parse"
STATUS_KEY = "status"
STARTED_KEY = "run_started_at"
PR_EVENT = "pull_request"
ALWAYS = "always()"
RUN_ID_KEY = "run-id"
ARTIFACT = "pr-attestation"
EVENT_VAR = "GITHUB_EVENT_NAME"
GIT_CHECKOUT = "checkout"
GIT_NOFF = "--no-ff"
EXPIRED = "expired"
DL_URL = "archive_download_url"
FAKE_ZIP = "https://example.invalid/a.zip"
ATTEST_ID = "attest"
K_TREE = "tested_tree_sha"
K_HEAD = "head_sha"
K_RUN = "run_id"
COMPLETED = "completed"
GIT_EMAIL = "user.email"
GIT_NAME = "user.name"

sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def wf() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _mod():
    import canonical_attestation

    return canonical_attestation


def _tree_of(repo, rev="HEAD") -> str:
    """Arbre d'une révision — un helper, pas quatre `^{tree}` recopiés (S1192)."""
    return subprocess.run(
        ("git", GIT_REVPARSE, f"{rev}^{{tree}}"), cwd=repo,
        check=True, capture_output=True, text=True).stdout.strip()


# ═════════ FAMILLE 1 — LA LOGIQUE ÉCHOUE FERMÉ ═════════


def test_the_default_is_full_not_reuse():
    """LA GARDE DE FOND. Le sens de l'asymétrie : un faux `FULL` coûte des
    minutes, un faux `REUSE` publie du code que rien n'a validé."""
    m = _mod()
    verdict, reason, _ = m.attest("", REPO, "token")
    assert verdict == m.FULL, reason


@pytest.mark.parametrize(
    ("sha", "repo", "token", "cas"),
    [
        ("", REPO, TOKEN, "H — provenance indéterminable"),
        ("deadbeef", REPO, "", "H — aucun jeton"),
        ("deadbeef", "", TOKEN, "H — dépôt inconnu"),
        ("0000000000000000000000000000000000000000", REPO, TOKEN,
         "H — SHA inexistant"),
    ],
)
def test_every_unknown_falls_back_to_full(sha, repo, token, cas):
    m = _mod()
    verdict, reason, _ = m.attest(sha, repo, token)
    assert verdict == m.FULL, f"{cas} → {verdict} ({reason})"


def test_a_direct_push_is_never_reused(tmp_path, monkeypatch):
    """CAS G. Un commit sans deux parents n'est pas un merge de PR : il n'y a
    aucune tête de PR dont on pourrait hériter le verdict."""
    m = _mod()
    repo = tmp_path / "r"
    repo.mkdir()
    def run(*a):
        subprocess.run(("git", *a), cwd=repo, check=True, capture_output=True)

    run("init", "-q", "-b", "main")
    run(GIT_CONFIG, GIT_EMAIL, "t@t")
    run(GIT_CONFIG, GIT_NAME, "t")
    (repo / "a.txt").write_text("1")
    run("add", ".")
    run(GIT_COMMIT, "-qm", "direct")
    sha = subprocess.run(("git", GIT_REVPARSE, "HEAD"), cwd=repo,
                         capture_output=True, text=True).stdout.strip()

    import os

    monkeypatch.setenv(EVENT_VAR, "push")
    cwd = os.getcwd()
    try:
        os.chdir(repo)
        verdict, reason, _ = m.attest(sha, REPO, TOKEN)
    finally:
        os.chdir(cwd)
    assert verdict == m.FULL
    assert "parent" in reason, reason


def test_a_changed_selection_mechanism_is_never_reused():
    """CAS F. Réutiliser un verdict produit par l'ANCIEN mécanisme reviendrait
    à faire valider la nouvelle règle par elle-même."""
    m = _mod()
    for path in (
        ".github/workflows/ci.yml",
        "scripts/canonical_attestation.py",
        "scripts/ci_test_shards.py",
        "scripts/run_ci_pytest.sh",
        "scripts/classify_change_scope.py",
    ):
        assert path.startswith(m.SELF_REFERENTIAL_PATHS), (
            f"{path} n'est pas couvert par l'auto-référence"
        )


def test_the_required_contexts_match_branch_protection():
    """Mesuré le 2026-09-01 sur l'API de protection de branche. Si la
    protection change, cette liste doit changer avec elle — sinon on
    attesterait sur des contrôles qui ne bloquent plus rien."""
    m = _mod()
    assert set(m.REQUIRED_CONTEXTS) == {REQUIRED_CHECK, SONAR_CHECK}


def test_the_module_needs_no_third_party_dependency():
    """Ce job doit rester le moins fragile du pipeline : il décide si les
    autres tournent. Une dépendance qui ne s'installe pas le rendrait rouge —
    donc `FULL` — mais pour une mauvaise raison."""
    src = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("import requests", "import httpx", "from github import"):
        assert forbidden not in src, forbidden


# ═════════ FAMILLE 1bis — LE CHEMIN PROFOND, SUR UN VRAI MERGE ═════════
#
# ⚠ POURQUOI CETTE FAMILLE EXISTE. Les gardes ci-dessus n'atteignent JAMAIS le
# cœur de l'attestation : elles échouent plus tôt, sur l'absence de jeton ou de
# merge. Vérifié en plantant — désarmer la comparaison d'arbres, ou faire
# renvoyer `REUSE` au gestionnaire d'erreur, les laissait toutes **VERTES**.
#
# C'est le mode d'échec de `DF-C` sous un troisième angle : une garde qui
# n'exerce que l'état d'entrée ne voit pas le défaut planté plus loin. D'où un
# VRAI dépôt git avec un VRAI merge à deux parents, et une API simulée.


def _repo_with_merge(tmp_path, *, base_moves: bool = False,
                     touch_workflow: bool = False):
    """Construit `base` + `feature`, puis fusionne. Renvoie `(dir, merge, head)`.

    `base_moves=True` reproduit la famille de défaut observée sur la PR #159 :
    la canonique avance AVANT le merge, donc l'arbre fusionné ne peut plus être
    celui que la CI de PR a testé.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    def g(*a):
        return subprocess.run(("git", *a), cwd=repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    g("init", "-q", "-b", "main")
    g(GIT_CONFIG, GIT_EMAIL, "t@t")
    g(GIT_CONFIG, GIT_NAME, "t")
    (repo / "app.py").write_text("v1\n")
    g("add", ".")
    g(GIT_COMMIT, "-qm", "base")

    g(GIT_CHECKOUT, "-q", "-b", BRANCH_FEATURE)
    (repo / "feature.py").write_text("f\n")
    if touch_workflow:
        wf = repo / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("name: CI\n")
    g("add", ".")
    g(GIT_COMMIT, "-qm", BRANCH_FEATURE)
    head = g(GIT_REVPARSE, "HEAD")

    g(GIT_CHECKOUT, "-q", "main")
    if base_moves:
        (repo / "other.py").write_text("moved\n")
        g("add", ".")
        g(GIT_COMMIT, "-qm", "la base avance")

    g("merge", GIT_NOFF, "-q", BRANCH_FEATURE, "-m", "Merge pull request #1")
    return repo, g(GIT_REVPARSE, "HEAD"), head


def _repo_with_reverted_base(tmp_path):
    """LE CONTRE-EXEMPLE. La base reçoit `X`, la CI teste `H + X`, la base
    ANNULE `X`, puis on fusionne.

    Résultat : `tree(M) == tree(H)` — l'ancienne règle concluait `REUSE` —
    alors que **la CI n'a jamais vu le contenu devenu canonique**.

    Renvoie `(dir, merge, head, tree_réellement_testé)`.
    """
    repo = tmp_path / "revert"
    repo.mkdir()

    def g(*a):
        return subprocess.run(("git", *a), cwd=repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    g("init", "-q", "-b", "main")
    g(GIT_CONFIG, GIT_EMAIL, "t@t")
    g(GIT_CONFIG, GIT_NAME, "t")
    (repo / "app.py").write_text("v1\n")
    g("add", ".")
    g(GIT_COMMIT, "-qm", "base")

    g(GIT_CHECKOUT, "-q", "-b", BRANCH_FEATURE)
    (repo / "f.py").write_text("f\n")
    g("add", ".")
    g(GIT_COMMIT, "-qm", BRANCH_FEATURE)
    head = g(GIT_REVPARSE, "HEAD")

    # la base reçoit X
    g(GIT_CHECKOUT, "-q", "main")
    (repo / "x.py").write_text("X\n")
    g("add", ".")
    g(GIT_COMMIT, "-qm", "X")
    base_with_x = g(GIT_REVPARSE, "HEAD")

    # ce que la CI de PR teste À CET INSTANT : merge(base+X, H)
    g(GIT_CHECKOUT, "-q", "-b", "preview", head)
    g("merge", GIT_NOFF, "-m", "apercu", base_with_x)
    tested_tree = _tree_of(repo)

    # la base ANNULE X
    g(GIT_CHECKOUT, "-q", "main")
    g("revert", "--no-edit", base_with_x)

    g("merge", GIT_NOFF, "-m", "Merge pull request #1", BRANCH_FEATURE)
    return repo, g(GIT_REVPARSE, "HEAD"), head, tested_tree


def test_the_old_tree_equality_rule_was_wrong(tmp_path):
    """LA PREUVE QUE L'ANCIENNE RÈGLE PRODUISAIT UN FAUX REUSE.

    Cette garde ne teste pas le code actuel : elle **fige le contre-exemple**,
    pour qu'on ne puisse plus jamais réintroduire l'ancien raisonnement en
    croyant l'avoir démontré.

    L'argument fautif était : « si `tree(M) == tree(H)`, la base est la base de
    branchement ». Faux — cela dit seulement que la contribution NETTE de la
    base est nulle, ce qui vaut aussi après un aller-retour.
    """
    repo, merge, head, tested_tree = _repo_with_reverted_base(tmp_path)

    def g(*a):
        return subprocess.run(("git", *a), cwd=repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    tree_m = _tree_of(repo, merge)
    tree_h = _tree_of(repo, head)

    assert tree_m == tree_h, (
        "le contre-exemple exige tree(M) == tree(H) — sinon il ne démontre rien"
    )
    assert tested_tree != tree_m, (
        "le contre-exemple exige que la CI ait testé AUTRE CHOSE"
    )


def test_the_counter_example_now_yields_full(tmp_path, monkeypatch):
    """ET LA NOUVELLE RÈGLE LE REFUSE. L'artefact atteste `H + X` ; l'arbre
    canonique est `tree(H)`. Ils diffèrent, donc `FULL`."""
    m = _mod()
    repo, merge, head, tested_tree = _repo_with_reverted_base(tmp_path)
    api = _green_api(tested_tree_sha=tested_tree, head_sha=head)
    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "n'est PAS celui testé" in reason, reason


def _green_api(head_run_id="4242", tested_tree_sha=None, head_sha=None):
    """Simulateur d'API. `tested_tree_sha` est ce que l'ARTEFACT atteste.

    Laissé à `None`, il est aligné sur l'arbre canonique par `_attest_in` —
    le cas nominal. Le contre-exemple, lui, le fixe à ce que la CI a
    réellement testé, qui diffère.
    """
    def fake(path, token):
        if RUNS_PATH in path:
            return {RUNS_KEY: [{
                "id": int(head_run_id), "name": "CI", "event": PR_EVENT,
                STATUS_KEY: COMPLETED, CONCLUSION: SUCCESS,
                STARTED_KEY: STARTED}]}
        if "/artifacts" in path:
            return {"artifacts": [{
                "name": ARTIFACT, EXPIRED: False,
                DL_URL: FAKE_ZIP}]}
        return {"jobs": [{"name": c, CONCLUSION: SUCCESS}
                         for c in (REQUIRED_CHECK, SONAR_CHECK)]}
    fake.tested_tree_sha = tested_tree_sha
    fake.head_sha = head_sha
    fake.run_id = head_run_id
    return fake


def _zip_payload(payload: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("pr_attestation.json", json.dumps(payload))
    return buf.getvalue()


def _attest_in(repo, sha, monkeypatch, api, event="push"):
    import os

    m = _mod()
    monkeypatch.setattr(m, "_api", api)

    # L'artefact que le run de PR aurait déposé. Par défaut il atteste l'arbre
    # canonique lui-même (cas nominal) ; un test peut le faire diverger.
    def _bytes(url, token):
        tree = getattr(api, K_TREE, None)
        if tree is None:
            tree = _tree_of(repo, sha)
        head = getattr(api, K_HEAD, None)
        if head is None:
            head = subprocess.run(
                ("git", "rev-list", "--parents", "-n", "1", sha), cwd=repo,
                capture_output=True, text=True).stdout.split()[-1]
        return _zip_payload({
            "tested_merge_sha": "a" * 40,
            K_TREE: tree,
            K_HEAD: head,
            "base_sha": "b" * 40,
            K_RUN: getattr(api, K_RUN, "4242"),
        })

    monkeypatch.setattr(m, "_api_bytes", _bytes)
    monkeypatch.setenv(EVENT_VAR, event)
    cwd = os.getcwd()
    try:
        os.chdir(repo)
        return m.attest(sha, REPO, TOKEN)
    finally:
        os.chdir(cwd)


def test_a_pull_request_is_never_attested(tmp_path, monkeypatch):
    """LE DÉFAUT TROUVÉ PAR LA CI RÉELLE, et sa correction.

    Première écriture : le job portait `if: github.event_name == 'push'`, donc
    il était IGNORÉ sur une PR — et cet état se propage dans le graphe. Mesuré
    sur le run 33534376497 : **`SonarCloud`, un contrôle REQUIS par la
    protection de branche, a cessé de rendre un verdict.** C'est exactement ce
    que le critère `A7` interdit.

    Rescaper `sonar` avec `always()` aurait masqué la cause. Elle est
    supprimée : le job tourne sur TOUS les événements et répond `FULL` hors
    `push`. Le graphe ne contient donc plus aucun job ignoré.

    Ce défaut n'était visible ni en local ni dans le YAML. Seule la CI réelle
    pouvait le montrer — c'est la raison d'être du tier `ci_infra`.
    """
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    verdict, reason, _ = _attest_in(
        repo, merge, monkeypatch, _green_api(), event=PR_EVENT
    )
    assert verdict == m.FULL, reason
    assert "événement" in reason, reason


def test_the_attestation_job_is_never_skipped(wf):
    """LA GARDE DE CÂBLAGE CORRESPONDANTE. Un job ignoré propage son état aux
    jobs qui en dépendent — jusqu'à un contrôle requis."""
    job = wf["jobs"][ATTESTATION_JOB]
    assert "if" not in job, (
        "le job d'attestation porte une condition — il peut donc être IGNORÉ, "
        "et cet état se propagerait jusqu'à un contrôle requis"
    )


def test_case_a_identical_tree_and_green_run_is_reused(tmp_path, monkeypatch):
    """CAS A. Le seul chemin qui doit conclure `REUSE`."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    verdict, reason, run_id = _attest_in(repo, merge, monkeypatch, _green_api())
    assert verdict == m.REUSE, reason
    assert run_id == "4242"


def test_case_b_a_moved_base_is_never_reused(tmp_path, monkeypatch):
    """CAS B — la famille de défaut de la PR #159, reproduite. La canonique a
    avancé avant le merge : l'arbre fusionné n'est plus celui testé."""
    m = _mod()
    repo, merge, head = _repo_with_merge(tmp_path, base_moves=True)
    # La CI de PR a tourné AVANT que la base bouge : elle a donc testé l'arbre
    # de la tête, pas celui du merge final. C'est ce que l'artefact atteste.
    tested = _tree_of(repo, head)
    api = _green_api(tested_tree_sha=tested, head_sha=head)
    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "n'est PAS celui testé" in reason, reason


def test_case_c_no_ci_run_is_never_reused(tmp_path, monkeypatch):
    """CAS C. ⚠ On épingle la RAISON, pas seulement le verdict : sans cela,
    retirer ce rejet laissait la garde verte — l'absence de run faisait
    échouer un appel plus loin, que l'attrape-tout traduisait en `FULL`. Bon
    verdict, mauvaise raison, propriété non gardée."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    def api(path, token):
        return {RUNS_KEY: []}

    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "aucun run CI" in reason, reason


@pytest.mark.parametrize(CONCLUSION, ["cancelled", "failure", "timed_out", None])
def test_cases_d_and_e_a_non_green_run_is_never_reused(
    tmp_path, monkeypatch, conclusion
):
    """CAS D et E."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)

    def api(path, token):
        if RUNS_PATH in path:
            return {RUNS_KEY: [{
                "id": 1, "name": "CI", "event": PR_EVENT,
                STATUS_KEY: COMPLETED, CONCLUSION: conclusion,
                STARTED_KEY: STARTED}]}
        # ⚠ Les contrôles requis sont VERTS ici, délibérément. Avec une liste
        # de jobs vide, retirer la vérification de conclusion laissait la garde
        # verte : le rejet des contrôles manquants rattrapait derrière. La
        # seule chose qui doit pouvoir rejeter ce cas est la CONCLUSION.
        return {"jobs": [{"name": c, CONCLUSION: SUCCESS}
                         for c in m.REQUIRED_CONTEXTS]}

    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "conclu" in reason, reason


def test_a_run_still_in_progress_is_never_reused(tmp_path, monkeypatch):
    """Un run non terminé n'a pas de verdict à prêter.

    ⚠ Ce cas manquait, et le planter l'a montré : désarmer la vérification de
    statut laissait les 32 gardes VERTES, parce qu'aucune ne construisait un
    run en cours. Une garde n'existe que pour l'état qu'elle fabrique.
    """
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)

    def api(path, token):
        if RUNS_PATH in path:
            return {RUNS_KEY: [{
                "id": 7, "name": "CI", "event": PR_EVENT,
                STATUS_KEY: "in_progress", CONCLUSION: None,
                STARTED_KEY: STARTED}]}
        return {"jobs": [{"name": c, CONCLUSION: SUCCESS}
                         for c in m.REQUIRED_CONTEXTS]}

    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "non terminé" in reason, reason


def test_a_missing_required_check_is_never_reused(tmp_path, monkeypatch):
    """Un run vert dont un contrôle REQUIS n'a pas tourné ne prouve rien."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)

    def api(path, token):
        if RUNS_PATH in path:
            return _green_api()(path, token)
        return {"jobs": [{"name": REQUIRED_CHECK, CONCLUSION: SUCCESS}]}

    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert SONAR_CHECK in reason, reason


def test_case_f_a_workflow_change_is_never_reused(tmp_path, monkeypatch):
    """CAS F. Réutiliser un verdict produit par l'ANCIEN mécanisme reviendrait
    à faire valider la nouvelle règle par elle-même."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path, touch_workflow=True)
    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, _green_api())
    assert verdict == m.FULL, reason
    assert "mécanisme" in reason, reason


def test_an_unreachable_api_is_never_reused(tmp_path, monkeypatch):
    """Une API muette n'est pas une preuve d'absence de défaut."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)

    def boom(path, token):
        raise m.Undecidable("réseau")

    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, boom)
    assert verdict == m.FULL, reason


def test_an_unexpected_exception_is_never_reused(tmp_path, monkeypatch):
    """Le gestionnaire attrape-tout doit conclure `FULL`. Sans cette garde,
    le remplacer par `REUSE` passait inaperçu — vérifié en plantant."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)

    def boom(path, token):
        raise RuntimeError("panne inattendue")

    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, boom)
    assert verdict == m.FULL, reason


# ═════════ FAMILLE 1quater — L'ARTEFACT EST LA SEULE SOURCE ═════════
#
# « Artefact absent, expiré, ambigu, différent ou non vérifiable => FULL. »
# Chacun de ces cinq mots est une garde.


def _api_with_artifacts(arts):
    def fake(path, token):
        if RUNS_PATH in path:
            return {RUNS_KEY: [{
                "id": 4242, "name": "CI", "event": PR_EVENT,
                STATUS_KEY: COMPLETED, CONCLUSION: SUCCESS,
                STARTED_KEY: STARTED}]}
        if "/artifacts" in path:
            return {"artifacts": arts}
        return {"jobs": [{"name": c, CONCLUSION: SUCCESS}
                         for c in (REQUIRED_CHECK, SONAR_CHECK)]}
    return fake


def test_a_missing_artifact_is_never_reused(tmp_path, monkeypatch):
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    verdict, reason, _ = _attest_in(
        repo, merge, monkeypatch, _api_with_artifacts([]))
    assert verdict == m.FULL, reason
    assert "aucun artefact" in reason, reason


def test_an_expired_artifact_is_never_reused(tmp_path, monkeypatch):
    """GitHub purge les artefacts. Un artefact expiré n'atteste plus rien."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    api = _api_with_artifacts([{
        "name": ARTIFACT, EXPIRED: True,
        DL_URL: FAKE_ZIP}])
    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "EXPIRÉ" in reason, reason


def test_an_ambiguous_artifact_set_is_never_reused(tmp_path, monkeypatch):
    """Deux artefacts du même nom : on ne sait pas lequel fait foi."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    one = {"name": ARTIFACT, EXPIRED: False,
           DL_URL: FAKE_ZIP}
    verdict, reason, _ = _attest_in(
        repo, merge, monkeypatch, _api_with_artifacts([one, dict(one)]))
    assert verdict == m.FULL, reason
    assert "ambigu" in reason, reason


def test_an_unreadable_artifact_is_never_reused(tmp_path, monkeypatch):
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    monkeypatch.setattr(_mod(), "_api_bytes", lambda url, tok: b"pas un zip")
    api = _green_api()
    monkeypatch.setattr(_mod(), "_api", api)
    import os

    monkeypatch.setenv(EVENT_VAR, "push")
    cwd = os.getcwd()
    try:
        os.chdir(repo)
        verdict, reason, _ = _mod().attest(merge, REPO, TOKEN)
    finally:
        os.chdir(cwd)
    assert verdict == m.FULL, reason
    assert "illisible" in reason, reason


def test_an_artifact_attesting_another_head_is_never_reused(tmp_path, monkeypatch):
    """L'artefact doit parler DE CETTE tête de PR, pas d'une autre."""
    m = _mod()
    repo, merge, _ = _repo_with_merge(tmp_path)
    api = _green_api(head_sha="f" * 40)
    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "atteste la tête" in reason, reason


def test_an_artifact_claiming_another_run_is_never_reused(tmp_path, monkeypatch):
    """L'artefact doit se réclamer DU run sur lequel on l'a trouvé.

    ⚠ Ce cas manquait, et le planter l'a montré : désarmer la vérification
    laissait les 53 gardes vertes, parce qu'aucune ne construisait un artefact
    incohérent avec son run. Une garde n'existe que pour l'état qu'elle
    fabrique — troisième fois dans cette tranche.
    """
    m = _mod()
    repo, merge, head = _repo_with_merge(tmp_path)
    api = _green_api(head_sha=head)
    api.run_id = "999999"          # l'artefact ment sur sa provenance
    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, api)
    assert verdict == m.FULL, reason
    assert "se réclame du run" in reason, reason


def test_the_capture_records_what_is_actually_checked_out(tmp_path, monkeypatch):
    """La moitié qui manquait : sans capture, on ne peut que DÉDUIRE."""
    import os

    m = _mod()
    repo, merge, head = _repo_with_merge(tmp_path)
    monkeypatch.setenv("PR_HEAD_SHA", head)
    monkeypatch.setenv("GITHUB_RUN_ID", "777")
    cwd = os.getcwd()
    try:
        os.chdir(repo)
        payload = m.capture_payload()
    finally:
        os.chdir(cwd)
    expected = _tree_of(repo)
    assert payload[K_TREE] == expected, payload
    assert payload[K_HEAD] == head, payload
    assert payload[K_RUN] == "777", payload


# ═════════ FAMILLE 1ter — LE SHADOW MODE EST LE DÉFAUT ═════════
#
# Phase 5 de l'ordre : « pendant plusieurs merges, calculer WOULD_REUSE /
# WOULD_FULL mais continuer à lancer FULL. Zéro faux REUSE autorisé. »
#
# Un mécanisme qui décide de NE PAS exécuter des tests doit d'abord prouver,
# sur des merges réels, qu'il aurait décidé juste. Le défaut est donc
# l'inaction : sans armement explicite, la suite complète tourne.


def _main_with(monkeypatch, tmp_path, env: dict, verdict: str):
    """Exécute `main()` en forçant le verdict, et renvoie les outputs écrits."""
    m = _mod()
    out = tmp_path / "gh_output"
    out.write_text("")
    monkeypatch.setattr(m, ATTEST_ID, lambda *a, **k: (verdict, "raison", "99"))
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv(m.ENABLE_VAR, raising=False)
    if m.ENABLE_VAR in env:
        monkeypatch.setenv(m.ENABLE_VAR, env[m.ENABLE_VAR])
    m.main(["--sha", "abc", "--repo", "o/r", "--github-output"])
    return dict(
        line.split("=", 1) for line in out.read_text().splitlines() if "=" in line
    )


def test_without_the_arming_variable_nothing_is_skipped(tmp_path, monkeypatch):
    """LA GARDE DE FOND DU SHADOW MODE. Même un verdict `REUSE` ne doit rien
    sauter tant que l'opérateur n'a pas armé."""
    m = _mod()
    outs = _main_with(monkeypatch, tmp_path, {}, m.REUSE)
    assert outs[WOULD_KEY] == "true", outs
    assert outs[SKIP_KEY] == "false", outs
    assert outs["armed"] == "false", outs


@pytest.mark.parametrize("value", ["", "false", "0", "yes", "TRUE ", "1"])
def test_only_the_exact_value_true_arms_the_reuse(tmp_path, monkeypatch, value):
    """Une variable mal orthographiée ne doit pas armer par accident.

    `TRUE ` avec espace est accepté (on strip et on abaisse la casse) ;
    `yes` et `1` ne le sont pas — ce sont des valeurs qu'on écrit en croyant
    activer, et une activation accidentelle est exactement ce qu'il faut
    empêcher."""
    m = _mod()
    outs = _main_with(monkeypatch, tmp_path, {m.ENABLE_VAR: value}, m.REUSE)
    expected = "true" if value.strip().lower() == "true" else "false"
    assert outs[SKIP_KEY] == expected, (value, outs)


def test_arming_alone_never_skips_a_full_verdict(tmp_path, monkeypatch):
    """L'armement n'est pas un contournement : un verdict `FULL` reste `FULL`."""
    m = _mod()
    outs = _main_with(monkeypatch, tmp_path, {m.ENABLE_VAR: "true"}, m.FULL)
    assert outs[WOULD_KEY] == "false", outs
    assert outs[SKIP_KEY] == "false", outs


def test_arming_plus_reuse_is_the_only_path_that_skips(tmp_path, monkeypatch):
    m = _mod()
    outs = _main_with(monkeypatch, tmp_path, {m.ENABLE_VAR: "true"}, m.REUSE)
    assert outs[SKIP_KEY] == "true", outs


def test_the_workflow_reads_the_arming_variable(wf):
    """Le câblage : sans cette variable dans l'environnement du step, le
    shadow mode serait permanent et la tranche n'aurait aucun effet possible."""
    step = next(
        s for s in wf["jobs"][ATTESTATION_JOB]["steps"] if s.get("id") == ATTEST_ID
    )
    assert "CI_CANONICAL_REUSE_ENABLED" in step["env"], step["env"]
    assert "vars.CI_CANONICAL_REUSE_ENABLED" in step["env"][
        "CI_CANONICAL_REUSE_ENABLED"
    ]


# ═════════ FAMILLE 2 — LE YAML CONSOMME RÉELLEMENT LE VERDICT ═════════


def test_the_attestation_job_exists_and_reads_the_event(wf):
    """L'attestation ne concerne que les pushs canoniques — mais ce filtre vit
    dans le SCRIPT, pas dans un `if:` de job.

    ⚠ Le filtre était dans le YAML. Le job était donc ignoré sur une PR, et cet
    état se propageait jusqu'à `SonarCloud`, un contrôle requis. Le déplacer
    dans le script supprime la cause au lieu de la contourner.
    """
    job = wf["jobs"][ATTESTATION_JOB]
    step = next(s for s in job["steps"] if s.get("id") == ATTEST_ID)
    assert EVENT_VAR in step["env"], step["env"]
    assert "github.event_name" in step["env"][EVENT_VAR]


def test_the_shards_are_gated_on_the_attestation_output(wf):
    """LE CÂBLAGE. Sans cette condition, le script serait décoratif."""
    cond = wf["jobs"][SHARD_JOB]["if"]
    # `skip_shards`, pas `would_reuse` : la PRÉDICTION ne doit jamais piloter
    # le workflow. Seule la sortie qui exige AUSSI l'armement le peut.
    assert f"needs.{ATTESTATION_JOB}.outputs.skip_shards != 'true'" in cond, cond
    assert "would_reuse" not in cond, (
        "le workflow consomme la prédiction au lieu de la décision armée"
    )


def test_the_shards_still_run_on_a_pull_request(wf):
    """LE PIÈGE QUI AURAIT TOUT CASSÉ. Un job qui dépend d'un job IGNORÉ est
    ignoré à son tour. Sur une PR, `canonical-attestation` est ignoré — sans
    `always()`, les trois shards le seraient aussi et **plus aucune PR ne
    serait testée**, avec une CI verte."""
    cond = wf["jobs"][SHARD_JOB]["if"]
    assert cond.startswith(ALWAYS), cond
    assert ATTESTATION_JOB in wf["jobs"][SHARD_JOB]["needs"]


def test_a_failed_attestation_still_runs_the_shards(wf):
    """Si le job d'attestation échoue, ses outputs sont vides. `'' != 'true'`
    est vrai, donc les shards tournent. Échec fermé par construction — et
    c'est `always()` qui le rend possible."""
    cond = wf["jobs"][SHARD_JOB]["if"]
    assert ALWAYS in cond, cond
    assert "!= 'true'" in cond, cond


def test_the_required_check_always_reports(wf):
    """`A7` — aucun contrôle requis ne doit rester Expected. L'agrégateur
    tourne dans les deux régimes."""
    job = wf["jobs"][AGG_JOB]
    assert job["if"] == ALWAYS, job["if"]
    assert job["name"] == REQUIRED_CHECK, job["name"]


def test_the_shard_failure_guard_survives_in_the_normal_regime(wf):
    """L'agrégateur ne doit JAMAIS conclure au succès par-dessus un shard
    rouge. La clause de réutilisation ne doit pas désarmer cette garde hors
    réutilisation."""
    step = next(
        s for s in wf["jobs"][AGG_JOB]["steps"]
        if s.get("name") == "Fail if any shard failed"
    )
    cond = step["if"]
    assert f"needs.{SHARD_JOB}.result != 'success'" in cond, cond
    assert "env.REUSE != 'true'" in cond, cond


def test_sonar_still_runs_on_a_reused_push(wf):
    """L'analyse Sonar sur `push` est une analyse DE BRANCHE, distincte de
    l'analyse de PR : elle met à jour le gate projet et la référence de code
    neuf. La sauter échangerait du calcul contre une dégradation de signal."""
    cond = wf["jobs"]["sonar"]["if"]
    assert "github.event_name == 'push'" in cond, cond
    assert "reuse" not in cond, "Sonar ne doit pas être conditionné à la réutilisation"


def test_a_reused_push_still_feeds_sonar_real_coverage(wf):
    """Sans cette étape, l'analyse de branche publierait une couverture nulle
    et abîmerait le gate projet."""
    steps = wf["jobs"][AGG_JOB]["steps"]
    imp = next(
        (s for s in steps
         if "coverage" in (s.get("name") or "").lower()
         and "attested" in (s.get("name") or "").lower()),
        None,
    )
    assert imp is not None, "aucune étape n'importe la couverture du run attesté"
    assert imp["with"][RUN_ID_KEY].strip().startswith("${{"), imp["with"]
    assert ATTESTATION_JOB in imp["with"][RUN_ID_KEY], imp["with"][RUN_ID_KEY]


def test_the_pull_request_run_uploads_its_attestation(wf):
    """LE CÂBLAGE DE LA CAPTURE. Sans ce dépôt, aucun push ne peut jamais
    réutiliser un verdict — et pire, on serait tenté de le DÉDUIRE."""
    steps = wf["jobs"][ATTESTATION_JOB]["steps"]
    up = next(
        (x for x in steps if "upload-artifact" in str(x.get("uses") or "")), None
    )
    assert up is not None, "le run de PR ne dépose aucune attestation"
    assert up["with"]["name"] == ARTIFACT, up["with"]
    assert up["if"] == "github.event_name == 'pull_request'", up["if"]
    assert up["with"]["if-no-files-found"] == "error", up["with"]


def test_the_capture_receives_the_pull_request_shas(wf):
    step = next(
        x for x in wf["jobs"][ATTESTATION_JOB]["steps"] if x.get("id") == ATTEST_ID
    )
    for var in ("PR_HEAD_SHA", "PR_BASE_SHA"):
        assert var in step["env"], step["env"]


def test_the_lint_job_is_never_gated_by_the_attestation(wf):
    """`lint` coûte 39 s et couvre ruff, bandit, actionlint, shellcheck,
    pip-audit, gitleaks. Aucune économie ne justifie de le sauter."""
    job = wf["jobs"]["lint"]
    assert ATTESTATION_JOB not in (job.get("needs") or [])
    assert ATTESTATION_JOB not in str(job.get("if") or "")


def test_the_qa_and_migration_checks_are_never_gated_by_the_attestation(wf):
    """≈ 5 s au total. Les sauter n'économise rien de mesurable et retirerait
    de la capacité au filet canonique."""
    for step in wf["jobs"][AGG_JOB]["steps"]:
        name = step.get("name") or ""
        if any(k in name for k in ("QA", "Alembic", "Schema", "Migration", "Perf")):
            assert "REUSE" not in str(step.get("if") or ""), name


def test_the_attestation_job_holds_least_privilege(wf):
    perms = wf["jobs"][ATTESTATION_JOB]["permissions"]
    assert perms == {"contents": "read", "actions": "read"}, perms


def test_production_deployment_is_untouched():
    """`A7` de la mission : le déploiement n'est pas dans le périmètre."""
    deploy = (ROOT / ".github/workflows/deploy-production.yml").read_text(
        encoding="utf-8"
    )
    assert "canonical_attestation" not in deploy
    assert "canonical-attestation" not in deploy
