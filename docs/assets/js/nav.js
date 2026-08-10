(function(){
  var sidebar = document.querySelector(".pf-v6-c-page__sidebar");
  var toggle = document.getElementById("sidebar-toggle");
  var sectionToggles = document.querySelectorAll(".nav-section-toggle");

  // Mobile sidebar toggle
  if (toggle && sidebar) {
    toggle.addEventListener("click", function() {
      var open = sidebar.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    document.addEventListener("click", function(e) {
      if (sidebar.classList.contains("is-open") &&
          !sidebar.contains(e.target) &&
          !toggle.contains(e.target)) {
        sidebar.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // Expandable nav sections
  Array.prototype.forEach.call(sectionToggles, function(btn) {
    var items = btn.nextElementSibling;
    if (!items) return;

    var hasActivePage = items.querySelector(".pf-m-current");
    if (hasActivePage) {
      btn.setAttribute("aria-expanded", "true");
      items.removeAttribute("hidden");
    }

    btn.addEventListener("click", function() {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", expanded ? "false" : "true");
      if (expanded) {
        items.setAttribute("hidden", "");
      } else {
        items.removeAttribute("hidden");
      }
    });
  });

  // Active page highlighting — mark parent section as expanded
  var currentLink = document.querySelector(".pf-v6-c-nav__link.pf-m-current");
  if (currentLink) {
    var parentSection = currentLink.closest(".pf-v6-c-nav__section");
    if (parentSection) {
      var parentBtn = parentSection.querySelector(".nav-section-toggle");
      var parentItems = parentSection.querySelector(".nav-section-items");
      if (parentBtn && parentItems) {
        parentBtn.setAttribute("aria-expanded", "true");
        parentItems.removeAttribute("hidden");
      }
    }
  }
})();
