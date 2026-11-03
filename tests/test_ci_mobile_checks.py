"""CI-01 — la logique mobile et ses types doivent participer à chaque CI.

La gate pixel observe des fixtures web ; elle ne remplace pas l'exécution des
tests Jest ni le contrat TypeScript du client natif.
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _mobile_job():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert "mobile-checks" in workflow["jobs"], "Jest et TypeScript absents de la CI"
    return workflow["jobs"]["mobile-checks"]


def test_jest_and_types_are_required_without_a_mobile_path_filter():
    job = _mobile_job()
    assert job["name"] == "mobile checks (Jest + TypeScript)"
    assert "if" not in job, "le job doit tourner aussi sur les changements serveur"
    assert not job.get("continue-on-error", False)
    runs = {step.get("run"): step for step in job["steps"] if "run" in step}
    for command in ("npm test -- --ci --runInBand", "npm run typecheck"):
        assert command in runs, f"vérification mobile manquante : {command}"
        assert not runs[command].get("continue-on-error", False)
    assert runs["npm test -- --ci --runInBand"].get("if") is None


def test_mobile_checks_install_the_lock_under_node_22():
    job = _mobile_job()
    assert job["defaults"]["run"]["working-directory"] == "clients/mobile"
    setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-node@"))
    assert str(setup["with"]["node-version"]) == "22"
    assert setup["with"]["cache"] == "npm"
    assert setup["with"]["cache-dependency-path"] == "clients/mobile/package-lock.json"
    install = next(step for step in job["steps"] if step.get("id") == "install")
    assert install["run"] == "npm ci --no-audit --no-fund"
    assert not install.get("continue-on-error", False)


def test_typecheck_still_runs_after_a_jest_failure_but_not_a_failed_install():
    job = _mobile_job()
    check = next(step for step in job["steps"] if step.get("run") == "npm run typecheck")
    assert check["if"] == "${{ !cancelled() && steps.install.outcome == 'success' }}"
