#!/usr/local/bin/python

import sys
import json
import boto3

config = json.loads(sys.stdin.read())
source = config.get('source', {})

session = boto3.session.Session(
    aws_access_key_id       = source.get('aws_access_key_id'),
    aws_secret_access_key   = source.get('aws_secret_access_key'),
    region_name             = source.get('region')
)

if not (source.get('aws_role_arn')  is None):
    sts = session.client("sts")
    response = sts.assume_role(
        RoleArn=source.get('aws_role_arn'),
        RoleSessionName="counter-session"
    )
    credentials = response['Credentials']
    # Create a new session using the assumed role credentials
    session = boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    
obj = session.resource('s3').Object(source['bucket'], source['key'])

try:
    count = int(obj.get()['Body'].read())
except Exception:
    count = 0

res = []
for i in range(0, count + 1):
    res.append({'count': str(i)})

print(json.dumps(res))

