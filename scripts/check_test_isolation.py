"""Chaque fichier de test modifié doit passer SEUL (`Sx_CI_TEST_ISOLATION_01`).

CE QUE CETTE ÉTAPE FERME
------------------------
Le verdict de la suite dépendait du **groupement**. Mesuré sur le même arbre,
le même jour : `test_train1c_progression_consolidation.py` était vert dans le
sweep complet et rouge dans un autre lot.

Deux propriétés du dépôt rendaient ce défaut invisible :

1. **L'ordre est entièrement déterministe.** `pytest-randomly` n'est pas
   installé — une dépendance au groupement ne se révèle donc jamais d'elle-même.
2. **Mais la liste de fichiers, elle, bouge.** La répartition en shards est un
   tourniquet PAR INDEX : ajouter un seul fichier de test déplace **229 fichiers
   sur 292 (79 %)**. Un défaut d'isolation surgit alors sur une PR sans rapport,
   et disparaît sur la suivante.

Résultat mesuré le 2026-09-03 : la canonique est tombée sur un test que
personne n'avait touché.

POURQUOI SEULEMENT LES FICHIERS MODIFIÉS
-----------------------------------------
Rejouer les 293 fichiers un par un coûterait plus cher que la suite entière.
On attrape la classe **au moment où elle est introduite**, sur le seul diff qui
peut l'introduire — quelques secondes par fichier.

CE QUE CETTE ÉTAPE N'EST PAS
-----------------------------
Ce n'est pas une garantie d'isolation complète : un test peut passer seul ET
polluer ses voisins. C'est l'autre sens, et il demanderait une exécution
croisée. Cette étape ferme le sens qui a réellement coûté une canonique.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

TEST_PREFIX = "tests/"


def changed_test_files(base: str, head: str) -> list[str]:
    out = subprocess.run(
        ("git", "diff", "--name-only", "--diff-filter=d", base, head),
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        # On ne sait pas ⇒ on ne prétend pas savoir. L'appelant décide.
        raise SystemExit(f"[isolation] git diff a échoué : {out.stderr.strip()[:200]}")
    return sorted(
        line for line in out.stdout.split()
        if line.startswith(TEST_PREFIX)
        and line.endswith(".py")
        and os.path.basename(line).startswith("test_")
    )


def run_alone(path: str) -> tuple[bool, str]:
    proc = subprocess.run(
        (sys.executable, "-m", "pytest", path, "-q", "--no-cov", "--tb=short"),
        capture_output=True, text=True, check=False,
    )
    return proc.returncode in (0, 5), proc.stdout[-1500:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.environ.get("ISOLATION_BASE", ""))
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)

    if not args.base:
        print("[isolation] aucune base fournie — rien à vérifier.")
        return 0

    files = changed_test_files(args.base, args.head)
    if not files:
        print("[isolation] aucun fichier de test modifié.")
        return 0

    print(f"[isolation] {len(files)} fichier(s) de test modifié(s) — chacun joué SEUL.")
    failed: list[str] = []
    for path in files:
        ok, tail = run_alone(path)
        print(f"[isolation] {'OK  ' if ok else 'ÉCHEC'} {path}")
        if not ok:
            failed.append(path)
            print(tail)

    if failed:
        print()
        print("[isolation] Ces fichiers ne passent QUE grâce à leurs voisins.")
        print("[isolation] Le shardage est un tourniquet par index : un seul")
        print("[isolation] fichier ajouté déplace 79 % de la partition, et le")
        print("[isolation] défaut réapparaîtra sur une PR sans rapport.")
        return 1
    print("[isolation] tous les fichiers modifiés passent seuls.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
