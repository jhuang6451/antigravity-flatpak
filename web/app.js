// Tabs, copy buttons, and the latest release label. The page works without any of it.
(function () {
  "use strict";

  // Tabs
  document.querySelectorAll("[data-tabs]").forEach(function (group) {
    var tabs = Array.prototype.slice.call(group.querySelectorAll('[role="tab"]'));
    function select(tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab); });
      tab.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowRight") next = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowLeft") next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (next) { e.preventDefault(); select(next); next.focus(); }
      });
    });
    select(tabs[0]);
  });

  // Copy buttons
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    var label = btn.querySelector(".copy-label");
    var original = label ? label.textContent : "";
    btn.addEventListener("click", function () {
      var source = document.getElementById(btn.getAttribute("data-copy"));
      if (!source) return;
      var text = source.textContent;
      var done = function () {
        if (!label) return;
        label.textContent = btn.getAttribute("data-copied") || "Copied";
        setTimeout(function () { label.textContent = original; }, 2000);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      }
    });
  });

  // Latest release label
  var target = document.querySelector("[data-version]");
  if (target && window.fetch) {
    fetch("https://api.github.com/repos/jhuang6451/antigravity-flatpak/releases/latest", {
      headers: { Accept: "application/vnd.github+json" }
    })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(function (data) {
        if (data && data.tag_name) {
          target.textContent = data.tag_name;
          target.closest("[data-version-wrap]").hidden = false;
        }
      })
      .catch(function () {});
  }
})();
