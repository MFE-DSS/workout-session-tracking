"""`Sb_CI_NODE24_RUNTIME_01` — aucune action de workflow ne tourne sur node20.

POURQUOI CETTE GARDE EXISTE, ET POURQUOI `actionlint` NE SUFFIT PAS
--------------------------------------------------------------------
Le 2026-09-16, la CI canonique est tombée sur `actionlint`, qui signalait :

    runtime "node20" is deprecated in GitHub Actions;
    removal is scheduled for September 23rd, 2026

Sept jours d'avance. Six contrôles REQUIS étaient sautés derrière l'échec —
shellcheck, pip-audit, **gitleaks**, protocole de spec, matrice de portée
d'auth, dérive du lock — dont deux scans de sécurité.

⚠ **ET AUCUNE PR NE POUVAIT L'ATTRAPER.** `reviewdog` filtre par défaut sur les
**lignes modifiées** : une PR qui ne touche aucun workflow ne produit aucune
finding, et le job passe au vert. Seul le push canonique, sans diff de
référence, voit le fichier entier. Le défaut était donc **structurellement
invisible** là où on peut encore le corriger sans rougir la canonique — ce qui
explique qu'il l'ait atteinte deux fois de suite.

Cette garde ferme exactement ce trou : elle tourne dans la suite pytest, donc
sur **chaque PR**, et elle regarde le fichier entier.

CE QU'ELLE INTERDIT, ET COMMENT CETTE LISTE A ÉTÉ ÉTABLIE
-----------------------------------------------------------
Pas de devinette : le `runs.using` de chaque version a été lu dans l'`action.yml`
publié, via l'API GitHub, le 2026-09-16. Les versions ci-dessous sont celles
**mesurées** en `node20` — y compris des versions qu'on croirait sûres :

  * `actions/upload-artifact@v5` est **node20** (la v5 n'avait qu'un support
    « préliminaire » de node24 ; c'est la **v6** qui bascule) ;
  * `actions/download-artifact@v5` **et** `@v6` sont **node20** ; il faut la
    **v7**.

Monter « à la version suivante » n'aurait donc rien corrigé. C'est la raison
d'être d'une liste mesurée plutôt que devinée.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"

#: `owner/repo` → plus petit majeur MESURÉ en `node24` le 2026-09-16.
#: Tout majeur strictement inférieur tourne sur node20.
PLANCHER_NODE24 = {
    "actions/checkout": 5,
    "actions/setup-python": 6,
    "actions/upload-artifact": 6,
    "actions/download-artifact": 7,
    "gitleaks/gitleaks-action": 3,
    # `@v5` était `composite`, `@v6` est repassée en `node20`, `@v7` est
    # `node24` : la progression d'un runtime n'est pas monotone, et c'est une
    # raison de plus de MESURER chaque version plutôt que de raisonner par
    # « la suivante sera au moins aussi récente ».
    "SonarSource/sonarqube-scan-action": 7,
}

#: Actions dont le runtime ne dépend pas de node — mesurées, pas supposées.
HORS_NODE = {
    "reviewdog/action-actionlint": "docker",
}

USES = re.compile(r"^\s*uses:\s*([^\s@]+)@([^\s#]+)", re.M)


def _tous_les_usages() -> list[tuple[Path, str, str]]:
    out = []
    for f in sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml")):
        for action, ref in USES.findall(f.read_text(encoding="utf-8")):
            out.append((f, action, ref))
    return out


def test_the_guard_actually_sees_the_workflows():
    """Une garde qui ne trouve aucun fichier passe pour la mauvaise raison."""
    usages = _tous_les_usages()
    assert usages, "aucun `uses:` relevé — la garde ne mesurerait rien"
    fichiers = {f.name for f, _, _ in usages}
    assert "ci.yml" in fichiers
    assert "deploy-production.yml" in fichiers, (
        "le workflow de DÉPLOIEMENT est hors du champ de la garde — c'est "
        "précisément celui dont la panne coûterait le plus cher"
    )


def test_no_workflow_action_runs_on_node20():
    """node20 est retiré des runners GitHub ; une action node20 cesse de partir.

    La panne ne serait pas dégradée mais TOTALE, et elle emporterait aussi
    `deploy-production.yml`.
    """
    fautes = []
    for fichier, action, ref in _tous_les_usages():
        if action in HORS_NODE:
            continue
        plancher = PLANCHER_NODE24.get(action)
        if plancher is None:
            continue
        m = re.fullmatch(r"v(\d+)(?:\.\d+)*", ref)
        if m is None:
            # Un SHA épinglé ou un tag non sémantique : la garde ne peut pas
            # trancher depuis le texte, et ne devine pas. Elle le DIT.
            fautes.append(
                f"{fichier.name}: {action}@{ref} — version non lisible, "
                f"runtime invérifiable depuis le workflow"
            )
            continue
        if int(m.group(1)) < plancher:
            fautes.append(
                f"{fichier.name}: {action}@{ref} tourne sur node20 "
                f"(premier majeur node24 : v{plancher})"
            )
    assert not fautes, "actions sur un runtime retiré :\n  " + "\n  ".join(fautes)


def test_every_action_used_is_covered_by_the_guard():
    """UNE GARDE QUI NE CONNAÎT PAS UNE ACTION NE LA GARDE PAS.

    Sans cette vérification, ajouter une action tierce la ferait passer sous le
    radar en silence : `PLANCHER_NODE24.get(...)` rendrait `None`, la boucle
    ci-dessus l'ignorerait, et la garde resterait verte en n'observant rien.
    C'est le mode d'échec le plus commun de ce dépôt.

    Ajouter une action impose donc de MESURER son `runs.using` et de l'inscrire
    ici — ou de la déclarer hors-node avec sa mesure.
    """
    connues = set(PLANCHER_NODE24) | set(HORS_NODE)
    inconnues = sorted(
        {action for _, action, _ in _tous_les_usages()} - connues
    )
    assert not inconnues, (
        "actions non couvertes par la garde — lire leur `runs.using` dans "
        "l'`action.yml` publié, puis les inscrire :\n  " + "\n  ".join(inconnues)
    )
