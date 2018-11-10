"""Application configuration"""
import os

# AWS configurations
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET_NAME)

# Application parameters
PORT = 5000
DEBUG = True

# Constants use in logic
ALLOWED_FILE_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = './temp'
MAX_BATCH_SIZE = 100
