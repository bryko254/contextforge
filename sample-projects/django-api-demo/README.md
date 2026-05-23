# Django API Demo

A compact Django REST Framework sample used by ContextForge to test project scanning and documentation generation.

The app exposes a small task API where authenticated users can own tasks, track status, and manage due dates.

## Stack

- Django
- Django REST Framework
- PostgreSQL through Docker Compose

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Shape

- `GET /api/tasks/`
- `POST /api/tasks/`
- `GET /api/tasks/<id>/`
- `PATCH /api/tasks/<id>/`
- `DELETE /api/tasks/<id>/`

## Environment

```env
DJANGO_SECRET_KEY=change-me
DATABASE_URL=postgres://contextforge:contextforge@localhost:5432/contextforge_tasks
```
