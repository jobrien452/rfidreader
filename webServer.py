#!/usr/bin/python3
import boto3
import flask import Flask, render_template, request, abort
import flask.json import jsonify
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

#Amazon decimal encoder class
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

app = Flask(__name__)
client = boto3.resource('dynamodb', 
                        aws_access_key_id='AKIAIIOO6CX7UFZIVIEA',
                        aws_secret_access_key='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',
                        region_name='us-east-1')
table = client.Table('rundata')
pe = "id, runtime"

#scans dynamodb for every index and returns them
def scan():
    responses = []
    query = {'q':[]}
    responses.append(table.scan(ProjectionExpression=pe))
    while 'LastEvaluatedKey' in responses[-1]:
        responses.append(table.scan(ProjectionExpression=pe))
    for r in responses:
        for i in r['Items']:
            query['q'].append(json.dumps(i, cls=DecimalEncoder))
    return query
    

@app.route('/')
def display():
    print(scan())
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True)
