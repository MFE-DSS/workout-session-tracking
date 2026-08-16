/* Sb_UI_PROFILE_PREFERENCES_REDESIGN_01 — classement des priorités.
 *
 * Ce script ne fait QUE de la synchronisation présentation ↔ input. Il ne
 * valide rien, ne persiste rien, n'invente aucune valeur.
 *
 * **Les trois <select> natifs restent la source de vérité.** Ils sont dans le
 * DOM, ils portent les noms `focus_1`, `focus_2`, `focus_3`, et ce sont eux
 * qui partent dans le POST. Le bloc classé écrit dedans, rien de plus — le
 * corps de la requête est donc rigoureusement identique avec ou sans JS.
 *
 * Sans JS : le bloc classé reste `hidden`, les <select> restent visibles et
 * pleinement fonctionnels. Enregistrer ses préférences n'exige jamais JS.
 *
 * Aucun framework, aucun bundler, aucune dépendance. Pas de glisser-déposer :
 * cliquer assigne le rang libre suivant, recliquer retire et recompacte.
 */
(function () {
  "use strict";

  var MAX_RANKS = 3;

  function init(form) {
    var ranked = form.querySelector("[data-prefs-ranked]");
    var fallback = form.querySelector("[data-prefs-fallback]");
    if (!ranked || !fallback) return;

    var selects = [];
    for (var i = 1; i <= MAX_RANKS; i++) {
      var el = form.querySelector('select[name="focus_' + i + '"]');
      if (!el) return; // contrat inattendu : on laisse le fallback natif seul
      selects.push(el);
    }

    var buttons = Array.prototype.slice.call(
      ranked.querySelectorAll("[data-focus-key]")
    );

    // L'ordre courant est LU depuis les selects, pas depuis un état parallèle :
    // le rendu serveur reste la seule origine de l'état initial.
    function currentOrder() {
      var out = [];
      selects.forEach(function (sel) {
        if (sel.value && out.indexOf(sel.value) === -1) out.push(sel.value);
      });
      return out;
    }

    function writeOrder(order) {
      selects.forEach(function (sel, index) {
        sel.value = order[index] || "";
      });
    }

    function paint() {
      var order = currentOrder();
      buttons.forEach(function (btn) {
        var key = btn.getAttribute("data-focus-key");
        var position = order.indexOf(key);
        var selected = position !== -1;
        var rank = btn.querySelector("[data-focus-rank]");

        btn.setAttribute("aria-pressed", selected ? "true" : "false");
        if (rank) rank.textContent = selected ? "0" + (position + 1) : "";
        // Une fois trois priorités choisies, les autres deviennent réellement
        // inopérantes — pas seulement grisées.
        btn.disabled = !selected && order.length >= MAX_RANKS;
      });
    }

    function toggle(key) {
      var order = currentOrder();
      var at = order.indexOf(key);
      if (at !== -1) {
        order.splice(at, 1); // retrait → les rangs suivants se recompactent
      } else if (order.length < MAX_RANKS) {
        order.push(key);
      }
      writeOrder(order);
      paint();
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        toggle(btn.getAttribute("data-focus-key"));
      });
    });

    // Le fallback n'est masqué qu'une fois l'amélioration réellement câblée.
    fallback.hidden = true;
    ranked.hidden = false;
    paint();
  }

  function boot() {
    Array.prototype.forEach.call(
      document.querySelectorAll("[data-prefs-form]"),
      init
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
