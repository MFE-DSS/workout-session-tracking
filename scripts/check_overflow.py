#!/usr/bin/env python3
"""Garde de débordement horizontal — RENDUE, pas statique.

POURQUOI CE SCRIPT EXISTE
--------------------------
`/` débordait horizontalement de 39 px à partir de 1024 px, et personne ne l'a
vu pendant des mois. Ni la CI, ni les gardes de gabarit, ni les relevés — parce
qu'aucun d'eux ne rendait la page **au-delà de 430 px**. Le défaut était
invisible par construction : la seule chose qui pouvait le voir était un
navigateur à une largeur qu'on ne regardait jamais.

Une garde statique ne peut pas remplacer celle-ci. Le débordement ne vient
d'aucune ligne fautive : il naît de la RENCONTRE entre `width: 100%`,
`flex-direction: row` et `flex-wrap: nowrap`, chacune correcte isolément.

⚠ OÙ CETTE GARDE TOURNE, ET OÙ ELLE NE TOURNE PAS
--------------------------------------------------
Playwright n'est ni dans `requirements.txt` ni dans le workflow CI. **Cette
garde ne tourne donc PAS en intégration continue** — c'est un contrôle de
poste, au même titre que `run_local_sweep.sh`.

Ce qui EST vérifié en CI, par `tests/test_overflow_gate_contract.py` :
  · le script existe et déclare les deux paliers de largeurs ;
  · sa liste de surfaces couvre **toutes** les routes GET atteignables du
    produit — une route neuve non couverte fait rougir la CI.

Autrement dit : la CI garantit que la garde ne se périme pas, le poste
garantit qu'elle passe. Faire tourner un navigateur en CI est une décision
`ci_infra` qui n'appartient pas à cette tranche.

USAGE
-----
    python scripts/check_overflow.py --port 8860

Le serveur de lab doit déjà tourner sur ce port avec un compte peuplé.
Sortie non nulle dès qu'une surface déborde. Rien ici ne peut rendre un
débordement réel vert.
"""
from __future__ import annotations

import argparse
import sys

#: Toute surface atteignable est vérifiée aux DEUX largeurs qui encadrent le
#: basculement de coque : mobile, et le seuil du rail latéral (1024 px), qui
#: est exactement là où le défaut vivait.
WIDTHS_ALL = (390, 1024)

#: Les surfaces SOUVERAINES sont vérifiées sur toute l'échelle. Une dérive y
#: est une régression (`AUREN_UI_BLUEPRINT`), et `/` a prouvé qu'un palier non
#: mesuré est un palier non tenu.
WIDTHS_SOVEREIGN = (360, 390, 430, 768, 1024, 1280)

#: `AUREN_UI_BLUEPRINT` — Accueil et Séance. La console de séance est
#: paramétrée à l'exécution : le script résout un identifiant réel.
SOVEREIGN = ("/", "/sessions/{session}")

#: Surfaces exclues du parcours, avec leur raison. Une exclusion nommée n'est
#: pas une dette cachée ; un `skip` silencieux en serait une.
EXCLUDED = {
    "/logout": "action, pas une surface",
    "/export/sessions.json": "téléchargement",
    "/export/sessions.csv": "téléchargement",
    "/body/export.json": "téléchargement",
    "/api/docs": "outil tiers, hors charte visuelle",
}

PROBE = """
() => {
  const docW = document.documentElement.clientWidth;
  const worst = [];
  const walk = el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.right > docW + 0.5) {
      worst.push({
        sel: el.tagName.toLowerCase() + '.' +
             (el.className || '').toString().split(' ')[0],
        over: Math.round(r.right - docW),
      });
    }
    for (const c of el.children) walk(c);
  };
  walk(document.body);
  worst.sort((a, b) => b.over - a.over);
  return {
    excess: document.documentElement.scrollWidth - docW,
    offenders: worst.slice(0, 3),
  };
}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8860)
    ap.add_argument("--user-id", type=int, default=3)
    ap.add_argument("--cookie", required=True,
                    help="cookie de session, au format nom=valeur")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[overflow] Playwright absent — cette garde est un contrôle de "
              "poste, pas un contrôle CI. Voir l'en-tête du script.",
              file=sys.stderr)
        return 2

    base = f"http://127.0.0.1:{args.port}"
    name, _, value = args.cookie.partition("=")
    cookie = {"name": name, "value": value, "domain": "127.0.0.1", "path": "/"}

    failures: list[tuple[str, int, int, str]] = []
    checked = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        surfaces = _discover(browser, base, cookie)

        for path in sorted(surfaces):
            widths = (WIDTHS_SOVEREIGN if _is_sovereign(path, surfaces)
                      else WIDTHS_ALL)
            for w in widths:
                ctx = browser.new_context(viewport={"width": w, "height": 900},
                                          locale="fr-FR")
                ctx.add_cookies([cookie])
                page = ctx.new_page()
                resp = page.goto(base + path, wait_until="networkidle",
                                 timeout=25000)
                if not resp or resp.status >= 400:
                    ctx.close()
                    continue
                # Un cookie refusé rend le formulaire de connexion SANS
                # échouer : la garde mesurerait alors la mauvaise page.
                if page.url.rstrip("/").endswith("/login"):
                    print("[overflow] ABANDON : cookie refusé — la garde "
                          "mesurerait /login.", file=sys.stderr)
                    return 2
                d = page.evaluate(PROBE)
                checked += 1
                if d["excess"] > 0:
                    who = ", ".join(f"{o['sel']} +{o['over']}px"
                                    for o in d["offenders"]) or "?"
                    failures.append((path, w, d["excess"], who))
                ctx.close()
        browser.close()

    print(f"[overflow] {len(surfaces)} surfaces · {checked} rendus vérifiés")
    if failures:
        print(f"[overflow] {len(failures)} DÉBORDEMENT(S) :", file=sys.stderr)
        for path, w, excess, who in failures:
            print(f"  {path}  @{w}px  +{excess}px  → {who}", file=sys.stderr)
        return 1
    print("[overflow] aucun débordement horizontal")
    return 0


def _is_sovereign(path: str, surfaces: set[str]) -> bool:
    if path == "/":
        return True
    return path.startswith("/sessions/") and path.count("/") == 2


def _discover(browser, base: str, cookie: dict) -> set[str]:
    """Parcourt le produit depuis la racine authentifiée.

    Une LISTE écrite à la main mesure ce à quoi on pense ; un parcours mesure
    ce que le produit expose. C'est un parcours qui a trouvé le défaut que
    treize surfaces choisies à la main avaient manqué.
    """
    from collections import deque

    ctx = browser.new_context(viewport={"width": 1024, "height": 900})
    ctx.add_cookies([cookie])
    page = ctx.new_page()

    seen, queue = {"/"}, deque(["/"])
    while queue:
        path = queue.popleft()
        resp = page.goto(base + path, wait_until="networkidle", timeout=25000)
        if not resp or resp.status >= 400:
            seen.discard(path)
            continue
        for href in page.eval_on_selector_all(
                "a[href]", "els => els.map(e => e.getAttribute('href'))"):
            if not href:
                continue
            if href.startswith(base):
                href = href[len(base):] or "/"
            href = href.split("#")[0]
            if (not href.startswith("/") or href.startswith("//")
                    or href in seen or href in EXCLUDED):
                continue
            seen.add(href)
            queue.append(href)
    ctx.close()
    return seen


if __name__ == "__main__":
    raise SystemExit(main())
