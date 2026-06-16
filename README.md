# KanMind Backend

Backend for the KanMind project built with Django and Django REST Framework.

## Tech Stack
- Python
- Django
- Django REST Framework

## Setup

1. Clone the repository
2. Create a virtual environment
3. Activate the virtual environment
4. Install dependencies
5. Run migrations
6. Start the server

## Local setup

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Admin user

```bash
python manage.py createsuperuser
```

## Notes
- The project uses a local SQLite database for development.
- `db.sqlite3` is ignored and must not be committed.
- Environment-specific values should be stored in `.env`.