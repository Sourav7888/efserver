# efserver
![Tests](https://github.com/EFTechnicalPM/efserver/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/EFTechnicalPM/efserver/branch/main/graph/badge.svg?token=N851jEIDBs)](https://codecov.io/gh/EFTechnicalPM/efserver)

# Deployment steps (heroku)

The following services are required:<br>

<ul>
    <li>Auth0</li>
    <li>RDS - posql as a default database (AWS)</li>
    <li>RDS - pgsql as a weather database (AWS)</li>
    <li>S3 - as default static storage</li>
    <li>CloudAMQP - cloud rabbitmq (heroku)</li>
    <li>Mailgun - if using 3rd party mailing service</li>
    <li>Gmail SMTP - if using 3rd party mailing service</li>
</ul>

If not present create a filename called Procfile and add the following:

        release: python manage.py migrate
        web: gunicorn server.wsgi --log-file -
        worker: celery -A server worker 
        --beat --scheduler django   
        --loglevel=info --concurrency=4 
        --max-tasks-per-child=1 
        --without-gossip --without-mingle -l INFO


Then create a file called runtime.txt and choose your python python runtime (recommended below):

        python-3.9.6


Configure environment variables, you will need the following:

    ENV_TYPE = [DEVELOPMENT or PRODUCTION]
    PRODUCTION_AUTH0_AUDIENCE =
    PRODUCTION_AUTH0_DOMAIN =
    PRODUCTION_AWS_ACCESS_KEY_ID =
    PRODUCTION_AWS_SECRET_ACCESS_KEY =
    PRODUCTION_AWS_STORAGE_BUCKET_NAME =
    PRODUCTION_DATABASE_HOST =
    PRODUCTION_DATABASE_NAME =
    PRODUCTION_DATABASE_PASSWORD =
    PRODUCTION_DATABASE_USER =
    PRODUCTION_GMAIL_SMTP_PASSWORD =
    PRODUCTION_GMAIL_SMTP_USER =
    PRODUCTION_MAILGUN_SMTP_PASSWORD =
    PRODUCTION_MAILGUN_SMTP_PORT =
    PRODUCTION_MAILGUN_SMTP_SERVER =
    PRODUCTION_MAILGUN_SMTP_USER =
    PRODUCTION_SECRET_KEY =
    WEATHER_DATABASE_HOST =
    WEATHER_DATABASE_NAME =
    WEATHER_DATABASE_PASSWORD =
    WEATHER_DATABASE_USER =

Deploy to heroku using either github integration or heroku CLI.
