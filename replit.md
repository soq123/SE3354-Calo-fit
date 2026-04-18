# CaloFit

A web-based calorie and meal tracking application built with Flask and SQLite.

## Architecture

- **Backend**: Python 3.12 / Flask 3.1.3
- **Database**: SQLite (file: `calofit.db`, auto-created on first run)
- **Frontend**: Jinja2 templates with HTML/CSS/JS in `app/templates/` and `app/static/`

## Project Structure

```
.
├── app/
│   ├── controllers/       # Route handlers (Flask Blueprints)
│   │   ├── analytics.py   # JSON endpoints for daily/weekly summaries
│   │   ├── foods.py       # Food-related routes
│   │   └── meals.py       # Meal logging and history routes
│   ├── models/            # Database interaction logic
│   │   ├── food_entry.py  # Food item search/retrieval
│   │   └── meal.py        # CRUD for meal logs
│   ├── static/            # CSS/JS assets
│   ├── templates/         # Jinja2 HTML templates
│   ├── db.py              # SQLite connection management
│   └── __init__.py        # Flask app factory (create_app)
├── config/
│   └── config.py          # Configuration settings
├── run.py                 # Entry point (dev: 0.0.0.0:5000)
├── schema.sql             # SQLite schema definition
├── seed_data.py           # Script to seed initial data
└── requirements.txt       # Python dependencies
```

## Running the Application

The app starts automatically via the configured workflow using:
```
python run.py
```

The database (`calofit.db`) is created automatically from `schema.sql` on first launch.

## Key Features

- Meal logging (Breakfast, Lunch, Dinner, Snack)
- Calorie and macronutrient tracking (protein, carbs, fats)
- Daily calorie goal with remaining calories display
- Weekly analytics and progress tracking
- Food search across meal history

## Deployment

Configured for autoscale deployment using gunicorn:
```
gunicorn --bind=0.0.0.0:5000 --reuse-port run:app
```

## Environment Variables

- `SECRET_KEY`: Flask secret key (set in `.env`)
