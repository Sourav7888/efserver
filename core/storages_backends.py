from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class Logos(S3Boto3Storage):
    location = 'Logos/'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    querystring_auth = True
    aws_querystring_expire = 18000