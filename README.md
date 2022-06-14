# efserver
![Tests](https://github.com/EFTechnicalPM/efserver/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/EFTechnicalPM/efserver/branch/main/graph/badge.svg?token=N851jEIDBs)](https://codecov.io/gh/EFTechnicalPM/efserver)

# Deployment steps (heroku)

The following services are required:<br>
    - Auth0
    - RDS - posql as a default database (AWS)
    - RDS - pgsql as a weather database (AWS)
    - CloudAMQP - cloud rabbitmq (heroku)
    - Mailgun - if using 3rd party mailing service
    - Gmail SMTP - if using 3rd party mailing service


