"""Atteste qu'un push canonique rejoue un contenu DÉJÀ validé (Sx_CI_CANONICAL_DEDUP_01).

Répond à UNE question, et échoue fermé sur tout le reste :

    le commit qui vient d'atterrir sur la canonique a-t-il exactement le contenu
    d'une tête de PR dont la CI est verte ?

    REUSE  — oui, prouvé. Les shards pytest ne sont pas programmés.
    FULL   — tout le reste. **C'est le défaut.**

CE QUE CE MÉCANISME REMPLACE
----------------------------
Mesuré sur 60 runs (2026-08-23 → 08-31) : le re-run canonique après merge
consomme **39 % de tout le temps de runner**, et sur les 20 derniers merges,
**19 rejouaient un arbre identique à l'octet** à celui que la CI de PR venait de
valider. Une exécution sur un arbre identique ne peut pas, par construction,
produire une information susceptible de changer le verdict.

POURQUOI L'ÉGALITÉ D'ARBRE SUFFIT — ET POURQUOI CE N'EST PAS UNE HEURISTIQUE
-----------------------------------------------------------------------------
`refs/pull/N/merge` est SUPPRIMÉ après merge : on ne peut pas récupérer a
posteriori l'arbre que la PR a testé, et l'API ne conserve pas la base du run
(`pull_requests` revient vide). La preuve passe donc par une démonstration :

    Soit `M` le commit de merge, de parents `(B, H)`.
    La CI de PR a testé `merge(B′, H)`, où `B′` est la tête canonique AU MOMENT
    DU RUN — donc un ancêtre de `B`, la canonique n'avançant que dans un sens.

    Si `tree(M) == tree(H)`, alors fusionner `B` dans `H` n'a rien apporté :
    `B` est la base de branchement. `B′ ≤ B` est donc lui aussi un ancêtre de
    `H`, et fusionner un ancêtre dans `H` ne change rien.

    ⇒ l'arbre testé valait `tree(H)` = `tree(M)`, QUELLE QUE SOIT `B′`.

Le cas contraire — la base a bougé avant le merge — donne `tree(M) != tree(H)`
et retombe en `FULL`. C'est exactement ce qui s'est produit sur la PR #159.

⚠ LA PROTECTION DE BRANCHE NE GARANTIT RIEN ICI. Mesuré le 2026-09-01 :
`required_status_checks.strict = false`, donc GitHub **n'exige pas** qu'une
branche soit à jour avant merge ; `enforce_admins = false` ; aucune revue
requise ; le push direct sur la canonique n'est pas bloqué. Le taux historique
de 19/20 est une conséquence de l'usage séquentiel, PAS un invariant appliqué.
La vérification d'arbre ne peut donc jamais être sautée : elle est le garde-fou.

CE QUI N'EST PAS COURT-CIRCUITÉ, ET POURQUOI
--------------------------------------------
Seuls les **shards pytest** sont évités. Restent, à l'identique :

* `lint` (39 s) — inchangé ;
* les contrôles QA / migrations / perf (≈ 5 s) — assurance à prix nul ;
* **SonarCloud** — l'analyse sur `push` est une analyse DE BRANCHE, distincte
  de l'analyse de PR : elle met à jour le gate projet et la référence de code
  neuf. La sauter dégraderait un signal. La couverture lui est fournie en
  récupérant l'artefact du run de PR attesté, si bien que son entrée est
  rigoureusement la même qu'après un run complet.

Usage :
    python scripts/canonical_attestation.py --sha <merge-sha> --github-output
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REUSE = "REUSE"
FULL = "FULL"

#: Variable de dépôt qui ARME la réutilisation. Absente ou différente de
#: `true` → **SHADOW MODE** : le verdict est calculé et journalisé, et la
#: suite complète tourne quand même.
#:
#: C'est la Phase 5 de l'ordre, et elle n'est pas négociable : « pendant
#: plusieurs merges, calculer WOULD_REUSE / WOULD_FULL mais continuer à lancer
#: FULL. Zéro faux REUSE autorisé. » Un mécanisme qui décide de ne pas
#: exécuter des tests doit d'abord prouver, sur des merges réels, qu'il aurait
#: décidé juste — et le seul moyen de le prouver est de le laisser prédire
#: pendant que la vérité continue d'être calculée à côté.
#:
#: Le défaut est donc l'inaction. Passer à `true` est une décision d'opérateur,
#: réversible en une variable, sans toucher au code.
ENABLE_VAR = "CI_CANONICAL_REUSE_ENABLED"

#: Les contrôles que la protection de branche exige sur une PR. Mesurés le
#: 2026-09-01 par `GET /repos/{owner}/{repo}/branches/{branch}/protection`.
#: Un run de PR qui ne les porte PAS tous en succès ne prouve rien.
REQUIRED_CONTEXTS: tuple[str, ...] = ("pytest + QA scripts", "SonarCloud")

#: Un change touchant l'un de ces chemins modifie le MÉCANISME QUI CHOISIT LES
#: TESTS. Réutiliser un verdict produit par l'ancien mécanisme reviendrait à
#: faire valider la nouvelle règle par elle-même.
SELF_REFERENTIAL_PATHS: tuple[str, ...] = (
    ".github/workflows",
    "scripts/canonical_attestation.py",
    "scripts/ci_test_shards.py",
    "scripts/run_ci_pytest.sh",
    "scripts/classify_change_scope.py",
)


class Undecidable(Exception):
    """Toute incertitude. Attrapée en haut, traduite en `FULL`."""


def _git(*args: str) -> str:
    out = subprocess.run(
        ("git", *args), capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        raise Undecidable(f"git {' '.join(args)} → {out.stderr.strip()[:120]}")
    return out.stdout.strip()


def _api(path: str, token: str) -> object:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        # Une API injoignable n'est PAS une preuve d'absence. On ne sait pas,
        # donc on rejoue tout.
        raise Undecidable(f"API GitHub inatteignable : {exc}") from exc


def parents_of(sha: str) -> list[str]:
    return _git("rev-list", "--parents", "-n", "1", sha).split()[1:]


def tree_of(sha: str) -> str:
    return _git("rev-parse", f"{sha}^{{tree}}")


def touches_self_referential(base: str, head: str) -> list[str]:
    changed = _git("diff", "--name-only", base, head)
    return [
        line for line in changed.splitlines()
        if line.strip().startswith(SELF_REFERENTIAL_PATHS)
    ]


def attest(sha: str, repo: str, token: str) -> tuple[str, str, str]:
    """`(verdict, raison, run_id_attesté)`. Ne lève jamais : tout devient FULL."""
    try:
        return _attest(sha, repo, token)
    except Undecidable as exc:
        return FULL, str(exc), ""
    # Attrape-tout DÉLIBÉRÉ : ce mécanisme décide si des tests tournent.
    # Une exception non prévue doit produire `FULL`, jamais une exception.
    except Exception as exc:  # noqa: BLE001
        return FULL, f"erreur inattendue : {type(exc).__name__}: {exc}", ""


def _merge_parents(sha: str) -> tuple[str, str]:
    """`(base, head)` d'un merge à deux parents, ou `Undecidable`."""
    parents = parents_of(sha)
    if len(parents) != 2:
        # Push direct, commit initial, ou merge octopus.
        raise Undecidable(
            f"{len(parents)} parent(s) — ce n'est pas un merge de PR à deux parents"
        )
    return parents[0], parents[1]


def _green_pr_run(head: str, repo: str, token: str) -> str:
    """L'identifiant du run de PR vert pour cette tête, ou `Undecidable`."""
    runs = _api(f"/repos/{repo}/actions/runs?head_sha={head}&per_page=100", token)
    if not isinstance(runs, dict):
        raise Undecidable("réponse d'API inattendue")
    ci_runs = [
        r for r in runs.get("workflow_runs", [])
        if r.get("name") == "CI" and r.get("event") == "pull_request"
    ]
    if not ci_runs:
        raise Undecidable(f"aucun run CI de PR pour la tête {head[:8]}")
    for run in ci_runs:
        if run.get("status") != "completed":
            raise Undecidable(f"run {run.get('id')} non terminé")
        if run.get("conclusion") != "success":
            raise Undecidable(
                f"run {run.get('id')} conclu « {run.get('conclusion')} »"
            )
    newest = max(ci_runs, key=lambda r: r.get("run_started_at") or "")
    return str(newest.get("id"))


def _required_checks_green(run_id: str, repo: str, token: str) -> None:
    """Lève si un contrôle exigé par la protection de branche manque."""
    jobs = _api(f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100", token)
    if not isinstance(jobs, dict):
        raise Undecidable("réponse d'API inattendue (jobs)")
    green = {
        j.get("name") for j in jobs.get("jobs", [])
        if j.get("conclusion") == "success"
    }
    missing = [c for c in REQUIRED_CONTEXTS if c not in green]
    if missing:
        raise Undecidable(
            f"contrôle requis absent ou non vert : {', '.join(missing)}"
        )


def _attest(sha: str, repo: str, token: str) -> tuple[str, str, str]:
    # ⚠ LE JOB TOURNE SUR TOUS LES ÉVÉNEMENTS, ET C'EST DÉLIBÉRÉ.
    #
    # Première écriture : le job portait `if: github.event_name == 'push'`, donc
    # il était IGNORÉ sur une PR. Mesuré sur la CI réelle (run 33534376497) :
    # cet état d'ignoré se propage dans le graphe, et **`SonarCloud` — un
    # contrôle REQUIS par la protection de branche — a cessé de rendre un
    # verdict**. C'est exactement ce que le critère `A7` de l'ordre interdit.
    #
    # Rescaper `sonar` avec `always()` aurait masqué la cause. On la supprime :
    # le job ne s'ignore plus jamais, il répond `FULL` hors `push`. Le graphe
    # ne contient donc plus aucun job ignoré, et la classe entière de problème
    # disparaît. Coût mesuré : ~10 s par run de PR.
    #
    # Ce défaut n'était visible NI en local NI dans le YAML — seule la CI
    # réelle pouvait le montrer. C'est la raison d'être du tier `ci_infra`.
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    if event != "push":
        raise Undecidable(
            f"événement « {event or 'inconnu'} » — l'attestation ne concerne "
            "que les pushs canoniques"
        )
    if not sha:
        raise Undecidable("aucun SHA fourni")
    if not token:
        raise Undecidable("aucun jeton GitHub")

    base, head = _merge_parents(sha)

    if tree_of(sha) != tree_of(head):
        raise Undecidable(
            "l'arbre du merge diffère de celui de la tête de PR — la base a bougé"
        )

    drift = touches_self_referential(base, sha)
    if drift:
        raise Undecidable(
            f"le mécanisme de sélection lui-même a changé : {', '.join(drift[:3])}"
        )

    run_id = _green_pr_run(head, repo, token)
    _required_checks_green(run_id, repo, token)

    return (
        REUSE,
        f"arbre identique à la tête {head[:8]}, validée par le run {run_id}",
        run_id,
    )


def _report(verdict: str, reason: str, *, armed: bool, skip: bool) -> None:
    print(f"[attestation] WOULD_{verdict} — {reason}")
    if armed:
        state = "NON programmés" if skip else "programmés"
        print(f"[attestation] ARMÉ ({ENABLE_VAR}=true) → shards {state}")
        return
    print(f"[attestation] SHADOW MODE — {ENABLE_VAR} n'est pas à `true`.")
    print("[attestation] La suite complète tourne quand même. Ce verdict est "
          "une PRÉDICTION, à comparer au résultat réel.")


def _write_outputs(
    verdict: str, reason: str, run_id: str, *, armed: bool, skip: bool
) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(f"would_reuse={'true' if verdict == REUSE else 'false'}\n")
        fh.write(f"skip_shards={'true' if skip else 'false'}\n")
        fh.write(f"armed={'true' if armed else 'false'}\n")
        fh.write(f"reason={reason}\n")
        fh.write(f"attested_run_id={run_id}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args(argv)

    verdict, reason, run_id = attest(
        args.sha, args.repo, os.environ.get("GITHUB_TOKEN", "")
    )
    armed = os.environ.get(ENABLE_VAR, "").strip().lower() == "true"
    # `skip_shards` est la SEULE sortie que le workflow consomme pour décider.
    # Elle exige DEUX conditions : un verdict `REUSE`, et l'armement explicite.
    skip = verdict == REUSE and armed

    _report(verdict, reason, armed=armed, skip=skip)
    if args.github_output:
        _write_outputs(verdict, reason, run_id, armed=armed, skip=skip)
    return 0


if __name__ == "__main__":
    sys.exit(main())
