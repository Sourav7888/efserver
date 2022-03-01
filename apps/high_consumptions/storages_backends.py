from storages.backends.s3boto3 import S3Boto3Storage


class HCDocs(S3Boto3Storage):
    location = "HCDocs/"
    default_acl = "private"
    file_overwrite = False
    custom_domain = False
    querystring_auth = True
    aws_querystring_expire = 18000


