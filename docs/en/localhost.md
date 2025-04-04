# Start server in localhost:

## default configuration in development:

### Database:
    Engine: sqlite3
    Name: db.sqlite3

### Secret_key:
    default

### DEBUG:
    True

### ALLOWED_HOSTS:
    ['localhost', '127.0.0.1']

### STATICFILES_DIRS:
```python
os.path.join(BASE_DIR, 'static')
```
### Run command:
```bash
python manage.py runserver
```

now can access the site on localhost [127.0.0.1:8000](http://127.0.0.1:8000)

