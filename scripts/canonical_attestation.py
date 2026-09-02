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

ON NE RECONSTRUIT PLUS L'ARBRE TESTÉ — ON LE CAPTURE
-----------------------------------------------------
⛔ UNE PREMIÈRE VERSION RAISONNAIT SUR `tree(M) == tree(H)` ET C'ÉTAIT FAUX.

L'argument était : « si `tree(M) == tree(H)`, la base est la base de
branchement, donc toute base antérieure est un ancêtre de `H`, donc l'arbre
testé valait `tree(H)` ». **L'étape du milieu est un saut.** `tree(M) ==
tree(H)` dit seulement que la contribution NETTE de la base est nulle — ce qui
est aussi vrai après un aller-retour.

CONTRE-EXEMPLE, REPRODUIT MÉCANIQUEMENT (garde dédiée) :

    1. la base reçoit `X`
    2. la CI de PR teste `merge(base+X, H)` — donc `H + X`
    3. la base ANNULE `X` (revert) → son arbre redevient celui de la base
    4. le merge final donne `tree(M) == tree(H)`

    L'ancienne règle conclut `REUSE`. **Or la CI a validé `H + X`, jamais le
    contenu qui devient canonique.** Faux `REUSE` — précisément ce que l'ordre
    interdit sans exception.

LA RÈGLE ACTUELLE NE DÉDUIT RIEN. Pendant le run `pull_request`, là où GitHub
a fait le checkout de `refs/pull/N/merge`, on CAPTURE ce qui a réellement été
testé — `tested_merge_sha`, `tested_tree_sha`, `head_sha`, `base_sha`,
`run_id` — et on le conserve en artefact.

Au push canonique, `REUSE` exige que `tree(M)` soit **exactement** égal au
`tested_tree_sha` attesté par un run de PR dont les contrôles requis sont
verts. Artefact absent, expiré, ambigu, divergent ou invérifiable → `FULL`.

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
import io
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

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

#: Artefact déposé par le run `pull_request`, consommé par le push canonique.
#: Il porte CE QUI A ÉTÉ RÉELLEMENT TESTÉ — pas une reconstruction.
ATTESTATION_ARTIFACT = "pr-attestation"
ATTESTATION_FILE = "pr_attestation.json"

#: Clés du payload d'attestation. Hoistées : chacune revient 3 fois ou plus et
#: déclencherait `S1192`. Le pré-scan AST les voit avant Sonar.
K_MERGE = "tested_merge_sha"
K_TREE = "tested_tree_sha"
K_HEAD = "head_sha"
K_BASE = "base_sha"
K_RUN = "run_id"
_REV_PARSE = "rev-parse"
_REPOS = "/repos/"
_CONCLUSION = "conclusion"

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
    req = urllib.request.Request(  # noqa: S310 — schéma validé, hôte littéral
        _require_https(f"https://api.github.com{path}"),
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


def _require_https(url: str) -> str:
    """Refuse tout ce qui n'est pas `https`.

    L'URL de téléchargement d'un artefact est fournie par l'API et pointe vers
    un stockage dont l'hôte varie : on ne peut pas l'épingler. Le schéma, si —
    et c'est ce que `S310` protège réellement (`file:` ou un schéma exotique).
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise Undecidable(f"schéma refusé : {parsed.scheme or '(aucun)'}")
    if not parsed.hostname:
        raise Undecidable("URL sans hôte")
    return url


def _api_bytes(url: str, token: str) -> bytes:
    req = urllib.request.Request(  # noqa: S310 — schéma validé ci-dessus
        _require_https(url),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
            return resp.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise Undecidable(f"artefact inatteignable : {exc}") from exc


def attested_payload(run_id: str, repo: str, token: str) -> dict:
    """Le contenu RÉELLEMENT testé par ce run de PR, ou `Undecidable`.

    Aucune reconstruction : on lit ce que le run a déposé pendant qu'il testait.
    """
    listing = _api(f"{_REPOS}{repo}/actions/runs/{run_id}/artifacts", token)
    if not isinstance(listing, dict):
        raise Undecidable("réponse d'API inattendue (artefacts)")
    named = [
        a for a in listing.get("artifacts", [])
        if a.get("name") == ATTESTATION_ARTIFACT
    ]
    if not named:
        raise Undecidable(
            f"aucun artefact « {ATTESTATION_ARTIFACT} » sur le run {run_id}"
        )
    if len(named) > 1:
        raise Undecidable(
            f"{len(named)} artefacts « {ATTESTATION_ARTIFACT} » — ambigu"
        )
    art = named[0]
    if art.get("expired"):
        raise Undecidable(f"artefact du run {run_id} EXPIRÉ")
    url = art.get("archive_download_url")
    if not url:
        raise Undecidable("artefact sans URL de téléchargement")

    try:
        with zipfile.ZipFile(io.BytesIO(_api_bytes(url, token))) as zf:
            payload = json.loads(zf.read(ATTESTATION_FILE))
    except (zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise Undecidable(f"artefact illisible : {type(exc).__name__}") from exc
    if not isinstance(payload, dict):
        raise Undecidable("artefact au format inattendu")
    for field in (K_MERGE, K_TREE, K_HEAD, K_RUN):
        if not payload.get(field):
            raise Undecidable(f"artefact incomplet : « {field} » manquant")
    return payload


def capture_payload() -> dict:
    """Ce que le run `pull_request` a RÉELLEMENT sous la main.

    Appelé depuis le checkout de `refs/pull/N/merge` : `HEAD` EST le contenu
    que les shards vont tester. On l'enregistre plutôt que de le déduire.
    """
    return {
        K_MERGE: _git(_REV_PARSE, "HEAD"),
        K_TREE: _git(_REV_PARSE, "HEAD^{tree}"),
        K_HEAD: os.environ.get("PR_HEAD_SHA", ""),
        K_BASE: os.environ.get("PR_BASE_SHA", ""),
        K_RUN: os.environ.get("GITHUB_RUN_ID", ""),
    }


def parents_of(sha: str) -> list[str]:
    return _git("rev-list", "--parents", "-n", "1", sha).split()[1:]


def tree_of(sha: str) -> str:
    return _git(_REV_PARSE, f"{sha}^{{tree}}")


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
    runs = _api(f"{_REPOS}{repo}/actions/runs?head_sha={head}&per_page=100", token)
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
        if run.get(_CONCLUSION) != "success":
            raise Undecidable(
                f"run {run.get('id')} conclu « {run.get('conclusion')} »"
            )
    newest = max(ci_runs, key=lambda r: r.get("run_started_at") or "")
    return str(newest.get("id"))


def _required_checks_green(run_id: str, repo: str, token: str) -> None:
    """Lève si un contrôle exigé par la protection de branche manque."""
    jobs = _api(f"{_REPOS}{repo}/actions/runs/{run_id}/jobs?per_page=100", token)
    if not isinstance(jobs, dict):
        raise Undecidable("réponse d'API inattendue (jobs)")
    green = {
        j.get("name") for j in jobs.get("jobs", [])
        if j.get(_CONCLUSION) == "success"
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
    drift = touches_self_referential(base, sha)
    if drift:
        raise Undecidable(
            f"le mécanisme de sélection lui-même a changé : {', '.join(drift[:3])}"
        )

    run_id = _green_pr_run(head, repo, token)
    _required_checks_green(run_id, repo, token)

    # ⛔ LE CŒUR, ET IL NE DÉDUIT RIEN.
    #
    # On compare l'arbre canonique à celui que le run de PR a CAPTURÉ pendant
    # qu'il testait. Une version antérieure comparait `tree(M)` à `tree(H)` et
    # en DÉDUISAIT l'arbre testé : faux. Contre-exemple reproduit dans les
    # gardes — la base reçoit `X`, la CI teste `H + X`, la base annule `X`, et
    # le merge final retrouve `tree(H)`. L'ancienne règle concluait `REUSE`
    # alors que la CI n'avait jamais vu le contenu devenu canonique.
    payload = attested_payload(run_id, repo, token)

    if payload[K_HEAD] != head:
        raise Undecidable(
            f"l'artefact atteste la tête {payload['head_sha'][:8]}, "
            f"le merge porte {head[:8]}"
        )
    if payload[K_RUN] != run_id:
        raise Undecidable(
            f"l'artefact se réclame du run {payload['run_id']}, trouvé sur {run_id}"
        )

    canonical_tree = tree_of(sha)
    if payload[K_TREE] != canonical_tree:
        raise Undecidable(
            f"l'arbre canonique {canonical_tree[:12]} n'est PAS celui testé "
            f"({payload['tested_tree_sha'][:12]}) — le contenu a changé entre "
            "le run de PR et le merge"
        )

    return (
        REUSE,
        f"arbre {canonical_tree[:12]} attesté testé par le run {run_id} "
        f"(merge d'aperçu {payload['tested_merge_sha'][:8]})",
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


def _capture_for_pull_request() -> None:
    """Dépose `pr_attestation.json` — ce que CE run va réellement tester.

    C'est la moitié qui manquait : sans capture, le push canonique ne peut
    que DÉDUIRE l'arbre testé, et cette déduction s'est révélée fausse.
    """
    payload = capture_payload()
    pathlib.Path(ATTESTATION_FILE).write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"[attestation] capture du contenu réellement testé → {ATTESTATION_FILE}")
    for key in (K_MERGE, K_TREE, K_HEAD, K_BASE):
        print(f"[attestation]   {key} = {payload[key] or '(vide)'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args(argv)

    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
        _capture_for_pull_request()

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
