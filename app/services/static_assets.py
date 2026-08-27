"""`STATIC_ASSET_COHERENCE_01` — une seule autorité d'URL pour les assets mutables.

LE DÉFAUT QUE CE MODULE FERME
------------------------------
Les feuilles et scripts étaient référencés par une URL **sans version** :

    url_for('static', path='js/session_focus.js')  →  /static/js/session_focus.js

Le serveur n'envoyait **aucun `Cache-Control`** : le navigateur appliquait donc
une fraîcheur *heuristique* de son cru. Un client pouvait conserver un ancien
fichier tandis que le HTML, lui, arrivait à jour.

**Ce n'est pas une hypothèse.** Banc adverse : l'ancien `session_focus.js` de
`9b41fa3` servi contre le HTML actuel reproduit **exactement** les deux
symptômes relevés en dogfood — compteur figé sur `1:30` et boutons `±15 s`
jamais révélés. La cause est structurelle : l'ancien script cherchait
`[data-start-rest]`, le HTML n'émet plus que `[data-rest-started]`, donc zéro
racine et une sortie silencieuse.

Le défaut n'appartient pas au minuteur. Il appartient au **couplage HTML ↔
asset** : toute évolution de contrat entre les deux échoue en silence chez qui
détient l'ancien fichier. Corriger le seul minuteur aurait laissé la mine en
place pour la fois suivante.

CE QUE CE MODULE GARANTIT
--------------------------
* **Empreinte dérivée du CONTENU** — `sha256` du fichier, tronqué. Aucun numéro
  de version à incrémenter à la main : un humain qui oublie de le faire est
  exactement le mode de défaillance qu'on retire.
* **Contenu inchangé → URL inchangée.** Le cache du client reste valide et rien
  n'est retéléchargé sans raison.
* **Contenu changé → URL changée.** L'ancien fichier devient inatteignable par
  cette URL : le client ne PEUT plus le servir.

POURQUOI UNE CHAÎNE DE REQUÊTE, ET NON UN NOM DE FICHIER HACHÉ
---------------------------------------------------------------
`?v=<empreinte>` fait partie de l'URL de cache pour tout navigateur, et ne
demande **ni réécriture de chemin, ni fichiers dupliqués sur le disque, ni
étape de build**. Le montage `StaticFiles` existant continue de servir le
fichier réel. Un nom haché imposerait une étape de génération que ce dépôt n'a
pas — et une étape de build qu'on oublie de lancer serait le même défaut sous
un autre nom.

LE CACHE INTERNE
----------------
Hacher à chaque rendu coûterait une lecture disque par balise et par page. On
mémorise donc l'empreinte, invalidée par `(mtime_ns, taille)` : en
développement un fichier réécrit est re-haché immédiatement ; en production le
hachage a lieu une fois par fichier après le déploiement.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

#: Longueur de l'empreinte publiée. 12 hexadécimaux = 48 bits : la collision
#: est hors de portée pour quelques dizaines de fichiers, et l'URL reste
#: lisible dans un journal ou un onglet réseau.
FINGERPRINT_LENGTH = 12

#: Ce qui est considéré comme MUTABLE, donc empreint. Les icônes et le
#: manifeste ne changent pas d'un déploiement à l'autre et n'ont jamais porté
#: de contrat avec le HTML ; ils restent servis par l'URL nue, avec la
#: sémantique de revalidation.
FINGERPRINTED_SUFFIXES = (".css", ".js")

_STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"

#: `chemin relatif -> (mtime_ns, taille, empreinte)`
_CACHE: dict[str, tuple[int, int, str]] = {}


class AssetNotFound(FileNotFoundError):
    """Un gabarit référence un asset qui n'existe pas.

    On lève au lieu de rendre une URL nue : une balise silencieusement cassée
    est précisément le genre de défaut que cette tranche existe pour retirer.
    """


def fingerprint(relative_path: str) -> str:
    """Empreinte de contenu d'un asset, mémorisée par `(mtime, taille)`."""
    target = _STATIC_ROOT / relative_path
    try:
        stat = target.stat()
    except OSError as exc:  # noqa: PERF203 - le message porte l'information
        raise AssetNotFound(
            f"asset introuvable : {relative_path} (attendu sous {_STATIC_ROOT})"
        ) from exc

    key = (stat.st_mtime_ns, stat.st_size)
    cached = _CACHE.get(relative_path)
    if cached is not None and cached[:2] == key:
        return cached[2]

    digest = hashlib.sha256(target.read_bytes()).hexdigest()[:FINGERPRINT_LENGTH]
    _CACHE[relative_path] = (key[0], key[1], digest)
    return digest


def is_fingerprinted(relative_path: str) -> bool:
    return relative_path.endswith(FINGERPRINTED_SUFFIXES)


def asset_url(relative_path: str) -> str:
    """L'URL canonique d'un asset. **Seule autorité** des gabarits.

    Rend `/static/<chemin>?v=<empreinte>` pour un asset mutable, et l'URL nue
    pour le reste. Toujours une URL absolue de chemin : la même quelle que soit
    la page qui la rend, donc la même entrée de cache.
    """
    base = f"/static/{relative_path.lstrip('/')}"
    if not is_fingerprinted(relative_path):
        # Vérifié quand même : une icône manquante doit se voir au test, pas
        # en production.
        fingerprint(relative_path)
        return base
    return f"{base}?v={fingerprint(relative_path)}"
