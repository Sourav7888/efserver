from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class InvestigationDocs(S3Boto3Storage):
    location = "InvestigationDocs/"
    default_acl = "private"
    file_overwrite = False
    custom_domain = False
    querystring_auth = True
    aws_querystring_expire = 18000
