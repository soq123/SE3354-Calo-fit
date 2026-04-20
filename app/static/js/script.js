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

  // ── Nutrition lookup ──────────────────────────────────────────────────────
  const lookupBtn = document.getElementById("nutrition-lookup-btn");
  const foodNameInput = document.getElementById("food_name");
  const nutritionFeedback = document.getElementById("nutrition-feedback");
  const nutritionResults = document.getElementById("nutrition-results");

  if (lookupBtn && foodNameInput) {
    lookupBtn.addEventListener("click", async () => {
      const query = foodNameInput.value.trim();
      if (!query) {
        setFeedback("Enter a food name first.", "text-warning");
        return;
      }

      lookupBtn.disabled = true;
      lookupBtn.textContent = "Looking up…";
      setFeedback("", "");
      clearResults();

      try {
        const res = await fetch(`/api/nutrition?query=${encodeURIComponent(query)}`);
        const json = await res.json();

        if (!res.ok || json.error) {
          setFeedback(json.error || "No data found.", "text-danger");
        } else {
          setFeedback("Select a result to auto-fill nutrition info:", "text-muted");
          renderResults(json.results);
        }
      } catch {
        setFeedback("Network error. Could not fetch nutrition data.", "text-danger");
      } finally {
        lookupBtn.disabled = false;
        lookupBtn.textContent = "Lookup Nutrition";
      }
    });
  }

  let selectedFood = null; // stores per-100g base values of the chosen result

  function renderResults(results) {
    if (!nutritionResults) return;
    nutritionResults.innerHTML = "";

    // Serving size row (persists after result selection)
    const servingRow = document.createElement("div");
    servingRow.className = "d-flex align-items-center gap-2 mb-2";
    servingRow.innerHTML =
      `<span class="small text-muted">Serving size:</span>
       <input id="serving-grams" type="number" class="form-control form-control-sm"
              style="width:75px" value="100" min="1" step="1">
       <span class="small text-muted">g &nbsp;(USDA values are per 100g)</span>`;
    nutritionResults.appendChild(servingRow);

    // Result buttons
    const btnWrap = document.createElement("div");
    btnWrap.id = "nutrition-result-btns";
    results.forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-sm btn-outline-primary me-1 mb-1";
      btn.title = `Per 100g: ${item.calories} kcal | ${item.protein_g}g protein | ${item.carbohydrates_total_g}g carbs | ${item.fat_total_g}g fat`;
      btn.textContent = item.name;
      btn.addEventListener("click", () => {
        selectedFood = item;
        applyNutrition();
        // Remove result buttons; keep serving input for live adjustment
        document.getElementById("nutrition-result-btns")?.remove();
        const label = document.createElement("p");
        label.id = "selected-food-label";
        label.className = "small text-muted mb-0 mt-1";
        label.textContent = `Selected: ${item.name}`;
        nutritionResults.appendChild(label);
      });
      btnWrap.appendChild(btn);
    });
    nutritionResults.appendChild(btnWrap);

    // Live recalculate when serving size changes
    document.getElementById("serving-grams").addEventListener("input", () => {
      if (selectedFood) applyNutrition();
    });
  }

  function applyNutrition() {
    const grams = parseFloat(document.getElementById("serving-grams")?.value) || 100;
    const f = grams / 100;
    const cal  = Math.round(selectedFood.calories * f);
    const prot = Math.round(selectedFood.protein_g * f * 10) / 10;
    const carb = Math.round(selectedFood.carbohydrates_total_g * f * 10) / 10;
    const fat  = Math.round(selectedFood.fat_total_g * f * 10) / 10;

    document.getElementById("calories").value = cal;
    document.getElementById("protein").value  = prot;
    document.getElementById("carbs").value    = carb;
    document.getElementById("fats").value     = fat;

    setFeedback(
      `✓ ${selectedFood.name} — ${grams}g: ${cal} kcal | ${prot}g protein | ${carb}g carbs | ${fat}g fat`,
      "text-success"
    );
  }

  function clearResults() {
    if (nutritionResults) nutritionResults.innerHTML = "";
    selectedFood = null;
  }

  function setFeedback(msg, cls) {
    if (!nutritionFeedback) return;
    nutritionFeedback.textContent = msg;
    nutritionFeedback.className = `small mt-1 ${cls}`;
  }

  function showAlert(form, message, type) {
    const existing = form.querySelector(".js-alert");
    if (existing) existing.remove();
    const div = document.createElement("div");
    div.className = `alert alert-${type} alert-dismissible fade show js-alert`;
    div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    form.prepend(div);
  }

});
