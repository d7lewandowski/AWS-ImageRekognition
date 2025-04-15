"""
The code is developed using reference from
https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/ex-lambda.html

"""

import json
import logging
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)



# Using boto3 S3 Client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    This code gets the S3 attributes from the trigger event,
    then invokes the rekognition api to detect labels.
    If the label matches the one present on the LABELS list,
    response is written in the S3 bucket with "Status":"Label Found",
    else the response is written in the S3 bucket with "Status":"Label Not Found".
    """
    logger.info(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    image = event['Records'][0]['s3']['object']['key']
    response = {'Status': 'Not Found', 'body': []}
    print(bucket)
    print(image)

    # Using rekognition boto3 client.
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html

    rekognition_client = boto3.client('rekognition')

    # Identify label
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_labels

    try:
        response_rekognition = rekognition_client.detect_labels(   # You are calling detect_labels API 
            Image={                                                # to analyzing Images Stored in an Amazon S3 Bucket
                'S3Object': {
                    'Bucket': bucket,
                    'Name': image
                }
            },
            MinConfidence=90                                        # MinConfidence specifies the minimum confidence  
        )                                                           # level for the labels to return.

    
        
        detected_labels = [] # Declaring empty label lists.
        

        for label in response_rekognition['Labels']:
            detected_labels.append(label['Name'].lower())

        label = detected_labels[0]

        if label:
            response['Status'] = f'Succes! {label} found'
            response['body'].append(detected_labels)
        else:
            response['Status'] = f'Faild! {label} not found'


        
                
    except Exception as error:
        print(error)

# Finally the file will be written in the S3 bucket output folder.
    output_key = f'output/{label}_rekognition_response.json'
    s3_client.put_object(
      Bucket=bucket,
      Key=output_key,
      Body=json.dumps(response, indent=4)
    )

    return response

'''
You can use below code to create test event to test
the Lambda function.
{
    "Records": [
                {
                "s3": {
                    "bucket": {
                    "name": "<Your_bucket_name>"
                    },
                    "object": {
                    "key": "input/ovni.png"
                    }
                }
                }
            ]
}
'''

# You can visit https://docs.aws.amazon.com/code-samples/latest/catalog/code-catalog-python-example_code-rekognition.html
# to get more sample codes.