# Admin Panel Verification Checklist

## Assumptions (Before Verification)
- DATABASE_URL configured
- PostgreSQL reachable
- Django installed
- Admin user created
- Roles created via `setup_roles`

---

## 1. Server Startup
- [ ] `python manage.py check` passes
- [ ] `python manage.py runserver` starts without errors
- [ ] Admin login page loads at `/admin/`

## 2. Authentication & Roles
- [ ] Superuser login works
- [ ] Roles created (Admin, Editor, Reviewer, Viewer)
- [ ] Role permissions enforced correctly
- [ ] Viewer cannot edit records

## 3. Core Models
- [ ] Exams visible in admin
- [ ] Exam Events visible and linked to Exams
- [ ] Page Metadata visible
- [ ] Status Change Events visible
- [ ] Monitoring Config visible
- [ ] Manual Review Queue visible

## 4. Dashboard Widgets
- [ ] Summary cards display correct counts
- [ ] Recent Status Changes list loads
- [ ] No template errors on admin index

## 5. Audit Log
- [ ] Audit log page loads
- [ ] Log entries are read-only
- [ ] Filters/search work

## 6. Performance
- [ ] Admin index loads < 2s
- [ ] Lists with 10k+ records still load via pagination

## 7. Styling
- [ ] Branding header renders correctly
- [ ] Cards styling present
- [ ] No CSS errors in console

## 8. Data Integrity
- [ ] Foreign keys resolve correctly
- [ ] No null pointer errors when related data missing

---

## Expected Outcome
All checks pass before production deployment.
