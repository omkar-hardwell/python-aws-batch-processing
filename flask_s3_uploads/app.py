"""Application routes"""
import csv
import datetime
import json
import math
import os.path
import shutil
import uuid

from .configs import S3_BUCKET_NAME, S3_LOCATION, ALLOWED_FILE_EXTENSIONS, \
    UPLOAD_FOLDER, MAX_BATCH_SIZE
from .helpers import s3

from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

# Application object
app = Flask(__name__)


@app.route("/")
def index():
    """Index route
    :return: Renders to upload page
    """
    return render_template("index.html")


@app.route("/", methods=["POST"])
def upload_file():
    """Upload batches to Amazon S3
    :return: Displays the S3 link otherwise error
    """
    output = []
    if "user_file" not in request.files:
        return "No user_file key in request.files"

    file = request.files["user_file"]
    """
        These attributes are also available

        file.filename               # The actual name of the file
        file.content_type
        file.content_length
        file.mimetype
    """
    if file.filename == "":
        return "Please select a file"
    if not request.form['release_id']:
        return "Release Id missing"

    if file and allowed_file(file.filename):
        now = datetime.datetime.today()
        date_time = now.strftime("%d-%m-%Y_%H%M%S")
        location = os.path.join(UPLOAD_FOLDER + '/' + date_time)
        if not os.path.exists(location):
            os.makedirs(location)
        # Upload csv file to /temp for making a batches
        resp_file_upload_to_local = upload_file_to_local(file, location)
        output.append(resp_file_upload_to_local)

        # Read csv file and making a batches
        resp_make_batches = make_batches(file, location)
        output.append(resp_make_batches)

        # Upload batches to Amazon S3
        resp_upload_batch_to_s3 = upload_batch_to_s3(location)
        output.append(resp_upload_batch_to_s3)

        # Remove files from /temp
        shutil.rmtree(location)

        return str(output)
    else:
        return redirect("/")


def allowed_file(file):
    """Verify file extension
    :param file: file name
    :return: bool
    """
    return '.' in file and \
        file.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS


def upload_file_to_s3(file, bucket_name, acl="public-read"):
    """Upload files to Amazon S3 via s3 client
    :param file: file object
    :param bucket_name: S3 bucket name
    :param acl: Access control list
    :return: S3 link otherwise exception
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened on uploading Amazon S3: ", e)
        return e

    return "{}{}".format(S3_LOCATION, file.filename)


def upload_batch_to_s3(location):
    """Upload batch to Amazon S3
    :param location: Local file path
    :return: S3 link otherwise exception
    """
    uploaded_files = []
    try:
        for root, dirs, files in os.walk(location):
            for file in files:
                if file.endswith(".json"):
                    s3.upload_file(
                        os.path.join(root, file), S3_BUCKET_NAME, file)
                    uploaded_files.append(str(file))
    except Exception as e:
        print("Something Happened on uploading Amazon S3: ", e)
        return e

    return ["{}{}".format(S3_LOCATION, file) for file in uploaded_files]


def upload_file_to_local(file, location='temp'):
    """Upload file to given location
    :param file: obj - File object
    :param location: str - Location to upload csv
    :return: Folder path of uploaded file
    """
    try:
        filename = secure_filename(file.filename)
        file.save(os.path.join(location, filename))
        return \
            'File {filename} uploaded successfully.'.format(filename=filename)
    except Exception as e:
        print("Something Happened on uploading file to local: ", e)
        return e


def divide_chunks(l, n):
    """Divide into chunks
    :param l: list - List to divide into chunks
    :param n: int - Max size of chunk
    :return: list - List of chunks with given max size
    """
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def make_batches(file, location):
    """Make batches in JSON format
    :param file: file - CSV file to make batches
    :param location: - File path to upload batches
    :return: Success message otherwise error
    """
    try:
        region_list = []
        with open(location + '/' + file.filename, 'r') as csv_file:
            csv_data = csv.reader(csv_file, delimiter=' ', quotechar='|')
            first_line = True
            for row in csv_data:
                if first_line:
                    first_line = False
                    continue
                region_list.append(row[0])
        total_no_of_batches = int(math.ceil(len(region_list) / MAX_BATCH_SIZE))
        total_batches = list(divide_chunks(region_list, MAX_BATCH_SIZE))
        for i in range(total_no_of_batches):
            json_data = {
                "release_id": request.form['release_id'],
                "region_restricted": total_batches[i],
                "action": request.form['operation']
            }
            f = open(location + '/batch_{0}.json'.format(uuid.uuid4()), 'w')
            f.write(json.dumps(json_data))
        return 'Batches created successfully.'
    except Exception as e:
        print("Something Happened while making batches: ", e)
        return e
