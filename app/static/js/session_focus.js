/* Sb_29.4 — Rest timer (progressive enhancement).
 *
 * Contrat verbatim Sb_29.4 :
 * - JS vanilla uniquement (aucun import, aucun framework, aucun bundler).
 * - Aucune requête réseau.
 * - Aucune action critique ne dépend de ce JS (no-JS fallback intégral).
 * - Lecture des éléments via data-start-rest / data-rest-duration.
 * - Countdown 90s par défaut si aucune durée valide.
 * - setInterval avec cleanup propre (clearInterval) à 0 ou sur skip.
 * - Bouton skip via data-rest-skip.
 * - Respect prefers-reduced-motion (pas d'animation introduite).
 * - Aucune erreur si aucun timer DOM présent.
 */
(function () {
  "use strict";

  var DEFAULT_REST_SECONDS = 90;

  function parseDuration(el) {
    var raw =
      el.getAttribute("data-rest-duration") ||
      el.getAttribute("data-start-rest");
    var n = parseInt(raw, 10);
    if (!isFinite(n) || n <= 0) {
      return DEFAULT_REST_SECONDS;
    }
    return n;
  }

  function format(seconds) {
    if (seconds <= 0) {
      return "Repos terminé";
    }
    return seconds + "s";
  }

  function startTimer(root) {
    var display = root.querySelector("[data-rest-display]");
    if (!display) {
      return;
    }
    var remaining = parseDuration(root);
    display.textContent = format(remaining);
    root.classList.add("session-focus__rest-timer--running");

    var intervalId = null;

    function stop() {
      if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
      }
      root.classList.remove("session-focus__rest-timer--running");
      root.classList.add("session-focus__rest-timer--done");
    }

    function tick() {
      remaining -= 1;
      if (remaining <= 0) {
        display.textContent = format(0);
        stop();
        return;
      }
      display.textContent = format(remaining);
    }

    intervalId = setInterval(tick, 1000);

    var skipBtn = root.querySelector("[data-rest-skip]");
    if (skipBtn) {
      skipBtn.addEventListener("click", function (ev) {
        ev.preventDefault();
        remaining = 0;
        display.textContent = format(0);
        stop();
      });
    }
  }

  function init() {
    var roots = document.querySelectorAll("[data-start-rest]");
    if (!roots || roots.length === 0) {
      return;
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
