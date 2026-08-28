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
 * LE CONTRAT MAINTENANT
 * ---------------------
 * - Le décompte ne démarre QUE si le serveur a posé `data-rest-started`.
 * - `±15 s` ajuste l'affichage, **rien n'est persisté** : la durée est un
 *   repli de présentation, pas une prescription (amendement C).
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

  function parseDuration(el) {
    var n = parseInt(el.getAttribute("data-rest-duration"), 10);
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

    var deadline = Date.now() + parseDuration(root) * 1000;
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
          form.requestSubmit(submitter);
        }

        fields.weight.addEventListener("keydown", onKey);
        fields.reps.addEventListener("keydown", onKey);
      })(forms[i]);
    }
  }

  function init() {
    /* LA CORRECTION : `data-rest-started` — posé par le serveur uniquement
       après une série réellement enregistrée — et non `[data-start-rest]`,
       qui était rendu sur toute carte active. */
    /* `DF-B` — l'auto-validation ne dépend PAS du repos : elle vit sur la
       série courante, c'est-à-dire précisément quand il n'y a pas de repos.
       La brancher après le `return` ci-dessous l'aurait rendue inopérante
       dans le seul état où elle sert. */
    initAutoCommit();

    var roots = document.querySelectorAll("[data-rest-started]");
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
