# اجرای سرور روی لوکال هاست:

## کانفیگ های پیشفرض استفاده شده در جنگو:
## میشه این تنظیمات رو در فایل .prod.env تغییر داد.

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
### دستور اجرا:
```bash
python manage.py runserver
```

حالا میشه در ادرس لوکال هاست به سایت دسترسی داشت [127.0.0.1:8000](http://127.0.0.1:8000)

