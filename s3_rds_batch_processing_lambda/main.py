"""Lambda logic for processing batch from s3 to RDS."""
import os
import json
import boto3
import pymysql

# s3 connection
s3 = boto3.client('s3')

# RDS instance connection
try:
    rds_conn = pymysql.connect(
        host=os.environ.get("RDS_HOST"),
        user=os.environ.get("RDS_USER"),
        passwd=os.environ.get("RDS_PASSWORD"),
        database=os.environ.get("RDS_DATABASE"),
        connect_timeout=5)
except Exception as ex:
    print(ex)
    print("ERROR: Unexpected error: "
          "Could not connect to Amazon RDS[MySql]:{} instance."
          .format(os.environ.get("RDS_HOST")))
    raise ex


def s3_rds_processing(event, context):
    """Process the s3 batch and performs action to RDS
    :param event: list
    :param context:
    :return: bool otherwise error message on failure
    :raise: Exception on failure
    """
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    print("s3 bucket : " + bucket)
    key = event['Records'][0]['s3']['object']['key']
    print("File : " + key)
    try:
        # Get .json object from s3 bucket
        response = s3.get_object(Bucket=bucket, Key=key)
        print("File object : " + str(response))
        # Parsing content to string using UTF-8 unicode
        file_content = response["Body"].read().decode('utf-8')
        print("File content : ", file_content)
        # Loads content in json/dict format
        json_content = json.loads(file_content)
        print("Json content : ", json_content)
        # Insert/Update/Delete operation on RDS
        print("Batch action : ", json_content['action'])
        if json_content['action'] == 'insert_update':
            # Insert/Update the records
            with rds_conn.cursor() as cursor:
                sql = "INSERT IGNORE INTO release_region_restriction " \
                      "(release_id, region_code) VALUES "
                for region_code in json_content['region_restricted']:
                    sql += "(" + json_content['release_id'] + \
                           ", '" + region_code + "'), "
                cursor.execute(sql[::-1].replace(",", "", 1)[::-1])
            rds_conn.commit()
        elif json_content['action'] == 'delete':
            # Delete the records
            with rds_conn.cursor() as cursor:
                sql = "DELETE FROM release_region_restriction " \
                      "WHERE release_id = " + json_content['release_id'] + \
                      " AND region_code IN (" + \
                      str(json_content['region_restricted']).strip('[]') + ")"
                cursor.execute(sql)
            rds_conn.commit()
        return True
    except Exception as e:
        print(e)
        print('Error while processing batch from s3 to RDS.')
        raise e
