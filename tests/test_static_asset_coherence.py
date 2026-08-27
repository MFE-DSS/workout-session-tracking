"""`STATIC_ASSET_COHERENCE_01` — le HTML et ses assets évoluent ensemble.

LE DÉFAUT, REPRODUIT AVANT D'ÊTRE FERMÉ
----------------------------------------
Les feuilles et scripts étaient servis par une URL **sans version**, et le
serveur n'envoyait **aucun `Cache-Control`** : le navigateur inventait sa
propre fraîcheur. Un client pouvait donc détenir un ancien script pendant que
le HTML arrivait à jour.

Banc adverse : l'ancien `session_focus.js` de `9b41fa3` servi contre le HTML
actuel reproduit **exactement** les deux symptômes du dogfood — compteur figé
sur `1:30`, boutons `±15 s` jamais révélés. L'ancien cherchait
`[data-start-rest]`, le HTML n'émet plus que `[data-rest-started]` : zéro
racine, sortie silencieuse, aucune erreur.

Le défaut n'appartenait pas au minuteur mais au **couplage HTML ↔ asset**.
Corriger le seul minuteur aurait laissé la mine en place.

CE QUE CES GARDES FERMENT
--------------------------
  1. UNE RÉFÉRENCE ÉCHAPPE À L'AUTORITÉ — il suffit d'un `url_for('static')`
     réintroduit sur une feuille ou un script.
  2. L'EMPREINTE CESSE DE SUIVRE LE CONTENU — un cache trop zélé, un numéro
     de version manuel, et l'URL ne change plus quand le fichier change.
  3. L'EMPREINTE CHANGE SANS RAISON — le client retélécharge tout à chaque
     déploiement, ce qui est l'autre façon de se tromper.
  4. LA SÉMANTIQUE DE CACHE DISPARAÎT — sans en-tête explicite, on retombe
     exactement dans l'état qui a produit l'incident.
"""
from __future__ import annotations

import pathlib
import re

from app.main import IMMUTABLE_MAX_AGE
from app.services.static_assets import (
    FINGERPRINT_LENGTH,
    asset_url,
    fingerprint,
    is_fingerprinted,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
STATIC = ROOT / "app/static"

JS_UNDER_TEST = "js/session_focus.js"
FINGERPRINT_RE = re.compile(rf"\?v=([0-9a-f]{{{FINGERPRINT_LENGTH}}})$")


def _uncommented(src: str) -> str:
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


# ═════════ 1. UNE SEULE AUTORITÉ, SANS EXCEPTION ═════════


def test_no_stylesheet_or_script_bypasses_the_authority():
    """LA GARDE DE FOND. Une seule référence oubliée rouvre le défaut pour ce
    fichier-là, en silence — aucune page ne casse, l'ancien contenu est juste
    servi indéfiniment."""
    offenders = []
    pattern = re.compile(
        r"""url_for\(\s*['"]static['"]\s*,\s*path\s*=\s*['"]((?:css|js)/[^'"]+)['"]"""
    )
    for tpl in TEMPLATES.rglob("*.html"):
        for hit in pattern.findall(_uncommented(tpl.read_text(encoding="utf-8"))):
            offenders.append(f"{tpl.relative_to(TEMPLATES)} → {hit}")
    assert not offenders, (
        "assets mutables référencés hors de l'autorité : " + ", ".join(offenders)
    )


def test_the_authority_is_actually_used_by_the_templates():
    """Le pendant : une garde qui n'interdit que l'ancienne forme resterait
    verte si TOUTES les références disparaissaient."""
    used = [
        tpl.relative_to(TEMPLATES).as_posix()
        for tpl in TEMPLATES.rglob("*.html")
        if "asset_url(" in _uncommented(tpl.read_text(encoding="utf-8"))
    ]
    assert len(used) >= 8, f"seulement {len(used)} gabarits utilisent l'autorité"
    assert "base.html" in used
    assert "session_detail.html" in used


def test_every_referenced_asset_exists_on_disk():
    """Une balise vers un fichier absent est un 404 silencieux dans l'onglet
    réseau — et une feuille qui ne s'applique jamais."""
    referenced = set()
    for tpl in TEMPLATES.rglob("*.html"):
        referenced.update(re.findall(
            r"""asset_url\(\s*['"]([^'"]+)['"]""",
            _uncommented(tpl.read_text(encoding="utf-8"))))
    assert referenced, "aucun asset référencé — la garde ne mesure rien"
    for rel in sorted(referenced):
        assert (STATIC / rel).is_file(), f"asset référencé mais absent : {rel}"


# ═════════ 2. L'EMPREINTE SUIT LE CONTENU — LE CŒUR ═════════


def test_unchanged_content_keeps_the_same_url():
    """Sinon chaque déploiement invalide tout le cache de tous les clients.

    ⚠ Comparer `asset_url()` à lui-même serait une tautologie : cela ne
    prouverait que la mémoïsation. On **vide le cache interne** entre les deux
    lectures — c'est ainsi qu'un redémarrage de processus, ou un déploiement
    qui réécrit les fichiers sans les modifier, se comporte réellement.
    """
    from app.services import static_assets

    before = asset_url(JS_UNDER_TEST)
    static_assets._CACHE.clear()
    assert asset_url(JS_UNDER_TEST) == before


def test_changed_content_changes_the_url(tmp_path):
    """LA GARDE COMPORTEMENTALE EXIGÉE. On modifie RÉELLEMENT le fichier et on
    vérifie que l'URL bouge — c'est la propriété qui rend l'incident
    impossible à reproduire : l'ancienne URL n'est plus demandée."""
    target = STATIC / JS_UNDER_TEST
    original = target.read_bytes()
    before = asset_url(JS_UNDER_TEST)
    try:
        target.write_bytes(original + b"\n/* mutation de garde */\n")
        after = asset_url(JS_UNDER_TEST)
    finally:
        target.write_bytes(original)

    assert before != after, (
        "le contenu a changé et l'URL est restée la même — le client "
        "continuerait de servir l'ancien fichier"
    )
    assert asset_url(JS_UNDER_TEST) == before, (
        "après restauration, l'URL doit redevenir la précédente : l'empreinte "
        "dépend du CONTENU, pas de l'horodatage"
    )


def test_the_fingerprint_is_content_derived_not_a_timestamp(tmp_path):
    """Deux fichiers de contenu identique rendent la même empreinte, même
    écrits à des instants différents. Un horodatage échouerait ici."""
    a = tmp_path / "a.js"
    b = tmp_path / "b.js"
    a.write_text("console.log(1);\n", encoding="utf-8")
    b.write_text("console.log(1);\n", encoding="utf-8")
    import hashlib
    ha = hashlib.sha256(a.read_bytes()).hexdigest()[:FINGERPRINT_LENGTH]
    hb = hashlib.sha256(b.read_bytes()).hexdigest()[:FINGERPRINT_LENGTH]
    assert ha == hb
    assert fingerprint(JS_UNDER_TEST) == hashlib.sha256(
        (STATIC / JS_UNDER_TEST).read_bytes()).hexdigest()[:FINGERPRINT_LENGTH]


def test_no_manual_version_number_anywhere():
    """« Pas d'incrément manuel » : un humain qui oublie de le faire EST le
    mode de défaillance qu'on retire."""
    src = (ROOT / "app/services/static_assets.py").read_text(encoding="utf-8")
    body = re.sub(r'"""[\s\S]*?"""', " ", src)
    for banned in ("VERSION =", "ASSET_VERSION", "BUILD_ID", "time.time",
                   "datetime", "uuid"):
        assert banned not in body, f"source de version non déterministe : {banned}"


def test_only_mutable_assets_are_fingerprinted():
    """Icônes et manifeste n'ont jamais porté de contrat avec le HTML : les
    empreindre ferait du bruit sans fermer quoi que ce soit."""
    assert is_fingerprinted("css/app.css")
    assert is_fingerprinted("js/session_focus.js")
    assert not is_fingerprinted("icons/favicon.svg")
    assert "?v=" not in asset_url("icons/favicon.svg")


# ═════════ 3. LE RENDU PORTE L'EMPREINTE ═════════


def test_the_rendered_page_carries_fingerprinted_urls(client):
    body = client.get("/").text
    urls = re.findall(r'(?:href|src)="(/static/(?:css|js)/[^"]+)"', body)
    assert urls, "aucune URL d'asset mutable rendue"
    for url in urls:
        assert FINGERPRINT_RE.search(url), f"URL sans empreinte rendue : {url}"


def test_the_session_surface_carries_a_fingerprinted_timer_script(client):
    """LA SURFACE DE L'INCIDENT, nommément.

    ⚠ Cette garde interrogeait d'abord `/` — qui ne charge PAS le script du
    minuteur. Elle passait donc à vide, sans jamais regarder la page
    concernée. On ouvre une vraie séance.
    """
    created = client.post("/sessions",
                          data={"template_slug": "push-a",
                                "creation_source": "library"},
                          follow_redirects=True)
    assert created.status_code == 200, created.status_code
    body = created.text
    assert "session_focus.js" in body, (
        "la séance ne charge pas le script du minuteur — garde aveugle"
    )
    refs = re.findall(r'src="(/static/js/session_focus\.js[^"]*)"', body)
    assert refs, "script du minuteur référencé autrement qu'attendu"
    for ref in refs:
        assert FINGERPRINT_RE.search(ref), f"script du minuteur sans empreinte : {ref}"


# ═════════ 4. LA SÉMANTIQUE DE CACHE EST EXPLICITE ═════════


def test_a_fingerprinted_asset_is_immutable(client):
    r = client.get(asset_url(JS_UNDER_TEST))
    assert r.status_code == 200
    cc = r.headers.get("cache-control", "")
    assert "immutable" in cc, cc
    assert "max-age=31536000" in cc, cc


def test_an_unversioned_asset_must_revalidate(client):
    """Le régime qui manquait. Sans en-tête, le navigateur inventait sa propre
    fraîcheur — c'est ce qui a rendu l'incident possible."""
    r = client.get(f"/static/{JS_UNDER_TEST}")
    assert r.status_code == 200
    assert r.headers.get("cache-control") == "no-cache", r.headers.get("cache-control")


def test_authenticated_html_is_private_and_revalidated(client):
    """Un HTML mis en cache par un intermédiaire servirait les données d'un
    utilisateur à un autre ; un HTML périmé rouvrirait le décalage avec les
    assets."""
    r = client.get("/")
    assert r.status_code == 200
    cc = r.headers.get("cache-control", "")
    assert "private" in cc, cc
    assert "no-cache" in cc, cc


def test_the_documented_reverse_proxy_matches_the_application_policy():
    """LA GARDE QUI M'A MANQUÉ D'ABORD.

    nginx sert `/static/` **depuis le disque** : la requête n'atteint jamais
    FastAPI, donc le middleware applicatif ne gouverne pas la production sur
    ce chemin. J'ai livré une politique applicative en croyant décrire la
    production — c'était faux, et seul l'examen de la configuration
    documentée l'a montré.

    L'ancien `expires 7d;` sur des URL sans empreinte est un mécanisme **plus
    fort** que la mise en cache heuristique : il autorisait explicitement sept
    jours sans revalidation. Cette garde interdit son retour et exige que les
    deux régimes de la doc correspondent à ceux du code.
    """
    doc = (ROOT / "deploy/README.md").read_text(encoding="utf-8")
    static_block = doc.split("location /static/", 1)
    assert len(static_block) == 2, "le bloc statique nginx a disparu de la doc"
    block = static_block[1].split("}", 1)[0] + doc.split("location /static/", 1)[1][:900]

    assert "expires 7d" not in block, (
        "`expires 7d` est de retour sur des assets : sept jours sans "
        "revalidation, c'est le mécanisme même de l'incident"
    )
    assert "immutable" in block, "le régime empreint n'est pas documenté"
    assert "no-cache" in block, "le régime nu n'est pas documenté"
    assert f"max-age={IMMUTABLE_MAX_AGE}" in block, (
        "la durée documentée diverge de celle du code"
    )


def test_no_asset_is_served_without_any_cache_directive(client):
    """L'état exact d'avant : ni `Cache-Control`, ni `Expires`."""
    for url in (asset_url(JS_UNDER_TEST), f"/static/{JS_UNDER_TEST}",
                "/static/icons/favicon.svg"):
        r = client.get(url)
        assert r.headers.get("cache-control"), f"aucune directive pour {url}"
