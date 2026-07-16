import boto3

dynamodb = boto3.resource(
    'dynamodb',
    region_name='ap-south-1'
)

table = dynamodb.Table('MovieSeats')

rows = ['A','B','C','D','E']

for row in rows:
    for col in range(1,11):

        seat = f"{row}{col}"

        table.put_item(
            Item={
                'seatNumber': seat,
                'status': 'available'
            }
        )

        print(
            f"Inserted {seat}"
        )

print("Done")