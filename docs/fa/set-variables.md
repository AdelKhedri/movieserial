# تنظیم متغییر ها

متغییر ها رو میتونید در فایل .env.prod تنظیم کنید

مقادیر پیشفرض در این فایل:
!!! bug "هشدار امنیتی"
    حتمی متغییر های مهم مثل پسورد ها رو تغییر بدید.

## متغییر های دیتابیس Postgresql:
1. **POSTGRES_DB:** `نام دیتابیس`
2. **POSTGRES_USER:** `یوزرنیم کاربری که توسط جنگو برای اتصال به دیتابیس استفاده میشه`
3. **POSTGRES_PASSWORD:** `پسورد یوزر دیتابیس`
4. **POSTGRES_HOST:** `ادرس هاست پستگرس. در این مورد چون پستگرس در لوکال و در سرویس های داکر هست نام سرویس دیتابیس در docker-compose.yml را وارد کنید.`
5. **POSTGRES_PORT:** `پورتی که پستگرس روی اون اجرا میشه(پیشفرض 5432 هست).`

## متغییر های جنگو
### متغییر های امنیتی جنگو
6. **DEBUG:** `این متغییر برای کمک به برنامه نویسان در پیدا کردن مشکلات هست و باید درحالت پروداکشن False باشه.`
7. **DJANGO_SECRET_KEY:** `کلید امنیتی جنگو. مراقب باشید لو نره و حتمن تغییرش بدید. خیلی مهمه`
8. **DJANGO_ALLOWED_HOSTS:** `ادرس هایی که میتونن به سرور gunicorn دسترسی داشته باشن. نام سرویسی که در docker-compose.yml حاوی سورس سایت است. در این مورد app`

### متیغییر های دیتابیس جنگو:
9. **DJANGO_DB_ENGINE:** `متور دیتابیس. در این مورد postgresql`
10. **DJANGO_DB_HOST:** `ادرس پستگرس. در این مورد نام سرویس دیتابیس توی فایل docker-compose.yml`
11. **DJANGO_DB_PORT:** `پورت دیتابیس که روی اون کار میکنه`
12. **DJANGO_DB_SUPERUSER_PASSWORD:** `پسورد کاربر سوپر یوزر مهمه که قبل از اجرای سرویس ابتدا این مورد رو ویرایش کنید`
13. در ادرس Docker/app/Dockerfile در خط 21 جلوی پرچم --user نام کاربری کاربر سوپر یوزر مشخص است, پیشفرض superuser است باید این مورد مهم رو هم تغییر بدید.
همچنین جلوی پرچم --number شماره تلفن کاربر سوپر یوزر رو هم تغییر بدید. پیشفرض: 09123456789