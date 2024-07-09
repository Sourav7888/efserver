FROM python:3.9.6

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=server.settings.prod

CMD ["gunicorn", "-b", "0.0.0.0:8000", "server.wsgi:application"]
