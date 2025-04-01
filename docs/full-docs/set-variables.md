# Set variables

Variables can set in .env.prod file

## Postgresql Database variables:
1. **POSTGRES_DB:** `Database name`
2. **POSTGRES_USER:** `Username of user to connect to the database`
3. **POSTGRES_PASSWORD:** `The password of user`
4. **POSTGRES_HOST:** `The postgres host. in this case host is the name of database service in docker-compose.yml`
5. **POSTGRES_PORT:** `The port on which postgres is running`

## Django variables
### Django security variables
6. **DEBUG:** `in this case it is 0`
7. **DJANGO_SECRET_KEY:** `The secret key. this is important`
8. **DJANGO_ALLOWED_HOSTS:** `Hosts that can access to the server`

### Django Database variables:
9. **DJANGO_DB_ENGINE:** `Database engine. in this case is postgresql`
10. **DJANGO_DB_HOST:** `Postgres host. in this case is the name of postgers service in docker-compose.yml`
11. **DJANGO_DB_PORT:** `Database port`
12. **DJANGO_DB_SUPERUSER_PASSWORD:** `The superuser password for create superuser`
