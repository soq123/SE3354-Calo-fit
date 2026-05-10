from statistics import mean


MOOD_NUTRITION_LINKS = {
    "Happy": [],
    "Focused": ["protein", "calories"],
    "Neutral": ["calories", "fiber"],
    "Tired": ["calories", "carbs", "protein", "iron"],
    "Stressed": ["protein", "fats", "magnesium"],
}

FOOD_LIBRARY = {
    "calories": [
        {"name": "Chicken rice bowl", "why": "balanced calories with protein and carbs", "meal_type": "Lunch", "calories": 520},
        {"name": "Peanut butter banana toast", "why": "quick energy-dense snack", "meal_type": "Snack", "calories": 360},
        {"name": "Oat smoothie", "why": "easy calories when intake is low", "meal_type": "Breakfast", "calories": 410},
    ],
    "protein": [
        {"name": "Greek yogurt with berries", "why": "high protein and easy to log", "meal_type": "Snack", "calories": 220},
        {"name": "Egg and veggie wrap", "why": "protein plus steady energy", "meal_type": "Breakfast", "calories": 390},
        {"name": "Chicken breast bowl", "why": "lean protein for daily target", "meal_type": "Lunch", "calories": 480},
    ],
    "carbs": [
        {"name": "Oatmeal with banana", "why": "carbs for low-energy days", "meal_type": "Breakfast", "calories": 340},
        {"name": "Rice bowl", "why": "simple carbs to refill energy", "meal_type": "Lunch", "calories": 460},
        {"name": "Whole grain toast", "why": "lighter carb option", "meal_type": "Snack", "calories": 180},
    ],
    "fats": [
        {"name": "Avocado toast", "why": "healthy fats and fiber", "meal_type": "Breakfast", "calories": 330},
        {"name": "Salmon with potatoes", "why": "healthy fats plus protein", "meal_type": "Dinner", "calories": 560},
        {"name": "Mixed nuts", "why": "small snack with healthy fats", "meal_type": "Snack", "calories": 200},
    ],
    "fiber": [
        {"name": "Beans and rice", "why": "fiber-rich balanced meal", "meal_type": "Lunch", "calories": 450},
        {"name": "Berry yogurt bowl", "why": "fiber with protein", "meal_type": "Breakfast", "calories": 300},
        {"name": "Vegetable wrap", "why": "adds volume and micronutrients", "meal_type": "Lunch", "calories": 380},
    ],
    "iron": [
        {"name": "Turkey spinach wrap", "why": "iron-supporting meal for tired days", "meal_type": "Lunch", "calories": 430},
        {"name": "Lean beef rice bowl", "why": "iron and protein support", "meal_type": "Dinner", "calories": 570},
        {"name": "Eggs with spinach", "why": "lighter iron-supporting option", "meal_type": "Breakfast", "calories": 310},
    ],
    "magnesium": [
        {"name": "Banana peanut butter oatmeal", "why": "stress-friendly carb and mineral support", "meal_type": "Breakfast", "calories": 420},
        {"name": "Trail mix", "why": "quick snack with nuts and seeds", "meal_type": "Snack", "calories": 250},
        {"name": "Black bean bowl", "why": "fiber and mineral support", "meal_type": "Lunch", "calories": 440},
    ],
}

MICRO_TARGETS = {
    "iron": 8,
    "zinc": 11,
    "calcium": 1000,
}


def _as_float(value, default=0.0):
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _safe_round(value):
    return round(_as_float(value), 1)


def _macro_targets_from_calorie_goal(calorie_goal):
    """Estimate daily macro targets from the user's calorie goal.

    Uses a simple 20/45/30 protein/carbs/fats split so the recommendation
    engine responds to each user's goal instead of using one fixed target.
    """
    goal = max(_as_float(calorie_goal, 2000), 1)
    return {
        "protein": round((goal * 0.20) / 4, 1),
        "carbs": round((goal * 0.45) / 4, 1),
        "fats": round((goal * 0.30) / 9, 1),
    }


def analyze_macro_deficiencies(macros, calorie_goal, consumed):
    targets = _macro_targets_from_calorie_goal(calorie_goal)
    consumed = _as_float(consumed)

    current = {
        "protein": _as_float(macros.get("total_protein")),
        "carbs": _as_float(macros.get("total_carbs")),
        "fats": _as_float(macros.get("total_fats")),
        "iron": _as_float(macros.get("total_iron")),
        "zinc": _as_float(macros.get("total_zinc")),
        "calcium": _as_float(macros.get("total_calcium")),
    }

    deficiencies = []
    details = []

    if consumed < _as_float(calorie_goal) * 0.75:
        deficiencies.append("calories")
        details.append("calories are below 75% of today's goal")

    for key, target in targets.items():
        if current[key] < target * 0.70:
            deficiencies.append(key)
            details.append(f"{key} is below 70% of the estimated target")

    # Micronutrients are optional in meal logs, so use a softer threshold.
    for key, target in MICRO_TARGETS.items():
        if current[key] > 0 and current[key] < target * 0.35:
            deficiencies.append(key)
            details.append(f"{key} appears low based on logged micronutrients")

    if current["carbs"] < targets["carbs"] * 0.65 and current["protein"] < targets["protein"] * 0.65:
        deficiencies.append("fiber")
        details.append("fiber-rich foods may help balance low carb/protein intake")

    return list(dict.fromkeys(deficiencies)), details, targets


def mood_based_deficiencies(mood_entry):
    if not mood_entry:
        return [], []

    mood_name = mood_entry.get("mood")
    energy_level = int(mood_entry.get("energy_level") or 3)

    linked = list(MOOD_NUTRITION_LINKS.get(mood_name, []))
    reasons = []

    if linked:
        reasons.append(f"{mood_name} mood can be supported with {', '.join(linked)} focused choices")

    if energy_level <= 2:
        linked.extend(["calories", "carbs", "iron"])
        reasons.append("low energy score adds extra focus on calories, carbs, and iron-supporting foods")
    elif energy_level >= 4 and mood_name in ("Happy", "Focused"):
        reasons.append("energy looks good, so suggestions stay balanced and maintenance-focused")

    return list(dict.fromkeys(linked)), reasons


def _build_food_recommendations(flags, remaining_calories):
    remaining = _as_float(remaining_calories)
    seen = set()
    results = []

    for flag in flags:
        for food in FOOD_LIBRARY.get(flag, []):
            name = food["name"]
            if name in seen:
                continue

            seen.add(name)
            suggestion = dict(food)
            suggestion["reason_tag"] = flag.title()

            if remaining > 0:
                if suggestion["calories"] <= remaining + 150:
                    suggestion["fit_note"] = "Fits today's remaining calories"
                else:
                    suggestion["fit_note"] = "Use a smaller portion today"
            else:
                suggestion["fit_note"] = "Save for tomorrow or choose a light portion"

            results.append(suggestion)

            if len(results) == 6:
                return results

    return results


def generate_recommendations(macros, calorie_goal, consumed, mood_entry=None):
    macro_flags, macro_reasons, targets = analyze_macro_deficiencies(
        macros,
        calorie_goal,
        consumed,
    )

    mood_flags, mood_reasons = mood_based_deficiencies(mood_entry)
    all_flags = list(dict.fromkeys(macro_flags + mood_flags))

    if not all_flags:
        all_flags = ["fiber"]

    remaining_calories = _as_float(calorie_goal) - _as_float(consumed)
    items = _build_food_recommendations(all_flags, remaining_calories)

    if not items:
        items = [
            {
                "name": "Balanced plate with lean protein, whole grains, and vegetables",
                "why": "keeps intake steady without targeting a major gap",
                "meal_type": "Any",
                "calories": 450,
                "reason_tag": "Balance",
                "fit_note": "Adjust portion to your goal",
            }
        ]

    if macro_flags:
        message = "Detected nutrition focus areas: " + ", ".join(flag.title() for flag in macro_flags) + "."
    else:
        message = "Today's logged nutrition is close to target, so suggestions focus on balance."

    if mood_reasons:
        message += " " + " ".join(mood_reasons) + "."

    return {
        "deficiencies": all_flags,
        "macro_reasons": macro_reasons,
        "mood_reasons": mood_reasons,
        "targets": targets,
        "message": message,
        "items": items,
        "foods": [item["name"] for item in items],
    }


def summarize_weekly_moods(mood_rows, top_moods=None):
    if not mood_rows:
        return {
            "top_mood": "No mood data",
            "avg_energy": 0,
            "entries": 0,
        }

    top_mood = top_moods[0]["mood"] if top_moods else "No mood data"

    avg_energy_values = [
        float(row["avg_energy"])
        for row in mood_rows
        if row.get("avg_energy") is not None
    ]

    return {
        "top_mood": top_mood,
        "avg_energy": _safe_round(mean(avg_energy_values) if avg_energy_values else 0),
        "entries": sum(int(row.get("entry_count", 0) or 0) for row in mood_rows),
    }