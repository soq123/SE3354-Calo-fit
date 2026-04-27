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
      lookupBtn.innerHTML = "⏳ Searching…";
      setFeedback("", "");
      clearResults();

      try {
        const res = await fetch(`/api/nutrition?query=${encodeURIComponent(query)}`);
        const json = await res.json();

        if (!res.ok || json.error) {
          setFeedback(json.error || "No data found.", "text-danger");
        } else {
          setFeedback("Pick a match to auto-fill the nutrition fields:", "text-muted");
          renderResults(json.results);
        }
      } catch {
        setFeedback("Network error. Could not fetch nutrition data.", "text-danger");
      } finally {
        lookupBtn.disabled = false;
        lookupBtn.innerHTML = "🔍 Lookup";
      }
    });
  }

  let selectedFood = null; // stores per-100g base values of the chosen result

  function renderResults(results) {
    if (!nutritionResults) return;
    nutritionResults.innerHTML = "";

    // Serving size row
    const servingRow = document.createElement("div");
    servingRow.className = "d-flex align-items-center gap-2 mb-2";
    servingRow.innerHTML =
      `<span class="small text-muted">Serving size:</span>
       <input id="serving-grams" type="number" class="form-control form-control-sm"
              style="width:75px" value="100" min="1" step="1">
       <span class="small text-muted">g (values are per 100g)</span>`;
    nutritionResults.appendChild(servingRow);

    // Result chips
    const chipWrap = document.createElement("div");
    chipWrap.id = "nutrition-result-btns";
    chipWrap.style.cssText = "display:flex;flex-wrap:wrap;gap:0.4rem;";
    results.forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.style.cssText =
        "border:1.5px solid #3d6b50;background:#f4faf6;color:#3d6b50;border-radius:20px;" +
        "padding:0.25rem 0.8rem;font-size:0.8rem;font-weight:600;cursor:pointer;transition:all 0.15s;";
      btn.title = `Per 100g — Cal: ${item.calories} kcal | Protein: ${item.protein_g}g | Carbs: ${item.carbohydrates_total_g}g | Fat: ${item.fat_total_g}g`;
      btn.textContent = item.name;
      btn.addEventListener("mouseenter", () => { btn.style.background = "#3d6b50"; btn.style.color = "#fff"; });
      btn.addEventListener("mouseleave", () => { btn.style.background = "#f4faf6"; btn.style.color = "#3d6b50"; });
      btn.addEventListener("click", () => {
        selectedFood = item;
        applyNutrition();
        document.getElementById("nutrition-result-btns")?.remove();
        const label = document.createElement("p");
        label.id = "selected-food-label";
        label.className = "small text-muted mb-0 mt-1";
        label.textContent = `✔ Using: ${item.name}`;
        nutritionResults.appendChild(label);
      });
      chipWrap.appendChild(btn);
    });
    nutritionResults.appendChild(chipWrap);

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
