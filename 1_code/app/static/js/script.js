document.addEventListener("DOMContentLoaded", () => {

  // ── Edit meal form → PATCH ────────────────────────────────────────────────
  const editForm = document.getElementById("edit-meal-form");
  if (editForm) {
    editForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(editForm));
      try {
        const res = await fetch(editForm.action, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        const json = await res.json();
        if (!res.ok) {
          showAlert(editForm, json.message || "Failed to update meal.", "danger");
        } else {
          window.location.href = json.redirect;
        }
      } catch {
        showAlert(editForm, "Network error. Please try again.", "danger");
      }
    });
  }

  // ── Delete buttons → DELETE ───────────────────────────────────────────────
  document.querySelectorAll(".delete-meal-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this meal?")) return;
      const url = btn.dataset.url;
      try {
        const res = await fetch(url, { method: "DELETE" });
        const json = await res.json();
        if (json.redirect) window.location.href = json.redirect;
      } catch {
        alert("Network error. Could not delete meal.");
      }
    });
  });

  // ── Nutrition auto-suggest ────────────────────────────────────────────────
  const foodNameInput   = document.getElementById("food_name");
  const suggestionBox   = document.getElementById("nutrition-suggestions");
  const servingSection  = document.getElementById("serving-section");
  const servingGrams    = document.getElementById("serving-grams");

  if (!foodNameInput || !suggestionBox) return;

  let debounceTimer = null;
  let selectedFood  = null;
  let lastQuery     = "";

  foodNameInput.addEventListener("input", () => {
    const q = foodNameInput.value.trim();
    clearTimeout(debounceTimer);

    if (q.length < 2) {
      hideSuggestions();
      return;
    }

    if (q === lastQuery) return;

    debounceTimer = setTimeout(() => doSearch(q), 650);
  });

  async function doSearch(q) {
    lastQuery = q;
    showLoading();

    try {
      const res  = await fetch(`/api/nutrition?query=${encodeURIComponent(q)}`);
      const json = await res.json();

      if (lastQuery !== q) return; // stale result

      if (!res.ok || json.error) {
        showError(json.error || "No results found.");
      } else {
        renderSuggestions(json.results);
      }
    } catch {
      showError("Network error — check your connection.");
    }
  }

  function renderSuggestions(results) {
    suggestionBox.innerHTML = "";
    suggestionBox.style.display = "block";

    const hdr = document.createElement("p");
    hdr.className = "nutrition-suggest-hdr";
    hdr.textContent = "Found in nutrition database — select to auto-fill:";
    suggestionBox.appendChild(hdr);

    results.forEach((item) => {
      const row = document.createElement("div");
      row.className = "nutrition-suggest-row";

      const info = document.createElement("div");
      info.className = "nutrition-suggest-info";
      info.innerHTML =
        `<span class="nutrition-suggest-name">${item.name}</span>` +
        `<span class="nutrition-suggest-macro">${item.calories} kcal &nbsp;·&nbsp; ${item.protein_g}g protein &nbsp;·&nbsp; ${item.carbohydrates_total_g}g carbs &nbsp;·&nbsp; ${item.fat_total_g}g fat <em>(per 100g)</em></span>`;

      const useBtn = document.createElement("button");
      useBtn.type = "button";
      useBtn.className = "nutrition-use-btn";
      useBtn.textContent = "Use →";
      useBtn.addEventListener("click", () => selectFood(item));

      row.appendChild(info);
      row.appendChild(useBtn);
      suggestionBox.appendChild(row);
    });
  }

  function selectFood(item) {
    selectedFood = item;
    foodNameInput.value = item.name;
    lastQuery = item.name;
    hideSuggestions();

    // Show serving section
    if (servingSection) {
      servingSection.style.display = "flex";
      if (servingGrams) {
        servingGrams.value = 100;
        servingGrams.addEventListener("input", applyNutrition);
      }
    }
    applyNutrition();
  }

  function applyNutrition() {
    if (!selectedFood) return;
    const grams = parseFloat(servingGrams?.value) || 100;
    const f     = grams / 100;
    const cal   = Math.round(selectedFood.calories * f);
    const prot  = Math.round(selectedFood.protein_g * f * 10) / 10;
    const carb  = Math.round(selectedFood.carbohydrates_total_g * f * 10) / 10;
    const fat   = Math.round(selectedFood.fat_total_g * f * 10) / 10;

    setValue("calories", cal);
    setValue("protein",  prot);
    setValue("carbs",    carb);
    setValue("fats",     fat);

    const banner = document.getElementById("nutrition-applied-banner");
    if (banner) {
      banner.textContent = `✔ ${selectedFood.name} — ${grams}g: ${cal} kcal · ${prot}g protein · ${carb}g carbs · ${fat}g fat`;
      banner.style.display = "block";
    }
  }

  function setValue(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val;
  }

  function showLoading() {
    suggestionBox.style.display = "block";
    suggestionBox.innerHTML = `<p class="nutrition-suggest-hdr" style="color:#888;">🔍 Searching nutrition database…</p>`;
  }

  function showError(msg) {
    suggestionBox.style.display = "block";
    suggestionBox.innerHTML = `<p class="nutrition-suggest-hdr" style="color:#c0392b;">${msg}</p>`;
  }

  function hideSuggestions() {
    if (suggestionBox) {
      suggestionBox.style.display = "none";
      suggestionBox.innerHTML = "";
    }
  }

  // Hide suggestions when clicking outside
  document.addEventListener("click", (e) => {
    if (!foodNameInput.contains(e.target) && !suggestionBox.contains(e.target)) {
      hideSuggestions();
    }
  });

  // ── showAlert helper ──────────────────────────────────────────────────────
  function showAlert(form, message, type) {
    const existing = form.querySelector(".js-alert");
    if (existing) existing.remove();
    const div = document.createElement("div");
    div.className = `alert alert-${type} alert-dismissible fade show js-alert`;
    div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    form.prepend(div);
  }

});
