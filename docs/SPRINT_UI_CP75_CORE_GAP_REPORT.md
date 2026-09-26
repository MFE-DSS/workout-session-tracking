# UI-CP7.5 — fermeture des deux derniers trous de la boucle primaire

**Statut** : `CONCEPT CLOS · SIX CORRECTIONS APPLIQUÉES` · **Base** : `42258ce`
· **Branche** : `sb/ui-cp75-core-gap`

> `CLAUDE.md §5.1` — aucune livraison UI sans exposition visuelle préalable.
> Deux paquets ont été rendus et soumis ; l'opérateur a tranché six décisions
> et refusé deux de mes propositions. Ce rapport porte l'état APRÈS
> corrections.

---

## 0. Arbitrage final — ce que l'opérateur a tranché

| | décision | ce que j'avais proposé |
|---|---|---|
| `D1` | relevé de séance gardé **temporairement** en profondeur, avec critère de sortie `UI-CP8` écrit | gardé, sans échéance |
| `D2` | la conséquence reste un FAIT, **pas un objet visuel** | un paragraphe rang `BODY` derrière un filet ambre |
| `D3` | **REFUS** de l'occupation forcée du viewport | `min-height: 100dvh` + tiroir poussé au pied |
| `D4` | **REFUS** du renversement — un profil vide n'énumère pas | onze lignes « Non renseigné » permanentes |
| `D5` | faits CONNUS en lignes · faits ABSENTS derrière UNE entrée | tous les faits en lignes |
| `D6` | e-mail → `ACCOUNT`, confirmé | idem |

⚠ **Deux de mes propositions sont refusées, et les deux avaient la même
faute** : j'avais traité « la ligne est devenue une porte » comme une licence
à faire occuper l'écran par des absences. Mesuré après correction, le refus
est chiffré — le profil partiel est passé de **1 536 px à 1 356 px**, soit
plus court qu'avant, là où ma version le poussait à 1 620 px.

---

## 1. Ce que la tranche referme

Deux surfaces de la boucle primaire étaient restées à leur architecture
héritée pendant que le reste du cockpit était recomposé :

| surface | trou |
|---|---|
| `session_done` | huit cartes concurrentes, cinq sorties de même rang, deux scores composites, zéro contrôle |
| `BODY_LEDGER` | relevé en lecture seule, écriture dans un tiroir de quatorze champs à trois écrans de distance |

---

## 2. Trois défauts RÉELS trouvés en construisant

Aucun n'était dans le périmètre annoncé. Tous trois ont été mesurés, pas
supposés.

### 2.1 — La rouverture d'une séance effaçait quatre colonnes, en production

`update_session` écrivait six champs **inconditionnellement** depuis le
formulaire. Or le bouton « Rouvrir pour éditer » poste un formulaire qui ne
porte que `action=reopen` :

```
avant rouverture : ('high', 'good', 78.5, 'bonne séance')
après rouverture : (None, None, None, None)
```

La gravité dépasse la perte de saisie : `concentration` et `global_state`
alimentent `behavioral` → `fatigue_score` → **le moteur de recommandation**.
Rouvrir une séance dégradait silencieusement la décision suivante.

### 2.2 — L'écriture des mesures corporelles ne demandait aucun consentement

`body_consents` modélise un consentement explicite, versionné, horodaté,
retirable. Une seule route l'appliquait : `POST /body/consent`, sur le
routeur `/body` — **rendu 404 en production** (mesuré par requête HTTP sur
spignos.com). Le consentement n'avait donc aucune porte atteignable, et
`POST /profile/measurements`, atteignable, ne l'interrogeait pas du tout.

Le contrat écrit disait « collection requires active consent ». Le produit
écrivait sans jamais demander.

### 2.3 — Troisième instance de la sémantique de remplacement

`profile_body_submit` écrivait e-mail, taille et FC repos inconditionnellement
depuis des paramètres de formulaire dont le défaut est `""`. Invisible tant
qu'un seul formulaire postait les trois ensemble ; **rendu atteignable par
l'acquisition ligne par ligne** — corriger sa taille aurait effacé son e-mail.

C'est la troisième occurrence de cette classe dans le programme, après
`update_measurement` et `update_session`. Les trois appliquent désormais le
même contrat : *soumis → écrit · absent → inchangé · soumis à vide →
effacement explicite*.

---

## 3. `CP7.5B` — l'instrument de transition

### Axes changés (`arbitrage §1`)

| axe | verdict | preuve |
|---|---|---|
| topologie d'objets | **OUI** | 8 cartes → 0 · 5 titres → 1 · 8 objets → 3 |
| hiérarchie de décision | **OUI** | 5 sorties de même rang → 1 commande dominante |
| modèle d'interaction | **OUI** | 0 contrôle → réparation de signal conditionnelle |
| propriété de l'information | **OUI** | analyse → `FLIGHT_RECORDER` · poids → `BODY_LEDGER` |
| chrome persistant | non | intact, et c'est lui qui porte les 4 sorties retirées |

### Mesure (390 × 844, même base, deux arbres)

| état | hauteur avant | après | cartes | sorties | scores |
|---|---|---|---|---|---|
| ordinaire | 2 360 px | **819 px** | 8 → 0 | 4 → 1 | 2 → 0 |
| cardio | 1 484 px | **819 px** | 6 → 0 | 4 → 1 | 2 → 0 |
| anomalie | 2 354 px | **819 px** | 8 → 0 | 4 → 1 | 2 → 0 |
| saisie creuse | 2 024 px | **869 px** | 7 → 0 | 4 → 1 | 2 → 0 |

### ⚠ L'audit de `§13` a corrigé ma première composition

J'allais poser un bilan de ressenti **permanent** sur le closeout. Or
`session_detail.html` collecte déjà `concentration` et `global_state` juste
au-dessus de « TERMINER LA SÉANCE » : c'eût été un second point de collecte
pour les mêmes colonnes — exactement ce que `Sb_SESSION_REVIEW_SIGNAL_01`
interdit, et à raison.

Le closeout ne demande donc **que ce qui manque**, et disparaît quand rien ne
manque. C'est aussi ce qui remplace la prose « Pense à indiquer ton ressenti
sur les prochaines séances » : un contrôle ici et maintenant, à la place
d'une consigne sur un futur.

### ⚠ Le relevé par exercice devait partir, et il reste

Renvoyé à `FLIGHT_RECORDER` avec le reste de l'analyse, puis **mesuré** :

```
GET /sessions/{id}   → 303  /sessions/{id}/done
GET /history         → note d'exercice : absente
                       note de séance  : absente
                       nom d'exercice  : absent
```

Une séance terminée n'a **pas d'autre surface de détail**. Le retirer aurait
supprimé la seule lecture de ce qu'on vient d'enregistrer — une soustraction
sans remplaçant (`CLAUDE.md §5.3`). Il change de RANG, pas de propriétaire,
faute de second propriétaire. Une garde épingle la redirection : le jour où
elle disparaît, elle dira que le relevé a un meilleur domicile.

**Résidu déclaré pour `UI-CP8 SESSION_LIFECYCLE`.**

---

## 4. `CP7.5A` — le relevé manipulable

### Le trou était plus profond que « le formulaire est loin »

Le relevé lisait **6 faits**, le formulaire en écrivait **13**. Cou, hanches,
largeur d'épaules, bras, et les côtés gauche/droit des cuisses et mollets
étaient saisissables et **jamais relus** — donc sans ligne, donc sans porte
possible. La cible *« USER TOUCHES THE FACT → USER EDITS THAT FACT »* était
structurellement inatteignable pour la moitié du corps.

`app/services/body_ledger.py` les rend tous, **résolus champ par champ**,
sans toucher au contrat du moteur (`MorphologyFacts` reste intact : y ajouter
des champs pour satisfaire une surface serait l'inversion que `Sx_MORPHO`
interdit).

### Axes changés

| axe | verdict | preuve |
|---|---|---|
| modèle d'interaction | **OUI** | 0 → 11 portes ; la ligne EST le contrôle |
| propriété de l'information | **OUI** | 6 faits lisibles → 12 · 7 faits sortent de l'invisibilité |
| topologie d'objets | **OUI** | 2 bandes + 1 tiroir de 14 champs → 1 relevé manipulable |
| hiérarchie de décision | non | le poids garde son rang `DISPLAY` et son quick-log |
| chrome persistant | non | intact |

### Le modèle d'état final (`D4` · `D5`)

    FAIT CONNU     → une ligne du relevé, directement manipulable
    FAIT ABSENT    → PAS de ligne ; UNE entrée d'acquisition unique

L'entrée ouvre la **sélection d'une intention** — quel fait veux-tu noter —
puis l'intention ouvre sa feuille : un fait, ou une paire naturellement
comprise ensemble, plus la date. Deux niveaux de `<details>` natifs, zéro
JavaScript, et jamais plus de deux valeurs ouvertes à la fois.

### Mesure finale (390 × 844, même base, deux arbres)

| état | hauteur | objets | commandes | champs au repos | rangées d'inconnus |
|---|---|---|---|---|---|
| vide — avant | 796 px | 2 | 7 | 1 | 0 |
| vide — **après** | **778 px** | 2 | **4** | 1 | **0** |
| partiel — avant | 1 536 px | 2 | 7 | 1 | **4** |
| partiel — **après** | **1 356 px** | 2 | 8 | 1 | **0** |

**Les deux états sont plus COURTS qu'avant**, et le profil partiel ne montre
plus une seule rangée « Non renseigné » — tout en rendant les treize faits
acquérables, contre six lisibles au départ. Toujours **un seul champ au
repos** : le quick-log du poids.

### La divergence que l'acquisition par ligne rendait atteignable

`get_latest_measurement` rendait la dernière **ligne** de mesure ; le relevé
résout **champ par champ**. Tant que le seul écrivain postait les treize
champs d'un coup, les deux coïncidaient. Dès qu'une feuille écrit un fait
isolé — noter son tour de taille crée une ligne où le poids est nul — la
réponse primaire aurait affiché « Non pesé » pendant que le relevé affichait
le poids. Une requête en remplace une autre ; les deux lectures sont
désormais la même.

---

## 5. Décisions antérieures — une redéfinie, une réaffirmée

### 5.1 — `Sb_SESSION_REVIEW_SIGNAL_01` : « la revue ne collecte rien »

Contredite par `§13` (« If non-derivable feedback still needs collecting,
make that the primary object »). La garde est **redéfinie, pas levée** : son
noyau survit — aucun signal par exercice ici, aucun champ inventé, et la
collecte est **conditionnelle à l'absence**, ce qui empêche le retour d'un
formulaire au repos.

### 5.2 — « Un profil vide ne s'énumère pas » (2026-08-20) : RÉAFFIRMÉE

⚠ **J'avais renversé cette décision. L'opérateur a refusé (`D4`).**

Mon raisonnement : depuis que chaque ligne est une PORTE, une ligne absente
n'est plus un constat. J'ai donc rendu les onze absences en lignes
permanentes. Mesuré : **+404 px sur un profil vide**, onze rangées « Non
renseigné » à la file — la même énumération qu'avant, en plus haute.

Ce que le renversement visait juste, c'était l'**impasse** : un utilisateur
neuf ne pouvait enregistrer que son poids, et le lien de l'état vide pointait
vers une ancre inexistante. L'impasse disparaît **sans** l'énumération, par
l'entrée d'acquisition unique. Les deux moitiés étaient séparables ; je les
avais liées à tort.

---

## 6. Budget de requêtes : 5 → 6

`−1` (`get_latest_measurement`, qui lisait la mauvaise chose) `+1` (le relevé
champ par champ) `+1` (`has_active_consent`, la seule réellement neuve, sans
laquelle l'interface ne peut pas router l'intention vers le consentement).

---

## 7. Gardes

| module | gardes | statut |
|---|---|---|
| `test_ui_cp75a_releve_manipulable.py` | 11 | neuf |
| `test_ui_cp75a_consentement_a_l_intention.py` | 8 | neuf |
| `test_ui_cp75b_instrument_de_transition.py` | 12 | neuf |
| `test_ui_cp75b_contrat_ecriture_seance.py` | 4 | neuf |
| `test_ui_cp75a_contrat_ecriture_corps.py` | 6 | neuf |

**Gardes repointées, aucune affaiblie** : `test_session_review_signal` ·
`test_session_done` · `test_session_done_pastilles` ·
`test_morphology_runtime` · `test_morphology_readmodel` ·
`test_profile_measurements` · `test_profile_enrich` ·
`test_ux4_profile_acquisition` · `test_train1d_epistemic_convergence` ·
`test_ui_session_choices` (registre) ·
`test_no_internal_link_traverses_a_redirect` (dérogation périmée levée) ·
`test_profile_query_budget` (5 → 6, décision écrite).

Chaque garde neuve a été **vue rouge par mutation** avant d'être gardée verte.

### Vérifications locales (`check_scope` → `SHARED_CODE`)

| garde | verdict |
|---|---|
| `ruff` (fichiers neufs) | **vert** — 3 findings corrigés à la main, jamais `--fix` |
| `check_ruff_budget` | **272 ≤ 548** |
| `check_spec_protocol` | **vert** |
| broad sweep ciblé | **1 884 passed · 1 skipped · 0 failed** |
| full sweep local | lancé — `run_local_sweep.sh`, chemin absolu, sans pipe |

⚠ Le broad sweep ciblé est un filtre `-k`, et un filtre `-k` **n'est pas un
sweep** : il borne ce qu'on a pensé à nommer, pas le rayon d'impact. Cette
tranche touche deux gabarits et une feuille globale, donc le full sweep est
lancé malgré le tier — la CI parallélisée sur PR reste le filet de vérité.

### ⚠ Trois de mes propres compteurs étaient faux

* `closest('details')` renvoie l'élément lui-même → tout tiroir fermé se
  déclarait invisible ;
* `url_for()` rend une URL **absolue** → « 1 sortie » sur une page qui en
  portait quatre ;
* un commentaire Python contenant `implicit_by_se` faisait conclure à ma
  garde que le calcul était resté.

Et un semis non représentatif — `template_id` omis — m'a fait conclure à tort
que la branche cardio du closeout était morte.

### ⚠ HUITIÈME FAÇON DE MESURER LE MAUVAIS OBJET — et je m'y suis pris DEUX fois

Un `uvicorn` lancé en arrière-plan **recharge Jinja à chaud, pas Python**. Il
servait donc le NOUVEAU gabarit avec l'ANCIENNE route : `releve` et
`a_consenti` absents du contexte, rendus **vides sans erreur**. J'ai capturé
un `/profile` au relevé vide et conclu à un défaut — la base portait trois
mesures et un consentement actif.

C'est plus traître qu'un serveur totalement périmé : le gabarit à jour PROUVE
visuellement qu'on regarde la bonne version. Règle retenue : **relancer le
serveur après toute modification d'un `.py`**, y compris un service que le
gabarit ne nomme pas, et vérifier par une chaîne que seul le nouveau code
produit avant de capturer.

---

## 8. Ce qui reste ouvert

| résidu | destination |
|---|---|
| **une séance terminée n'a pas de surface de détail durable** — critère de sortie `D1` : dès que ce propriétaire existe, le relevé QUITTE la profondeur du closeout | `UI-CP8 SESSION_LIFECYCLE` |
| `ACCOUNT` — l'e-mail y est arrivé, l'ontologie reste à finir | `UI-CP8 ACCOUNT` |
| archive / restauration de programme : service présent, route absente | `UI-CP8 PROGRAM_LIFECYCLE` |
| `/body` reste éteint ; consentement, export et suppression à réunir | `UI-CP8 BODY_DATA_CONTROL` |
| le quick-log du poids s'offre sans consentement et rebondit sur le refus serveur, qui l'explique | à trancher, non bloquant |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
