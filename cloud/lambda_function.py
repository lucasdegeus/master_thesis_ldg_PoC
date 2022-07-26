import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
def lambda_handler(event, context):
   
    ALERT_TYPE = event['type']
    PATIENT_ID = event['patient_id']
    PATIENT_LOCATION = event['patient_location']
    TIME = event['timestamp']
    
    SENDER = 'YOUR_SENDER_EMAIL' # MUST BE A VERIFIED SES IDENTITY
    RECIPIENT = 'YOUR_RECEIVER_EMAIL_ADRESS' # MUST BE A VERIFIED SES IDENTITY
    AWS_REGION = "YOUR_AWS_REGION"
    
    SUBJECT = "[PATIENT " + ALERT_TYPE + "] - PATIENT ID:" + str(PATIENT_ID)
    
    if ALERT_TYPE == "ALERT":
        BODY_TEXT = "Patient in wheelchair has fallen over and needs urgent help, details:\nPatient ID: " + str(PATIENT_ID) + "\nPatient location: " + PATIENT_LOCATION + "\nTime of accident: " + str(datetime.fromtimestamp(TIME)) + "\nGoogle maps: https://www.google.com/maps/search/" + PATIENT_LOCATION
    elif ALERT_TYPE == "FIXED":
        BODY_TEXT = "Patient with patient ID " + str(PATIENT_ID) + " has resolved his/her problem and does no longer require assistance "
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    # Create SES client
    ses = boto3.client('ses', region_name=AWS_REGION)
    try:
        #Provide the contents of the email.
        response = ses.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
    # Display an error if something goes wrong. 
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    
  
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }