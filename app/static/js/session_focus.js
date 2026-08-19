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

  function startTimer(root) {
    var display = root.querySelector("[data-rest-display]");
    if (!display) {
      return;
    }

    var remaining = parseDuration(root);
    var intervalId = null;

    function paint() {
      display.textContent = format(remaining);
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

    function tick() {
      remaining -= 1;
      if (remaining <= 0) {
        remaining = 0;
        paint();
        stop(true);
        return;
      }
      paint();
    }

    function adjust(delta) {
      remaining = Math.min(CEILING_SECONDS,
                           Math.max(FLOOR_SECONDS, remaining + delta));
      paint();
      if (remaining === 0) {
        stop(true);
      }
    }

    paint();
    root.classList.add("session-focus__rest-timer--running");
    intervalId = setInterval(tick, 1000);

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

  function init() {
    /* LA CORRECTION : `data-rest-started` — posé par le serveur uniquement
       après une série réellement enregistrée — et non `[data-start-rest]`,
       qui était rendu sur toute carte active. */
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
