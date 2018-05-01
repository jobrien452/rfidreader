import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from raceOrder import raceOrder

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

#Setup db writes
client = boto3.resource('dynamodb', 
                        aws_access_key_id='AKIAIIOO6CX7UFZIVIEA',
                        aws_secret_access_key='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',
                        region_name='us-east-2')
table = client.Table('runtime2')
pe = "id, event, runtime, lane, rname"

runnerList = [{'lane':1,'rname':"Matt"},
              {'lane':2,'rname':"Jake"},
              {'lane':3,'rname':"Sam"},
              {'lane':4,'rname':"Steve"},
              {'lane':5,'rname':"Zach"}]

raceCount = 0
for race in raceOrder:
    print(race)
    for runner in runnerList:
        response = table.put_item(
            Item={
                    'id':(runner['lane']+(raceCount*5)),
                    'runtime':"00:00:00",
                    'event':race,
                    'lane':runner['lane'],
                    'rname':runner['rname']
                }
            )

        print("PutItem succeeded:")
        #print(json.dumps(response, indent=4, cls=DecimalEncoder))
    raceCount += 1


#try:
#    response = table.get_item(
#        Key={
#             'id':99,
#             'event':"Mens 100"
#             #'lane':rfidLaneMap[x][0]
#        }
#    )
#except ClientError as e:
#    print(e.response['Error']['Message'])
#else:
#    item = response['Item']
#    print("GetItem succeeded:")
#    print(json.dumps(item, indent=4, cls=DecimalEncoder))


#response = table.update_item(
#    Key={
#        'id':99,
#        'event':"Mens 100"
#    },
#    UpdateExpression="set runtime = :r",
#    ExpressionAttributeValues={
#        ':r': "00:00:07"
#    },
#    #ReturnValues="UPDATED_NEW"
#)
