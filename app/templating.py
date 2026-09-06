"""Single Jinja2Templates instance shared across routers.

Adds a `local` Jinja filter that converts a UTC-aware datetime to the
application default timezone (DEFAULT_TIMEZONE, Europe/Paris). Storage
stays UTC; only the display layer converts.

The filter tolerates naive datetimes by assuming UTC — SQLite may round-
trip `DateTime(timezone=True)` columns as naive on some drivers.
"""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, DEFAULT_TIMEZONE
from app.services.static_assets import asset_url
from app.services.time_format import format_date_short, format_datetime_short

_DEFAULT_TZ = ZoneInfo(DEFAULT_TIMEZONE)


def to_local(dt: datetime | None) -> datetime | None:
    """Convert a datetime to the default timezone (Europe/Paris).

    - None → None (template should guard with `{% if ... %}`)
    - Naive datetime → assume UTC (SQLite roundtrip safety)
    - Aware datetime → astimezone conversion
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(_DEFAULT_TZ)


def local_weekday_iso(dt: datetime | None) -> int | None:
    """ISO weekday (1=Mon..7=Sun) in the user's local timezone."""
    local = to_local(dt)
    if local is None:
        return None
    return local.isoweekday()


templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
def date_fr(dt: datetime | None) -> str:
    """« Sam 05/09 » — la date d'un coup d'œil, en français.

    `Sb_UI_HISTORIQUE_01` — L'HISTORIQUE RENDAIT SES JOURS EN ANGLAIS.
    Il appelait `strftime('%a %d/%m %H:%M')`, et `%a` rend l'abréviation de la
    locale du PROCESSUS : « Sat 05/09 07:54 », dix fois par écran, dans une
    interface française.

    Les pièces existaient pourtant toutes les deux — le filtre `local_weekday`
    juste au-dessus, et la table `WEEKDAY_LABELS`. Aucune n'était atteignable
    depuis un gabarit sans les connaître. Ce filtre les réunit pour que la
    prochaine surface n'ait plus de raison d'écrire sa propre version.

    Localise avant de formater : formater un UTC brut décalerait le jour de la
    semaine d'un cran une nuit sur deux.
    """
    return format_date_short(to_local(dt))


def datetime_fr(dt: datetime | None) -> str:
    """« Sam 05/09 07:54 » — quand l'heure borne quelque chose.

    Distincte de `date_fr` pour une raison de sens, pas de commodité : sur le
    récap d'une séance, l'heure de début borne la séance avec celle de fin.
    Sur une liste d'historique, elle n'est jamais relue.
    """
    return format_datetime_short(to_local(dt))


#: Terminaisons où le pluriel français n'est **pas toujours** un `s` ajouté.
#:
#: Ce n'est PAS une liste de mots irréguliers, et c'est délibéré. Le français
#: n'offre pas de règle par terminaison : `-al` donne « chevaux » mais aussi
#: « carnavals » ; `-ail` donne « travaux » mais aussi « détails » ; `-ou`
#: donne « bijoux » mais aussi « clous ». Tenir la liste exacte des exceptions
#: serait une dette de maintenance pour un gain nul — le produit pluralise
#: onze mots, tous réguliers.
#:
#: Le filtre **refuse donc la classe entière** : sur une terminaison ambiguë il
#: lève, et l'auteur écrit le pluriel à la main. Sur-refuser est sans danger ;
#: sous-refuser rend une faute que personne ne relit.
#:
#: ⚠ `ail` a été ajouté APRÈS une plantation : `travail` ne finit pas par
#: « al », et le filtre rendait « travails » sans rien dire. La liste des
#: terminaisons paraissait complète ; elle ne l'était pas.
_PLURIELS_AMBIGUS = ("al", "ail", "au", "eu", "ou", "s", "x", "z")


def pluriel(mot: str, n: int) -> str:
    """« séance » ou « séances », selon `n`. En français : pluriel dès 2.

    POURQUOI UN FILTRE PLUTÔT QUE DU JINJA EN LIGNE

    Le produit connaissait déjà la règle — dix-huit endroits écrivaient
    `séance{% if n > 1 %}s{% endif %}` correctement. Mais la règle n'était
    écrite nulle part, seulement répétée ; et neuf autres endroits, dans trois
    gabarits, avaient dérivé vers `séance(s)`, la parenthèse qui économise la
    condition en abîmant la phrase.

    C'est le même constat que pour `date_fr` juste au-dessus : la pièce
    existait, elle n'était pas **atteignable** depuis un gabarit sans la
    connaître. Un filtre nommé est atteignable.

    ⚠ CE FILTRE REFUSE CE DONT IL N'EST PAS SÛR. Il ajoute un `s` — correct
    pour les onze mots que le produit pluralise aujourd'hui, faux pour
    « cheval » ou « travail ». Sur une terminaison **ambiguë** il lève, plutôt
    que de rendre une faute que personne ne relira. Un filtre qui devine est
    pire qu'une condition en ligne : il a l'air d'avoir décidé.

    Il sur-refuse, et c'est le bon sens de l'erreur : « détail » et « pneu »
    sont réguliers mais partagent la terminaison d'irréguliers, donc ils
    lèvent aussi. Le coût est d'écrire un pluriel à la main ; le coût inverse
    est « travails » en production.

    Le seuil est `> 1`, et c'est le français : « 0 séance », « 1 séance »,
    « 2 séances ». Le seuil anglais (`!= 1`) rendrait « 0 séances ».
    """
    if n > 1 and mot.lower().endswith(_PLURIELS_AMBIGUS):
        raise ValueError(
            f"pluriel(« {mot} ») : terminaison ambiguë en français. "
            f"Ce filtre ajoute un `s` et ne peut pas garantir ce pluriel — "
            f"l'écrire à la main plutôt que de lui faire dire une faute."
        )
    return f"{mot}s" if n > 1 else mot


def nombre_fr(valeur: float | int | None, decimales: int | None = None) -> str:
    """« 586,0 » devient « 586 » · « 75.63 » devient « 75,6 » · `None` devient « — ».

    POURQUOI UN FILTRE, ENCORE

    Même histoire que `pluriel` juste au-dessus, et cette fois **j'en suis
    l'auteur**. Le produit avait tranché d'écrire les nombres en français, et
    trois gabarits l'appliquaient avec trois orthographes différentes :

        {{ x | string | replace(".", ",") }}
        {{ "%.1f" | format(x) | replace('.', ',') }}
        {{ x | round(1) | string | replace(".", ",") }}

    Deux de ces trois viennent de `Sb_UI_SESSION_DONE_01`, écrites par moi.
    Une quatrième surface — le classement de squad — n'avait rien du tout et
    affichait « 586.0 pts » à côté d'un « 75,6 kg » correct.

    La décision existait. Le moyen de l'appliquer n'existait pas, donc chacun
    l'a réinventé, et le quatrième a oublié.

    ⚠ LE ZÉRO DÉCIMAL DISPARAÎT PAR DÉFAUT. « 586,0 pts » promet une précision
    au dixième que le score n'a pas. Passer `decimales` force le contraire
    quand la précision est réelle — un poids de corps s'écrit « 75,0 kg »,
    parce que le dixième y a été mesuré.
    """
    if valeur is None:
        return "—"
    if decimales is None:
        arrondi = round(float(valeur), 1)
        texte = f"{arrondi:g}"
    else:
        texte = f"{float(valeur):.{decimales}f}"
    return texte.replace(".", ",")


def role_squad(cle: str | None) -> str:
    """« owner » devient « Propriétaire ». La clé reste la clé.

    `role` est un identifiant : il vit en base, et trois gabarits comparent
    dessus (`membership.role == 'owner'`). Le renommer casserait l'autorisation.
    Ce filtre ne traduit que l'AFFICHAGE.

    Le repli rend la clé plutôt que d'escamoter la ligne : si un rôle apparaît
    sans libellé, il faut le VOIR. C'est le comportement qui a révélé, sur le
    récap de séance, qu'une valeur d'énumération semée par mon labo n'existait
    pas dans le produit.
    """
    from app.models.squad import SQUAD_ROLE_LABELS

    if cle is None:
        return ""
    return SQUAD_ROLE_LABELS.get(cle, cle)


templates.env.filters["local"] = to_local
templates.env.filters["local_weekday"] = local_weekday_iso
templates.env.filters["date_fr"] = date_fr
templates.env.filters["datetime_fr"] = datetime_fr
templates.env.filters["pluriel"] = pluriel
templates.env.filters["nombre_fr"] = nombre_fr
templates.env.filters["role_squad"] = role_squad

# `STATIC_ASSET_COHERENCE_01` — L'AUTORITÉ D'URL DES ASSETS MUTABLES.
#
# Les gabarits appellent `asset_url('js/session_focus.js')` et jamais
# `url_for('static', …)` pour une feuille ou un script : l'URL nue est
# dépourvue d'empreinte, donc un client peut conserver un ancien fichier
# pendant que le HTML arrive à jour. Ce couplage rompu a été REPRODUIT — il ne
# reste pas une hypothèse (cf. `SPRINT_STATIC_ASSET_COHERENCE_01_REPORT`).
templates.env.globals["asset_url"] = asset_url
