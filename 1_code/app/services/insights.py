from statistics import mean


MOOD_DEFICIENCY_MAP = {
    "Tired": ["calories", "carbs", "protein"],
    "Low Energy": ["calories", "carbs", "protein"],
    "Stressed": ["protein", "fats"],
    "Neutral": ["calories"],
    "Focused": [],
    "Happy": [],
}


FOOD_LIBRARY = {
    "protein": [
        "Greek yogurt",
        "Eggs",
        "Chicken breast",
        "Turkey wrap",
    ],
    "carbs": [
        "Oatmeal",
        "Rice bowl",
        "Whole grain toast",
        "Banana",
    ],
    "fats": [
        "Avocado toast",
        "Salmon",
        "Peanut butter",
        "Mixed nuts",
    ],
    "calories": [
        "Chicken rice bowl",
        "Peanut butter sandwich",
        "Smoothie with oats",
        "Salmon with potatoes",
    ],
    "fiber": [
        "Apple with oats",
        "Beans and rice",
        "Berry yogurt bowl",
        "Vegetable wrap",
    ],
}


TARGET_MACROS = {
    "protein": 100,
    "carbs": 225,
    "fats": 65,
}


def _safe_round(value):
    return round(float(value), 1) if value is not None else 0.0


def analyze_macro_deficiencies(macros, calorie_goal, consumed):
    deficiencies = []
    protein = float(macros.get("total_protein", 0) or 0)
    carbs = float(macros.get("total_carbs", 0) or 0)
    fats = float(macros.get("total_fats", 0) or 0)

    if consumed < calorie_goal * 0.75:
        deficiencies.append("calories")
    if protein < TARGET_MACROS["protein"] * 0.7:
        deficiencies.append("protein")
    if carbs < TARGET_MACROS["carbs"] * 0.7:
        deficiencies.append("carbs")
    if fats < TARGET_MACROS["fats"] * 0.7:
        deficiencies.append("fats")
    if carbs < TARGET_MACROS["carbs"] * 0.65 and protein < TARGET_MACROS["protein"] * 0.65:
        deficiencies.append("fiber")

    return list(dict.fromkeys(deficiencies))


def mood_based_deficiencies(mood_name):
    if not mood_name:
        return []
    return MOOD_DEFICIENCY_MAP.get(mood_name, [])


def generate_recommendations(macros, calorie_goal, consumed, mood_entry=None):
    deficiencies = analyze_macro_deficiencies(macros, calorie_goal, consumed)
    mood_name = mood_entry.get("mood") if mood_entry else None
    linked = mood_based_deficiencies(mood_name)
    all_flags = list(dict.fromkeys(deficiencies + linked))

    suggested_foods = []
    for flag in all_flags:
        suggested_foods.extend(FOOD_LIBRARY.get(flag, []))

    if not suggested_foods:
        suggested_foods = ["Keep your current meal pattern going", "Add fruit or vegetables for balance"]

    messages = []
    if deficiencies:
        messages.append(
            "Possible intake gaps: " + ", ".join(flag.title() for flag in deficiencies) + "."
        )
    else:
        messages.append("Your intake is close to target for today.")

    if linked:
        messages.append(
            f"Your most recent mood ({mood_name}) is often associated with lower "
            + ", ".join(flag.title() for flag in linked)
            + "."
        )

    return {
        "deficiencies": all_flags,
        "message": " ".join(messages),
        "foods": list(dict.fromkeys(suggested_foods))[:6],
    }


def summarize_weekly_moods(mood_rows, top_moods=None):
    if not mood_rows:
        return {
            "top_mood": "No mood data",
            "avg_energy": 0,
            "entries": 0,
        }

    top_mood = top_moods[0]["mood"] if top_moods else "No mood data"
    avg_energy_values = [float(row["avg_energy"]) for row in mood_rows if row.get("avg_energy") is not None]
    return {
        "top_mood": top_mood,
        "avg_energy": _safe_round(mean(avg_energy_values) if avg_energy_values else 0),
        "entries": sum(int(row.get("entry_count", 0) or 0) for row in mood_rows),
    }
