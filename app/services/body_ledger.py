"""`UI-CP7.5A` — le relevé corporel devient la PORTE de sa propre écriture.

⚠ LE DÉFAUT QUE CE MODULE FERME, ET IL EST MESURÉ.

`BODY_LEDGER` (`/profile`) lisait **six faits** — taille, envergure, tour de
taille, poitrine, cuisse, mollet — parce qu'il les empruntait à
`morphology_readmodel`, dont le rôle est de présenter les entrées du MOTEUR
morphologique. Or le formulaire de saisie en écrit **treize**.

Sept faits capturés n'avaient donc **aucune ligne** dans le relevé : cou,
hanches, largeur d'épaules, bras gauche et droit, cuisse gauche et droite
séparément, mollet gauche et droit séparément. On pouvait les saisir, jamais
les relire — et surtout, ils n'avaient aucune ligne qui puisse servir de porte
à leur propre correction. La cible `« USER TOUCHES THE FACT -> USER EDITS THAT
FACT »` était structurellement inatteignable pour la moitié du corps.

CE MODULE NE TOUCHE PAS AU CONTRAT DU MOTEUR. `MorphologyFacts` est l'entrée
d'un moteur pur ; y ajouter des champs pour satisfaire une surface serait
exactement l'inversion que `Sx_MORPHO` interdit. Le relevé est une
PRÉSENTATION, et il lit les mesures directement.

⚠ ET IL NE CRÉE PAS UN SECOND LECTEUR CONCURRENT.
`profile` lisait déjà les valeurs par `get_latest_measurement`, c'est-à-dire
**la dernière LIGNE**. Avec une acquisition fait par fait — noter son tour de
taille aujourd'hui crée une ligne où le poids est nul — cette lecture aurait
fait disparaître le poids de l'écran alors que le relevé, lui, le montrait
toujours. Deux lectures contradictoires de la même donnée sur le même écran.

Ici tout est résolu **champ par champ**, comme `morphology_runtime` le fait
déjà pour ses six faits, et avec la même règle de latéralité : deux côtés ne
sont réunis que s'ils viennent de la MÊME ligne — moyenner la cuisse gauche de
mardi avec la droite de janvier fabriquerait une valeur jamais mesurée.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement
from app.services.time_format import relative_hours_ago

#: Unités sémantiques du corps (`arbitrage §6`). Elles NE SONT PAS rendues
#: comme quatre cartes — elles ordonnent le relevé et rien de plus. Le
#: regroupement visible, c'est la LIGNE ; l'unité dit seulement dans quel
#: ordre les lignes se suivent.
UNITE_POIDS = "POIDS"
UNITE_SUIVI = "SUIVI"
UNITE_ZONES = "ZONES"
UNITE_CHARPENTE = "CHARPENTE"
UNITE_REFERENCE = "RÉFÉRENCE"


@dataclass(frozen=True)
class ChampDeSaisie:
    """Un input de la feuille d'acquisition."""

    cle: str
    libelle: str
    min: float
    max: float
    pas: str = "0.1"


@dataclass(frozen=True)
class LigneDuReleve:
    """Une ligne du relevé, ET la porte de son écriture.

    `champs` porte AU PLUS DEUX entrées, et c'est la règle qui empêche ce
    relevé de redevenir un formulaire : « One user intent must never open
    fourteen unrelated inputs. » Une paire gauche/droite se comprend ensemble,
    donc s'édite ensemble ; au-delà, ce n'est plus une intention, c'est une
    grille.
    """

    cle: str
    libelle: str
    unite_semantique: str
    #: Valeur affichée, déjà formatée ; `None` quand le fait est absent.
    valeur: str | None
    unite: str
    #: « mesure directe », « moyenne gauche + droite », « profil »…
    #: `None` quand le fait est ABSENT : une ligne jamais mesurée n'a pas de
    #: provenance, et écrire « mesure directe » à côté d'un tiret annoncerait
    #: une mesure qui n'existe pas. L'ignorance est un état légitime, elle ne
    #: se déguise pas en méthode.
    provenance: str | None
    #: « il y a 7 j » ; `None` quand la donnée n'est pas horodatée.
    age: str | None
    champs: tuple[ChampDeSaisie, ...]
    #: Vers quelle route la feuille poste. Deux écrivains canoniques existent
    #: déjà — les mesures et les données de référence — et on n'en crée pas un
    #: troisième.
    route: str
    #: Un dérivé ne s'écrit pas : il vaut ses sources.
    derive: bool = False

    @property
    def connue(self) -> bool:
        return self.valeur is not None

    @property
    def editable(self) -> bool:
        return not self.derive


_CM = "cm"

#: Le plan du relevé. Chaque entrée produit UNE ligne, et une ligne ouvre au
#: plus deux champs. L'ordre est celui des unités sémantiques.
#:
#: ⚠ Les bornes ne sont pas réécrites ici : elles sont lues sur
#: `body_profile.BODY_MEASUREMENT_FIELDS`, qui est la liste blanche de
#: l'écrivain canonique. Les recopier créerait une seconde source de vérité
#: pour une validation déjà versionnée — et la divergence serait silencieuse,
#: parce qu'une borne de gabarit trop large ne fait qu'obtenir un rejet
#: serveur que l'utilisateur ne comprendrait pas.
PLAN_DU_RELEVE: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    # (clé de ligne, libellé, unité sémantique, clés de champ)
    ("weight_kg", "Poids", UNITE_POIDS, ("weight_kg",)),
    ("waist_cm", "Tour de taille", UNITE_SUIVI, ("waist_cm",)),
    ("chest_cm", "Tour de poitrine", UNITE_ZONES, ("chest_cm",)),
    ("arm_cm", "Bras", UNITE_ZONES, ("arm_cm_left", "arm_cm_right")),
    ("thigh_cm", "Cuisses", UNITE_ZONES, ("thigh_cm_left", "thigh_cm_right")),
    ("shoulder_width_cm", "Largeur d'épaules", UNITE_CHARPENTE,
     ("shoulder_width_cm",)),
    ("wingspan_cm", "Envergure", UNITE_CHARPENTE, ("wingspan_cm",)),
    ("hip_cm", "Tour de hanches", UNITE_CHARPENTE, ("hip_cm",)),
    ("neck_cm", "Tour de cou", UNITE_CHARPENTE, ("neck_cm",)),
    ("calf_cm", "Mollets", UNITE_CHARPENTE,
     ("calf_cm_left", "calf_cm_right")),
)

#: Libellés courts pour la feuille. Ceux de `BODY_MEASUREMENT_FIELDS` portent
#: leur unité entre parenthèses (« Bras gauche (cm) »), ce qui est juste dans
#: un formulaire de treize champs où rien d'autre ne la donne — et redondant
#: dans une feuille dont l'en-tête est déjà « Bras · cm ».
_LIBELLES_COURTS = {
    "arm_cm_left": "Gauche",
    "arm_cm_right": "Droit",
    "thigh_cm_left": "Gauche",
    "thigh_cm_right": "Droite",
    "calf_cm_left": "Gauche",
    "calf_cm_right": "Droit",
}

PROVENANCE_DIRECTE = "mesure directe"
PROVENANCE_MOYENNE = "moyenne gauche + droite"
PROVENANCE_GAUCHE = "côté gauche seul"
PROVENANCE_DROIT = "côté droit seul"
PROVENANCE_DERIVEE = "envergure − taille"

#: ⚠ LES TROIS RÉGIMES DE CONFIANCE DE `UI-CP1`, REPRIS MOT POUR MOT.
#:
#: J'avais d'abord écrit « profil » pour la taille ET pour la FC repos, ce qui
#: effaçait une distinction que la tranche précédente avait établie sur preuve
#: et fait garder par un test. La fraîcheur ne s'applique PAS uniformément :
#:
#:   OBSERVATION       tours et poids → l'âge est chiffré
#:   RÉFÉRENCE STABLE  la taille → PAS d'âge, et elle se NOMME comme telle.
#:                     Une taille d'adulte ne périme pas ; lui coller un âge
#:                     suggérerait qu'elle doit être reprise, et noierait les
#:                     âges qui, eux, comptent.
#:   INCONNU           la FC repos → `users.resting_hr` est un `Integer` nu,
#:                     le schéma N'A PAS de colonne de date. Le silence
#:                     laisserait croire à une donnée fraîche : l'ignorance se
#:                     DIT, elle ne se maquille pas.
PROVENANCE_REFERENCE = "Donnée de référence · profil"
PROVENANCE_PROFIL_NON_DATE = "profil · date inconnue"


def _mesures(db: Session, user_id: int) -> list[BodyMeasurement]:
    """Les mesures du propriétaire, les plus récentes d'abord.

    Scopé par `user_id` : la mesure d'un autre n'est pas « refusée », elle est
    introuvable. UNE requête, et c'est la seule que ce module émet — le
    cliquet `test_profile_query_budget` est strict dans les deux sens.
    """
    return list(
        db.execute(
            select(BodyMeasurement)
            .where(BodyMeasurement.user_id == user_id)
            .order_by(
                BodyMeasurement.measured_at.desc(), BodyMeasurement.id.desc()
            )
        ).scalars().all()
    )


def _dernier_non_nul(rows, champ: str):
    for row in rows:
        v = getattr(row, champ, None)
        if v is not None:
            return float(v), row
    return None


def _lateral(rows, gauche: str, droit: str):
    """Réduction latérale sur la ligne la plus récente qui porte un côté.

    Règle reprise telle quelle de `morphology_runtime._lateral` : les deux
    côtés doivent venir de la MÊME ligne.
    """
    for row in rows:
        g = getattr(row, gauche, None)
        d = getattr(row, droit, None)
        if g is not None and d is not None:
            return (float(g) + float(d)) / 2, row, PROVENANCE_MOYENNE
        if g is not None:
            return float(g), row, PROVENANCE_GAUCHE
        if d is not None:
            return float(d), row, PROVENANCE_DROIT
    return None


def _nombre(valeur: float) -> str:
    """Le nombre, en français, au dixième.

    ⚠ J'AVAIS ÉCRIT UNE QUATRIÈME ORTHOGRAPHE, ET C'EST EXACTEMENT LE DÉFAUT
    QUE `nombre_fr` A ÉTÉ CRÉÉ POUR TUER.

    Le filtre canonique existe depuis qu'on a trouvé trois écritures
    concurrentes de la virgule décimale dans trois gabarits, dont deux de ma
    main — et une quatrième surface qui n'avait rien et rendait « 586.0 pts »
    à côté d'un « 75,6 kg » correct. Ma version (`rstrip("0")`) en aurait
    ajouté une cinquième, ET aurait escamoté le dixième.

    `decimales=1` est délibéré et suit la doctrine du filtre : *« un poids de
    corps s'écrit "75,0 kg", parce que le dixième y a été mesuré. »* Un tour
    de taille de 80 cm a été mesuré au mètre ruban : « 80,0 cm » dit la
    précision réelle, « 80 » la perd.
    """
    from app.templating import nombre_fr

    return nombre_fr(valeur, 1)


def _champs_de(cles: tuple[str, ...], unite: str) -> tuple[ChampDeSaisie, ...]:
    """Les champs d'une feuille, étiquetés par ce qu'ils AJOUTENT.

    ⚠ MESURÉ AU RENDU : la feuille du tour de taille portait un champ
    étiqueté « Tour de taille (cm) », à deux centimètres du titre de la
    rangée qui disait déjà « Tour de taille ». Le libellé complet de
    `BODY_MEASUREMENT_FIELDS` est juste dans un formulaire de treize champs,
    où rien d'autre ne nomme la mesure. Dans une feuille dont l'en-tête EST
    le nom du fait, il ne fait que répéter.

    Un champ unique n'ajoute donc que son UNITÉ ; une paire ajoute son CÔTÉ.
    """
    from app.services.body_profile import _FIELD_BY_KEY

    sortie = []
    for cle in cles:
        spec = _FIELD_BY_KEY[cle]
        sortie.append(ChampDeSaisie(
            cle=cle,
            libelle=_LIBELLES_COURTS.get(cle, unite),
            min=spec.min,
            max=spec.max,
            pas="0.1",
        ))
    return tuple(sortie)


def _ligne_mesuree(rows, maintenant, cle, libelle, unite_sem, cles_champs):
    """Une ligne issue de `body_measurements`, résolue CHAMP PAR CHAMP."""
    if len(cles_champs) == 2:
        resolu = _lateral(rows, *cles_champs)
        valeur, row, provenance = resolu if resolu else (None, None, None)
    else:
        resolu = _dernier_non_nul(rows, cles_champs[0])
        valeur, row = resolu if resolu else (None, None)
        provenance = PROVENANCE_DIRECTE if resolu else None

    mesure_le = row.measured_at if row is not None else None
    unite = "kg" if cle == "weight_kg" else _CM
    return LigneDuReleve(
        cle=cle,
        libelle=libelle,
        unite_semantique=unite_sem,
        valeur=_nombre(valeur) if valeur is not None else None,
        unite=unite,
        provenance=provenance,
        age=(relative_hours_ago(maintenant, mesure_le)
             if mesure_le is not None else None),
        champs=_champs_de(cles_champs, unite),
        route="profile_measurements_submit",
    )


def _lignes_de_reference(user) -> list[LigneDuReleve]:
    """Taille et FC repos — elles vivent sur `User`, pas sur la mesure.

    Une seconde copie divergerait (`Sx_MORPHO §4.2`), donc elles gardent leur
    écrivain — mais elles gagnent la même porte que les autres. L'utilisateur
    n'a pas à savoir que « taille » et « tour de taille » sont stockés dans
    deux tables pour corriger l'une ou l'autre.
    """
    from app.services.body_profile import HEIGHT_BOUNDS

    return [
        LigneDuReleve(
            cle="height_cm",
            libelle="Taille",
            unite_semantique=UNITE_REFERENCE,
            valeur=_nombre(float(user.height_cm)) if user.height_cm else None,
            unite=_CM,
            provenance=PROVENANCE_REFERENCE if user.height_cm else None,
            # ⚠ PAS D'ÂGE, et ce n'est pas un oubli : `users.height_cm` est un
            # entier nu, sans colonne de date. Une fraîcheur affichée ici
            # serait une fabrication. Et la taille d'un adulte ne périme pas.
            age=None,
            champs=(ChampDeSaisie("height_cm", _CM,
                                  HEIGHT_BOUNDS[0], HEIGHT_BOUNDS[1],
                                  pas="1"),),
            route="profile_body_submit",
        ),
        LigneDuReleve(
            cle="resting_hr",
            libelle="FC repos",
            unite_semantique=UNITE_REFERENCE,
            valeur=str(user.resting_hr) if user.resting_hr else None,
            unite="bpm",
            provenance=PROVENANCE_PROFIL_NON_DATE if user.resting_hr else None,
            age=None,
            champs=(ChampDeSaisie("resting_hr", "bpm", 30, 220, pas="1"),),
            route="profile_body_submit",
        ),
    ]


def _ligne_derivee(lignes, user) -> LigneDuReleve | None:
    """L'ape index — il n'est PAS acquérable : il vaut ses deux sources.

    Il n'apparaît que quand les deux existent. Refuser de le calculer sinon
    est la règle du moteur, et la surface la tient aussi.
    """
    envergure = next(
        (ligne for ligne in lignes if ligne.cle == "wingspan_cm"), None)
    if envergure is None or not envergure.connue or not user.height_cm:
        return None
    ecart = float(envergure.valeur.replace(",", ".")) - float(user.height_cm)
    return LigneDuReleve(
        cle="ape_index_cm",
        libelle="Ape index",
        unite_semantique=UNITE_REFERENCE,
        valeur=("+" if ecart > 0 else "") + _nombre(ecart),
        unite=_CM,
        provenance=PROVENANCE_DERIVEE,
        age=None,
        champs=(),
        route="",
        derive=True,
    )


def construire_releve(
    db: Session, user_id: int, user, *, now: datetime | None = None
) -> tuple[LigneDuReleve, ...]:
    """Une entrée par fait corporel acquérable, connu ou non.

    ⚠ CE MODULE ÉMET TOUT ; C'EST LE GABARIT QUI DÉCIDE DE LA FORME.

    Un fait connu devient une LIGNE du relevé, directement manipulable. Un
    fait absent ne devient PAS une ligne : il devient une INTENTION dans
    l'entrée d'acquisition unique (arbitrage opérateur `D4`/`D5`). Les deux
    ensembles se dérivent d'ici par `connue`.

    ⚠ La docstring précédente affirmait le contraire — « une ligne absente
    est rendue, et c'est le point ». C'était la conception que l'opérateur a
    refusée : onze rangées « Non renseigné » sur un profil vide, soit
    +404 px pour la même énumération qu'on venait de retirer. Le modèle de
    lecture n'a pas changé ; sa RESTITUTION, si.

    Les trois provenances sont extraites en fonctions nommées — mesure,
    référence, dérivé — parce qu'elles suivent trois règles différentes, pas
    pour faire baisser un compteur : `Sonar S3776` a signalé la complexité,
    et les trois blocs se lisaient déjà comme trois paragraphes distincts.
    """
    maintenant = now or datetime.now(UTC)
    rows = _mesures(db, user_id)

    lignes = [_ligne_mesuree(rows, maintenant, *entree)
              for entree in PLAN_DU_RELEVE]
    lignes += _lignes_de_reference(user)

    derivee = _ligne_derivee(lignes, user)
    if derivee is not None:
        lignes.append(derivee)

    return tuple(lignes)
