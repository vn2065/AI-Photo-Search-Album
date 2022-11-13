import json
import os
import time
import boto3
from datetime import datetime
import requests
from requests_aws4auth import AWS4Auth



region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

rekognition = boto3.client('rekognition')
client=boto3.client('s3')
host = 'https://search-photos-pvzbo2yvcxuovtbht53cme6hkm.us-east-1.es.amazonaws.com' # the OpenSearch Service domain, with https://
index = 'album'
type = 'photo'
url = host + '/' + index + '/' + type + '/'
headers = { "Content-Type": "application/json" }


def handler(event, context):

    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    records = event['Records']
    print(records)

    for record in records:

        s3object = record['s3']
        print(s3object)
        bucket = s3object['bucket']['name']
        objectKey = s3object['object']['key']
        print(bucket)
        print(objectKey)
        response = client.head_object(Bucket=bucket,Key=objectKey)
        print(response)
        #customlabels = response['ResponseMetadata']['HTTPHeaders']['content-type'].split(';')[1].split(',')
        #print(customlabels)
        image = {
            'S3Object' : {
                'Bucket' : bucket,
                'Name' : objectKey
            }
        }

        response = rekognition.detect_labels(Image = image)
        print(response)
        labels = list(map(lambda x : x['Name'], response['Labels'])) #+ customlabels
        timestamp = datetime.now().strftime('%Y-%d-%mT%H:%M:%S')

        esObject = {
            'objectKey' : objectKey,
            'bucket' : bucket,
            'createdTimesatamp' : timestamp,
            'labels' : labels
        }
        r = requests.put(url + objectKey, auth=awsauth, json=esObject, headers=headers)
        print(esObject)
        print(r.content)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
