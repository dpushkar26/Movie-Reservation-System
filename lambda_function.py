import json
import boto3
import uuid
from botocore.exceptions import ClientError

# AWS Resources
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

SEAT_TABLE = dynamodb.Table('MovieSeats')
BOOKING_TABLE = dynamodb.Table('Bookings')

TOPIC_ARN = "arn:aws:sns:ap-south-1:344596481776:movie-ticket-confirmation"

# CORS Headers
HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Content-Type": "application/json"
}


def lambda_handler(event, context):
    try:

        print("REQUEST:", json.dumps(event))

        method = event["requestContext"]["http"]["method"]

        ###########################################################
        # Handle OPTIONS (Preflight Request)
        ###########################################################
        if method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": HEADERS,
                "body": json.dumps({
                    "message": "CORS preflight successful"
                })
            }

        ###########################################################
        # GET ALL SEATS
        ###########################################################
        elif method == "GET":

            response = SEAT_TABLE.scan()

            return {
                "statusCode": 200,
                "headers": HEADERS,
                "body": json.dumps(response["Items"])
            }

        ###########################################################
        # BOOK SEAT
        ###########################################################
        elif method == "POST":

            body = json.loads(event["body"])

            name = body["name"]
            email = body["email"]
            seat = body["seat"]

            # Prevent double booking
            try:

                SEAT_TABLE.update_item(
                    Key={
                        "seatNumber": seat
                    },
                    UpdateExpression="SET #s = :booked",
                    ConditionExpression="#s = :available",
                    ExpressionAttributeNames={
                        "#s": "status"
                    },
                    ExpressionAttributeValues={
                        ":available": "available",
                        ":booked": "booked"
                    }
                )

            except ClientError as e:

                if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                    return {
                        "statusCode": 400,
                        "headers": HEADERS,
                        "body": json.dumps({
                            "message": "Seat already booked"
                        })
                    }

                raise e

            booking_id = str(uuid.uuid4())

            BOOKING_TABLE.put_item(
                Item={
                    "bookingId": booking_id,
                    "name": name,
                    "email": email,
                    "seat": seat
                }
            )

            # Publish confirmation
            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="Ticket Confirmed",
                Message=f"""
Hello {name},

Your booking has been confirmed.

Seat Number: {seat}

Booking ID: {booking_id}

Enjoy your movie!
"""
            )

            return {
                "statusCode": 200,
                "headers": HEADERS,
                "body": json.dumps({
                    "message": "Ticket booked successfully",
                    "bookingId": booking_id
                })
            }

        ###########################################################
        # METHOD NOT ALLOWED
        ###########################################################
        else:
            return {
                "statusCode": 405,
                "headers": HEADERS,
                "body": json.dumps({
                    "message": "Method not allowed"
                })
            }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "headers": HEADERS,
            "body": json.dumps({
                "error": str(e)
            })
        }