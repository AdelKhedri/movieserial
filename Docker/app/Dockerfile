FROM python:alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFRED=1

RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip
ADD ../../requirements.txt .

RUN apk update --no-cache
RUN apk upgrade --no-cache

RUN apk add --no-cache gcc python3-dev
RUN pip install -r requirements.txt --no-cache
RUN pip install psycopg
CMD ["sh", "-c", "python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py createsuperuser --user superuser --number 09123456789 --email superuser@gmail.com --noinput ; \
    gunicorn -b 0.0.0.0:8000 netmovie.wsgi" ]
