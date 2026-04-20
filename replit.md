# CaloFit

A web-based calorie and meal tracking application built with Flask and SQLite.

## Architecture

- **Backend**: Python 3.12 / Flask 3.1.3
- **Database**: SQLite (file: `1_code/calofit.db`, auto-created on first run)
- **Frontend**: Jinja2 templates with HTML/CSS/JS in `1_code/app/templates/` and `1_code/app/static/`

## Project Structure

```
.
├── 1_code/                    # Main application code
│   ├── app/
│   │   ├── controllers/       # Route handlers (Flask Blueprints)
│   │   │   ├── analytics.py   # JSON endpoints for daily/weekly summaries
│   │   │   ├── auth.py        # Authentication routes
│   │   │   ├── foods.py       # Food-related routes
│   │   │   ├── meals.py       # Meal logging and history routes
│   │   │   └── mood.py        # Mood/energy logging routes
│   │   ├── models/            # Database interaction logic
│   │   │   ├── food_entry.py  # Food item search/retrieval
│   │   │   ├── meal.py        # CRUD for meal logs
│   │   │   └── user.py        # User model
│   │   ├── services/          # Business logic
│   │   │   └── insights.py    # Nutrition insights and recommendations
│   │   ├── static/            # CSS/JS assets
│   │   ├── templates/         # Jinja2 HTML templates
│   │   ├── db.py              # SQLite connection management
│   │   └── __init__.py        # Flask app factory (create_app)
│   ├── config/
│   │   └── config.py          # Configuration settings
│   ├── run.py                 # Entry point (dev: 0.0.0.0:5000)
│   ├── schema.sql             # SQLite schema definition
│   ├── calofit.db             # SQLite database (auto-created)
│   └── requirements.txt       # Python dependencies
├── 2_data_collection/         # Database seeding scripts
│   └── seed_data.py
├── 3_basic_function_testing/  # Automated tests
│   ├── test_calofit.py
│   └── test_app.py
└── 4_documentation/           # Project documentation / README files
    ├── README1.txt
    ├── README2.txt
    └── README3.txt
```

## Running the Application

The app starts automatically via the configured workflow using:
```
python 1_code/run.py
```

The database (`1_code/calofit.db`) is created automatically from `1_code/schema.sql` on first launch.

## Key Features

- User authentication (register, login, email verification, password reset)
- Meal logging (Breakfast, Lunch, Dinner, Snack)
- Calorie and macronutrient tracking (protein, carbs, fats)
- Food search via USDA FoodData Central API
- Mood and energy level logging
- Daily calorie goal with remaining calories display
- Weekly analytics and progress tracking
- Nutrition insights and recommendations

## Deployment

Configured for autoscale deployment using gunicorn.

## Environment Variables

- `SECRET_KEY`: Flask secret key
- `USDA_FDC_API_KEY`: USDA FoodData Central API key (defaults to DEMO_KEY)
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Email config for Flask-Mail
