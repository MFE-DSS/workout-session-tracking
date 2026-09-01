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

import pathlib
import subprocess
import sys

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

sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def wf() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _mod():
    import canonical_attestation

    return canonical_attestation


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


def test_a_direct_push_is_never_reused(tmp_path):
    """CAS G. Un commit sans deux parents n'est pas un merge de PR : il n'y a
    aucune tête de PR dont on pourrait hériter le verdict."""
    m = _mod()
    repo = tmp_path / "r"
    repo.mkdir()
    def run(*a):
        subprocess.run(("git", *a), cwd=repo, check=True, capture_output=True)

    run("init", "-q", "-b", "main")
    run(GIT_CONFIG, "user.email", "t@t")
    run(GIT_CONFIG, "user.name", "t")
    (repo / "a.txt").write_text("1")
    run("add", ".")
    run(GIT_COMMIT, "-qm", "direct")
    sha = subprocess.run(("git", GIT_REVPARSE, "HEAD"), cwd=repo,
                         capture_output=True, text=True).stdout.strip()

    import os

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
    g(GIT_CONFIG, "user.email", "t@t")
    g(GIT_CONFIG, "user.name", "t")
    (repo / "app.py").write_text("v1\n")
    g("add", ".")
    g(GIT_COMMIT, "-qm", "base")

    g("checkout", "-q", "-b", BRANCH_FEATURE)
    (repo / "feature.py").write_text("f\n")
    if touch_workflow:
        wf = repo / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("name: CI\n")
    g("add", ".")
    g(GIT_COMMIT, "-qm", BRANCH_FEATURE)
    head = g(GIT_REVPARSE, "HEAD")

    g("checkout", "-q", "main")
    if base_moves:
        (repo / "other.py").write_text("moved\n")
        g("add", ".")
        g(GIT_COMMIT, "-qm", "la base avance")

    g("merge", "--no-ff", "-q", BRANCH_FEATURE, "-m", "Merge pull request #1")
    return repo, g(GIT_REVPARSE, "HEAD"), head


def _green_api(head_run_id="4242"):
    def fake(path, token):
        if RUNS_PATH in path:
            return {RUNS_KEY: [{
                "id": int(head_run_id), "name": "CI", "event": PR_EVENT,
                STATUS_KEY: "completed", CONCLUSION: SUCCESS,
                STARTED_KEY: STARTED}]}
        return {"jobs": [{"name": c, CONCLUSION: SUCCESS}
                         for c in (REQUIRED_CHECK, SONAR_CHECK)]}
    return fake


def _attest_in(repo, sha, monkeypatch, api):
    import os

    m = _mod()
    monkeypatch.setattr(m, "_api", api)
    cwd = os.getcwd()
    try:
        os.chdir(repo)
        return m.attest(sha, REPO, TOKEN)
    finally:
        os.chdir(cwd)


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
    repo, merge, _ = _repo_with_merge(tmp_path, base_moves=True)
    verdict, reason, _ = _attest_in(repo, merge, monkeypatch, _green_api())
    assert verdict == m.FULL, reason
    assert "arbre" in reason, reason


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
                STATUS_KEY: "completed", CONCLUSION: conclusion,
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
    monkeypatch.setattr(m, "attest", lambda *a, **k: (verdict, "raison", "99"))
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
        s for s in wf["jobs"][ATTESTATION_JOB]["steps"] if s.get("id") == "attest"
    )
    assert "CI_CANONICAL_REUSE_ENABLED" in step["env"], step["env"]
    assert "vars.CI_CANONICAL_REUSE_ENABLED" in step["env"][
        "CI_CANONICAL_REUSE_ENABLED"
    ]


# ═════════ FAMILLE 2 — LE YAML CONSOMME RÉELLEMENT LE VERDICT ═════════


def test_the_attestation_job_exists_and_only_runs_on_push(wf):
    job = wf["jobs"][ATTESTATION_JOB]
    assert job["if"] == "github.event_name == 'push'", job["if"]


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
