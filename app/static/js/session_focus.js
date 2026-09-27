/* Repos — amélioration progressive. `Sx_UIV3_02 §7.5`, amendement C.
 *
 * LE DÉFAUT QUE CE FICHIER CORRIGE (Sx_UIV3_02B §D3)
 * --------------------------------------------------
 * La version précédente démarrait le décompte sur TOUT élément portant
 * `[data-start-rest]` — attribut rendu inconditionnellement par le gabarit.
 * Le serveur émettait bien `data-rest-started` après un `nav=stay`, donc
 * après une série réellement enregistrée ; **personne ne lisait cet
 * attribut**. Mesuré au navigateur, sur une URL sans `rest=1` et sans
 * qu'aucune série n'ait été saisie : `running=True, 89s`.
 *
 * Autrement dit : le minuteur de repos tournait PENDANT la série.
 *
 * Deux tests couvraient le sujet et n'assertaient que la présence de la
 * chaîne dans le HTML — ni l'un ni l'autre n'exerçait le comportement. Le
 * contrat était écrit, publié, gardé, et inopérant.
 *
 * LE CONTRAT MAINTENANT (révisé par `UI-CP8R`)
 * --------------------------------------------
 * - Le décompte ne démarre QUE si le serveur a posé `data-rest-remaining`,
 *   et il démarre à CETTE valeur. L'attribut précédent,
 *   `data-rest-started`, était un booléen : il disait qu'un repos courait,
 *   pas depuis quand, et le décompte repartait donc de 90 s à chaque
 *   rendu. Le serveur dérive maintenant le restant de `SetLog.completed_at`.
 * - **Ce fichier ne décide de rien.** Il n'y a plus de repos « démarré par
 *   le client » : le client peint un état que le serveur a déjà tranché.
 * - `±15 s` ajuste l'affichage, **rien n'est persisté** : la durée est un
 *   repli de présentation, pas une prescription (amendement C). Un
 *   rechargement revient donc à la base serveur, et c'est voulu.
 * - Aucune action critique n'en dépend : sans JS, l'utilisateur lit
 *   « Repos suggéré · 1:30 » et `PASSER LE REPOS` reste un lien fonctionnel.
 * - Aucun réseau, aucun framework, aucun bundler, aucune dépendance.
 */
(function () {
  "use strict";

  var FALLBACK_SECONDS = 90;
  var STEP_SECONDS = 15;
  var FLOOR_SECONDS = 0;
  var CEILING_SECONDS = 600;

  /* `UI-CP8R` — ON LIT CE QUI RESTE, PLUS CE QUE ÇA DURE.

     L'attribut précédent, `data-rest-duration`, portait la durée NOMINALE
     (90 s). Le décompte repartait donc de 90 à chaque rendu : repos à 1:30,
     attendre 3 s, recharger, 1:30 de nouveau. Le défaut n'était pas ici —
     ce fichier faisait exactement ce qu'on lui donnait — mais le serveur
     n'avait aucune origine de temps à lui donner.

     `data-rest-remaining` est dérivé côté serveur de `SetLog.completed_at`.
     Le client ne décide plus s'il y a repos ni depuis quand : il peint une
     valeur déjà tranchée. `FALLBACK_SECONDS` reste le repli si l'attribut
     manque ou n'est pas lisible — un décompte faux vaut mieux qu'une page
     cassée, et le rechargement suivant remettra la vérité serveur. */
  function parseRemaining(el) {
    var n = parseInt(el.getAttribute("data-rest-remaining"), 10);
    if (!isFinite(n) || n <= 0) {
      return FALLBACK_SECONDS;
    }
    return n;
  }

  /* `1:30`, pas `90s` — une durée de repos se lit en minutes:secondes. */
  function format(seconds) {
    if (seconds <= 0) {
      return "terminé";
    }
    var m = Math.floor(seconds / 60);
    var s = seconds % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  /* `DF-B` — LE MINUTEUR RAISONNE SUR UNE ÉCHÉANCE, PAS SUR UN DÉCRÉMENT.

     La version précédente faisait `remaining -= 1` à chaque tick. Un
     `setInterval` n'est pas une horloge : le navigateur bride les rappels
     quand l'onglet passe en arrière-plan, quand l'appareil économise
     l'énergie, ou simplement quand le fil est occupé. Chaque rappel manqué
     devenait une seconde de repos qui n'existait pas — la dérive s'accumule
     et le compteur ment d'autant plus qu'on le regarde moins.

     On fixe donc une ÉCHÉANCE, et chaque tick ne fait que lire l'heure. Un
     rappel en retard corrige au lieu de dériver ; `±15 s` déplace
     l'échéance, ce qui reste local à la requête et n'est jamais persisté. */
  function startTimer(root) {
    var display = root.querySelector("[data-rest-display]");
    if (!display) {
      return;
    }

    /* `UI-CP8R §6` — `Date.now()`, PAS `performance.now()`, ET C'EST
       DÉLIBÉRÉ. `performance.now()` n'avance pas de façon fiable au travers
       d'une mise en veille de l'OS ou du navigateur sur WebKit : un
       téléphone verrouillé pendant le repos rendrait un décompte figé.

       `Date.now()` n'est PAS une vérité de domaine pour autant — c'est une
       horloge d'AFFICHAGE, valable entre deux rendus serveur. Au
       rechargement, le serveur re-dérive tout depuis `completed_at`, et
       cette échéance locale est jetée. Aucun horodatage client n'est jamais
       persisté. */
    var deadline = Date.now() + parseRemaining(root) * 1000;
    var resumeUrl = root.getAttribute("data-rest-resume-url");
    var intervalId = null;
    var done = false;

    function remaining() {
      return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    }

    function paint() {
      display.textContent = format(remaining());
    }

    function stop(doneClass) {
      if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
      }
      root.classList.remove("session-focus__rest-timer--running");
      if (doneClass) {
        root.classList.add("session-focus__rest-timer--done");
      }
    }

    /* À ZÉRO, ON SORT — on ne reste pas sur « terminé » avec la série encore
       verrouillée, ce qui imposerait un tap de plus pour rien. La navigation
       mène exactement où le lien de la ligne de série mène : même URL, même
       état d'arrivée. Rien n'est enregistré au passage. */
    function finish() {
      if (done) {
        return;
      }
      done = true;
      stop(true);
      paint();
      if (resumeUrl) {
        window.location.assign(resumeUrl);
      }
    }

    function tick() {
      paint();
      if (remaining() <= 0) {
        finish();
      }
    }

    function adjust(delta) {
      if (done) {
        return;
      }
      var next = Math.min(CEILING_SECONDS,
                          Math.max(FLOOR_SECONDS, remaining() + delta));
      deadline = Date.now() + next * 1000;
      paint();
      if (next === 0) {
        finish();
      }
    }

    paint();
    root.classList.add("session-focus__rest-timer--running");
    intervalId = setInterval(tick, 1000);

    /* Revenir d'un onglet en arrière-plan doit RATTRAPER, pas reprendre où
       l'on croyait en être. C'est le pendant du raisonnement par échéance. */
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) {
        tick();
      }
    });

    /* `±15 s` n'existe que si JS tourne : sans lui, la valeur affichée est
       un repli statique et il n'y a rien à ajuster. Les boutons sont donc
       rendus `hidden` et révélés ici. L'ajustement NE PERSISTE PAS. */
    var steps = root.querySelectorAll("[data-rest-step]");
    for (var i = 0; i < steps.length; i++) {
      (function (btn) {
        btn.hidden = false;
        btn.addEventListener("click", function (ev) {
          ev.preventDefault();
          var d = parseInt(btn.getAttribute("data-rest-step"), 10);
          adjust(isFinite(d) ? d : 0);
        });
      })(steps[i]);
    }
  }

  /* ════════════════════════════════════════════════════════════════════
     `DF-B` — SAISIR EST VALIDER, MAIS SEULEMENT SUR UNE TRANSITION EXPLICITE.

     LE DÉFAUT. Le domaine dit déjà que la donnée remplie EST la preuve du
     set : `completed` se dérive de `weight OR reps`, et la case « Fait » a
     été retirée pour cette raison. L'interface, elle, exigeait encore un
     `VALIDER Sx`. En dogfood ce tap est régulièrement oublié — et c'est
     logique : après avoir noté la charge et les répétitions, l'acte est
     mentalement terminé.

     CE QUI DÉCLENCHE, ET CE QUI NE DÉCLENCHE PAS. On valide sur un geste
     EXPLICITE de fin de saisie : `Entrée` / `Done` au clavier. **Jamais sur
     la frappe, jamais sur le `blur`.** Un `blur` part quand on touche l'écran
     ailleurs, quand le clavier se referme, quand on veut juste relire — ce
     n'est pas une intention de valider, et enregistrer là surprendrait.

     CE QUI EST ENVOYÉ. `form.requestSubmit(boutonDominant)` : exactement la
     soumission qu'un appui sur le bouton aurait produite. Pas de `fetch`, pas
     d'endpoint parallèle, pas de mini-POST — le formulaire sérialise TOUTES
     les valeurs de la carte, et n'en envoyer qu'une partie effacerait le
     reste. Le serveur reste l'unique autorité de persistance.

     OÙ L'ON NE VALIDE PAS. En `CORRECTION`, la rectification doit rester
     intentionnelle. Et tant que les deux champs ne portent pas une valeur,
     il n'y a rien à enregistrer.
     ════════════════════════════════════════════════════════════════════ */
  function currentFields(form) {
    var line = form.querySelector(".setline--current:not(.setline--resting)");
    if (!line) {
      return null;
    }
    var weight = line.querySelector("[name$='_weight_kg']:not([type=hidden])");
    var reps = line.querySelector("[name$='_reps']:not([type=hidden])");
    if (!weight || !reps) {
      return null;
    }
    return {line: line, weight: weight, reps: reps};
  }

  function readyToCommit(fields) {
    return fields.weight.value.trim() !== "" && fields.reps.value.trim() !== "";
  }

  function initAutoCommit() {
    var forms = document.querySelectorAll("[data-session-form]");
    for (var i = 0; i < forms.length; i++) {
      (function (form) {
        var submitter = form.querySelector("[data-dominant-submit]");
        if (!submitter) {
          return;   /* aucun soumetteur dominant : rien à automatiser */
        }
        var fields = currentFields(form);
        if (!fields) {
          return;   /* repos, correction, exercice fini : pas de saisie */
        }
        if (fields.line.classList.contains("setline--correcting")) {
          return;   /* corriger reste un geste délibéré */
        }

        var committed = false;

        function commit() {
          /* Une seule soumission. `change` et `keydown` peuvent se suivre de
             quelques millisecondes — `Entrée` valide le champ ET le quitte —
             et deux `requestSubmit` enverraient deux POST. */
          if (committed) {
            return;
          }
          committed = true;
          form.requestSubmit(submitter);
        }

        function onKey(ev) {
          if (ev.key !== "Enter" && ev.keyCode !== 13) {
            return;
          }
          /* Empêcher la soumission NATIVE d'`Entrée` : sans soumetteur
             explicite elle n'enverrait pas `nav`, et le serveur ne saurait
             pas s'il doit enchaîner sur un repos. */
          ev.preventDefault();
          if (!readyToCommit(fields)) {
            /* Incomplet : on passe au champ suivant plutôt que d'enregistrer
               une série à moitié saisie. */
            if (ev.target === fields.weight) {
              fields.reps.focus();
            }
            return;
          }
          commit();
        }

        /* ════════════════════════════════════════════════════════════════
           `R5` — LA VALIDATION N'EST PLUS UNE ÉTAPE. Opérateur, 2026-09-04 :
           « si je mets un kilo, un nombre de reps, c'est que j'ai validé la
           série. Il n'y a pas d'étape de validation. »

           POURQUOI `change` ET NON `input` NI `blur`.

           `input` partirait EN COURS DE FRAPPE : avec les répétitions déjà
           saisies, taper « 82 » enverrait la série sur le « 8 ».

           `blur` a été refusé, et le motif reste écrit plus haut : il part
           quand on touche l'écran ailleurs, quand le clavier se referme,
           quand on veut juste relire. Ce n'est pas une intention.

           `change` est la troisième voie et c'est ce qui la rend admissible :
           **il ne part que si la VALEUR a changé.** Relire ne le déclenche
           pas. Rouvrir le clavier non plus. Il dit « j'ai fini de saisir ce
           champ », ce qui est exactement l'intention recherchée.

           ⚠ `D9`/`D10` sont donc AMENDÉS, pas contournés : le déclencheur
           s'élargit, le motif qui les fondait est intact.

           On écoute les DEUX champs, pas « le second » : rien n'oblige à
           saisir la charge avant les répétitions. La condition reste la
           même — les deux portent une valeur.
           ════════════════════════════════════════════════════════════════ */
        function onChange() {
          if (readyToCommit(fields)) {
            commit();
          }
        }

        fields.weight.addEventListener("keydown", onKey);
        fields.reps.addEventListener("keydown", onKey);
        fields.weight.addEventListener("change", onChange);
        fields.reps.addEventListener("change", onChange);
      })(forms[i]);
    }
  }

  /* ════════════════════════════════════════════════════════════════════
     `UI-CP8I` — TAMPON DE RÉCUPÉRATION, PAS UNE PERSISTANCE.

     LE DÉFAUT, MESURÉ. Une valeur tapée dans la série courante et non
     validée était PERDUE — au rechargement, en naviguant ailleurs dans
     AUREN et en revenant, en changeant d'exercice, et par le bouton retour
     du navigateur. Quatre chemins ordinaires, quatre pertes.

     CE QUE CE TAMPON N'EST PAS. Il n'est pas de la donnée d'entraînement.
     Le serveur reste la SEULE source durable : rien ici ne touche
     `completed`, ni `completed_at`, ni `rest_dismissed_at`, ni le repos,
     ni la recommandation, ni les analyses. Une valeur restaurée n'est
     qu'une valeur AFFICHÉE ; elle n'existe pour le domaine qu'après le
     POST normal, inchangé.

     POURQUOI `sessionStorage` ET NON L'AUTRE. Mesuré : le tampon survit au
     rechargement, à la navigation dans l'onglet et au bouton retour —
     exactement les quatre pertes — et il meurt à la fermeture de l'onglet,
     où le produit ne promet rien. Un stockage qui survivrait au navigateur
     entier promettrait une continuité que la mesure n'a jamais montrée, et
     demanderait une politique d'expiration à inventer.

     PROTECTION CONTRE LE BROUILLON PÉRIMÉ. Un brouillon ne doit JAMAIS
     écraser une vérité serveur plus récente. Chaque entrée mémorise donc
     la valeur CANONIQUE au moment de la saisie :

         base == canonique rendue  →  restaurer dans les champs
         base != canonique rendue  →  le serveur a bougé, on JETTE

     ISOLATION. La clé porte l'identité de la séance et de la série. Une
     séance appartient à un compte et le serveur refuse les autres : un
     autre utilisateur ne peut pas rendre la page, donc ne peut jamais lire
     l'entrée. Le stockage est en plus borné à l'onglet, ce qui donne
     l'indépendance entre onglets sans une ligne de code.
     ════════════════════════════════════════════════════════════════════ */

  var PREFIXE = "auren:d:";

  function _ss() {
    /* Un navigateur en navigation privée stricte, ou un réglage qui bloque
       le stockage, fait LEVER l'accès lui-même. Sans ce garde, la page
       entière casserait pour une commodité. */
    try {
      var s = window.sessionStorage;
      s.getItem(PREFIXE + "probe");
      return s;
    } catch (e) {
      return null;
    }
  }

  function _champs(form, setId) {
    return {
      w: form.querySelector('[name="set_' + setId + '_weight_kg"]'),
      r: form.querySelector('[name="set_' + setId + '_reps"]')
    };
  }

  /* L'identité de la séance vient de l'ACTION du formulaire, pas de l'URL :
     c'est le serveur qui l'a écrite, et elle ne dépend d'aucun paramètre. */
  function _sessionId(form) {
    var m = (form.getAttribute("action") || "").match(/\/sessions\/(\d+)\//);
    return m ? m[1] : null;
  }

  function _cle(sessionId, setId) {
    return PREFIXE + sessionId + ":" + setId;
  }

  function _ligneCourante(form) {
    return form.querySelector(".setline--current:not(.setline--resting)");
  }

  function _setIdDe(ligne) {
    var m = (ligne.getAttribute("id") || "").match(/^set-(\d+)$/);
    return m ? m[1] : null;
  }

  function sauverBrouillon(store, form, setId) {
    var c = _champs(form, setId);
    if (!c.w || !c.r) {
      return;
    }
    var w = c.w.value.trim();
    var r = c.r.value.trim();
    var cle = _cle(_sessionId(form), setId);
    /* DEUX CHAMPS VIDES N'EST PAS UN BROUILLON. Mémoriser le vide créerait
       une entrée qui ne récupère rien et qui, restaurée, ferait croire à
       une saisie. On efface plutôt. */
    if (w === "" && r === "") {
      try { store.removeItem(cle); } catch (e) { /* plein : tant pis */ }
      return;
    }
    try {
      store.setItem(cle, JSON.stringify({
        w: w,
        r: r,
        b: [c.w.defaultValue, c.r.defaultValue],
        t: Date.now()
      }));
    } catch (e) {
      /* Quota atteint ou stockage refusé : la saisie en cours reste dans le
         DOM, on perd seulement la récupération. Jamais une erreur visible
         pour une commodité. */
    }
  }

  /* Les séries que le SERVEUR déclare enregistrées, toutes cartes
     confondues. Indispensable à l'état REPOS, où la bande de séries n'est
     pas rendue : sans cette liste, le brouillon de la série qu'on vient
     d'enregistrer survivait à son propre POST, faute de champ à comparer. */
  function _setsEnregistrees() {
    var vues = {};
    var formes = document.querySelectorAll("[data-sets-enregistrees]");
    for (var i = 0; i < formes.length; i++) {
      var ids = (formes[i].getAttribute("data-sets-enregistrees") || "")
          .split(",");
      for (var j = 0; j < ids.length; j++) {
        var id = ids[j].trim();
        if (id) {
          vues[id] = true;
        }
      }
    }
    return vues;
  }

  /* ⚠ `defaultValue` EST LA VALEUR CANONIQUE, `value` EST CE QUI EST TAPÉ.
     Le serveur rend `value="..."` dans le HTML ; le navigateur en fait
     `defaultValue`, que la frappe ne modifie PAS. Comparer `value` aurait
     comparé le brouillon à lui-même — la garde n'aurait jamais rien vu. */
  function restaurerBrouillons(store, form) {
    var sessionId = _sessionId(form);
    if (!sessionId) {
      return;
    }
    var enregistrees = _setsEnregistrees();
    var prefixe = PREFIXE + sessionId + ":";
    var cles = [];
    for (var i = 0; i < store.length; i++) {
      var k = store.key(i);
      if (k && k.indexOf(prefixe) === 0) {
        cles.push(k);
      }
    }
    for (var j = 0; j < cles.length; j++) {
      var cle = cles[j];
      var setId = cle.slice(prefixe.length);
      var c = _champs(form, setId);
      if (!c.w || !c.r) {
        /* AUCUN CHAMP RENDU — on ne peut pas comparer. Deux cas, et ils ne
           se traitent pas pareil :

           · la série est déclarée ENREGISTRÉE par le serveur ⇒ son
             brouillon n'a plus d'objet, on l'efface. C'est ce qui réalise
             l'effacement après un POST confirmé, y compris à l'état REPOS,
             où la bande de séries n'existe pas et où le brouillon
             survivait sinon à son propre POST ;

           · sinon, on ne conclut RIEN et on garde. Effacer ici jetterait
             le brouillon d'un exercice simplement replié. */
        if (enregistrees[setId]) {
          try { store.removeItem(cle); } catch (e) { /* rien à faire */ }
        }
        continue;
      }
      var brouillon = null;
      try {
        brouillon = JSON.parse(store.getItem(cle));
      } catch (e) {
        brouillon = null;
      }
      if (!brouillon || !brouillon.b) {
        try { store.removeItem(cle); } catch (e) { /* rien à faire */ }
        continue;
      }
      var perime = brouillon.b[0] !== c.w.defaultValue ||
                   brouillon.b[1] !== c.r.defaultValue;
      if (perime) {
        /* Le serveur a bougé depuis la saisie — un POST réussi, une
           correction depuis un autre onglet. La vérité serveur gagne
           toujours, sans exception et sans question. */
        try { store.removeItem(cle); } catch (e) { /* rien à faire */ }
        continue;
      }
      /* Champs masqués : la série n'est pas en saisie. On garde l'entrée
         sans rien peindre. */
      if (c.w.type === "hidden" || c.r.type === "hidden") {
        continue;
      }
      c.w.value = brouillon.w;
      c.r.value = brouillon.r;
      /* ⚠ ON NE DÉCLENCHE AUCUN ÉVÉNEMENT. Un `change` synthétique ici
         réveillerait l'auto-validation de `DF-B` et SOUMETTRAIT la série :
         une récupération d'affichage deviendrait un événement de domaine,
         exactement ce que cette tranche a pour mandat d'éviter. */
    }
  }

  function initBrouillons() {
    var store = _ss();
    if (!store) {
      return;
    }
    var form = document.querySelector("[data-session-form]");
    if (!form) {
      return;
    }
    restaurerBrouillons(store, form);

    var ligne = _ligneCourante(form);
    if (!ligne) {
      return;
    }
    var setId = _setIdDe(ligne);
    if (!setId) {
      return;
    }
    var c = _champs(form, setId);
    if (!c.w || !c.r || c.w.type === "hidden") {
      return;
    }
    /* ON ÉCRIT À LA FRAPPE, PAS À LA SORTIE DE PAGE.
       `unload` / `beforeunload` ne se déclenchent pas de façon fiable sur
       mobile : un onglet évincé par l'OS ne les voit jamais. La charge est
       minuscule, l'écrire à chaque frappe coûte moins qu'un mécanisme qui
       rate. `visibilitychange` reste un filet, jamais l'unique occasion. */
    function sauver() {
      sauverBrouillon(store, form, setId);
    }
    c.w.addEventListener("input", sauver);
    c.r.addEventListener("input", sauver);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) {
        sauver();
      }
    });
  }

  /* LA DÉCONNEXION EMPORTE LES BROUILLONS.
     Portée honnête : ce module ne tourne que sur la console de séance,
     donc ce nettoyage couvre la déconnexion DEPUIS cette surface. Ailleurs,
     l'isolation reste structurelle — le stockage meurt avec l'onglet, et un
     autre compte ne peut pas rendre la séance, donc ne peut jamais lire
     l'entrée. Les pages d'authentification portent un contrat « aucun
     script » qu'une garde épingle : on ne l'ouvre pas pour ça. */
  function initPurgeDeconnexion() {
    var store = _ss();
    if (!store) {
      return;
    }
    var formes = document.querySelectorAll('form[action$="/logout"]');
    for (var i = 0; i < formes.length; i++) {
      formes[i].addEventListener("submit", function () {
        var aJeter = [];
        for (var j = 0; j < store.length; j++) {
          var k = store.key(j);
          if (k && k.indexOf(PREFIXE) === 0) {
            aJeter.push(k);
          }
        }
        for (var m = 0; m < aJeter.length; m++) {
          try { store.removeItem(aJeter[m]); } catch (e) { /* rien à faire */ }
        }
      });
    }
  }

  function init() {
    /* `UI-CP8I` — avant tout le reste : une valeur récupérée doit être
       visible dès le premier rendu. */
    initBrouillons();
    initPurgeDeconnexion();

    /* `UI-CP8R` — LA RACINE EST `[data-rest-remaining]`.

       C'était `[data-rest-started]`, un drapeau booléen posé depuis
       `?rest=1`. Il répondait « oui il y a un repos », jamais « depuis
       quand ». L'attribut qui le remplace porte la réponse dérivée par le
       serveur, donc il sert à la fois de déclencheur ET d'origine — un seul
       attribut, une seule source. */
    /* `DF-B` — l'auto-validation ne dépend PAS du repos : elle vit sur la
       série courante, c'est-à-dire précisément quand il n'y a pas de repos.
       La brancher après le `return` ci-dessous l'aurait rendue inopérante
       dans le seul état où elle sert. */
    initAutoCommit();

    var roots = document.querySelectorAll("[data-rest-remaining]");
    if (!roots || roots.length === 0) {
      return;   /* aucune racine : rien à faire, et surtout aucune erreur */
    }
    for (var i = 0; i < roots.length; i++) {
      startTimer(roots[i]);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
