# KanMind Backend

Kanban Task Management API built with Django REST Framework.  
It provides resource-oriented endpoints for managing boards, tasks, and comments, including board membership/ownership permissions, task assignment and review flows, and user-specific task views (e.g. “assigned to me”, “reviewing”), following clean, beginner-friendly DRF best practices.

## Tech Stack
- Python 3.14
- Django 6.0
- Django REST Framework 3.17

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