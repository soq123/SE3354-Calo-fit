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


RECOMMENDATION_REASONS = {
    "calories": "your calorie intake is below your daily goal",
    "protein": "your protein intake is below the target range",
    "carbs": "your carbohydrate intake is below the target range",
    "fats": "your fat intake is below the target range",
    "fiber": "your current intake may need more balanced high-fiber foods",
}


def _safe_round(value):
    return round(float(value), 1) if value is not None else 0.0


def analyze_macro_deficiencies(macros, calorie_goal, consumed):
    deficiencies = []

    protein = float(macros.get("total_protein", 0) or 0)
    carbs = float(macros.get("total_carbs", 0) or 0)
    fats = float(macros.get("total_fats", 0) or 0)
    consumed = float(consumed or 0)
    calorie_goal = float(calorie_goal or 0)

    if calorie_goal > 0 and consumed < calorie_goal * 0.75:
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


def build_recommendation_details(flags):
    details = []

    for flag in flags:
        details.append(
            {
                "category": flag.title(),
                "reason": RECOMMENDATION_REASONS.get(
                    flag,
                    "this area may need attention based on your current log",
                ),
                "foods": FOOD_LIBRARY.get(flag, []),
            }
        )

    return details


def generate_recommendations(macros, calorie_goal, consumed, mood_entry=None):
    macro_flags = analyze_macro_deficiencies(macros, calorie_goal, consumed)

    mood_name = mood_entry.get("mood") if mood_entry else None
    mood_flags = mood_based_deficiencies(mood_name)

    all_flags = list(dict.fromkeys(macro_flags + mood_flags))

    suggested_foods = []
    for flag in all_flags:
        suggested_foods.extend(FOOD_LIBRARY.get(flag, []))

    if not suggested_foods:
        suggested_foods = [
            "Keep your current meal pattern going",
            "Add fruit or vegetables for balance",
        ]

    messages = []

    if macro_flags:
        messages.append(
            "Possible nutrition gaps detected: "
            + ", ".join(flag.title() for flag in macro_flags)
            + "."
        )
    else:
        messages.append("Your logged intake is close to target for today.")

    if mood_flags and mood_name:
        messages.append(
            f"Because you logged {mood_name}, CaloFit also checks patterns related to "
            + ", ".join(flag.title() for flag in mood_flags)
            + "."
        )

    if all_flags:
        messages.append("Suggested foods are chosen to help support those areas.")

    return {
        "deficiencies": all_flags,
        "macro_flags": macro_flags,
        "mood_flags": mood_flags,
        "message": " ".join(messages),
        "foods": list(dict.fromkeys(suggested_foods))[:6],
        "details": build_recommendation_details(all_flags),
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
