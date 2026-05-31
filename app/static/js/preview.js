/* Sb_22b — L2 preview card binding.
 *
 * Spec §A.bis v2.1 pattern preview-vs-clic :
 *   - Desktop hover sur .lb-row__name-link → preview après 200ms
 *   - Mobile : 1er tap → preview ; 2ème tap → navigation /users/{X}
 *   - Échap ou clic dehors ferme la preview
 *
 * SSR-first : aucune dépendance, fetch natif, ~80 lignes.
 * Fallback graceful : si le fetch échoue, le clic suit le href natif.
 */
(function () {
  "use strict";

  if (typeof document === "undefined") return;

  var portal = null;
  var hoverTimer = null;
  var currentLink = null;
  var primedLink = null; // mobile : link "armé" pour 2ème tap = navigation

  function ensurePortal() {
    if (portal) return portal;
    portal = document.createElement("div");
    portal.className = "preview-portal";
    portal.setAttribute("aria-hidden", "true");
    document.body.appendChild(portal);
    return portal;
  }

  function hide() {
    if (!portal) return;
    portal.classList.remove("preview-portal--visible");
    portal.innerHTML = "";
    portal.setAttribute("aria-hidden", "true");
    primedLink = null;
  }

  function positionPortal(link) {
    var rect = link.getBoundingClientRect();
    var top = window.scrollY + rect.bottom + 6;
    var left = window.scrollX + rect.left;
    var maxLeft = window.scrollX + window.innerWidth - 290;
    if (left > maxLeft) left = maxLeft;
    if (left < 8) left = 8;
    portal.style.top = top + "px";
    portal.style.left = left + "px";
  }

  function showPreview(link) {
    var username = link.dataset.previewUser;
    if (!username) return;
    ensurePortal();
    portal.innerHTML = '<div class="card profile-preview" style="opacity:.6">Chargement…</div>';
    positionPortal(link);
    portal.classList.add("preview-portal--visible");
    portal.setAttribute("aria-hidden", "false");

    fetch("/users/" + encodeURIComponent(username) + "/preview", {
      headers: { "Accept": "text/html" },
      credentials: "same-origin",
    })
      .then(function (r) {
        if (!r.ok) throw new Error("preview fetch failed: " + r.status);
        return r.text();
      })
      .then(function (html) {
        portal.innerHTML = html;
        positionPortal(link);
      })
      .catch(function () {
        hide(); // graceful — link click will follow href
      });
  }

  function onMouseEnter(e) {
    var link = e.currentTarget;
    if (hoverTimer) clearTimeout(hoverTimer);
    currentLink = link;
    hoverTimer = setTimeout(function () {
      if (currentLink === link) showPreview(link);
    }, 200);
  }

  function onMouseLeave() {
    if (hoverTimer) clearTimeout(hoverTimer);
    hoverTimer = null;
    currentLink = null;
    // Note: we don't hide on mouseleave — let the user move into the
    // preview itself. A click-outside / Esc closes it.
  }

  function onClick(e) {
    var link = e.currentTarget;
    // Detect mobile touch by absence of hover (or no fine pointer).
    var coarsePointer = window.matchMedia && window.matchMedia("(hover: none)").matches;
    if (!coarsePointer) return; // desktop : click follows native href
    if (primedLink === link) {
      // 2nd tap → navigation : let the default href happen
      primedLink = null;
      return;
    }
    // 1st tap → preview, prevent navigation
    e.preventDefault();
    primedLink = link;
    showPreview(link);
  }

  function onDocumentClick(e) {
    if (!portal || !portal.classList.contains("preview-portal--visible")) return;
    if (portal.contains(e.target)) return;
    var isPreviewLink = e.target.closest && e.target.closest(".lb-row__name-link");
    if (isPreviewLink) return;
    hide();
  }

  function onKeyDown(e) {
    if (e.key === "Escape") hide();
  }

  function init() {
    var links = document.querySelectorAll(".lb-row__name-link[data-preview-user]");
    for (var i = 0; i < links.length; i++) {
      var link = links[i];
      link.addEventListener("mouseenter", onMouseEnter);
      link.addEventListener("mouseleave", onMouseLeave);
      link.addEventListener("click", onClick);
    }
    document.addEventListener("click", onDocumentClick, true);
    document.addEventListener("keydown", onKeyDown);
    window.addEventListener("scroll", hide, { passive: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
