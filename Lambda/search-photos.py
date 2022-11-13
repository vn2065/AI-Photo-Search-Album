import json
import math
import dateutil.parser
import datetime
import time
import os
import boto3
import requests
import urllib.parse
from requests_aws4auth import AWS4Auth

host = 'https://search-photos-pvzbo2yvcxuovtbht53cme6hkm.us-east-1.es.amazonaws.com'  # the OpenSearch Service domain, with https://
index = 'album'
type = 'photo'
url = host + '/' + index + '/' + '/_search'
headers = {"Content-Type": "application/json"}
# host = 'https://search-photos-4xttynqx2xfjhzz4cvf4tlz2ma.us-west-2.es.amazonaws.com/'
region = 'us-east-1'
lex = boto3.client('lex-runtime', region_name=region)
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


def lambda_handler(event, context):
    print('event : ', event)
    print('context', context)
    q1 = event["queryStringParameters"]['q']

    # if(q1 == "searchAudio" ):
    #     q1 = convert_speechtotext()

    print("q1:", q1)
    labels = get_labels(q1)
    print("labels", labels)
    img_paths = []
    if len(labels) != 0:
        img_paths = list(set(get_photo_path(labels)))

    if len(img_paths) == 0:
        return {
            'statusCode': 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps('No Results found')
        }
    else:
        return {
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps(img_paths),
            'isBase64Encoded': False
        }


def get_labels(query):
    response = lex.post_text(
        botName='search_queries',
        botAlias='photoalbum',
        userId="1234567890",
        inputText=query
    )
    print("lex-response", response)

    labels = []
    if 'slots' not in response:
        print("No photo collection for query {}".format(query))
    else:
        print("slot: ", response['slots'])
        slot_val = response['slots']
        for key, value in slot_val.items():
            if value != None:
                labels.append(value)
    return labels


def get_photo_path(keys):
    resp = []
    for key in keys:
        if (key is not None) and key != '':
            query = {"query": {"match": {"labels": key}}, "fields": ["_id"], "_source": False}
            headers = {"Content-Type": "application/json"}
            r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
            resp.append(r.json())

    print(resp)
    output = []
    for r in resp:
        if 'hits' in r:
            for val in r['hits']['hits']:
                key = val['_id']
                if key not in output:
                    output.append(key)
    print(output)
    return output
