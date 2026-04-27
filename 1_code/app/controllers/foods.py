import os
import requests
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.food_entry import search_food_history

foods_bp = Blueprint("foods", __name__)

# ── Local nutrition database (per 100g) ───────────────────────────────────────
# Macros in g; iron, zinc, calcium in mg.
LOCAL_DB = [
    # ── Fruits ──────────────────────────────────────────────────────────────
    {"name": "Apple, raw",             "calories": 52,  "protein_g": 0.3, "carbohydrates_total_g": 14.0, "fat_total_g": 0.2,  "iron_mg": 0.1, "zinc_mg": 0.0, "calcium_mg": 6},
    {"name": "Banana, raw",            "calories": 89,  "protein_g": 1.1, "carbohydrates_total_g": 23.0, "fat_total_g": 0.3,  "iron_mg": 0.3, "zinc_mg": 0.2, "calcium_mg": 5},
    {"name": "Orange, raw",            "calories": 47,  "protein_g": 0.9, "carbohydrates_total_g": 12.0, "fat_total_g": 0.1,  "iron_mg": 0.1, "zinc_mg": 0.1, "calcium_mg": 40},
    {"name": "Mango, raw",             "calories": 60,  "protein_g": 0.8, "carbohydrates_total_g": 15.0, "fat_total_g": 0.4,  "iron_mg": 0.2, "zinc_mg": 0.1, "calcium_mg": 11},
    {"name": "Grapes, raw",            "calories": 69,  "protein_g": 0.7, "carbohydrates_total_g": 18.0, "fat_total_g": 0.2,  "iron_mg": 0.4, "zinc_mg": 0.1, "calcium_mg": 10},
    {"name": "Strawberry, raw",        "calories": 32,  "protein_g": 0.7, "carbohydrates_total_g": 7.7,  "fat_total_g": 0.3,  "iron_mg": 0.4, "zinc_mg": 0.1, "calcium_mg": 16},
    {"name": "Blueberry, raw",         "calories": 57,  "protein_g": 0.7, "carbohydrates_total_g": 14.5, "fat_total_g": 0.3,  "iron_mg": 0.3, "zinc_mg": 0.2, "calcium_mg": 6},
    {"name": "Watermelon, raw",        "calories": 30,  "protein_g": 0.6, "carbohydrates_total_g": 7.6,  "fat_total_g": 0.2,  "iron_mg": 0.2, "zinc_mg": 0.1, "calcium_mg": 7},
    {"name": "Pineapple, raw",         "calories": 50,  "protein_g": 0.5, "carbohydrates_total_g": 13.1, "fat_total_g": 0.1,  "iron_mg": 0.3, "zinc_mg": 0.1, "calcium_mg": 13},
    {"name": "Avocado, raw",           "calories": 160, "protein_g": 2.0, "carbohydrates_total_g": 9.0,  "fat_total_g": 15.0, "iron_mg": 0.6, "zinc_mg": 0.6, "calcium_mg": 12},
    {"name": "Peach, raw",             "calories": 39,  "protein_g": 0.9, "carbohydrates_total_g": 9.5,  "fat_total_g": 0.3,  "iron_mg": 0.3, "zinc_mg": 0.2, "calcium_mg": 6},
    {"name": "Pear, raw",              "calories": 57,  "protein_g": 0.4, "carbohydrates_total_g": 15.2, "fat_total_g": 0.1,  "iron_mg": 0.2, "zinc_mg": 0.1, "calcium_mg": 9},
    {"name": "Kiwi, raw",              "calories": 61,  "protein_g": 1.1, "carbohydrates_total_g": 14.7, "fat_total_g": 0.5,  "iron_mg": 0.3, "zinc_mg": 0.1, "calcium_mg": 34},
    {"name": "Cherry, raw",            "calories": 63,  "protein_g": 1.1, "carbohydrates_total_g": 16.0, "fat_total_g": 0.2,  "iron_mg": 0.4, "zinc_mg": 0.1, "calcium_mg": 13},
    {"name": "Lemon, raw",             "calories": 29,  "protein_g": 1.1, "carbohydrates_total_g": 9.3,  "fat_total_g": 0.3,  "iron_mg": 0.6, "zinc_mg": 0.1, "calcium_mg": 26},
    # ── Vegetables ──────────────────────────────────────────────────────────
    {"name": "Broccoli, raw",          "calories": 34,  "protein_g": 2.8, "carbohydrates_total_g": 7.0,  "fat_total_g": 0.4,  "iron_mg": 0.7, "zinc_mg": 0.4, "calcium_mg": 47},
    {"name": "Spinach, raw",           "calories": 23,  "protein_g": 2.9, "carbohydrates_total_g": 3.6,  "fat_total_g": 0.4,  "iron_mg": 2.7, "zinc_mg": 0.5, "calcium_mg": 99},
    {"name": "Carrot, raw",            "calories": 41,  "protein_g": 0.9, "carbohydrates_total_g": 10.0, "fat_total_g": 0.2,  "iron_mg": 0.3, "zinc_mg": 0.2, "calcium_mg": 33},
    {"name": "Tomato, raw",            "calories": 18,  "protein_g": 0.9, "carbohydrates_total_g": 3.9,  "fat_total_g": 0.2,  "iron_mg": 0.3, "zinc_mg": 0.2, "calcium_mg": 10},
    {"name": "Cucumber, raw",          "calories": 15,  "protein_g": 0.7, "carbohydrates_total_g": 3.6,  "fat_total_g": 0.1,  "iron_mg": 0.3, "zinc_mg": 0.2, "calcium_mg": 16},
    {"name": "Potato, raw",            "calories": 77,  "protein_g": 2.0, "carbohydrates_total_g": 17.5, "fat_total_g": 0.1,  "iron_mg": 0.8, "zinc_mg": 0.3, "calcium_mg": 12},
    {"name": "Sweet potato, raw",      "calories": 86,  "protein_g": 1.6, "carbohydrates_total_g": 20.1, "fat_total_g": 0.1,  "iron_mg": 0.6, "zinc_mg": 0.3, "calcium_mg": 30},
    {"name": "Onion, raw",             "calories": 40,  "protein_g": 1.1, "carbohydrates_total_g": 9.3,  "fat_total_g": 0.1,  "iron_mg": 0.2, "zinc_mg": 0.2, "calcium_mg": 23},
    {"name": "Garlic, raw",            "calories": 149, "protein_g": 6.4, "carbohydrates_total_g": 33.1, "fat_total_g": 0.5,  "iron_mg": 1.7, "zinc_mg": 1.2, "calcium_mg": 181},
    {"name": "Bell pepper, raw",       "calories": 31,  "protein_g": 1.0, "carbohydrates_total_g": 6.0,  "fat_total_g": 0.3,  "iron_mg": 0.4, "zinc_mg": 0.2, "calcium_mg": 7},
    {"name": "Lettuce, raw",           "calories": 15,  "protein_g": 1.4, "carbohydrates_total_g": 2.9,  "fat_total_g": 0.2,  "iron_mg": 0.9, "zinc_mg": 0.2, "calcium_mg": 36},
    {"name": "Corn, sweet, raw",       "calories": 86,  "protein_g": 3.2, "carbohydrates_total_g": 19.0, "fat_total_g": 1.2,  "iron_mg": 0.5, "zinc_mg": 0.5, "calcium_mg": 2},
    {"name": "Peas, green, raw",       "calories": 81,  "protein_g": 5.4, "carbohydrates_total_g": 14.5, "fat_total_g": 0.4,  "iron_mg": 1.5, "zinc_mg": 1.2, "calcium_mg": 25},
    {"name": "Cauliflower, raw",       "calories": 25,  "protein_g": 1.9, "carbohydrates_total_g": 5.0,  "fat_total_g": 0.3,  "iron_mg": 0.4, "zinc_mg": 0.3, "calcium_mg": 22},
    {"name": "Mushroom, raw",          "calories": 22,  "protein_g": 3.1, "carbohydrates_total_g": 3.3,  "fat_total_g": 0.3,  "iron_mg": 0.5, "zinc_mg": 0.5, "calcium_mg": 3},
    {"name": "Zucchini, raw",          "calories": 17,  "protein_g": 1.2, "carbohydrates_total_g": 3.1,  "fat_total_g": 0.3,  "iron_mg": 0.4, "zinc_mg": 0.3, "calcium_mg": 16},
    # ── Grains & Carbs ───────────────────────────────────────────────────────
    {"name": "Oatmeal, cooked",        "calories": 71,  "protein_g": 2.5, "carbohydrates_total_g": 12.0, "fat_total_g": 1.5,  "iron_mg": 0.8, "zinc_mg": 0.6, "calcium_mg": 10},
    {"name": "Oats, dry",              "calories": 389, "protein_g": 17.0,"carbohydrates_total_g": 66.0, "fat_total_g": 7.0,  "iron_mg": 4.7, "zinc_mg": 4.0, "calcium_mg": 54},
    {"name": "White rice, cooked",     "calories": 130, "protein_g": 2.7, "carbohydrates_total_g": 28.2, "fat_total_g": 0.3,  "iron_mg": 0.2, "zinc_mg": 0.5, "calcium_mg": 10},
    {"name": "Brown rice, cooked",     "calories": 112, "protein_g": 2.6, "carbohydrates_total_g": 23.5, "fat_total_g": 0.9,  "iron_mg": 0.4, "zinc_mg": 0.6, "calcium_mg": 10},
    {"name": "Pasta, cooked",          "calories": 131, "protein_g": 5.0, "carbohydrates_total_g": 25.1, "fat_total_g": 1.1,  "iron_mg": 1.3, "zinc_mg": 0.5, "calcium_mg": 7},
    {"name": "Bread, white",           "calories": 265, "protein_g": 9.0, "carbohydrates_total_g": 49.0, "fat_total_g": 3.2,  "iron_mg": 2.7, "zinc_mg": 0.7, "calcium_mg": 77},
    {"name": "Bread, whole wheat",     "calories": 247, "protein_g": 13.0,"carbohydrates_total_g": 41.0, "fat_total_g": 3.4,  "iron_mg": 2.5, "zinc_mg": 1.8, "calcium_mg": 161},
    {"name": "Quinoa, cooked",         "calories": 120, "protein_g": 4.4, "carbohydrates_total_g": 21.3, "fat_total_g": 1.9,  "iron_mg": 1.5, "zinc_mg": 1.1, "calcium_mg": 17},
    {"name": "Cereal, corn flakes",    "calories": 357, "protein_g": 7.5, "carbohydrates_total_g": 84.0, "fat_total_g": 0.4,  "iron_mg": 2.3, "zinc_mg": 0.2, "calcium_mg": 1},
    {"name": "Granola",                "calories": 471, "protein_g": 10.0,"carbohydrates_total_g": 64.0, "fat_total_g": 20.0, "iron_mg": 2.0, "zinc_mg": 1.6, "calcium_mg": 40},
    {"name": "Tortilla, flour",        "calories": 312, "protein_g": 8.0, "carbohydrates_total_g": 54.0, "fat_total_g": 7.0,  "iron_mg": 2.4, "zinc_mg": 0.6, "calcium_mg": 149},
    {"name": "Bagel",                  "calories": 250, "protein_g": 10.0,"carbohydrates_total_g": 48.0, "fat_total_g": 1.6,  "iron_mg": 2.8, "zinc_mg": 0.7, "calcium_mg": 53},
    {"name": "Croissant",              "calories": 406, "protein_g": 8.2, "carbohydrates_total_g": 46.0, "fat_total_g": 21.0, "iron_mg": 1.7, "zinc_mg": 0.6, "calcium_mg": 42},
    # ── Proteins — Meat & Seafood ─────────────────────────────────────────────
    {"name": "Chicken breast, cooked", "calories": 165, "protein_g": 31.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 3.6,  "iron_mg": 0.7, "zinc_mg": 1.0, "calcium_mg": 11},
    {"name": "Chicken thigh, cooked",  "calories": 209, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 11.0, "iron_mg": 1.0, "zinc_mg": 2.4, "calcium_mg": 11},
    {"name": "Beef, ground, cooked",   "calories": 254, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 17.0, "iron_mg": 2.7, "zinc_mg": 4.8, "calcium_mg": 18},
    {"name": "Beef steak, grilled",    "calories": 271, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 18.0, "iron_mg": 2.6, "zinc_mg": 4.3, "calcium_mg": 11},
    {"name": "Salmon, cooked",         "calories": 208, "protein_g": 20.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 13.0, "iron_mg": 0.3, "zinc_mg": 0.6, "calcium_mg": 13},
    {"name": "Tuna, canned in water",  "calories": 116, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 1.0,  "iron_mg": 1.3, "zinc_mg": 0.7, "calcium_mg": 16},
    {"name": "Shrimp, cooked",         "calories": 99,  "protein_g": 24.0,"carbohydrates_total_g": 0.2,  "fat_total_g": 0.3,  "iron_mg": 0.5, "zinc_mg": 1.5, "calcium_mg": 64},
    {"name": "Turkey breast, cooked",  "calories": 135, "protein_g": 30.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 1.0,  "iron_mg": 1.4, "zinc_mg": 2.6, "calcium_mg": 22},
    {"name": "Pork chop, cooked",      "calories": 231, "protein_g": 25.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 14.0, "iron_mg": 0.9, "zinc_mg": 2.9, "calcium_mg": 14},
    {"name": "Lamb, cooked",           "calories": 258, "protein_g": 26.0,"carbohydrates_total_g": 0.0,  "fat_total_g": 16.0, "iron_mg": 1.9, "zinc_mg": 4.5, "calcium_mg": 17},
    {"name": "Egg, whole, cooked",     "calories": 155, "protein_g": 13.0,"carbohydrates_total_g": 1.1,  "fat_total_g": 11.0, "iron_mg": 1.2, "zinc_mg": 1.3, "calcium_mg": 56},
    {"name": "Egg white, cooked",      "calories": 52,  "protein_g": 11.0,"carbohydrates_total_g": 0.7,  "fat_total_g": 0.2,  "iron_mg": 0.1, "zinc_mg": 0.0, "calcium_mg": 7},
    # ── Dairy ─────────────────────────────────────────────────────────────────
    {"name": "Milk, whole",            "calories": 61,  "protein_g": 3.2, "carbohydrates_total_g": 4.8,  "fat_total_g": 3.3,  "iron_mg": 0.0, "zinc_mg": 0.4, "calcium_mg": 113},
    {"name": "Milk, skimmed",          "calories": 34,  "protein_g": 3.4, "carbohydrates_total_g": 5.0,  "fat_total_g": 0.1,  "iron_mg": 0.0, "zinc_mg": 0.4, "calcium_mg": 125},
    {"name": "Greek yogurt, plain",    "calories": 59,  "protein_g": 10.0,"carbohydrates_total_g": 3.6,  "fat_total_g": 0.4,  "iron_mg": 0.1, "zinc_mg": 0.6, "calcium_mg": 110},
    {"name": "Yogurt, plain",          "calories": 63,  "protein_g": 5.3, "carbohydrates_total_g": 7.0,  "fat_total_g": 1.6,  "iron_mg": 0.1, "zinc_mg": 0.6, "calcium_mg": 121},
    {"name": "Cheddar cheese",         "calories": 403, "protein_g": 25.0,"carbohydrates_total_g": 1.3,  "fat_total_g": 33.0, "iron_mg": 0.7, "zinc_mg": 3.1, "calcium_mg": 710},
    {"name": "Mozzarella cheese",      "calories": 280, "protein_g": 28.0,"carbohydrates_total_g": 2.2,  "fat_total_g": 17.0, "iron_mg": 0.3, "zinc_mg": 2.9, "calcium_mg": 505},
    {"name": "Butter",                 "calories": 717, "protein_g": 0.9, "carbohydrates_total_g": 0.1,  "fat_total_g": 81.0, "iron_mg": 0.0, "zinc_mg": 0.1, "calcium_mg": 24},
    {"name": "Cream cheese",           "calories": 342, "protein_g": 6.2, "carbohydrates_total_g": 4.1,  "fat_total_g": 34.0, "iron_mg": 0.3, "zinc_mg": 0.6, "calcium_mg": 98},
    {"name": "Ice cream, vanilla",     "calories": 207, "protein_g": 3.5, "carbohydrates_total_g": 24.0, "fat_total_g": 11.0, "iron_mg": 0.1, "zinc_mg": 0.4, "calcium_mg": 128},
    # ── Legumes & Plant Protein ───────────────────────────────────────────────
    {"name": "Lentils, cooked",        "calories": 116, "protein_g": 9.0, "carbohydrates_total_g": 20.0, "fat_total_g": 0.4,  "iron_mg": 3.3, "zinc_mg": 1.3, "calcium_mg": 19},
    {"name": "Chickpeas, cooked",      "calories": 164, "protein_g": 8.9, "carbohydrates_total_g": 27.0, "fat_total_g": 2.6,  "iron_mg": 2.9, "zinc_mg": 1.5, "calcium_mg": 49},
    {"name": "Black beans, cooked",    "calories": 132, "protein_g": 8.9, "carbohydrates_total_g": 24.0, "fat_total_g": 0.5,  "iron_mg": 2.1, "zinc_mg": 1.0, "calcium_mg": 27},
    {"name": "Kidney beans, cooked",   "calories": 127, "protein_g": 8.7, "carbohydrates_total_g": 23.0, "fat_total_g": 0.5,  "iron_mg": 2.2, "zinc_mg": 1.1, "calcium_mg": 28},
    {"name": "Tofu, firm",             "calories": 76,  "protein_g": 8.0, "carbohydrates_total_g": 1.9,  "fat_total_g": 4.8,  "iron_mg": 2.0, "zinc_mg": 0.8, "calcium_mg": 350},
    {"name": "Edamame, cooked",        "calories": 121, "protein_g": 11.9,"carbohydrates_total_g": 8.9,  "fat_total_g": 5.2,  "iron_mg": 2.3, "zinc_mg": 1.4, "calcium_mg": 63},
    # ── Nuts & Seeds ──────────────────────────────────────────────────────────
    {"name": "Almonds",                "calories": 579, "protein_g": 21.0,"carbohydrates_total_g": 22.0, "fat_total_g": 50.0, "iron_mg": 3.7, "zinc_mg": 3.1, "calcium_mg": 264},
    {"name": "Walnuts",                "calories": 654, "protein_g": 15.0,"carbohydrates_total_g": 14.0, "fat_total_g": 65.0, "iron_mg": 2.9, "zinc_mg": 3.1, "calcium_mg": 98},
    {"name": "Cashews",                "calories": 553, "protein_g": 18.0,"carbohydrates_total_g": 30.0, "fat_total_g": 44.0, "iron_mg": 6.7, "zinc_mg": 5.8, "calcium_mg": 37},
    {"name": "Peanuts",                "calories": 567, "protein_g": 26.0,"carbohydrates_total_g": 16.0, "fat_total_g": 49.0, "iron_mg": 2.3, "zinc_mg": 3.3, "calcium_mg": 54},
    {"name": "Peanut butter",          "calories": 588, "protein_g": 25.0,"carbohydrates_total_g": 20.0, "fat_total_g": 50.0, "iron_mg": 1.5, "zinc_mg": 2.5, "calcium_mg": 49},
    {"name": "Chia seeds",             "calories": 486, "protein_g": 17.0,"carbohydrates_total_g": 42.0, "fat_total_g": 31.0, "iron_mg": 7.7, "zinc_mg": 4.6, "calcium_mg": 631},
    {"name": "Sunflower seeds",        "calories": 584, "protein_g": 21.0,"carbohydrates_total_g": 20.0, "fat_total_g": 51.0, "iron_mg": 5.3, "zinc_mg": 5.0, "calcium_mg": 78},
    # ── Fast food & Common Meals ──────────────────────────────────────────────
    {"name": "Pizza, cheese",          "calories": 266, "protein_g": 11.0,"carbohydrates_total_g": 33.0, "fat_total_g": 10.0, "iron_mg": 1.5, "zinc_mg": 1.5, "calcium_mg": 200},
    {"name": "Burger, beef",           "calories": 295, "protein_g": 17.0,"carbohydrates_total_g": 24.0, "fat_total_g": 14.0, "iron_mg": 2.3, "zinc_mg": 3.5, "calcium_mg": 60},
    {"name": "French fries",           "calories": 312, "protein_g": 3.4, "carbohydrates_total_g": 41.0, "fat_total_g": 15.0, "iron_mg": 0.7, "zinc_mg": 0.4, "calcium_mg": 15},
    {"name": "Hot dog",                "calories": 290, "protein_g": 11.0,"carbohydrates_total_g": 22.0, "fat_total_g": 17.0, "iron_mg": 1.5, "zinc_mg": 2.0, "calcium_mg": 50},
    {"name": "Sandwich, turkey",       "calories": 218, "protein_g": 16.0,"carbohydrates_total_g": 28.0, "fat_total_g": 4.3,  "iron_mg": 1.5, "zinc_mg": 1.5, "calcium_mg": 80},
    # ── Drinks ────────────────────────────────────────────────────────────────
    {"name": "Orange juice",           "calories": 45,  "protein_g": 0.7, "carbohydrates_total_g": 10.4, "fat_total_g": 0.2,  "iron_mg": 0.2, "zinc_mg": 0.1, "calcium_mg": 11},
    {"name": "Apple juice",            "calories": 46,  "protein_g": 0.1, "carbohydrates_total_g": 11.4, "fat_total_g": 0.1,  "iron_mg": 0.1, "zinc_mg": 0.0, "calcium_mg": 8},
    {"name": "Coca-Cola",              "calories": 42,  "protein_g": 0.0, "carbohydrates_total_g": 10.6, "fat_total_g": 0.0,  "iron_mg": 0.0, "zinc_mg": 0.0, "calcium_mg": 2},
    {"name": "Coffee, black",          "calories": 2,   "protein_g": 0.3, "carbohydrates_total_g": 0.0,  "fat_total_g": 0.0,  "iron_mg": 0.0, "zinc_mg": 0.0, "calcium_mg": 2},
    {"name": "Coffee with milk",       "calories": 13,  "protein_g": 0.6, "carbohydrates_total_g": 1.0,  "fat_total_g": 0.5,  "iron_mg": 0.0, "zinc_mg": 0.1, "calcium_mg": 15},
    {"name": "Green tea",              "calories": 1,   "protein_g": 0.0, "carbohydrates_total_g": 0.2,  "fat_total_g": 0.0,  "iron_mg": 0.0, "zinc_mg": 0.0, "calcium_mg": 0},
    # ── Snacks & Sweets ───────────────────────────────────────────────────────
    {"name": "Chocolate, dark",        "calories": 546, "protein_g": 5.0, "carbohydrates_total_g": 60.0, "fat_total_g": 31.0, "iron_mg": 12.0,"zinc_mg": 3.3, "calcium_mg": 73},
    {"name": "Chocolate, milk",        "calories": 535, "protein_g": 8.0, "carbohydrates_total_g": 59.0, "fat_total_g": 30.0, "iron_mg": 0.7, "zinc_mg": 0.9, "calcium_mg": 189},
    {"name": "Potato chips",           "calories": 536, "protein_g": 7.0, "carbohydrates_total_g": 53.0, "fat_total_g": 35.0, "iron_mg": 1.6, "zinc_mg": 0.9, "calcium_mg": 17},
    {"name": "Crackers",               "calories": 424, "protein_g": 9.0, "carbohydrates_total_g": 68.0, "fat_total_g": 13.0, "iron_mg": 3.0, "zinc_mg": 1.0, "calcium_mg": 65},
    {"name": "Popcorn",                "calories": 375, "protein_g": 11.0,"carbohydrates_total_g": 74.0, "fat_total_g": 4.0,  "iron_mg": 0.9, "zinc_mg": 0.8, "calcium_mg": 3},
    {"name": "Protein bar",            "calories": 390, "protein_g": 30.0,"carbohydrates_total_g": 40.0, "fat_total_g": 10.0, "iron_mg": 2.0, "zinc_mg": 1.5, "calcium_mg": 150},
    {"name": "Honey",                  "calories": 304, "protein_g": 0.3, "carbohydrates_total_g": 82.0, "fat_total_g": 0.0,  "iron_mg": 0.4, "zinc_mg": 0.2, "calcium_mg": 6},
    # ── Oils & Condiments ─────────────────────────────────────────────────────
    {"name": "Olive oil",              "calories": 884, "protein_g": 0.0, "carbohydrates_total_g": 0.0,  "fat_total_g": 100.0,"iron_mg": 0.6, "zinc_mg": 0.0, "calcium_mg": 1},
    {"name": "Mayonnaise",             "calories": 680, "protein_g": 1.0, "carbohydrates_total_g": 0.6,  "fat_total_g": 75.0, "iron_mg": 0.3, "zinc_mg": 0.0, "calcium_mg": 13},
    {"name": "Ketchup",                "calories": 112, "protein_g": 1.3, "carbohydrates_total_g": 27.0, "fat_total_g": 0.1,  "iron_mg": 0.4, "zinc_mg": 0.1, "calcium_mg": 10},
    {"name": "Hummus",                 "calories": 166, "protein_g": 8.0, "carbohydrates_total_g": 14.0, "fat_total_g": 10.0, "iron_mg": 2.4, "zinc_mg": 1.0, "calcium_mg": 38},
    {"name": "Salsa",                  "calories": 36,  "protein_g": 1.6, "carbohydrates_total_g": 7.4,  "fat_total_g": 0.2,  "iron_mg": 0.5, "zinc_mg": 0.1, "calcium_mg": 16},
]

# Simple in-memory USDA cache — avoids duplicate API calls this session
_usda_cache: dict = {}


def search_local(query: str) -> list:
    q = query.lower().strip()
    matches = [f for f in LOCAL_DB if q in f["name"].lower()]
    matches.sort(key=lambda f: (0 if f["name"].lower().startswith(q) else 1, f["name"]))
    return matches[:5]


def search_usda(query: str) -> list:
    if query in _usda_cache:
        return _usda_cache[query]

    api_key = os.environ.get("USDA_FDC_API_KEY", "DEMO_KEY")
    try:
        resp = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={"query": query, "api_key": api_key,
                    "dataType": "SR Legacy,Foundation", "pageSize": 5},
            timeout=8,
        )
        if resp.status_code == 429:
            return []
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        return []

    MACRO_IDS  = {1008: "calories", 1003: "protein_g", 1005: "carbohydrates_total_g", 1004: "fat_total_g"}
    MACRO_NUMS = {"208": "calories", "203": "protein_g", "205": "carbohydrates_total_g", "204": "fat_total_g"}
    MICRO_IDS  = {1089: "iron_mg", 1095: "zinc_mg", 1087: "calcium_mg"}
    MICRO_NUMS = {"303": "iron_mg", "309": "zinc_mg", "301": "calcium_mg"}

    results = []
    for food in data.get("foods", []):
        vals = {v: 0.0 for v in list(MACRO_IDS.values()) + list(MICRO_IDS.values())}
        for n in food.get("foodNutrients", []):
            key = (MACRO_IDS.get(n.get("nutrientId")) or MACRO_NUMS.get(str(n.get("nutrientNumber", "")))
                   or MICRO_IDS.get(n.get("nutrientId")) or MICRO_NUMS.get(str(n.get("nutrientNumber", ""))))
            if key:
                try:
                    vals[key] = float(n.get("value", 0))
                except (TypeError, ValueError):
                    pass
        results.append({
            "name": food.get("description", query).title(),
            "calories": round(vals["calories"]),
            "protein_g": round(vals["protein_g"], 1),
            "carbohydrates_total_g": round(vals["carbohydrates_total_g"], 1),
            "fat_total_g": round(vals["fat_total_g"], 1),
            "iron_mg": round(vals["iron_mg"], 1),
            "zinc_mg": round(vals["zinc_mg"], 1),
            "calcium_mg": round(vals["calcium_mg"], 1),
        })

    _usda_cache[query] = results
    return results


# ─────────────────────────────────────────────────────────────────────────────

@foods_bp.route("/foods")
@login_required
def foods_home():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        results = search_food_history(current_user.id, query)
    return render_template("foods.html", query=query, results=results)


@foods_bp.route("/api/nutrition")
@login_required
def nutrition_lookup():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400

    results = search_local(query)
    if not results:
        results = search_usda(query)

    if not results:
        return jsonify({"error": f"No results found for '{query}'. Try a different spelling."}), 404

    return jsonify({"results": results})
