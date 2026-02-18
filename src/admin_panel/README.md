# ExamForms Admin Panel

## Assumptions
- Django is installed
- PostgreSQL schema already exists
- DATABASE_URL or DB_* env vars are configured

## Run Locally

```bash
export DATABASE_URL=postgres://user:pass@localhost:5432/examforms
python manage.py createsuperuser
python manage.py setup_roles
python manage.py runserver
```

Access: http://localhost:8000/admin/

## Notes
- Models are mapped to existing tables (`managed = False`)
- Admin UI is styled via `static/admin/custom.css`
